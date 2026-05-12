import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem
)
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QIcon, QPainter, QColor

from ..functions.pokedex_functions import find_details_move
from ..functions.gui_functions import type_icon_path, move_category_path
from ..utils import format_move_name

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            # Handle '--', '---' or empty strings as 0
            t1 = self.text().replace('--', '0').replace('---', '0').replace('None', '0').strip()
            t2 = other.text().replace('--', '0').replace('---', '0').replace('None', '0').strip()
            if not t1: t1 = '0'
            if not t2: t2 = '0'
            return float(t1) < float(t2)
        except ValueError:
            return super().__lt__(other)

class IconDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Draw background
        option.widget.style().drawControl(option.widget.style().ControlElement.CE_ItemViewItem, option, painter)
        
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon:
            # Determine icon size from table
            icon_size = option.decorationSize
            if icon_size.width() <= 0:
                icon_size = QSize(50, 30)
            
            rect = option.rect
            x = rect.x() + (rect.width() - icon_size.width()) // 2
            y = rect.y() + (rect.height() - icon_size.height()) // 2
            
            icon.paint(painter, QRect(x, y, icon_size.width(), icon_size.height()), Qt.AlignmentFlag.AlignCenter)

class MovePickerDialog(QDialog):
    def __init__(self, pokemon_name, all_moves, current_moves, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Learn a Move")
        self.setMinimumSize(1000, 600)
        self.setStyleSheet("font-size: 15px;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        header_label = QLabel(pokemon_name)
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #60a5fa;")
        layout.addWidget(header_label)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter moves by name...")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self.filter_moves)
        layout.addWidget(self.search_bar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Category", "Power", "Accuracy", "PP", "Details"])
        self.table.setIconSize(QSize(50, 30))
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(45)
        
        # Center icons
        self.icon_delegate = IconDelegate()
        self.table.setItemDelegateForColumn(1, self.icon_delegate)
        self.table.setItemDelegateForColumn(2, self.icon_delegate)
        
        # Sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Name
        
        for i, width in [(1, 60), (2, 60), (3, 70), (4, 80), (5, 50)]:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(i, width)
            
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)          # Details
        
        self.table.setStyleSheet("QTableWidget { gridline-color: #1e293b; background: #0f172a; font-size: 15px; color: white; } QHeaderView::section { font-size: 15px; font-weight: bold; background-color: #1e293b; color: white; }")
        self.table.setSortingEnabled(True)
        
        self.all_moves = [m for m in all_moves if m not in current_moves]
        self.move_data_cache = {}
        for move_name in self.all_moves:
            self.move_data_cache[move_name] = find_details_move(move_name)
            
        layout.addWidget(self.table)
        
        self.buttons = QHBoxLayout()
        self.learn_btn = QPushButton("Learn Move")
        self.learn_btn.setEnabled(False)
        self.learn_btn.setFixedSize(120, 30)
        self.learn_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedSize(100, 30)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.buttons.addStretch()
        self.buttons.addWidget(self.learn_btn)
        self.buttons.addWidget(self.cancel_btn)
        layout.addLayout(self.buttons)
        
        self.table.itemSelectionChanged.connect(self.update_btn_state)
        self.populate_moves()

    def update_btn_state(self):
        self.learn_btn.setEnabled(len(self.table.selectedItems()) > 0)

    def populate_moves(self, filter_text=""):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        filter_text = filter_text.lower()
        
        row_idx = 0
        for move_name in self.all_moves:
            if filter_text and filter_text not in move_name.lower():
                continue
                
            move = self.move_data_cache.get(move_name)
            if not move: continue
            
            self.table.insertRow(row_idx)
            
            # Name
            name_item = QTableWidgetItem(format_move_name(move_name))
            name_item.setData(Qt.ItemDataRole.UserRole, move_name)
            
            # Type Icon
            m_type = move.get("type", "Normal")
            type_item = QTableWidgetItem("")
            t_icon_path = type_icon_path(m_type.lower())
            if t_icon_path.exists():
                type_item.setIcon(QIcon(str(t_icon_path)))
            type_item.setToolTip(m_type)
            
            self.table.setItem(row_idx, 0, name_item)
            self.table.setItem(row_idx, 1, type_item)
            
            # Category Icon
            cat = move.get("category", "Status")
            cat_item = QTableWidgetItem("")
            c_icon_path = move_category_path(cat)
            if c_icon_path.exists():
                cat_item.setIcon(QIcon(str(c_icon_path)))
            cat_item.setToolTip(cat)
            self.table.setItem(row_idx, 2, cat_item)
            
            # BP
            bp = str(move.get("basePower", "0"))
            bp_item = NumericTableWidgetItem(bp if bp != "0" else "--")
            bp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, bp_item)
            
            # Accuracy
            acc = move.get("accuracy")
            acc_str = str(acc) if isinstance(acc, int) else "100"
            acc_item = NumericTableWidgetItem(acc_str if acc_str != "True" else "---")
            acc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, acc_item)
            
            # PP
            pp_item = NumericTableWidgetItem(str(move.get("pp", "5")))
            pp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, pp_item)
            
            # Description
            desc_item = QTableWidgetItem(move.get("shortDesc", ""))
            self.table.setItem(row_idx, 6, desc_item)
            
            row_idx += 1
            
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    def filter_moves(self, text):
        self.populate_moves(text)

    def get_selected_move(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        return self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
