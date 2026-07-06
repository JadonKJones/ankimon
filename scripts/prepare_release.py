import os
import json
import subprocess
import argparse
import requests
import re
from typing import List, Dict, Optional

# Sentinel written into a contributor's nickname/discord_id when a profile entry is
# auto-created for them (here as a release-time fallback, or by nudge-contributor.yml
# when a PR is opened). It means "the contributor has not reviewed this yet" and is
# treated as empty everywhere it would otherwise be displayed, so it never leaks into
# a changelog as a fake nickname or Discord ping.
PENDING_PROFILE = "PENDING_REVIEW"

# Commit-author / co-author emails containing any of these markers are bots or
# tools, never human contributors, so they're excluded from acknowledgement.
_BOT_EMAIL_MARKERS = ("[bot]", "github-actions", "noreply@anthropic.com")

# GitHub "noreply" commit emails encode the account login directly:
#   12345+login@users.noreply.github.com  (modern, id-prefixed)
#   login@users.noreply.github.com        (legacy)
# Reading the login from here credits a commit author without any API call.
_NOREPLY_EMAIL = re.compile(
    r'^(?:\d+\+)?([A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)@users\.noreply\.github\.com$'
)
_COAUTHOR_TRAILER = re.compile(r'^\s*co-authored-by:\s*.*<([^>]+)>', re.IGNORECASE)


def run_command(command: List[str], check: bool = True) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=check)
    return result.stdout.strip()

def get_previous_tag(current_version: str) -> Optional[str]:
    try:
        # Find all tags, sort by creation date
        tags = run_command(["git", "for-each-ref", "--sort=-creatordate", "--format=%(refname:short)", "refs/tags"]).split("\n")
        # Filter for standard version tags (e.g. starts with digit, and is not the current version)
        version_pattern = re.compile(r'^\d+(\.\d+)*(-[A-Z])?$')
        version_tags = [t.strip() for t in tags if version_pattern.match(t.strip()) and t.strip() != current_version]
        return version_tags[0] if version_tags else None
    except Exception as e:
        print(f"Error finding previous tag: {e}")
        return None


def fetch_prs_since_tag(repo: str, previous_tag: str) -> List[Dict]:
    # Get the date of the previous tag
    tag_date = run_command(["git", "log", "-1", "--format=%cI", previous_tag])
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    
    pull_requests = []
    page = 1
    
    while True:
        url = f"https://api.github.com/repos/{repo}/pulls?state=closed&base=main&sort=updated&direction=desc&per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        prs = response.json()
        
        if not prs:
            break
            
        for pr in prs:
            merged_at = pr.get("merged_at")
            if not merged_at or merged_at <= tag_date:
                continue
                
            # Filter out automated release PRs
            author = pr.get("user", {}).get("login", "")
            title = pr.get("title", "")
            if author == "github-actions[bot]" or author == "jules-invoke[bot]" or "bump version" in title.lower() or "release v" in title.lower():
                continue
                
            pull_requests.append(pr)
                
        # Since PRs are sorted by 'updated_at', if the oldest PR in this page was updated
        # before our tag_date, we can safely stop paginating.
        if prs[-1].get("updated_at", "") < tag_date:
            break
            
        page += 1

    return pull_requests


def parse_contributor_emails(git_log_text: str) -> List[str]:
    """Pull every contributor email out of ``git log`` output formatted as
    ``<RS>%ae%n%b`` per commit (RS = the \\x1e record separator): the commit's
    own author email plus the address on any ``Co-authored-by:`` trailer in its
    body. Kept pure (no git call) so it can be unit-tested with canned text."""
    emails: List[str] = []
    for record in git_log_text.split("\x1e"):
        record = record.strip("\n")
        if not record:
            continue
        lines = record.split("\n")
        emails.append(lines[0].strip())  # %ae — the commit author
        for line in lines[1:]:
            m = _COAUTHOR_TRAILER.match(line)
            if m:
                emails.append(m.group(1).strip())  # a co-author
    return emails


def logins_from_emails(emails: List[str]) -> set:
    """Resolve GitHub 'noreply' commit emails to their login (original case
    preserved), skipping bots, GitHub's ``web-flow`` merge author, and any
    private/non-noreply address that can't be mapped to a login offline."""
    logins: Dict[str, str] = {}  # lower-case login -> first-seen canonical case
    for email in emails:
        email = email.strip()
        if not email or "@" not in email:
            continue
        if any(marker in email.lower() for marker in _BOT_EMAIL_MARKERS):
            continue
        m = _NOREPLY_EMAIL.match(email)
        if not m:
            continue
        login = m.group(1)
        if login.lower() == "web-flow":  # GitHub's merge-commit author
            continue
        logins.setdefault(login.lower(), login)
    return set(logins.values())


