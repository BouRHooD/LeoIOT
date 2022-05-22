import json

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from settings.calc_conf import *
from nodeeditor.node_editor_widget import NodeEditorWidget
from widgets.node_base import *
from nodeeditor.node_edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER
from nodeeditor.utils import dumpException

DEBUG = False
DEBUG_CONTEXT = False


# Ищем в каком массиве нод находится класс, который мы ищем
def get_nodes(name_class):
    for select_nodes in ALL_NODES:
        for select_node in select_nodes:
            type_node = str(select_nodes[select_node].content_label_objname)
            if name_class in type_node:
                return select_nodes


class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()

        self.initNewNodeActions()

        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self._close_event_listeners = []

    # data['op_code'] из serialization, события копировать из рабочей области
    def getNodeClassFromData(self, data):
        if 'op_code' not in data: return Node
        return get_class_from_opcode(data['op_code'], get_nodes(data['name_class']))

    def fileLoad(self, filename):
        if super().fileLoad(filename):
            # eval all output nodes
            for node in self.scene.nodes:
                if node.__class__.__name__ == "CalcNode_Output":
                    node.eval()
            return True

        return False

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            node = CALC_NODES[key]
            self.node_actions[node.op_code] = QAction(QIcon(node.icon), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)

    def initNodesContextMenu(self):
        context_menu = QMenu(self)
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys: context_menu.addAction(self.node_actions[key])
        return context_menu

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners: callback(self, event)

    def onDragEnter(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            # print(" ... denied drag enter event")
            event.setAccepted(False)

    def onDrop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            pixmap = QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readInt()
            text = dataStream.readQString()
            some_nodes = dict_ALL_NODES.get(dataStream.readQString())

            mouse_position = event.pos()
            scene_position = self.scene.grScene.views()[0].mapToScene(mouse_position)

            if DEBUG: print("GOT DROP: [%d] '%s'" % (op_code, text), "mouse:", mouse_position, "scene:", scene_position)

            try:
                # Проверяем есть ли уже экземпляр класса для ноды (для нод умных вещей)
                select_node = some_nodes.get(op_code)
                node_type = str(type(select_node))
                if "CalcNode_some_thing" in node_type:
                    node = select_node
                    self.scene.addNode(node)
                    self.scene.grScene.addItem(node.grNode)
                    node.scene = self.scene
                else:
                    node = get_class_from_opcode(op_code, some_nodes)(self.scene)
                node.setPos(scene_position.x(), scene_position.y())

                self.scene.history.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as e: dumpException(e)


            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()

    def contextMenuEvent(self, event):
        try:
            select_pose = event.pos()
            item = self.scene.getItemAt(select_pose)

            # if type(item) == QGraphicsProxyWidget:
            #    item = item.widget()

            # if hasattr(item, 'node') and hasattr(item, 'icon_set'):
            #     select_pose_item_x = event.pos().x()
            #     select_pose_item_y = event.pos().y()
            #     if select_pose_item_x:
            #        self.handleNodeContextMenu(event)
            # elif hasattr(item, 'edge'):
            #    self.handleEdgeContextMenu(event)
            # elif item is None:
            #    self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e: dumpException(e)

    def handleNodeContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: NODE")
        context_menu = QMenu(self)
        markDirtyAct = context_menu.addAction("Mark Dirty")
        markDirtyDescendantsAct = context_menu.addAction("Mark Descendant Dirty")
        markInvalidAct = context_menu.addAction("Mark Invalid")
        unmarkInvalidAct = context_menu.addAction("Unmark Invalid")
        evalAct = context_menu.addAction("Eval")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
        if type(item) == QGraphicsProxyWidget:

           item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node
        if hasattr(item, 'socket'):
            selected = item.socket.node

        if DEBUG_CONTEXT: print("got item:", selected)
        if selected and action == markDirtyAct: selected.markDirty()
        if selected and action == markDirtyDescendantsAct: selected.markDescendantsDirty()
        if selected and action == markInvalidAct: selected.markInvalid()
        if selected and action == unmarkInvalidAct: selected.markInvalid(False)
        if selected and action == evalAct:
            val = selected.eval()
            if DEBUG_CONTEXT: print("EVALUATED:", val)


    def handleEdgeContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: EDGE")
        context_menu = QMenu(self)
        bezierAct = context_menu.addAction("Bezier Edge")
        directAct = context_menu.addAction("Direct Edge")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezierAct: selected.edge_type = EDGE_TYPE_BEZIER
        if selected and action == directAct: selected.edge_type = EDGE_TYPE_DIRECT


    def handleNewNodeContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: EMPTY SPACE")
        context_menu = self.initNodesContextMenu()
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            new_calc_node = get_class_from_opcode(action.data())(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_calc_node.setPos(scene_pos.x(), scene_pos.y())
            if DEBUG_CONTEXT: print("Selected node:", new_calc_node)


