from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import sys

from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER
from nodeeditor.utils import dumpException


class CalcGraphicsNode(QDMGraphicsNode):
    DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__))).replace("\\", "/")
    DIR_ICONS = DIR_MAIN + "/styles/icons" + "/"
    DIR_CSS = DIR_MAIN + "/styles/qss" + "/"

    def initSizes(self):
        super().initSizes()
        self.width = 200
        self.height = 74 + 16
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 40
        self.title_vertical_padding = -3

    def initAssets(self):
        super().initAssets()
        # self.icons_status = QImage(self.DIR_ICONS + "status_icons.png")
        self.icons_status = QImage(".")
        self.icon = QImage(self.node.icon)
        self.icon_set = QPixmap(self.DIR_ICONS + 'settings.png').scaled(32, 32, Qt.KeepAspectRatio)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # Рисуем границы виджета
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        # Рисуем иконку вещи
        painter.drawImage(
            QRectF(5, 3, 32.0, 32.0),
            QImage(self.icon).scaled(32, 32, Qt.KeepAspectRatio),
            QRectF(0, 0, 0, 0)
        )

        # Рисуем иконку настроек
        # painter.drawImage(
        #     QRectF(self.width - 36.5, 3, 32.0, 32.0),
        #     QImage(self.icon_set).scaled(32, 32, Qt.KeepAspectRatio),
        #     QRectF(0, 0, 0, 0)
        # )

        # Рисуем иконку статуса
        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons_status,
            QRectF(offset, 0, 24.0, 24.0)
        )


class CalcContent(QDMNodeContentWidget):
    def initUI(self):
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)


class CalcNode(Node):
    icon = ""
    op_code = 0
    op_title = "Undefined"
    obj_title = "A0"
    obj_port = None
    obj_data = None
    content_label = ""
    content_label_objname = "calc_node_bg"

    def __init__(self, scene, inputs=[2,2], outputs=[1]):
        super().__init__(scene, self.op_title, self.obj_title, self.obj_port, self.obj_data, inputs, outputs)
        self.value = None

        # Изначально помечаем ноду как испорченную
        self.markDirty()

    def initInnerClasses(self):
        self.content = CalcContent(self)
        self.grNode = CalcGraphicsNode(self)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def evalOperation(self, input1, input2):
        return 123

    def evalImplementation(self):
        i1 = self.getInput(0)
        i2 = self.getInput(1)

        if i1 is None or i2 is None:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:
            val = self.evalOperation(i1.eval(), i2.eval())
            self.value = val
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")
            self.markDescendantsDirty()
            self.evalChildren()

            return val

    def eval(self):
        if not self.isDirty() and not self.isInvalid():
            print(" _> returning cached %s value:" % self.__class__.__name__, self.value)
            return self.value

        try:
            val = self.evalImplementation()
            return val
        except ValueError as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            dumpException(e)

    def onInputChanged(self, new_edge):
        print("%s::__onInputChanged" % self.__class__.__name__)
        self.markDirty()
        self.eval()

    def serialize(self):
        res = super().serialize()
        name_class = self.__class__.content_label_objname
        class_op_code = self.__class__.op_code
        object_op_code = self.op_code

        # Если у нас уже существует экземплят объекта, то отправляем его op_code
        if object_op_code != class_op_code:
            res['op_code'] = object_op_code
        elif object_op_code == class_op_code:
            res['op_code'] = class_op_code
        res['name_class'] = name_class
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        print("Deserialized CalcNode '%s'" % self.__class__.__name__, "res:", res)
        return res