def fetch_commit_contributors(previous_tag: Optional[str]) -> set:
    """Logins of everyone whose work landed on ``main`` since ``previous_tag`` —
    read from commit authors *and* ``Co-authored-by:`` trailers across the whole
    range. This credits contributors whose PRs targeted a feature/integration
    branch that was later merged in (their PR never had ``base=main``, so
    ``fetch_prs_since_tag`` can't see them) plus co-authors of ported commits,
    without giving any of them a changelog line-item."""
    if not previous_tag:
        return set()
    try:
        # \x1e (record separator) delimits commits so a multi-line body can't be
        # mistaken for the next commit's author line.
        raw = run_command(
            ["git", "log", f"{previous_tag}..HEAD", "--format=\x1e%ae%n%b"]
        )
    except Exception as e:
        print(f"Warning: could not read commit contributors from git history: {e}")
        return set()
    return logins_from_emails(parse_contributor_emails(raw))


def update_manifest(version: str):
    path = "src/Ankimon/manifest.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["version"] = version
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Updated {path} to {version}")

def update_contributors(logins):
    """Ensure every contributor login has an entry in ``.all-contributorsrc``,
    auto-creating a ``PENDING_REVIEW`` placeholder profile for anyone new so they
    can self-serve their nickname / Discord ID later (see nudge-contributor.yml).
    ``logins`` is any iterable of GitHub logins — base=main PR authors *and*
    branch-only / co-author contributors — so nobody who shipped code is left out
    of the credits or the README contributors table."""
    path = ".all-contributorsrc"
    if not os.path.exists(path):
        return
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Compare case-insensitively (GitHub logins are), but keep the canonical case.
    existing = {c["login"].lower() for c in data.get("contributors", [])}
    new_found = False
    
    for login in sorted(logins):
        if not login or login.lower() in existing or login.lower().endswith("[bot]"):
            continue
        print(f"Adding new contributor: {login}")
        data["contributors"].append({
            "login": login,
            "name": login,
            "avatar_url": f"https://github.com/{login}.png",
            "profile": f"https://github.com/{login}",
            "contributions": ["code"],
            "nickname": PENDING_PROFILE,
            "discord_id": PENDING_PROFILE
        })
        existing.add(login.lower())
        new_found = True
            
    if new_found:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

