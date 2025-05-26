import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QHBoxLayout, QVBoxLayout, QSizePolicy, QMessageBox,
    QTableWidget, QTableWidgetItem, QMenu
)
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QDrag
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal


class DraggableBox(QPushButton):
    def __init__(self, width_ratio, height_ratio):
        super().__init__()
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.setText(f"{width_ratio:.1f}×{height_ratio:.1f}")
        self.setFixedSize(80, int(80 * height_ratio))
        self.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"{self.width_ratio},{self.height_ratio}")
            drag.setMimeData(mime)
            drag.exec_(Qt.CopyAction)


class PlaceholderPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(120)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Drag Boxes</b>"))
        layout.addStretch()
        for _ in range(6):
            w = random.uniform(0.2, 0.3)
            h = random.uniform(0.5, 0.9)
            box = DraggableBox(width_ratio=w, height_ratio=h)
            layout.addWidget(box)
        layout.addStretch()
        self.setLayout(layout)


class ProductTableWidget(QTableWidget):
    def __init__(self):
        super().__init__(0, 3)
        self.setHorizontalHeaderLabels(["Shelf", "Size", "Index"])
        self.setMinimumWidth(200)
        self.cellClicked.connect(self.row_selected)
        self.selection_callback = None

    def row_selected(self, row, _col):
        shelf = int(self.item(row, 0).text()) - 1
        index = int(self.item(row, 2).text())
        if self.selection_callback:
            self.selection_callback(shelf, index)

    def update_from_inventory(self, items):
        self.setRowCount(0)
        for shelf_index, boxes in items.items():
            for i, (x_ratio, width, height) in enumerate(boxes):
                self.insertRow(self.rowCount())
                self.setItem(self.rowCount() - 1, 0, QTableWidgetItem(str(shelf_index + 1)))
                self.setItem(self.rowCount() - 1, 1, QTableWidgetItem(f"{width:.2f}×{height:.2f}"))
                self.setItem(self.rowCount() - 1, 2, QTableWidgetItem(str(i)))


