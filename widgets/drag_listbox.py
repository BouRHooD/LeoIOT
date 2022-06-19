from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from settings.calc_conf import *
from nodeeditor.utils import dumpException


def find_some_nodes(SOME_NODES):
    if SOME_NODES == CALC_NODES:
        return "CALC_NODES"
    if SOME_NODES == THING_NODES:
        return "THING_NODES"
    return "None"


class TWListbox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.setDragEnabled(False)

    def addMyItem(self, input_node):
        item = QListWidgetItem(input_node.obj_title, self)  # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(input_node.icon if input_node.icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
        self.list_thing.addItem(item)


class QDMDragListbox(QListWidget):
    def __init__(self, parent=None, SOME_NODES=None, checkable=False):
        super().__init__(parent)
        self.checkable = checkable
        self.SOME_NODES = SOME_NODES
        self.clear()
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addMyItems()

    def addMyItems(self):
        keys = list(self.SOME_NODES.keys())
        keys.sort()
        for key in keys:
            node = get_class_from_opcode(key, self.SOME_NODES)
            self.addMyItem(name=node.op_title, icon=node.icon, op_code=node.op_code)

    def addMyItem(self, name, icon=None, op_code=0, obj_title="T0", obj_port=None, thing_in=True):
        try:
            if op_code not in self.SOME_NODES:

                print(icon)
                # Если было сохранено на ПК с windows
                if icon is not None and ('C:\\Users' in icon or 'C:/Users' in icon):
                    filename = os.path.basename(icon)
                    icon = DIR_ICONS + filename
                    print(icon)

                from nodes.some_thing import CalcNode_some_thing_in
                from nodes.some_thing import CalcNode_some_thing_out
                if thing_in:
                    new_class = CalcNode_some_thing_in(scene=None, icon=str(icon), op_code=int(op_code), op_title=str(name),
                                                       obj_title=str(obj_title), obj_port=str(obj_port))
                else:
                    new_class = CalcNode_some_thing_out(scene=None, icon=str(icon), op_code=int(op_code), op_title=str(name),
                                                        obj_title=str(obj_title), obj_port=str(obj_port))
                new_register_node = register_node(int(op_code), self.SOME_NODES, new_class)
                self.SOME_NODES.update({int(op_code): new_register_node})

            if self.checkable:
                item_text = f"({obj_title}) {name}"
            else:
                item_text = f"{name}"

            item = QListWidgetItem(item_text, self) # can be (icon, text, parent, <int>type)
            pixmap = QPixmap(icon if icon is not None else ".")
            item.setIcon(QIcon(pixmap))
            item.setSizeHint(QSize(32, 32))

            if self.checkable:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
            else:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

            # setup data
            item.setData(Qt.UserRole, pixmap)
            item.setData(Qt.UserRole + 1, int(op_code))
        except Exception as ex:
            dumpException(ex)

    def startDrag(self, *args, **kwargs):
        try:
            item = self.currentItem()
            op_code = item.data(Qt.UserRole + 1)

            if op_code is None:
                op_code = 1

            pixmap = QPixmap(item.data(Qt.UserRole)).scaled(32, 32, QtCore.Qt.KeepAspectRatio)

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap
            dataStream.writeInt(int(op_code))
            dataStream.writeQString(item.text())
            dataStream.writeQString(find_some_nodes(self.SOME_NODES))

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() / 2, pixmap.height() / 2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e: dumpException(e)