def generate_changelogs(version: str, pull_requests: List[Dict], highlights: str, nicknames: Dict, extra_contributors: Optional[set] = None):
    version_no_v = version.lstrip('v')
    os.makedirs("assets/changelogs", exist_ok=True)
    
    repo_url = "https://github.com/h0tp-ftw/ankimon"
    
    categories = {
        "critical": [],
        "enhancement": [],
        "bug": [],
        "documentation": [],
        "other": []
    }
    
    contributors = set()
    
    for pr in pull_requests:
        labels = [l["name"].lower() for l in pr.get("labels", [])]
        if any(l in labels for l in ["ignore-for-changelog", "exclude-from-changelog"]):
            continue
            
        login = pr["user"]["login"]
        contributors.add(login)
        nick_data = nicknames.get(login, {})
        
        # App Entry (needs explicit markdown links)
        pr_link = f"[#{pr['number']}]({repo_url}/pull/{pr['number']})"
        user_link = f"[@{login}](https://github.com/{login})"
        
        # Include nickname if it's different from the login and is not empty
        nick = nick_data.get("nickname")
        if nick and nick != login and nick != PENDING_PROFILE:
            user_link += f" ({nick})"
            
        entry = f"- {pr['title']} {pr_link} {user_link}"
        
        cat = "other"
        if "critical" in labels:
            cat = "critical"
        elif any(l in labels for l in ["enhancement", "feature", "type: enhancement"]):
            cat = "enhancement"
        elif any(l in labels for l in ["bug", "fix", "type: bug"]):
            cat = "bug"
        elif any(l in labels for l in ["documentation", "docs", "type: documentation"]):
            cat = "documentation"
            
        categories[cat].append(entry)
        
    # Build App Changelog (assets/changelogs/<version>.md)
    github_path = f"assets/changelogs/{version_no_v}.md"
    with open(github_path, "w", encoding="utf-8") as f:
        f.write(f"## 🌟 Ankimon v{version_no_v} 🌟\n\n")
        
        # Acknowledge everyone who contributed since the last release — including
        # people whose PRs targeted a feature/integration branch (never base=main)
        # and co-authors credited via Co-authored-by trailers. They're thanked in
        # this roll-call but deliberately get NO line-item in the Full changelog
        # below (their internal branch PRs aren't release-worthy entries).
        acknowledged = set(contributors)
        seen = {c.lower() for c in acknowledged}
        for login in (extra_contributors or ()):
            if login.lower() not in seen:
                acknowledged.add(login)
                seen.add(login.lower())

        thank_you = "Thank you to all contributors! <3"
        if acknowledged:
            c_links = []
            for u in sorted(acknowledged):
                nick = nicknames.get(u, {}).get('nickname')
                link = f"[@{u}](https://github.com/{u})"
                if nick and nick != u and nick != PENDING_PROFILE:
                    link += f" ({nick})"
                c_links.append(link)
            thank_you = f"A huge thank you to {', '.join(c_links)} for their contributions to this update! <3"
        
        f.write(f"{thank_you}\n\n")

        # Break down enhancements and bug fixes
        num_enhancements = len(categories["enhancement"])
        num_bugs = len(categories["bug"])
        # Count only PRs actually included in the changelog (excluding filtered ones)
        total_included_prs = sum(len(prs) for prs in categories.values())
        f.write(f"This release includes {total_included_prs} merged pull requests with {num_enhancements} enhancements and {num_bugs} bug fixes!\n\n")
        
        if highlights:
            f.write(f"{highlights}\n\n")
            
        # Discord Section
        f.write("### 💬 Join the [Discord](https://discord.gg/Vkvdawxd5s)!\n")
        f.write("Want to stay updated or get involved? Join our server for the latest updates on what's going on, or to get help from our custom AI assistant dedicated to Ankimon development!\n\n")
        
        f.write("— h0tp 💖\n\n***\n\n")
        f.write(f"## 📜 Full changelog — v{version_no_v}\n\n")
        
        if categories["critical"]:
            f.write("### 🚨 Critical Changes!\n\n")
            f.write("\n".join(categories["critical"]) + "\n\n")
        if categories["enhancement"]:
            f.write("### ✨ Features & Improvements!\n\n")
            f.write("\n".join(categories["enhancement"]) + "\n\n")
        if categories["bug"]:
            f.write("### 🐛 Bug Fixes & Stability!\n\n")
            f.write("\n".join(categories["bug"]) + "\n\n")
        if categories["documentation"]:
            f.write("### 📚 Documentation!\n\n")
            f.write("\n".join(categories["documentation"]) + "\n\n")
        if categories["other"]:
            f.write("### 🔧 Other Changes!\n\n")
            f.write("\n".join(categories["other"]) + "\n\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--highlights", default="")
    parser.add_argument("--psa", default="")
    parser.add_argument("--repo", default="h0tp-ftw/ankimon")
    args = parser.parse_args()
    
    prev_tag = get_previous_tag(args.version)
    print(f"Previous tag: {prev_tag}")
    
    prs = []
    if prev_tag:
        prs = fetch_prs_since_tag(args.repo, prev_tag)
    else:
        print("No previous tag found, skipping PR fetch.")
        
    nicknames = {}
    all_contrib_path = ".all-contributorsrc"
    if os.path.exists(all_contrib_path):
        with open(all_contrib_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for c in data.get("contributors", []):
                nicknames[c["login"]] = {
                    "nickname": c.get("nickname", ""),
                    "discord_id": c.get("discord_id", "")
                }
            
    # Contributors whose commits reached main via a feature/integration branch or
    # a Co-authored-by trailer — credited for acknowledgement, never as line-items.
    commit_contributors = fetch_commit_contributors(prev_tag)
    if commit_contributors:
        print(f"Branch/co-author contributors since {prev_tag}: {', '.join(sorted(commit_contributors))}")

    pr_logins = {pr.get("user", {}).get("login") for pr in prs}
    pr_logins.discard(None)

    update_manifest(args.version)
    update_contributors(pr_logins | commit_contributors)
    generate_changelogs(args.version, prs, args.highlights, nicknames, extra_contributors=commit_contributors)
    
    print("Release preparation complete!")

if __name__ == "__main__":
    main()
