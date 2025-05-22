from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QLabel, QFrame,
    QToolBar, QAction
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
import sys
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Asset Manager")
        self.setGeometry(100, 100, 1100, 600)

        # === Toolbar ===
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))

        # Actions
        home_action = QAction(QIcon("home.png"), "Home", self)
        add_action = QAction(QIcon("add.png"), "Add Asset", self)
        delete_action = QAction(QIcon("delete.png"), "Delete Asset", self)

        toolbar.addAction(home_action)
        toolbar.addAction(add_action)
        toolbar.addAction(delete_action)
        self.addToolBar(toolbar)

        # === Central Widget ===
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # === Sidebar ===
        sidebar = QFrame()
        sidebar.setFixedWidth(350)
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar_layout = QVBoxLayout(sidebar)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.search_table)
        sidebar_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Description', 'Part Number'])

        # Generate 100 fake entries
        device_types = [
            "iPhone 13", "iPhone 14", "Samsung Galaxy S22", "Samsung Note 20",
            "LG Velvet", "Huawei P50", "Raspberry Pi 4", "Google Pixel 6",
            "MacBook Pro", "Dell XPS 13", "Asus ROG Phone", "OnePlus 11"
        ]
        self.data = [
            (random.choice(device_types), f"PN-{random.randint(10000, 99999)}")
            for _ in range(100)
        ]

        self.populate_table(self.data)

        # Handle row click
        self.table.cellClicked.connect(self.display_item_details)

        sidebar_layout.addWidget(self.table)

        # === Detail Panel (Right) ===
        content = QFrame()
        content.setFrameShape(QFrame.StyledPanel)
        content_layout = QVBoxLayout(content)

        self.description_field = QLineEdit()
        self.part_number_field = QLineEdit()

        content_layout.addWidget(QLabel("Description:"))
        content_layout.addWidget(self.description_field)
        content_layout.addWidget(QLabel("Part Number:"))
        content_layout.addWidget(self.part_number_field)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

    def populate_table(self, data):
        self.table.setRowCount(len(data))
        for row, (desc, part_num) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(desc))
            self.table.setItem(row, 1, QTableWidgetItem(part_num))
        self.table.resizeColumnsToContents()

    def search_table(self):
        query = self.search_input.text().strip().lower()
        self.filtered_data = [
            (desc, part_num) for desc, part_num in self.data
            if query in desc.lower() or query in part_num.lower()
        ]
        self.populate_table(self.filtered_data)

    def display_item_details(self, row, column):
        item = self.table.item(row, 0).text()
        part = self.table.item(row, 1).text()
        self.description_field.setText(item)
        self.part_number_field.setText(part)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