class BookshelfWidget(QWidget):
    inventory_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumSize(400, 500)
        self.shelf_count = 5
        self.side_cushion_ratio = 0.05
        self.items = self.generate_packed_shelves()
        self.hover_box = None
        self.hovered_box = None
        self.selected_box = None
        self.setMouseTracking(True)

        # ✅ Ensure table is populated on startup
        self.inventory_changed.emit(self.items)

    def generate_packed_shelves(self):
        items = {}
        for shelf in range(self.shelf_count):
            x_cursor = 0.0
            shelf_items = []
            while x_cursor < 1.0:
                remaining = 1.0 - x_cursor
                width_ratio = min(random.uniform(0.1, 0.2), remaining)
                height_ratio = random.uniform(0.4, 0.8)
                shelf_items.append((x_cursor, width_ratio, height_ratio))
                x_cursor += width_ratio + 0.02
            items[shelf] = shelf_items
        return items

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_bookshelf(painter)

    def draw_bookshelf(self, painter):
        width = self.width()
        height = self.height()
        margin = 30
        shelf_height = (height - 2 * margin) / self.shelf_count
        content_width = width - 2 * margin

        painter.setPen(QPen(Qt.black, 3))
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(margin, margin, content_width, height - 2 * margin)

        for i in range(self.shelf_count):
            shelf_y = margin + int((i + 1) * shelf_height)
            painter.setPen(QPen(Qt.black, 2))
            painter.drawLine(margin, shelf_y, width - margin, shelf_y)

            if i in self.items:
                for j, (x_ratio, width_ratio, height_ratio) in enumerate(self.items[i]):
                    highlight = (self.hovered_box == (i, j)) or (self.selected_box == (i, j))
                    self.draw_box(painter, i, x_ratio, width_ratio, height_ratio,
                                  shelf_height, width, margin, highlight=highlight)

        if self.hover_box:
            shelf_index, x_ratio, width_ratio, height_ratio = self.hover_box
            self.draw_box(painter, shelf_index, x_ratio, width_ratio, height_ratio,
                          shelf_height, width, margin, preview=True)

    def draw_box(self, painter, shelf_index, x_ratio, width_ratio, height_ratio,
                 shelf_height, total_width, margin, preview=False, highlight=False):
        content_width = total_width - 2 * margin
        usable_width = content_width * (1 - 2 * self.side_cushion_ratio)
        x = margin + content_width * self.side_cushion_ratio + usable_width * x_ratio
        box_width = usable_width * width_ratio
        box_height = (shelf_height - 8) * height_ratio
        shelf_bottom_y = margin + int((shelf_index + 1) * shelf_height)
        y = shelf_bottom_y - box_height

        if preview:
            painter.setBrush(QBrush(QColor(100, 100, 100, 80)))
            painter.setPen(QPen(Qt.DashLine))
        elif highlight:
            painter.setBrush(QBrush(QColor(220, 220, 220)))
            painter.setPen(QPen(QColor(0, 120, 255), 2, Qt.DashLine))
        else:
            painter.setBrush(QBrush(QColor(200, 200, 200)))
            painter.setPen(QPen(Qt.black, 2))

        painter.drawRect(x, y, box_width, box_height)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        try:
            width_ratio, height_ratio = map(float, event.mimeData().text().split(","))
        except ValueError:
            return

        pos = event.pos()
        margin = 30
        height = self.height()
        shelf_height = (height - 2 * margin) / self.shelf_count
        self.hover_box = None

        for shelf_index in range(self.shelf_count):
            shelf_top = margin + shelf_index * shelf_height
            shelf_bottom = shelf_top + shelf_height
            if shelf_top <= pos.y() <= shelf_bottom:
                items = self.items.setdefault(shelf_index, [])
                used_ranges = [(x, x + w) for x, w, _ in items]
                used_ranges.sort()

                x_cursor = 0.0
                padding = 0.02
                for start, end in used_ranges:
                    if x_cursor + width_ratio <= start:
                        break
                    x_cursor = end + padding

                if x_cursor + width_ratio <= 1.0:
                    self.hover_box = (shelf_index, x_cursor, width_ratio, height_ratio)
                break

        self.update()

    def dragLeaveEvent(self, event):
        self.hover_box = None
        self.update()

    def dropEvent(self, event):
        try:
            width_ratio, height_ratio = map(float, event.mimeData().text().split(","))
        except ValueError:
            return

        if self.hover_box:
            shelf_index, x_ratio, _, _ = self.hover_box
            self.items.setdefault(shelf_index, []).append((x_ratio, width_ratio, height_ratio))

        self.hover_box = None
        self.inventory_changed.emit(self.items)
        self.update()
        event.acceptProposedAction()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        margin = 30
        content_width = self.width() - 2 * margin
        shelf_height = (self.height() - 2 * margin) / self.shelf_count
        usable_width = content_width * (1 - 2 * self.side_cushion_ratio)

        self.hovered_box = None
        for shelf_index in range(self.shelf_count):
            shelf_y_top = margin + shelf_index * shelf_height
            shelf_y_bottom = shelf_y_top + shelf_height

            if shelf_y_top <= pos.y() <= shelf_y_bottom:
                if shelf_index in self.items:
                    for i, (x_ratio, width_ratio, height_ratio) in enumerate(self.items[shelf_index]):
                        x = margin + content_width * self.side_cushion_ratio + usable_width * x_ratio
                        width = usable_width * width_ratio
                        box_height = (shelf_height - 8) * height_ratio
                        y = margin + (shelf_index + 1) * shelf_height - box_height

                        if x <= pos.x() <= x + width and y <= pos.y() <= y + box_height:
                            self.hovered_box = (shelf_index, i)
                            self.setCursor(Qt.PointingHandCursor)
                            self.update()
                            return
        self.setCursor(Qt.ArrowCursor)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton and self.hovered_box:
            shelf_index, box_index = self.hovered_box
            menu = QMenu(self)
            remove_action = menu.addAction("Remove Box")
            action = menu.exec_(event.globalPos())
            if action == remove_action:
                confirm = QMessageBox.question(
                    self, "Confirm Removal",
                    "Are you sure you want to remove this box?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirm == QMessageBox.Yes:
                    del self.items[shelf_index][box_index]
                    self.hovered_box = None
                    self.inventory_changed.emit(self.items)
                    self.update()

    def select_box(self, shelf_index, box_index):
        self.selected_box = (shelf_index, box_index)
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bookshelf – Inventory with Product Table")
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)

        self.table = ProductTableWidget()
        self.bookshelf = BookshelfWidget()
        self.placeholder = PlaceholderPanel()

        self.table.selection_callback = self.bookshelf.select_box
        self.bookshelf.inventory_changed.connect(self.table.update_from_inventory)
        self.bookshelf.inventory_changed.emit(self.bookshelf.items)  # ensure table loads

        layout.addWidget(self.table)
        layout.addWidget(self.bookshelf)
        layout.addWidget(self.placeholder)

        self.setCentralWidget(main_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
