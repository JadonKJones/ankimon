with open("src/Ankimon/singletons.py", "r") as f:
    content = f.read()

import re

new_content = re.sub(
    r'def notify_stats_changed\(\):\n\s*try:\n.*?pass\n\n\s*"""Tell the open',
    r'''def notify_stats_changed():
    try:
        from .services import services
        if getattr(services, 'trainer_card', None):
            services.trainer_card.sync_leaderboard()
    except Exception as e:
        print(f"[Ankimon] Leaderboard sync from notify_stats_changed failed: {e}")

    """Tell the open''',
    content,
    flags=re.DOTALL
)

with open("src/Ankimon/singletons.py", "w") as f:
    f.write(new_content)
