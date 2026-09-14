from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFileDialog,
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
            "device has the data you want to keep. Point the folder below at "
            "a folder synced by Syncthing (or similar) between your devices."
        )
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)

        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        current = self.cloud_sync.get_cloud_folder()
        if current is not None:
            self.folder_edit.setText(str(current))
        self.folder_edit.setPlaceholderText("Cloud Sync Folder path...")
        self.folder_edit.editingFinished.connect(self.save_folder)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(browse_button)
        main_layout.addLayout(folder_layout)

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

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Cloud Sync Folder")
        if folder:
            self.folder_edit.setText(folder)
            self.save_folder()

    def save_folder(self):
        self.cloud_sync.set_cloud_folder(self.folder_edit.text().strip())
