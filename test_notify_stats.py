import sys
import threading
from unittest.mock import Mock, patch
sys.path.append("src")

with patch('Ankimon.utils.is_main_thread', return_value=True):
    import Ankimon.singletons
    from Ankimon.singletons import notify_stats_changed

print(notify_stats_changed.__doc__)
