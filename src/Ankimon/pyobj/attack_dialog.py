from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor

from ..utils import format_move_name
from ..functions.pokedex_functions import find_details_move
from ..functions.gui_functions import type_icon_path, move_category_path


class AttackDialog(QDialog):
    """Pick which of the current 4 moves to overwrite with ``new_attack``.

    Shows the full stat line (type, category, power, accuracy, PP, effect) for
    the new move and every current move side by side, so the player can tell
    which move is worth keeping. ``self.selected_attack`` holds the RAW move id
    of the move to replace; the dialog is rejected to discard the new move.
    """

    def __init__(self, attacks, new_attack, parent=None):
        super().__init__(parent)
        self.attacks = list(attacks)
        self.new_attack = new_attack
        self.selected_attack = None
        self.initUI()

    def _row_cells(self, move_name):
        move = find_details_move(move_name) or {}

        name_item = QTableWidgetItem(format_move_name(move_name))
        name_item.setData(Qt.ItemDataRole.UserRole, move_name)

        m_type = (move.get("type") or "Normal")
        type_item = QTableWidgetItem("")
        tp = type_icon_path(m_type.lower())
        if tp.exists():
            type_item.setIcon(QIcon(str(tp)))
        type_item.setToolTip(m_type)

        cat = move.get("category") or "Status"
        cat_item = QTableWidgetItem("")
        cp = move_category_path(cat)
        if cp.exists():
            cat_item.setIcon(QIcon(str(cp)))
        cat_item.setToolTip(cat)

        bp = move.get("basePower")
        bp_item = QTableWidgetItem("--" if bp in (None, 0, "0") else str(bp))
        bp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        acc = move.get("accuracy")
        if isinstance(acc, bool):
            acc_str = "--"
        elif isinstance(acc, int):
            acc_str = str(acc)
        else:
            acc_str = "100"
        acc_item = QTableWidgetItem(acc_str)
        acc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        pp = move.get("pp")
        pp_item = QTableWidgetItem(str(pp) if pp is not None else "5")
        pp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        from ..move_names import format_move_description
        desc_item = QTableWidgetItem(
            format_move_description(move_name, move.get("shortDesc") or "")
        )

        return [name_item, type_item, cat_item, bp_item, acc_item, pp_item, desc_item]

    def initUI(self):
        new_display = format_move_name(self.new_attack)
        self.setWindowTitle(f"Learn {new_display}?")
        self.setMinimumSize(820, 340)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                f"<b>{new_display}</b> wants to be learned, but moves are full.\n"
                "Compare the moves below and pick one to replace — or reject the new move."
            )
        )

        rows = [("new", self.new_attack)] + [("cur", a) for a in self.attacks]

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Type", "Category", "Power", "Accuracy", "PP", "Effect"]
        )
        self.table.setRowCount(len(rows))
        self.table.setIconSize(QSize(44, 26))
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        for r, (kind, name) in enumerate(rows):
            for c, cell in enumerate(self._row_cells(name)):
                if kind == "new":
                    cell.setForeground(QColor("#2563eb"))
                self.table.setItem(r, c, cell)
            if kind == "new":
                item = self.table.item(r, 0)
                item.setText(item.text() + "  (new)")

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.table.itemSelectionChanged.connect(self._update_btn)

        btns = QHBoxLayout()
        self.reject_btn = QPushButton("Reject new move")
        self.reject_btn.clicked.connect(self.reject)
        self.replace_btn = QPushButton("Replace selected move")
        self.replace_btn.setEnabled(False)
        self.replace_btn.setDefault(True)
        self.replace_btn.clicked.connect(self._confirm)
        btns.addWidget(self.reject_btn)
        btns.addStretch()
        btns.addWidget(self.replace_btn)
        layout.addLayout(btns)

    def _selected_current_move(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return None
        row = sel[0].row()
        if row == 0:  # the new move itself — not a valid replace target
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _update_btn(self):
        move = self._selected_current_move()
        self.replace_btn.setEnabled(move is not None)
        if move:
            self.replace_btn.setText(f"Replace {format_move_name(move)}")
        else:
            self.replace_btn.setText("Replace selected move")

    def _confirm(self):
        move = self._selected_current_move()
        if move is None:
            return
        self.selected_attack = move
        self.accept()
