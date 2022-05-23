from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QDMGraphicsNode(QGraphicsItem):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.content = self.node.content

        # init our flags
        self._was_moved = False
        self._last_selected_state = False

        self.initSizes()
        self.initAssets()
        self.initUI()

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        # init title
        self.initTitle()
        self.title(self.node.op_title, self.node.op_code)

        self.initContent()

    def initSizes(self):
        self.width = 200
        self.height = 240
        self.edge_roundness = 10.0
        self.edge_padding = 10.0
        self.title_height = 40.0
        self.title_horizontal_padding = 4.0
        self.title_vertical_padding = -3
        self.text_size = 9
        self.size_button_set = 32

    def initAssets(self):
        self._title_color = Qt.white
        self._title_font = QFont("Ubuntu", self.text_size)

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))

        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self._brush_title_b = QBrush(QColor("#7F000000"))

    def onSelected(self):
        self.node.scene.grScene.itemSelected.emit()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        for node in self.scene().scene.nodes:
            node.change_pos()
            if node.grNode.isSelected():
                node.updateConnectedEdges()

        self._was_moved = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        # handle when grNode moved
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory("Node moved", setModified=True)

            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = True

            # we need to store the last selected state, because moving does also select the nodes
            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()

            # now we want to skip storing selection
            return

        # handle when grNode was clicked on
        if self._last_selected_state != self.isSelected() or self.node.scene._last_selected_items != self.node.scene.getSelectedItems():
            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def title(self, value, value2, value3=None):
        self._title = value
        self._title_obj = value2
        self._title_obj_port = value3
        if self._title_obj_port is None or self._title_obj_port == "None":
            self.title_item.setPlainText(self._title + f' ({str(self._title_obj)})')
        else:
            self.title_item.setPlainText(self._title + f' ({str(self._title_obj)})' + f' ({str(self._title_obj_port)})')
        # self.object_item.setPlainText('(' + str(self._title_obj)+ ')')

    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    def initTitle(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, self.title_vertical_padding)
        # self.title_item.setTextWidth(self.width - self.title_horizontal_padding - self.size_button_set)
        self.title_item.setTextWidth(self.width - self.title_horizontal_padding)

        self.object_item = QGraphicsTextItem(self)
        self.object_item.node = self.node
        self.object_item.setDefaultTextColor(self._title_color)
        self.object_item.setFont(self._title_font)
        self.object_item.setPos(self.title_horizontal_padding, self.title_vertical_padding + self.text_size + 7)
        self.object_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)

    def initContent(self):
        self.grContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edge_padding, self.title_height + self.edge_padding,
                                 self.width - 2 * self.edge_padding, self.height - 2 * self.edge_padding - self.title_height)
        self.grContent.setWidget(self.content)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness)
        path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        path_title.addRect(self.width - self.edge_roundness, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # title outline image icon settings
        # path_outline_set = QPainterPath()
        # path_outline_set.setFillRule(Qt.WindingFill)
        # path_outline_set.addRoundedRect(self.width - 37.5, 2.5, 34, 34, self.edge_roundness, self.edge_roundness)
        # painter.setPen(self._pen_default)
        # painter.setBrush(self._brush_title)
        # painter.drawPath(path_outline_set.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(self.width - self.edge_roundness, self.title_height, self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())


        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_roundness, self.edge_roundness)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())