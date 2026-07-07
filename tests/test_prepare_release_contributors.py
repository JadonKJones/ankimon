"""Unit tests for contributor acknowledgement in scripts/prepare_release.py.

These cover the pure parsing helpers that let the release changelog credit
people whose work reached ``main`` *without* a base=main PR — i.e. authors of
PRs that targeted a feature/integration branch, and co-authors credited via
``Co-authored-by:`` trailers. Those contributors are acknowledged (thank-you
roll-call + auto-onboarded to .all-contributorsrc) but get no changelog
line-item; only real base=main PRs become line-items.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import prepare_release as pr  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

RS = "\x1e"  # record separator prepare_release uses between commits


# --- version validation + timezone-aware date compare (release-review fixes) ---


def test_version_regex_accepts_valid_incl_v_prefix():
    for v in ("2.03", "v2.03", "2.02-E", "1.3962-E", "2", "10.0"):
        assert pr._VERSION_RE.match(v), v


def test_version_regex_rejects_malformed_and_traversal():
    for v in ("", "sprites", "../etc/passwd", "2.03; rm -rf /", "v", "2.03-e", "2.0-EE"):
        assert not pr._VERSION_RE.match(v), v


def test_iso_to_utc_normalizes_z_and_offsets():
    assert pr._iso_to_utc("2026-07-05T12:00:00Z") == pr._iso_to_utc("2026-07-05T12:00:00+00:00")
    assert pr._iso_to_utc("2026-07-05T12:00:00+02:00") == datetime(2026, 7, 5, 10, 0, tzinfo=timezone.utc)


def test_iso_to_utc_empty_and_invalid_are_none():
    assert pr._iso_to_utc(None) is None
    assert pr._iso_to_utc("") is None
    assert pr._iso_to_utc("not-a-date") is None


def test_iso_to_utc_fixes_cross_timezone_ordering():
    # The exact bug: git '%cI' emits a local offset, the API emits UTC 'Z'. A PR
    # merged AFTER the tag can sort BEFORE it as raw strings; as UTC datetimes it
    # orders correctly, so the PR is no longer wrongly skipped.
    tag_local = "2026-07-05T14:00:00+02:00"   # == 12:00 UTC
    merged_api = "2026-07-05T13:00:00Z"       # 13:00 UTC — genuinely later
    assert merged_api < tag_local                                 # raw-string compare is WRONG
    assert pr._iso_to_utc(merged_api) > pr._iso_to_utc(tag_local)  # datetime compare is RIGHT


def test_login_from_id_prefixed_noreply():
    assert pr.logins_from_emails(
        ["74561421+hakimh2@users.noreply.github.com"]
    ) == {"hakimh2"}


def test_login_from_legacy_noreply():
    assert pr.logins_from_emails(["someone@users.noreply.github.com"]) == {"someone"}


def test_login_case_is_preserved():
    # GitHub logins are case-insensitive, but we keep the canonical display case.
    assert pr.logins_from_emails(
        ["66210743+AIbrahimv2@users.noreply.github.com"]
    ) == {"AIbrahimv2"}


def test_hyphenated_login():
    assert pr.logins_from_emails(
        ["141889580+h0tp-ftw@users.noreply.github.com"]
    ) == {"h0tp-ftw"}


def test_bots_and_tools_are_skipped():
    emails = [
        "41898282+github-actions[bot]@users.noreply.github.com",
        "198982749+google-labs-jules[bot]@users.noreply.github.com",
        "noreply@anthropic.com",  # Claude co-author trailer
        "noreply@github.com",     # non-users.noreply address
    ]
    assert pr.logins_from_emails(emails) == set()


def test_web_flow_merge_author_skipped():
    assert pr.logins_from_emails(["web-flow@users.noreply.github.com"]) == set()


def test_private_non_noreply_email_ignored():
    # Can't be resolved to a login offline; skipped here. Such an author is still
    # credited if they also opened a base=main PR (handled elsewhere).
    assert pr.logins_from_emails(["jane@example.com"]) == set()


def test_dedup_is_case_insensitive_first_seen_wins():
    got = pr.logins_from_emails([
        "1+Someon1e@users.noreply.github.com",
        "2+someon1e@users.noreply.github.com",
    ])
    assert got == {"Someon1e"}


def test_parse_author_and_coauthor_trailers():
    log = (
        f"{RS}141889580+h0tp-ftw@users.noreply.github.com\n"
        "feat: port a BRRRR feature\n"
        "\n"
        "Co-authored-by: Jupytrr <291307696+jupiterslegacy@users.noreply.github.com>\n"
        "Co-Authored-By: Hakimh2 <74561421+hakimh2@users.noreply.github.com>\n"
        f"{RS}74561421+hakimh2@users.noreply.github.com\n"
        "fix: a solo commit\n"
    )
    logins = pr.logins_from_emails(pr.parse_contributor_emails(log))
    # The co-author (jupiterslegacy) is the person a base=main PR query can't see.
    assert logins == {"h0tp-ftw", "jupiterslegacy", "hakimh2"}


def test_coauthor_trailer_is_case_insensitive():
    log = (
        f"{RS}1+author@users.noreply.github.com\n"
        "subject\n\n"
        "co-authored-by: X <9+lowertrailer@users.noreply.github.com>\n"
    )
    assert pr.logins_from_emails(pr.parse_contributor_emails(log)) == {
        "author",
        "lowertrailer",
    }


def test_empty_inputs():
    assert pr.parse_contributor_emails("") == []
    assert pr.logins_from_emails([]) == set()
    assert pr.fetch_commit_contributors(None) == set()
