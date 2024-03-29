import os
import json
from collections import OrderedDict

from PyQt5 import QtCore

from nodeeditor.utils import dumpException
from nodeeditor.node_serializable import Serializable
from nodeeditor.node_graphics_scene import QDMGraphicsScene
from nodeeditor.node_node import Node
from nodeeditor.node_edge import Edge
from nodeeditor.node_scene_history import SceneHistory
from nodeeditor.node_scene_clipboard import SceneClipboard
from widgets.drag_listbox import QDMDragListbox


class InvalidFile(Exception): pass


class Scene(Serializable):
    thingListChanged = QtCore.pyqtSignal(QDMDragListbox)

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.scene_width = 64000
        self.scene_height = 64000

        self._has_been_modified = False
        self._last_selected_items = []

        # initialiaze all listeners
        self._has_been_modified_listeners = []
        self._item_selected_listeners = []
        self._items_deselected_listeners = []

        # here we can store callback for retrieving the class for Nodes
        self.node_class_selector = None

        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)

    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)


    def onItemSelected(self):
        current_selected_items = self.getSelectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            self.history.storeHistory("Selection Changed")
            for callback in self._item_selected_listeners: callback()

    def onItemsDeselected(self):
        self.resetLastSelectedStates()
        if self._last_selected_items != []:
            self._last_selected_items = []
            self.history.storeHistory("Deselected Everything")
            for callback in self._items_deselected_listeners: callback()

    def isModified(self):
        return self.has_been_modified

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    @property
    def has_been_modified(self):
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            # set it now, because we will be reading it soon
            self._has_been_modified = value

            # call all registered listeners
            for callback in self._has_been_modified_listeners: callback()

        self._has_been_modified = value

    # our helper listener functions
    def addHasBeenModifiedListener(self, callback):
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback):
        self._item_selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callback):
        self._items_deselected_listeners.append(callback)

    def addDragEnterListener(self, callback):
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback):
        self.getView().addDropListener(callback)

    # custom flag to detect node or edge has been selected....
    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._last_selected_state = False

    def getView(self):
        select_view = self.grScene.views()
        return select_view[0]

    def getItemAt(self, pos):
        item = self.getView().itemAt(pos)
        return item

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes: self.nodes.remove(node)
        else: print("!W:", "Scene::removeNode", "wanna remove node", node, "from self.nodes but it's not in the list!")

    def removeEdge(self, edge):
        if edge in self.edges: self.edges.remove(edge)
        else: print("!W:", "Scene::removeEdge", "wanna remove edge", edge, "from self.edges but it's not in the list!")

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False

    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write( json.dumps( self.serialize(), indent=4 ) )
            print("saving to", filename, "was successfull.")

            self.has_been_modified = False

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            raw_data = file.read()
            try:
                data = json.loads(raw_data)
                self.deserialize(data)
                self.has_been_modified = False
            except json.JSONDecodeError:
                raise InvalidFile("%s is not a valid JSON file" % os.path.basename(filename))
            except Exception as e:
                dumpException(e)

    def setNodeClassSelector(self, class_selecting_function):
        """ When the function self.node_class_selector is set, we can use different Node Classes """
        self.node_class_selector = class_selecting_function

    def getNodeClassFromData(self, data):
        return Node if self.node_class_selector is None else self.node_class_selector(data)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        self.clear()
        hashmap = {}

        if restore_id: self.id = data['id']

        # create nodes
        for node_data in data['nodes']:
            # Перед добавлением на сцену, добавляем в лист вещей, если такой ноды нет
            if "name_class" in node_data and 'node_some_thing' in node_data["name_class"] and "op_code" in node_data:
                thingListWidget = self.thingListChanged
                if thingListWidget is not None:

                    # let thingListWidget haven elements in it.
                    list_items = []
                    for x in range(thingListWidget.count()):
                        from settings.calc_conf import THING_NODES
                        index_thing = x
                        keys = list(THING_NODES)
                        item_thing = THING_NODES.get(keys[index_thing])
                        list_items.append(item_thing)

                    flag_need_to_add = True
                    if node_data["op_code"] not in list_items:
                        for item in list_items:
                            if int(node_data["op_code"]) == int(item.op_code):
                                flag_need_to_add = False
                                break

                    if flag_need_to_add:
                        thing_in = False
                        if "_in" in node_data["name_class"]:
                            thing_in = True
                        thingListWidget.addMyItem(name=node_data["title"], op_code=node_data["op_code"],
                                                  icon=node_data["icon"], obj_title=node_data["obj_title"],
                                                  obj_port=node_data["obj_port"], thing_in=thing_in)

            node = self.getNodeClassFromData(node_data)
            if "Node" in str(type(node)):
                node = self.deserialize_node(node, node_data, hashmap, restore_id)
            else:
                node = node(self).deserialize(node_data, hashmap, restore_id)

        # create edges
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap, restore_id)

        # Загружаем параметры входных данных
        # Если нет имён у входных/выходных параметров, то добавляем их из параметра obj_title
        # Текущей список нод на сцене
        list_nodes = self.nodes
        for select_node in list_nodes:
            select_node.createInParam()

        return True

    def deserialize_node(self, node, data, hashmap={}, restore_id=True):
        try:
            if restore_id:
                id = data['id']
            hashmap[data['id']] = node.id

            node.setPos(data['pos_x'], data['pos_y'])

            if hasattr(node, 'obj_port') and node.obj_port is not None:
                node.title(data['title'], data['obj_title'], data['obj_port'])
            else:
                node.title(data['title'], data['obj_title'])

            # Если нет имён у входных/выходных параметров, то добавляем их из параметра obj_title
            if hasattr(node, 'outputs_names') and (node.outputs_names is None or len(node.outputs_names) <= 0):
                new_list = []
                for _index in range(len(node.outputs)):
                    if hasattr(node, 'obj_title') and node.obj_title is not None:
                        new_list.append(node.obj_title)
                node.outputs_names = new_list

            data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
            data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
            num_inputs = len(data['inputs'])
            num_outputs = len(data['outputs'])

            node.inputs = []
            from nodeeditor.node_socket import Socket
            for socket_data in data['inputs']:
                new_socket = Socket(node=node, index=socket_data['index'], position=socket_data['position'],
                                    socket_type=socket_data['socket_type'], count_on_this_node_side=num_inputs,
                                    is_input=True)
                new_socket.deserialize(socket_data, hashmap, restore_id)
                node.inputs.append(new_socket)

            node.outputs = []
            for socket_data in data['outputs']:
                new_socket = Socket(node=node, index=socket_data['index'], position=socket_data['position'],
                                    socket_type=socket_data['socket_type'], count_on_this_node_side=num_outputs,
                                    is_input=False)
                new_socket.deserialize(socket_data, hashmap, restore_id)
                node.outputs.append(new_socket)

            self.addNode(node)
            self.grScene.addItem(node.grNode)
            node.scene = self
        except Exception as e:
            dumpException(e)

        # also deseralize the content of the node
        res = node.content.deserialize(data['content'], hashmap)

        return res