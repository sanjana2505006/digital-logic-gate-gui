import sys
from PySide6.QtWidgets import QApplication
from NodeGraphQt import NodeGraph
from NodeGraphQt.nodes.base_node import BaseNode


class MyInputNode(BaseNode):
    __identifier__ = 'nodes.input'
    NODE_NAME = 'Input'

    def __init__(self):
        super().__init__()
        self.add_text_input('value', 'Input Value')
        self.add_output('Output')


class MyAndNode(BaseNode):
    __identifier__ = 'nodes.logic'
    NODE_NAME = 'AND Gate'

    def __init__(self):
        super().__init__()
        self.add_input('Input A')
        self.add_input('Input B')
        self.add_output('Output')


class MyOrNode(BaseNode):
    __identifier__ = 'nodes.logic'
    NODE_NAME = 'OR Gate'

    def __init__(self):
        super().__init__()
        self.add_input('Input A')
        self.add_input('Input B')
        self.add_output('Output')


class MyNotNode(BaseNode):
    __identifier__ = 'nodes.logic'
    NODE_NAME = 'NOT Gate'

    def __init__(self):
        super().__init__()
        self.add_input('Input')
        self.add_output('Output')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    graph = NodeGraph()

    # Register nodes
    graph.register_node(MyInputNode)
    graph.register_node(MyAndNode)
    graph.register_node(MyOrNode)
    graph.register_node(MyNotNode)

    # Create the GUI widget
    graph_widget = graph.widget
    graph_widget.setWindowTitle('Logic Gate Editor')
    graph_widget.resize(1100, 800)
    graph.show()

    sys.exit(app.exec())