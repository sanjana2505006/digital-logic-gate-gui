import sys
from PyQt5.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QMainWindow,
    QGraphicsItem, QToolBar, QAction, QFileDialog, QMessageBox,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsSimpleTextItem,
    QGraphicsProxyWidget, QLineEdit, QMenu
)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QTransform
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF
import datetime


class GridBackground(QGraphicsItem):
    def __init__(self, parent=None):
        super(GridBackground, self).__init__(parent)
        self.setZValue(-1)

    def boundingRect(self):
        return QRectF(-5000, -5000, 10000, 10000)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        step = 20
        left = int(self.boundingRect().left())
        right = int(self.boundingRect().right())
        top = int(self.boundingRect().top())
        bottom = int(self.boundingRect().bottom())

        for x in range(left, right, step):
            painter.drawLine(x, top, x, bottom)
        for y in range(top, bottom, step):
            painter.drawLine(left, y, right, y)


class EditableTextItem(QGraphicsTextItem):
    def __init__(self, default_text="0", parent=None):
        super().__init__(default_text, parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setDefaultTextColor(Qt.yellow)
        font = QFont("Courier", 12, QFont.Bold)
        self.setFont(font)


class GateItem(QGraphicsItem):
    gate_symbols = {
        "AND": "&",
        "OR": "≥1",
        "NOT": "¬",
        "NAND": "&̅",
        "NOR": "≥̅1",
        "XOR": "⊕",
        "INPUT": "IN",
        "OUTPUT": "OUT"
    }

    def __init__(self, gate_type):
        super().__init__()
        self.gate_type = gate_type
        self.width = 100
        self.height = 60
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.selected_for_wire = False

        if self.gate_type in ["INPUT", "OUTPUT"]:
            self.text_item = EditableTextItem("0", self)
            self.text_item.setPos(35, 15)
        else:
            self.text_item = QGraphicsSimpleTextItem(self)
            self.text_item.setBrush(Qt.white)
            self.text_item.setFont(QFont("Arial", 20, QFont.Bold))
            self.text_item.setText(self.gate_symbols.get(self.gate_type, "?"))
            self.text_item.setPos(35, 15)

        if self.gate_type == "OUTPUT":
            self.output_button = QGraphicsSimpleTextItem("Save", self)
            self.output_button.setBrush(Qt.cyan)
            self.output_button.setFont(QFont("Arial", 10))
            self.output_button.setPos(35, 40)
            self.output_button.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        if hasattr(self, 'output_button') and self.output_button.contains(event.pos()):
            text = self.text_item.toPlainText()
            filename = f"output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(text)
            QMessageBox.information(None, "Saved Output", f"Output saved to {filename}")
        else:
            super().mousePressEvent(event)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        if self.selected_for_wire:
            painter.setBrush(QColor(0, 180, 90))
        else:
            painter.setBrush(QColor(50, 50, 50))

        painter.setPen(QPen(Qt.white, 2))
        painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)

        painter.setPen(QPen(Qt.lightGray))
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(QRectF(0, self.height - 20, self.width, 20), Qt.AlignCenter, self.gate_type)

    def input_position(self):
        return self.mapToScene(QPointF(0, self.height / 2))

    def output_position(self):
        return self.mapToScene(QPointF(self.width, self.height / 2))


class WireItem(QGraphicsLineItem):
    def __init__(self, start_gate, end_gate):
        super().__init__()
        self.start_gate = start_gate
        self.end_gate = end_gate
        self.setZValue(-2)
        self.setPen(QPen(Qt.green, 2))
        self.update_positions()

    def update_positions(self):
        line = QLineF(self.start_gate.output_position(), self.end_gate.input_position())
        self.setLine(line)


class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_gate = None

    def mousePressEvent(self, event):
        clicked_item = self.itemAt(event.scenePos(), QTransform())

        if isinstance(clicked_item, GateItem):
            if self.selected_gate is None:
                self.selected_gate = clicked_item
                clicked_item.selected_for_wire = True
            else:
                if clicked_item != self.selected_gate:
                    wire = WireItem(self.selected_gate, clicked_item)
                    self.addItem(wire)
                self.selected_gate.selected_for_wire = False
                self.selected_gate = None
            self.update()
        else:
            if self.selected_gate:
                self.selected_gate.selected_for_wire = False
                self.selected_gate = None
            self.update()

        super().mousePressEvent(event)


class LogicGateEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FOSSEE Logic Gate Editor")
        self.setGeometry(100, 100, 1200, 700)

        self.view = QGraphicsView()
        self.scene = CustomGraphicsScene(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        self.view.setRenderHint(QPainter.Antialiasing)

        grid = GridBackground()
        self.scene.addItem(grid)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                color: #ffffff;
            }
            QGraphicsView {
                background-color: #1e1e1e;
                border: none;
            }
            QToolBar {
                background: #1f1f1f;
                spacing: 10px;
                padding: 5px;
            }
            QToolButton {
                color: white;
            }
        """)

        self.init_menu()
        self.init_toolbar()

    def init_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)

        new_action.triggered.connect(self.new_file)
        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Edit")
        cut_action = QAction("Cut", self)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)
        delete_action = QAction("Delete", self)

        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addAction(delete_action)

        window_menu = menu_bar.addMenu("Window")
        reset_zoom_action = QAction("Reset Zoom", self)
        window_menu.addAction(reset_zoom_action)

    def init_toolbar(self):
        toolbar = QToolBar("Gate Tools")
        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        gates = ["INPUT", "OUTPUT", "AND", "OR", "NOT", "NAND", "NOR", "XOR"]
        for gate in gates:
            action = QAction(gate, self)
            action.triggered.connect(lambda checked, g=gate: self.add_gate(g))
            toolbar.addAction(action)

    def new_file(self):
        self.scene.clear()
        grid = GridBackground()
        self.scene.addItem(grid)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Logic Files (*.logic)")
        if filename:
            QMessageBox.information(self, "Open File", f"Would open: {filename}")

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Logic Files (*.logic)")
        if filename:
            QMessageBox.information(self, "Save File", f"Would save to: {filename}")

    def add_gate(self, gate_type):
        gate = GateItem(gate_type)
        gate.setPos(QPointF(100, 100))
        self.scene.addItem(gate)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = LogicGateEditor()
    editor.show()
    sys.exit(app.exec_())