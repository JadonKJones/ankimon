from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
)
from PyQt6.QtCore import Qt

from ..pyobj.cloud_sync import CloudSync


class CloudSyncDialog(QDialog):
    def __init__(self, cloud_sync: CloudSync, parent=None):
        super().__init__(parent)
        self.cloud_sync = cloud_sync
        self.setWindowTitle("Ankimon Cloud Sync")
        self.setMinimumWidth(480)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        info_label = QLabel(
            "Push and Pull are manual and one-directional: you decide which "
            "device has the data you want to keep. Add the folder below to "
            "Syncthing (or similar) on EVERY device — it's the same path "
            "everywhere, so there's nothing else to set up."
        )
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)

        self.folder_label = QLabel(str(self.cloud_sync.get_cloud_folder()))
        self.folder_label.setWordWrap(True)
        self.folder_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        main_layout.addWidget(self.folder_label)

        button_layout = QHBoxLayout()
        push_button = QPushButton("Push to Cloud")
        push_button.setObjectName("PushButton")
        push_button.clicked.connect(self.cloud_sync.push)
        pull_button = QPushButton("Pull from Cloud")
        pull_button.setObjectName("PullButton")
        pull_button.clicked.connect(self.cloud_sync.pull)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        button_layout.addWidget(push_button)
        button_layout.addWidget(pull_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
