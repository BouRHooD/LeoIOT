from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint

from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_socket import *
from nodeeditor.utils import dumpException

DEBUG = False

class rectangle_inout(QtWidgets.QGraphicsRectItem):

    def __init__(self, scene, title="Undefined Rect"):
        super().__init__()
        self._title = title
        self.scene = scene

class Node(Serializable):
    icon = "."

    def __init__(self, scene, title="Undefined Node", obj_title="Undefined", obj_port=None, obj_data=None,
                 inputs=[], outputs=[], inputs_names=[], outputs_names=[]):
        super().__init__()
        self._title = title
        self._obj_title = obj_title
        self.scene = scene
        self.obj_port = obj_port
        self.obj_data = obj_data
        self.inputs = inputs
        self.outputs = outputs
        self.inputs_names = inputs_names
        self.outputs_names = outputs_names

        self.initInnerClasses()
        self.initSettings()

        self.title(title, obj_title, obj_port)

        # Подключение модуля serial (pyserial)
        import serial
        try:
            #self.port = serial.Serial(port='COM3', baudrate=9600, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
            self.port = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, stopbits=serial.STOPBITS_ONE,
                                      bytesize=serial.EIGHTBITS)
            print(self.port)
        except:
            pass

        if scene is not None:
            self.scene.addNode(self)
            self.scene.grScene.addItem(self.grNode)

        # create socket for inputs and outputs
        self.inputs = []
        self.outputs = []
        self.initSockets(inputs, outputs)

        # dirty and evaluation
        self._is_dirty = False
        self._is_invalid = False

    def serialConnect(self):
        serlocations = ['/dev/ttyACM', '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4',
                        '/dev/ttyACM5', '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/ttyUSB4',
                        '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7', '/dev/ttyUSB8', '/dev/ttyUSB9', '/dev/ttyUSB10',
                        '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7',
                        'com8', 'com9', 'com10', 'com11', 'com12', 'com13', 'com14', 'com15', 'com16', 'com17', 'com18',
                        'com19', 'com20', 'com21', 'com1', 'end']
        for device in serlocations:
            try:
                import serial
                ser = serial.Serial(
                    port=device,
                    baudrate=9600,
                    parity=serial.PARITY_ODD,
                    stopbits=serial.STOPBITS_TWO,
                    bytesize=serial.SEVENBITS
                )
                print(device)
                return ser
            except:
                x = 0
            if device == 'end':
                print ("No Device Found")


    def initInnerClasses(self):
        self.content = QDMNodeContentWidget(self)
        self.grNode = QDMGraphicsNode(self)

    def initSettings(self):
        self.socket_spacing = 22

        self.input_socket_position = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.input_multi_edged = False
        self.output_multi_edged = True

    def initSockets(self, inputs, outputs, reset=True):
        """ Create sockets for inputs and outputs"""

        if reset:
            # clear old sockets
            if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
                # remove grSockets from scene
                for socket in (self.inputs+self.outputs):
                    self.scene.grScene.removeItem(socket.grSocket)
                self.inputs = []
                self.outputs = []

        # create new sockets
        counter = 0
        for item in inputs:
            socket = Socket(node=self, index=counter, position=self.input_socket_position,
                            socket_type=item, multi_edges=self.input_multi_edged,
                            count_on_this_node_side=len(inputs), is_input=True
            )
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = Socket(node=self, index=counter, position=self.output_socket_position,
                            socket_type=item, multi_edges=self.output_multi_edged,
                            count_on_this_node_side=len(outputs), is_input=False
            )
            counter += 1
            self.outputs.append(socket)


    def onEdgeConnectionChanged(self, new_edge):
        print("%s::onEdgeConnectionChanged" % self.__class__.__name__, new_edge)

    def onInputChanged(self, new_edge):
        print("%s::onInputChanged" % self.__class__.__name__, new_edge)
        self.markDirty()
        self.markDescendantsDirty()

    def __str__(self):
        return "<Node %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    @property
    def pos(self):
        return self.grNode.pos()        # QPointF

    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    def setAlligment(self, str):
        if str == "Left":
            pass

    def title(self, value, value2, value3=None):
        self._title = value
        self._obj_title = value2
        self._obj_port = value3
        if self._obj_port is not None:
            self.grNode.title(self._title, self._obj_title, self._obj_port)
        else:
            self.grNode.title(self._title, self._obj_title)


    def getSocketPosition(self, index, position, num_out_of=1):
        x = 0 if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM)) else self.grNode.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - self.grNode.edge_roundness - self.grNode.title_vertical_padding - index * self.socket_spacing
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            num_sockets = num_out_of
            node_height = self.grNode.height
            top_offset = self.grNode.title_height + 2 * self.grNode.title_vertical_padding + self.grNode.edge_padding
            available_height = node_height - top_offset

            total_height_of_all_sockets = num_sockets * self.socket_spacing
            new_top = available_height - total_height_of_all_sockets

            # y = top_offset + index * self.socket_spacing + new_top / 2
            y = top_offset + available_height/2.0 + (index-0.5)*self.socket_spacing
            if num_sockets > 1:
                y -= self.socket_spacing * (num_sockets-1)/2

        elif position in (LEFT_TOP, RIGHT_TOP):
            # start from top
            y = self.grNode.title_height + self.grNode.title_vertical_padding + self.grNode.edge_roundness + index * self.socket_spacing
        else:
            # this should never happen
            y = 0

        return [x, y]

    def change_pos(self):
        try:
            select_node = self
            node_type = str(type(select_node))

            mouse_position = self.pos
            #scene_position = node.scene.grScene.views()[0].mapToScene(mouse_position.toPoint())
            scene_position = mouse_position
            # Left corner
            if "CalcNode_some_thing_in" in node_type or "_Input" in node_type:
                # Знаем расположение левого края в программе
                views = self.scene.grScene.views()
                geometry_view = views[0].geometry()
                point_left_corner = QPoint(geometry_view.x(), geometry_view.y())
                left_corner_pos = views[0].mapToScene(point_left_corner)

                new_x = left_corner_pos.x()
                new_y = scene_position.y()
                self.setPos(new_x, new_y)
            # Right corner
            elif "CalcNode_some_thing_out" in node_type or "_Output" in node_type:
                # Знаем расположение правого края в программе
                views = self.scene.grScene.views()
                geometry_view = views[0].geometry()
                point_left_corner = QPoint(geometry_view.x() + geometry_view.width(),
                                           geometry_view.y() + geometry_view.height())
                left_corner_pos = views[0].mapToScene(point_left_corner)

                new_x = left_corner_pos.x() - self.grNode.width
                new_y = scene_position.y()
                self.setPos(new_x, new_y)
            # IOT
            # Left corner
            elif len(select_node.inputs) <= 0 and len(select_node.outputs) > 0:
                # Знаем расположение левого края в программе
                views = self.scene.grScene.views()
                geometry_view = views[0].geometry()
                point_left_corner = QPoint(geometry_view.x(), geometry_view.y())
                left_corner_pos = views[0].mapToScene(point_left_corner)

                new_x = left_corner_pos.x()
                new_y = scene_position.y()
                self.setPos(new_x, new_y)
            # Right corner
            elif len(select_node.inputs) > 0 and len(select_node.outputs) <= 0:
                # Знаем расположение правого края в программе
                views = self.scene.grScene.views()
                geometry_view = views[0].geometry()
                point_left_corner = QPoint(geometry_view.x() + geometry_view.width(),
                                           geometry_view.y() + geometry_view.height())
                left_corner_pos = views[0].mapToScene(point_left_corner)

                new_x = left_corner_pos.x() - self.grNode.width
                new_y = scene_position.y()
                self.setPos(new_x, new_y)
        except Exception as ex:
            print(ex)

    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            # if socket.hasEdge():
            for edge in socket.edges:
                edge.updatePositions()


    def remove(self):
        if DEBUG: print("> Удаляем ноду", self)
        if DEBUG: print(" - Удаляем все связи")
        for socket in (self.inputs+self.outputs):
            # if socket.hasEdge():
            for edge in socket.edges:
                if DEBUG: print("    - удалено из сокета:", socket, "связь:", edge)
                edge.remove()
        if DEBUG: print(" - remove grNode")
        self.scene.grScene.removeItem(self.grNode)
        #self.grNode = None
        if DEBUG: print(" - remove node from the scene")
        self.scene.removeNode(self)
        if DEBUG: print(" - everything was done.")


    # node evaluation stuff

    def isDirty(self):
        return self._is_dirty

    def markDirty(self, new_value=True):
        self._is_dirty = new_value
        if self._is_dirty: self.onMarkedDirty()

    def delete_node(self):
        for item in self.scene.grScene.selectedItems():
            from nodeeditor.node_graphics_edge import QDMGraphicsEdge
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()
        self.scene.grScene.scene.history.storeHistory("Delete selected", setModified=True)

    def change_data_node(self):
        for sel_node in self.scene.grScene.selectedItems():
            from windows.dialogs import change_node_data_window
            # Обновляем значения входных параметров перед открытием диалога
            sel_node.node.updateInParam()
            node_window = change_node_data_window(item_node=sel_node)
            new_data = node_window.exec_()
            if new_data is not None and len(new_data) > 0:
                if sel_node.node.inputs_names != new_data['inputs_names']:
                    for sel_socket in sel_node.node.inputs:
                        sel_index = sel_node.node.inputs.index(sel_socket)
                        try:
                            for sel_edge in sel_socket.edges:
                                if sel_edge.start_socket.node != sel_node.node:
                                    node_change = sel_edge.start_socket.node
                                    new_param_val = new_data['inputs_names'][sel_index]
                                    old_param_val = node_change.obj_title
                                    # Меняем параметр объекта и обновляем на сцене графику
                                    node_change.obj_title = new_param_val
                                    if hasattr(node_change, 'obj_port') and node_change.obj_port is not None:
                                        node_change.title(node_change.op_title, node_change.obj_title, node_change.obj_port)
                                    else:
                                        node_change.title(node_change.op_title, node_change.obj_title)

                                    # Обновляем параметры в изменяемой ноде
                                    for outputs_name in node_change.outputs_names:
                                        param_index = node_change.outputs_names.index(outputs_name)
                                        if outputs_name == old_param_val:
                                            node_change.outputs_names[param_index] = new_param_val

                                    # Обновляем в исходной ноде параметры
                                    sel_node.node.inputs_names = new_data['inputs_names']
                                    break
                                elif sel_edge.end_socket.node != sel_node.node:
                                    node_change = sel_edge.end_socket.node
                                    new_param_val = new_data['inputs_names'][sel_index]
                                    old_param_val = node_change.obj_title
                                    # Меняем параметр объекта и обновляем на сцене графику
                                    if new_data['inputs_names'][0] != node_change.obj_title:
                                        node_change.obj_title = new_param_val
                                        if hasattr(node_change, 'obj_port') and node_change.obj_port is not None:
                                            node_change.title(node_change.op_title, node_change.obj_title,
                                                              node_change.obj_port)
                                        else:
                                            node_change.title(node_change.op_title, node_change.obj_title)

                                    # Обновляем параметры в изменяемой ноде
                                    for outputs_name in node_change.outputs_names:
                                        param_index = node_change.outputs_names.index(outputs_name)
                                        if outputs_name == old_param_val:
                                            node_change.outputs_names[param_index] = new_param_val

                                    # Обновляем в исходной ноде параметры
                                    sel_node.node.inputs_names = new_data['inputs_names']
                                    break
                        except Exception as ex:
                            pass

                # Если изменены выходные данные, то только для выбранного объекта, в других обновляем их параметры
                if sel_node.node.outputs_names != new_data['outputs_names']:
                    for sel_socket in sel_node.node.outputs:
                        sel_index = sel_node.node.outputs.index(sel_socket)
                        try:
                            for sel_edge in sel_socket.edges:
                                if sel_edge.start_socket.node != sel_node.node:
                                    node_change = sel_edge.end_socket.node
                                    new_param_val = new_data['outputs_names'][sel_index]
                                    old_param_val = sel_node.node.obj_title

                                    # Обновляем параметры в изменяемой ноде
                                    for inputs_name in node_change.inputs_names:
                                        param_index = node_change.inputs_names.index(inputs_name)
                                        if inputs_name == old_param_val:
                                            node_change.inputs_names[param_index] = new_param_val

                                    # Обновляем в исходной ноде параметры
                                    sel_node.node.outputs_names = new_data['outputs_names']

                                    # Обновляем графику у данного объекта, в зависимости от 1 параметра outputs_names
                                    # Меняем параметр объекта и обновляем на сцене графику
                                    if new_data['outputs_names'][0] != sel_node.node.obj_title:
                                        sel_node.node.obj_title = new_param_val
                                        if hasattr(sel_node.node, 'obj_port') and sel_node.node.obj_port is not None:
                                            sel_node.node.title(sel_node.node.op_title, sel_node.node.obj_title,
                                                                sel_node.node.obj_port)
                                        else:
                                            sel_node.node.title(sel_node.node.op_title, sel_node.node.obj_title)

                                    break
                                elif sel_edge.end_socket.node != sel_node.node:
                                    node_change = sel_edge.end_socket.node
                                    new_param_val = new_data['outputs_names'][sel_index]
                                    old_param_val = sel_node.node.obj_title

                                    # Обновляем параметры в изменяемой ноде
                                    for inputs_name in node_change.inputs_names:
                                        param_index = node_change.inputs_names.index(inputs_name)
                                        if inputs_name == old_param_val:
                                            node_change.inputs_names[param_index] = new_param_val

                                    # Обновляем в исходной ноде параметры
                                    sel_node.node.outputs_names = new_data['outputs_names']

                                    # Обновляем графику у данного объекта, в зависимости от 1 параметра outputs_names
                                    # Меняем параметр объекта и обновляем на сцене графику
                                    if new_data['outputs_names'][0] != sel_node.node.obj_title:
                                        sel_node.node.obj_title = new_param_val
                                        if hasattr(sel_node.node, 'obj_port') and sel_node.node.obj_port is not None:
                                            sel_node.node.title(sel_node.node.op_title, sel_node.node.obj_title,
                                                                sel_node.node.obj_port)
                                        else:
                                            sel_node.node.title(sel_node.node.op_title, sel_node.node.obj_title)

                                    break
                        except Exception as ex:
                            pass
            break
        self.scene.grScene.scene.history.storeHistory("change data selected", setModified=True)

    def onMarkedDirty(self): pass

    def createInParam(self):
        try:
            if hasattr(self, 'inputs_names') and \
                    (self.inputs_names is None or len(self.inputs_names) <= 0):
                new_list = []
                for sel_socket in self.inputs:
                    try:
                        for sel_edge in sel_socket.edges:
                            in_node = None
                            if sel_edge.start_socket.node != self:
                                in_node = sel_edge.start_socket.node
                            elif sel_edge.end_socket.node != self:
                                in_node = sel_edge.end_socket.node
                            if in_node is not None and hasattr(self, 'obj_title') \
                                    and self.obj_title is not None:
                                new_list.append(in_node.obj_title)
                    except:
                        pass
                self.inputs_names = new_list
        except Exception as ex:
            print(ex)

    def createOutParam(self):
        try:
            if hasattr(self, 'outputs_names') and (self.outputs_names is None or len(self.outputs_names) <= 0):
                new_list = []
                for _index in range(len(self.outputs)):
                    try:
                        if hasattr(self, 'obj_title') and self.obj_title is not None:
                            new_list.append(self.obj_title)
                    except:
                        pass
                self.outputs_names = new_list
        except Exception as ex:
            print(ex)

    def updateInParam(self):
        try:
            if hasattr(self, 'inputs_names'):
                new_list = []
                for sel_socket in self.inputs:
                    try:
                        for sel_edge in sel_socket.edges:
                            in_node = None
                            if sel_edge.start_socket.node != self:
                                in_node = sel_edge.start_socket.node
                            elif sel_edge.end_socket.node != self:
                                in_node = sel_edge.end_socket.node
                            if in_node is not None and hasattr(self, 'obj_title') \
                                    and self.obj_title is not None:
                                new_list.append(in_node.obj_title)
                    except:
                        pass
                self.inputs_names = new_list
        except Exception as ex:
            print(ex)

    def markChildrenDirty(self, new_value=True):
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)

    def markDescendantsDirty(self, new_value=True):
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markChildrenDirty(new_value)

    def isInvalid(self):
        return self._is_invalid

    def markInvalid(self, new_value=True):
        self._is_invalid = new_value
        if self._is_invalid: self.onMarkedInvalid()

    def onMarkedInvalid(self): pass

    def markChildrenInvalid(self, new_value=True):
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)

    def markDescendantsInvalid(self, new_value=True):
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
            other_node.markChildrenInvalid(new_value)

    def eval(self):
        self.markDirty(False)
        self.markInvalid(False)
        return 0

    def evalChildren(self):
        for node in self.getChildrenNodes():
            node.eval()

            if (node.value == 1):
                self.portWriteON()

            if (node.value == 0):
                self.portWriteOFF()

    def portWriteOFF(self):
        # Команда привязки для устройства-датчика на 0-й канал
        # Подробнее по ссылке http://lnnk.in/@noo
        package = bytearray([171, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 173, 172])
        # Подсчёт контрольной суммы для 15го байта в массиве (младший байт от суммы байтов с 0-го по 14-ый включительно)
        byteSumm = 0
        for outcomingByte in range(0, 15):
            byteSumm += package[outcomingByte]
        package[15] = byteSumm % 256

        try:
            c = self.port.write(package)

            print("Ответ от mtrf:")
            # Выводим шапку таблицы columnNames, форматируя вывод
            columnNames = ['ST', 'MODE', 'CTR', 'TOGL', 'CH', 'CMD', 'FMT', 'D0', 'D1', 'D2', 'D3', 'ID0', 'ID1', 'ID2',
                           'ID3', 'CRC', 'SP']
            for column in columnNames:
                print(column.ljust(4, ' '), end=' ')
        except:
            pass

    def portWriteON(self):
        # Команда привязки для устройства-датчика на 0-й канал
        # Подробнее по ссылке http://lnnk.in/@noo
        package = bytearray([171, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 175, 172])
        # Подсчёт контрольной суммы для 15го байта в массиве (младший байт от суммы байтов с 0-го по 14-ый включительно)
        byteSumm = 0
        for outcomingByte in range(0, 15):
            byteSumm += package[outcomingByte]
        package[15] = byteSumm % 256

        try:
            c = self.port.write(package)

            print("Ответ от mtrf:")
            # Выводим шапку таблицы columnNames, форматируя вывод
            columnNames = ['ST', 'MODE', 'CTR', 'TOGL', 'CH', 'CMD', 'FMT', 'D0', 'D1', 'D2', 'D3', 'ID0', 'ID1', 'ID2',
                           'ID3', 'CRC', 'SP']
            for column in columnNames:
                print(column.ljust(4, ' '), end=' ')
        except:
            pass

    # traversing nodes functions
    def getChildrenNodes(self):
        if self.outputs == []: return []
        other_nodes = []
        for ix in range(len(self.outputs)):
            for edge in self.outputs[ix].edges:
                other_node = edge.getOtherSocket(self.outputs[ix]).node
                other_nodes.append(other_node)
        return other_nodes


    def getInput(self, index=0):
        try:
            edge = self.inputs[index].edges[0]
            socket = edge.getOtherSocket(self.inputs[index])
            return socket.node
        except IndexError:
            print("EXC: Trying to get input, but none is attached to", self)
            return None
        except Exception as e:
            dumpException(e)
            return None


    def getInputs(self, index=0):
        ins = []
        for edge in self.inputs[index].edges:
            other_socket = edge.getOtherSocket(self.inputs[index])
            ins.append(other_socket.node)
        return ins

    def getOutputs(self, index=0):
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outs.append(other_socket.node)
        return outs


    # serialization functions

    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())
        return OrderedDict([
            ('id', self.id),
            ('title', self.op_title),
            ('icon', self.icon),
            ('obj_title', self.obj_title),
            ('obj_port', self.obj_port),
            ('obj_data', self.obj_data),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', self.content.serialize()),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        try:
            if restore_id: self.id = data['id']
            hashmap[data['id']] = self

            self.setPos(data['pos_x'], data['pos_y'])
            if 'obj_port' in data and data['obj_port'] is not None:
                self.title(data['title'], data['obj_title'], data['obj_port'])
            else:
                self.title(data['title'], data['obj_title'])

            data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
            data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
            num_inputs = len(data['inputs'])
            num_outputs = len(data['outputs'])

            self.inputs = []
            for socket_data in data['inputs']:
                new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                    socket_type=socket_data['socket_type'], count_on_this_node_side=num_inputs,
                                    is_input=True)
                new_socket.deserialize(socket_data, hashmap, restore_id)
                self.inputs.append(new_socket)

            self.outputs = []
            for socket_data in data['outputs']:
                new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                    socket_type=socket_data['socket_type'], count_on_this_node_side=num_outputs,
                                    is_input=False)
                new_socket.deserialize(socket_data, hashmap, restore_id)
                self.outputs.append(new_socket)

            if 'obj_data' in data and data["obj_data"] is not None:
                self.obj_data = data["obj_data"]

            if 'obj_port' in data and data["obj_port"] is not None:
                self.obj_data = data["obj_port"]

            if 'icon' in data and data["icon"] is not None:
                self.icon = data["icon"]

            # Если нет имён у входных/выходных параметров, то добавляем их из параметра obj_title
            self.createOutParam()

            return self
        except Exception as e: dumpException(e)

        # also deseralize the content of the node
        res = self.content.deserialize(data['content'], hashmap)

        return True & res