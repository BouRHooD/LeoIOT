import json

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from settings.calc_conf import *
from nodeeditor.node_editor_widget import NodeEditorWidget
from widgets.node_base import *
from nodeeditor.node_edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER
from nodeeditor.utils import dumpException
from windows.dialogs import PopUpDialogThingWorx, PopUpDialogThingWorxCountInOut

DEBUG = False
DEBUG_CONTEXT = False


# Ищем в каком массиве нод находится класс, который мы ищем
def get_nodes(name_class):
    for select_nodes in ALL_NODES:
        for select_node in select_nodes:
            type_node = str(select_nodes[select_node].content_label_objname)
            if name_class in type_node:
                return select_nodes


class IOTSubWindow(NodeEditorWidget):
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
                    # Если объект является thingworx, то спрашиваем у пользователя настройки для создания объекта
                    self.return_value = None
                    node_lbl = select_node.content_label_objname
                    if node_lbl in ['node_thingworx_obj', "node_fogwing_iiot_obj"]:
                        if 'node_thingworx_obj' in node_lbl:
                            dialog_thingworx = PopUpDialogThingWorxCountInOut()
                            self.return_value = dialog_thingworx.exec_()

                        if 'node_fogwing_iiot_obj' in node_lbl:
                            dialog_thingworx = PopUpDialogThingWorxCountInOut(outputs_enable=False, outputs_value=1)
                            self.return_value = dialog_thingworx.exec_()

                        if self.return_value is None:
                            return

                    # Создаём экземпляр ноды на сцене для thingworx
                    if self.return_value is not None:
                        node = get_class_from_opcode(op_code, some_nodes)(scene=self.scene,
                                                                          inputs=self.return_value["inputs"],
                                                                          outputs=self.return_value["outputs"])
                    # Создаём экземпляр ноды на сцене для остальных объектов
                    else:
                        node = get_class_from_opcode(op_code, some_nodes)(scene=self.scene)

                # Ставим объект в нужную позицию на сцене и после прикрепляем его к краям, если это необходимо
                node.setPos(scene_position.x(), scene_position.y())
                node.change_pos()

                # Если объект является thingworx, то спрашиваем у пользователя настройки для создания объекта
                self.return_value = None
                node_lbl = select_node.content_label_objname
                if node_lbl in ['node_thingworx_obj', "node_fogwing_iiot_obj"]:
                    if 'node_thingworx_obj' in node_lbl:
                        dialog_thingworx = PopUpDialogThingWorx(server_name="PP-2107252209MI.portal.ptc.io",
                                                                thing_name="Home_IoT", service_name="InOut",
                                                                appkey_data='768cecc2-f48a-4783-b2c6-29fdd734e538')
                        self.return_value = dialog_thingworx.exec_()

                    if 'node_fogwing_iiot_obj' in node_lbl:
                        dialog_thingworx = PopUpDialogThingWorx(server_name_exp_lbl="portal.fogwing.net",
                                                                thing_name_lbl="Account ID",
                                                                service_name_lbl="devEui",
                                                                appkey_data_lbl="apiKey",
                                                                server_name="portal.fogwing.net",
                                                                thing_name="2170", service_name="581e098c9ac93f07",
                                                                appkey_data='b5d4a44eeaa24a5aac02a1c30ec911d2')
                        self.return_value = dialog_thingworx.exec_()

                    if self.return_value is None:
                        pass
                    else:
                        node.obj_data = self.return_value

                """
                views = self.scene.grScene.views()
                geometry_view = views[0].geometry()
                point_left_corner = QPoint(geometry_view.x(), geometry_view.y())
                left_corner_pos = views[0].mapToScene(point_left_corner)

                new_x = left_corner_pos.x()
                new_y = left_corner_pos.y()

                from nodeeditor.node_node import rectangle_inout
                rec_in = rectangle_inout(scene=self.scene, title="REC_IN")
                rec_in.setRect(QtCore.QRectF(new_x, new_y, 200, geometry_view.height()))
                rec_in.setBrush(QBrush(Qt.gray))
                rec_in.setZValue(-5)
                rec_in.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
                self.scene.grScene.addItem(rec_in)

                rec_out = rectangle_inout(scene=self.scene, title="REC_OUT")
                rec_out.setRect(QtCore.QRectF(new_x, new_y, 200, geometry_view.height()))
                rec_out.setBrush(QBrush(Qt.gray))
                rec_out.setZValue(-5)
                rec_out.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
                self.scene.grScene.addItem(rec_out)
                """

                self.scene.history.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as ex:
                print(ex)

            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()

    def contextMenuEvent(self, event):
        try:
            select_pose = event.pos()
            item = self.scene.getItemAt(select_pose)

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node'):
                select_pose_item_x = event.pos().x()
                select_pose_item_y = event.pos().y()
                if select_pose_item_x:
                   self.handleNodeContextMenu(event)
            # elif hasattr(item, 'edge'):
            #    self.handleEdgeContextMenu(event)
            # elif item is None:
            #    self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e: dumpException(e)

    def handleNodeContextMenu(self, event):
        if DEBUG_CONTEXT: print("CONTEXT: NODE")
        context_menu = QMenu(self)
        # markDirtyAct = context_menu.addAction("Mark Dirty")
        # markDirtyDescendantsAct = context_menu.addAction("Mark Descendant Dirty")
        # markInvalidAct = context_menu.addAction("Mark Invalid")
        # unmarkInvalidAct = context_menu.addAction("Unmark Invalid")
        # evalAct = context_menu.addAction("Eval")
        deleteNodeAct = context_menu.addAction("Удалить ноду")
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

        if selected and action == deleteNodeAct: selected.delete_node()
        # if selected and action == markDirtyAct: selected.markDirty()
        # if selected and action == markDirtyDescendantsAct: selected.markDescendantsDirty()
        # if selected and action == markInvalidAct: selected.markInvalid()
        # if selected and action == unmarkInvalidAct: selected.markInvalid(False)
        # if selected and action == evalAct:
        #     val = selected.eval()
        #     if DEBUG_CONTEXT: print("EVALUATED:", val)


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


