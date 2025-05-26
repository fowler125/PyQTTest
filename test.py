from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QLabel, QFrame,
    QToolBar, QAction, QGroupBox, QTabWidget, QComboBox, QStackedWidget,
    QPushButton, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSize
from datetime import datetime, timedelta
import sys
import random
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Asset Manager")
        self.setGeometry(100, 100, 1200, 800)

        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.addAction(QAction(QIcon(resource_path("home.png")), "Home", self))
        toolbar.addAction(QAction(QIcon(resource_path("add.png")), "Add Asset", self))
        toolbar.addAction(QAction(QIcon(resource_path("delete.png")), "Delete Asset", self))
        self.addToolBar(toolbar)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        sidebar = QFrame()
        sidebar.setFixedWidth(460)
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar_layout = QVBoxLayout(sidebar)

        search_group = QGroupBox("Quick Search")
        search_layout = QVBoxLayout(search_group)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        search_group.setFont(font)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.textChanged.connect(self.search_table)
        search_layout.addWidget(self.search_input)
        sidebar_layout.addWidget(search_group)

        device_types = [
            "iPhone 13", "Samsung Galaxy S22", "LG Velvet", "Huawei P50",
            "Raspberry Pi 4", "Google Pixel 6", "MacBook Pro", "Dell XPS 13"
        ]

        self.data = []
        for _ in range(500):
            desc = random.choice(device_types)
            part = f"PN-{random.randint(10000, 99999)}"
            last_cal = datetime.today() - timedelta(days=random.randint(0, 30))
            due_cal = last_cal + timedelta(days=30)
            self.data.append((desc, part, last_cal.strftime("%Y-%m-%d"), due_cal.strftime("%Y-%m-%d")))

        self.filtered_data = self.data.copy()
        self.recently_viewed = []

        self.assets_stack = QStackedWidget()

        assets_group = QGroupBox("Assets")
        assets_layout = QVBoxLayout()
        assets_group.setLayout(assets_layout)

        self.assets_title = QLabel("Asset Table")
        self.assets_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 6px;")
        assets_layout.addWidget(self.assets_title)

        # === Page 0: Search Results + Recently Viewed ===
        page0 = QWidget()
        page0_layout = QVBoxLayout(page0)

        search_label = QLabel("Search Results")
        search_label.setFont(QFont("Arial", 12, QFont.Bold))
        page0_layout.addWidget(search_label)

        self.search_results_table = QTableWidget()
        self.search_results_table.setColumnCount(4)
        self.search_results_table.setHorizontalHeaderLabels([
            'Description', 'Part Number', 'Last Calibration', 'Calibration Due'
        ])
        self.search_results_table.setMinimumHeight(250)
        self.search_results_table.cellClicked.connect(self.display_item_details)
        page0_layout.addWidget(self.search_results_table)

        recent_label = QLabel("Recently Viewed")
        recent_label.setFont(QFont("Arial", 12, QFont.Bold))
        page0_layout.addWidget(recent_label)

        self.recently_viewed_table = QTableWidget()
        self.recently_viewed_table.setColumnCount(4)
        self.recently_viewed_table.setHorizontalHeaderLabels([
            'Description', 'Part Number', 'Last Calibration', 'Calibration Due'
        ])
        self.recently_viewed_table.setMinimumHeight(200)
        page0_layout.addWidget(self.recently_viewed_table)

        self.assets_stack.addWidget(page0)

        # === Page 1: Calibration Summary ===
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            'Description', 'Part Number', 'Last Calibration', 'Calibration Due'
        ])
        self.table.cellClicked.connect(self.display_item_details)
        self.assets_stack.addWidget(self.table)

        assets_layout.addWidget(self.assets_stack)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(10)

        prev_button = QPushButton("<- Prev")
        next_button = QPushButton("Next ->")

        prev_button.setFixedHeight(24)
        next_button.setFixedHeight(24)

        prev_button.clicked.connect(lambda: self.assets_stack.setCurrentIndex(
            (self.assets_stack.currentIndex() - 1) % self.assets_stack.count()
        ))
        next_button.clicked.connect(lambda: self.assets_stack.setCurrentIndex(
            (self.assets_stack.currentIndex() + 1) % self.assets_stack.count()
        ))

        nav_layout.addWidget(prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(next_button)
        assets_layout.addLayout(nav_layout)

        sidebar_layout.addWidget(assets_group)
        self.assets_stack.currentChanged.connect(self.update_assets_title)
        self.update_assets_title()

        content = QFrame()
        content.setFrameShape(QFrame.StyledPanel)
        content_layout = QVBoxLayout(content)

        tabs = QTabWidget()
        content_layout.addWidget(tabs)

        tab_asset_info = QWidget()
        tab_asset_layout = QVBoxLayout(tab_asset_info)

        group_box = QGroupBox("Asset Info")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        group_box.setFont(font)
        group_layout = QVBoxLayout(group_box)

        label_style = """
            QLabel {
                border: 1px solid gray;
                background-color: #f0f0f0;
                padding: 10px 20px;
                font-size: 16px;
                min-width: 250px;
            }
        """

        self.description_label = QLabel("Description: —")
        self.description_label.setFrameShape(QFrame.Panel)
        self.description_label.setFrameShadow(QFrame.Raised)
        self.description_label.setLineWidth(2)
        self.description_label.setStyleSheet(label_style)
        group_layout.addWidget(self.description_label)

        row_two_layout = QHBoxLayout()

        self.part_number_label = QLabel("Part Number: —")
        self.part_number_label.setFrameShape(QFrame.Panel)
        self.part_number_label.setFrameShadow(QFrame.Raised)
        self.part_number_label.setLineWidth(2)
        self.part_number_label.setStyleSheet(label_style)

        self.serial_number_label = QLabel("Serial Number: —")
        self.serial_number_label.setFrameShape(QFrame.Panel)
        self.serial_number_label.setFrameShadow(QFrame.Raised)
        self.serial_number_label.setLineWidth(2)
        self.serial_number_label.setStyleSheet(label_style)

        row_two_layout.addWidget(self.part_number_label)
        row_two_layout.addSpacing(30)
        row_two_layout.addWidget(self.serial_number_label)

        group_layout.addLayout(row_two_layout)
        tab_asset_layout.addWidget(group_box)
        tab_asset_layout.addStretch()
        tabs.addTab(tab_asset_info, "Asset Info")

        tab_other = QWidget()
        tab_other_layout = QVBoxLayout(tab_other)
        tab_other_layout.addWidget(QLabel("Other content here..."))
        tabs.addTab(tab_other, "More Info")

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

        self.populate_table(self.filtered_data, self.table)

    from PyQt5.QtGui import QColor

    def populate_table(self, data, table):
        table.setRowCount(len(data))
        for row, (desc, part_num, last_cal, due_cal) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(desc))
            table.setItem(row, 1, QTableWidgetItem(part_num))
            table.setItem(row, 2, QTableWidgetItem(last_cal))
            table.setItem(row, 3, QTableWidgetItem(due_cal))

            # === Apply Gradient Based on Calibration Due ===
            try:
                due_date = datetime.strptime(due_cal, "%Y-%m-%d")
                days_left = (due_date - datetime.today()).days

                if days_left < 0:
                    color = QColor(255, 100, 100)  # Red
                elif days_left <= 7:
                    color = QColor(255, 165, 0)    # Orange
                else:
                    color = QColor(144, 238, 144)  # Light Green

                for col in range(4):
                    table.item(row, col).setBackground(color)
            except Exception as e:
                print(f"Error parsing date: {e}")

        table.resizeColumnsToContents()


    def search_table(self):
        query = self.search_input.text().strip().lower()
        self.assets_stack.setCurrentIndex(0)

        if not query:
            self.search_results_table.setRowCount(0)  # Clear the table
            return

        self.filtered_data = [
            item for item in self.data
            if query in item[0].lower() or query in item[1].lower()
        ]
        self.populate_table(self.filtered_data, self.search_results_table)



    def display_item_details(self, row, column):
        current_index = self.assets_stack.currentIndex()
        table = self.search_results_table if current_index == 0 else self.table
        item = (
            table.item(row, 0).text(),
            table.item(row, 1).text(),
            table.item(row, 2).text(),
            table.item(row, 3).text(),
        )
        desc, part, *_ = item
        serial = f"SN-{random.randint(100000, 999999)}"
        self.description_label.setText(f"Description: {desc}")
        self.part_number_label.setText(f"Part Number: {part}")
        self.serial_number_label.setText(f"Serial Number: {part}")

        # Update recently viewed
        if item not in self.recently_viewed:
            self.recently_viewed.insert(0, item)
            self.recently_viewed = self.recently_viewed[:20]  # Limit to 20 items
            self.populate_table(self.recently_viewed, self.recently_viewed_table)

    def update_assets_title(self):
        titles = {
            0: "Search Results / Recently Viewed",
            1: "Calibration Summary"
        }
        index = self.assets_stack.currentIndex()
        self.assets_title.setText(titles.get(index, ""))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
