import json
from pathlib import Path
from typing import Optional

from aqt import mw
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QDialogButtonBox,
    Qt,
)

from ..pyobj.settings import Settings


BRRR_DEPRECATION_SETTING_KEY = "misc.brrr_deprecation_notice_shown"
MESSAGE_TITLE = "Ankimon — Important Channel Update"


def get_message_html() -> str:
    """Generate theme-aware HTML content for the deprecation notice."""
    try:
        from aqt.theme import theme_manager
        is_dark = theme_manager.night_mode
    except Exception:
        is_dark = False

    header_color = "#4fc3f7" if is_dark else "#1976d2"
    text_color = "#e0e0e0" if is_dark else "#212121"

    return f"""
<div style="font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; color: {text_color};">
    <h2 style="color: {header_color}; margin-top: 0;">Thank You for Testing BRRRR_Experimental!</h2>
    <p>Thank you for participating in testing on the <b>BRRRR_Experimental</b> branch!</p>
    <p>I (BRRRRRRR) loved my time working on Ankimon and building features for the community. It saddens me to say that I have decided not to work on Ankimon for the foreseeable future. However, active development is continuing with other contributors.</p>
    <p>Your installation has been <b>automatically migrated to the main branch</b>. You do not need to take any manual action.</p>
    <p>Moving forward, you will automatically receive every update pushed to the <b>main</b> branch, exactly like you did on BRRRR_Experimental.</p>
</div>
"""


class BRRRDeprecationNoticeDialog(QDialog):
    """One-time pop-up notification shown to users migrated from BRRRR_Experimental to main."""

    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle(MESSAGE_TITLE)
        self.setMinimumWidth(480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(get_message_html())
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)


def check_and_show_brrr_deprecation_notice(parent=None) -> bool:
    """Show the BRRRR_Experimental deprecation notice if it hasn't been shown yet.

    Returns True if the notice was displayed, False otherwise.
    """
    try:
        settings = Settings()
        if settings.get(BRRR_DEPRECATION_SETTING_KEY, False):
            return False

        # Mark as shown before presenting dialog to prevent re-entrancy
        settings.set(BRRR_DEPRECATION_SETTING_KEY, True)

        from ..services import services
        if hasattr(services, "ui") and hasattr(services.ui, "notify_brrr_deprecation"):
            services.ui.notify_brrr_deprecation()
        else:
            dialog = BRRRDeprecationNoticeDialog(parent=parent)
            dialog.exec()
        return True
    except Exception as e:
        print(f"Ankimon: Error showing BRRRR_Experimental deprecation notice: {e}")
        return False
