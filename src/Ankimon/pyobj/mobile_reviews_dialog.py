import os
import math
import time
from aqt import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, mw
from aqt.qt import Qt

class MobileReviewsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mobile & Web Reviews")
        self.resize(400, 220)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 13px; margin: 10px;")
        self.layout.addWidget(self.info_label)

        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-size: 13px; margin: 10px; color: #58a6ff;")
        self.result_label.setVisible(False)
        self.layout.addWidget(self.result_label)

        self.btn_layout = QHBoxLayout()
        self.layout.addLayout(self.btn_layout)

        self.resolve_btn = QPushButton("Resolve All Reviews")
        self.resolve_btn.setStyleSheet("font-weight: bold; padding: 6px;")
        self.resolve_btn.clicked.connect(self.on_resolve)
        self.btn_layout.addWidget(self.resolve_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.btn_layout.addWidget(self.close_btn)

        self.update_count()

    def update_count(self):
        count = mw.ankimon_db.get_pending_mobile_count()
        if count > 0:
            self.info_label.setText(
                f"You have <b>{count}</b> pending reviews from AnkiMobile/AnkiWeb.<br><br>"
                "Would you like to simulate their battles and apply catches, experience, and cash to your local collection?"
            )
            self.resolve_btn.setEnabled(True)
        else:
            self.info_label.setText(
                "No pending reviews from AnkiMobile/AnkiWeb found.<br><br>"
                "Make sure you sync Anki so your mobile reviews are downloaded first!"
            )
            self.resolve_btn.setEnabled(False)

    def on_resolve(self):
        self.resolve_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.info_label.setText("Simulating battles, please wait...")
        
        # Keep UI responsive
        mw.app.processEvents()

        try:
            from ..functions.mobile_sync import resolve_all
            from ..services import services
            
            result = resolve_all(
                db=mw.ankimon_db,
                settings_obj=mw.settings_obj,
                tracker=getattr(mw, "ankimon_tracker_obj", None),
                trainer_card=getattr(mw, "trainer_card", None),
                main_pokemon=getattr(mw, "main_pokemon", None),
                logger=services.logger,
                day_cutoff=mw.col.sched.day_cutoff if (mw and mw.col) else 0,
            )

            if result.get("success"):
                resolved = result.get("resolved", 0)
                reviews = result.get("reviews_processed", 0)
                xp = result.get("xp_gained", 0)
                cash = result.get("cash_gained", 0)
                txp = result.get("trainer_xp_gained", 0)
                caught = result.get("caught_list", [])

                summary = (
                    f"⚔ <b>Successfully resolved {resolved} battles</b> (from {reviews} reviews)!<br><br>"
                    f"💰 <b>Gained:</b> {xp} XP, {cash}¥, and {txp} Trainer XP.<br>"
                )
                if caught:
                    summary += f"🎉 <b>Caught:</b> {', '.join(caught)}"

                self.result_label.setText(summary)
                self.result_label.setVisible(True)
                self.info_label.setText("Resolution complete!")
            else:
                QMessageBox.warning(self, "Error", f"Failed to resolve reviews: {result.get('error', 'Unknown error')}")
                self.info_label.setText("Resolution failed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during resolution: {e}")
            self.info_label.setText("An error occurred.")
        
        self.close_btn.setEnabled(True)
        self.update_count()
