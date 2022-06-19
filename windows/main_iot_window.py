import json
import sys
import os
import time

import requests
from PyQt5 import QtWidgets, QtNetwork, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from multiprocessing.dummy import Pool

from nodeeditor.utils import loadStylesheets
from nodeeditor.node_editor_window import NodeEditorWindow
from windows.sub_window import IOTSubWindow
from widgets.drag_listbox import QDMDragListbox, TWListbox
from nodeeditor.utils import dumpException, pp
from settings.calc_conf import *

# images for the dark skin
import styles.qss.nodeeditor_dark_resources

DEBUG = False

class MainIOTWindow(NodeEditorWindow):
    DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__))).replace("\\", "/")
    DIR_ICONS = DIR_MAIN + "/styles/icons" + "/"
    DIR_CSS = DIR_MAIN + "/styles/qss" + "/"
    thingListWidget = None

    def initUI(self):
        self.name_company = 'Surflay'
        self.name_product = 'Шлюз интернет вещей'

        self.ON_OFF_SEND_DATA = False
        self.ON_OFF_GPIO_PORTS = False

        self.stylesheet_filename = self.DIR_CSS + "nodeeditor.qss"
        loadStylesheets(
            self.stylesheet_filename
        )

        self.empty_icon = QIcon(self.DIR_MAIN)

        if DEBUG:
            print("Registered nodes:")
            pp(CALC_NODES)

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createNodesDock()

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("Home IoT")                            # Название главного окна
        self.setWindowIcon(QIcon(self.DIR_ICONS + "surflay.ico"))  # Иконка на гланое окно

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()


    def createActions(self):
        super().createActions()

        self.actClose = QAction("Закрыть текущее окно", self, statusTip="Закрыть текущее окно", triggered=self.mdiArea.closeActiveSubWindow)
        # self.actCloseAll = QAction("Закрыть все окна", self, statusTip="Close all the windows", triggered=self.mdiArea.closeAllSubWindows)
        # self.actTile = QAction("Плиточные окна", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        # self.actCascade = QAction("Каскад окон", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        # self.actNext = QAction("Следующий", self, shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        # self.actPrevious = QAction("Предыдущий", self, shortcut=QKeySequence.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

        self.actAbout = QAction("О программе", self, statusTip='Показать окно "О приложении"', triggered=self.about)

    def getCurrentNodeEditorWidget(self):
        """ we're returning NodeEditorWidget here... """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def onFileNew(self):
        try:
            subwnd = self.createMdiChild()
            subwnd.widget().fileNew()
            subwnd.show()
        except Exception as e: dumpException(e)

    def onFileOpen(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Загрузить график из файла')

        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        # we need to create new subWindow and open the file
                        nodeeditor = IOTSubWindow()
                        nodeeditor.scene.thingListChanged = self.thingListWidget
                        if nodeeditor.fileLoad(fname):
                            self.statusBar().showMessage("File %s loaded" % fname, 5000)
                            nodeeditor.setTitle()
                            subwnd = self.createMdiChild(nodeeditor)
                            subwnd.show()
                        else:
                            nodeeditor.close()
        except Exception as e: dumpException(e)

    def about(self):
        QMessageBox.about(self, "О программе Home IoT",
                "Это программа для автоматизации подключеных устройств и отправки данных в интернет облако, "
                "например, "
                "<a href='https://https://developer.thingworx.com//'>ThingWorx</a>")

    def createMenus(self):
        super().createMenus()

        self.windowMenu = self.menuBar().addMenu("Окно")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("Помощь")
        self.helpMenu.addAction(self.actAbout)

        self.editMenu.aboutToShow.connect(self.updateEditMenu)

    def updateMenus(self):
        # print("update Menus")
        active = self.getCurrentNodeEditorWidget()
        hasMdiChild = (active is not None)

        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        self.actClose.setEnabled(hasMdiChild)
        # self.actCloseAll.setEnabled(hasMdiChild)
        # self.actTile.setEnabled(hasMdiChild)
        # self.actCascade.setEnabled(hasMdiChild)
        # self.actNext.setEnabled(hasMdiChild)
        # self.actPrevious.setEnabled(hasMdiChild)
        self.actSeparator.setVisible(hasMdiChild)

        self.updateEditMenu()

    def updateEditMenu(self):
        try:
            # print("update Edit Menu")
            active = self.getCurrentNodeEditorWidget()
            hasMdiChild = (active is not None)

            self.actPaste.setEnabled(hasMdiChild)

            self.actCut.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actCopy.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actDelete.setEnabled(hasMdiChild and active.hasSelectedItems())

            self.actUndo.setEnabled(hasMdiChild and active.canUndo())
            self.actRedo.setEnabled(hasMdiChild and active.canRedo())
        except Exception as e: dumpException(e)

    def updateWindowMenu(self):
        self.windowMenu.clear()

        toolbar_nodes = self.windowMenu.addAction("Логические узлы")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())

        toolbar_thing = self.windowMenu.addAction("Узлы подключенных вещей")
        toolbar_thing.setCheckable(True)
        toolbar_thing.triggered.connect(self.onWindowThingToolbar)
        toolbar_thing.setChecked(self.thingDock.isVisible())

        #toolbar_tw = self.windowMenu.addAction("Связь с ThingWorx")
        #toolbar_tw.setCheckable(True)
        #toolbar_tw.triggered.connect(self.onWindowConnectTWToolbar)
        #toolbar_tw.setChecked(self.thing_connectDock.isVisible())

        self.windowMenu.addSeparator()

        self.windowMenu.addAction(self.actClose)
        # self.windowMenu.addAction(self.actCloseAll)
        # self.windowMenu.addSeparator()
        # self.windowMenu.addAction(self.actTile)
        # self.windowMenu.addAction(self.actCascade)
        # self.windowMenu.addSeparator()
        # self.windowMenu.addAction(self.actNext)
        # self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)

        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def onWindowNodesToolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def onWindowThingToolbar(self):
        if self.thingDock.isVisible():
            self.thingDock.hide()
        else:
            self.thingDock.show()

    def onWindowConnectTWToolbar(self):
        if self.thing_connectDock.isVisible():
            self.thing_connectDock.hide()
        else:
            self.thing_connectDock.show()

    def createToolBars(self):
        pass

    def changeComboLogic(self, str):
        copy_dict = CALC_NODES
        new_dict = {}
        if str == "Основные операции":
            for key in copy_dict:
                item = copy_dict.get(key)
                if item is not None and item.content_label_objname not in iot_list:
                    new_dict[key] = item
            self.nodesListWidget.clear()
            keys = list(new_dict.keys())
            keys.sort()
            for key in keys:
                node = get_class_from_opcode(key, new_dict)
                self.nodesListWidget.addMyItem(name=node.op_title, icon=node.icon, op_code=node.op_code)
        elif str == "Платформы интернета вещей":
            for key in copy_dict:
                item = copy_dict.get(key)
                if item is not None and item.content_label_objname in iot_list:
                    new_dict[key] = item
            self.nodesListWidget.clear()
            keys = list(new_dict.keys())
            keys.sort()
            for key in keys:
                node = get_class_from_opcode(key, new_dict)
                self.nodesListWidget.addMyItem(name=node.op_title, icon=node.icon, op_code=node.op_code)
        else:
            self.nodesListWidget.clear()
            keys = list(CALC_NODES.keys())
            keys.sort()
            for key in keys:
                node = get_class_from_opcode(key, CALC_NODES)
                self.nodesListWidget.addMyItem(name=node.op_title, icon=node.icon, op_code=node.op_code)
        QtCore.QCoreApplication.processEvents()

    def createNodesDock(self):
        # "Логические узлы"
        self.nodesListWidget = QDMDragListbox(SOME_NODES=CALC_NODES)

        self.comboLogic = QComboBox(self)
        self.comboLogic.addItem("Основные операции")
        self.comboLogic.addItem("Платформы интернета вещей")
        self.comboLogic.currentTextChanged.connect(self.changeComboLogic)
        self.changeComboLogic("Основные операции")

        self.layout_logic = QtWidgets.QBoxLayout(2)
        self.layout_logic.addWidget(self.comboLogic)
        self.layout_logic.addWidget(self.nodesListWidget)

        self.dockedWidget = QtWidgets.QWidget()
        self.dockedWidget.setLayout(self.layout_logic)

        self.nodesDock = QDockWidget("Логические узлы")
        self.nodesDock.setFloating(True)
        self.nodesDock.setWidget(self.dockedWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodesDock)


        # "Узлы подключенных вещей"
        self.thingListWidget = QDMDragListbox(SOME_NODES=THING_NODES, checkable=False)
        self.thingListWidget.itemClicked.connect(self.state_change)
        self.thingListWidget.addMyItem(name='Датчик освещенности', icon=self.DIR_ICONS + 'icon-brightness-1758514.png', op_code=11, obj_title="T0")
        self.thingListWidget.addMyItem(name='Датчик температуры',  icon=self.DIR_ICONS + 'icon-temperature-sensor-1485456.png', op_code=12, obj_title="T1")
        self.thingListWidget.addMyItem(name='Лампа',  icon=self.DIR_ICONS + 'icon-lightbulb-673876.png', op_code=13, obj_title="T2", thing_in=False)
        self.thingListWidget.addMyItem(name='Вентилятор',  icon=self.DIR_ICONS + 'icon-fan-877921.png', op_code=14, obj_title="T3", thing_in=False)

        self.ON_OFFsendButton_tw = QtWidgets.QPushButton("Включить отправку на сервера", clicked=self.ON_OFFsendDataTW)
        self.ON_OFF_GPIO_PORTS_button = QtWidgets.QPushButton("Включить работу с портами", clicked=self.on_off_gpio_ports)
        self.addButton = QtWidgets.QPushButton(text='Добавить вещь', clicked=self.addThing_element)
        self.delButton = QtWidgets.QPushButton(text='Удалить вещь', clicked=self.deleteThing_element)

        self.layout_things = QtWidgets.QBoxLayout(2)
        self.layout_things.addWidget(self.ON_OFFsendButton_tw)
        self.layout_things.addWidget(self.ON_OFF_GPIO_PORTS_button)
        self.layout_things.addWidget(self.thingListWidget)
        self.layout_things.addWidget(self.addButton)
        self.layout_things.addWidget(self.delButton)

        self.dockedWidget = QtWidgets.QWidget()
        self.dockedWidget.setLayout(self.layout_things)

        self.thingDock = QDockWidget("Узлы подключенных вещей")
        self.thingDock.setWidget(self.dockedWidget)
        self.thingDock.setFloating(True)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.thingDock)

        # "Связь с ThingWorx"
        self.list_thing = TWListbox()
        self.list_thing_to_send = TWListbox()
        self.sendButton_tw = QtWidgets.QPushButton('Отправить данные', clicked=self.sendDataTW)
        self.add_select_Button_tw = QtWidgets.QPushButton('->', clicked=self.relocateToDataTW)
        self.del_select_Button_tw = QtWidgets.QPushButton('<-', clicked=self.relocateFromDataTW)

        grid = QGridLayout()
        grid.setSpacing(10)

        # list_thing ячейка начинается с нулевой строки нулевой колонки, и занимает 5 строки и 1 колонку.
        grid.addWidget(self.list_thing, 0, 0, 5, 1)
        grid.addWidget(self.sendButton_tw, 1, 1)
        grid.addWidget(self.add_select_Button_tw, 2, 1)
        grid.addWidget(self.del_select_Button_tw, 3, 1)
        grid.addWidget(self.list_thing_to_send, 0, 2, 5, 1)

        self.dockedWidget_tw = QtWidgets.QWidget()
        self.dockedWidget_tw.setLayout(grid)

        self.thing_connectDock = QDockWidget("Связь с ThingWorx")
        self.thing_connectDock.setWidget(self.dockedWidget_tw)
        self.thing_connectDock.setFloating(True)
        #self.addDockWidget(Qt.TopDockWidgetArea, self.thing_connectDock)

    def state_change(self, item):
        index = self.thingListWidget.indexFromItem(item).row()
        if item.checkState() == Qt.Checked:
            pass

    def relocateToDataTW(self):
        pass

    def relocateFromDataTW(self):
        pass

    def ON_OFFsendDataTW(self):
        if self.ON_OFF_SEND_DATA:
            self.ON_OFF_SEND_DATA = False
            self.ON_OFFsendButton_tw.setText("Включить отправку на сервера")
        else:
            self.ON_OFF_SEND_DATA = True
            self.ON_OFFsendButton_tw.setText("Отключить отправку на сервера")
            self.sendDataTW()

    def on_off_gpio_ports(self):
        if self.ON_OFF_GPIO_PORTS:
            self.ON_OFF_GPIO_PORTS = False
            self.ON_OFF_GPIO_PORTS_button.setText("Включить работу с портами")
        else:
            self.ON_OFF_GPIO_PORTS = True
            self.ON_OFF_GPIO_PORTS_button.setText("Отключить работу с портами")
            pool_gpio = Pool()
            pool_gpio.apply_async(self.call_gpio_poll)

    def call_gpio_poll(self):
        while self.ON_OFF_GPIO_PORTS:
            try:
                list_dict_data = self.getDictDataForGPIO()
                print(list_dict_data)
                try:
                    import RPi.GPIO as GPIO
                    # GPIO.BCM - будет использоваться нумерация GPIO
                    # GPIO.BOARD - будет использоваться нумерация пинов P1-26
                    GPIO.setmode(GPIO.BCM)

                    for dict_data in list_dict_data:
                        try:
                            print(dict_data)
                            select_node = dict_data["node"]
                            select_type_node = dict_data["select_type_node"]
                            select_type_port = dict_data["select_type_port"]
                            select_num_port = dict_data["select_num_port"]
                            if select_num_port is None: continue

                            select_num_port = int(select_num_port)

                            if select_type_node == "input" and select_type_port == "digital":
                                pass
                                # Конфигурируем GPIO как вход
                                GPIO.setup(select_num_port, GPIO.IN)
                                # Считываем сигнал с GPIO 8 в переменную pin_signal_input
                                pin_signal_input = GPIO.input(select_num_port)
                                print(f'pin_signal_input: {pin_signal_input}')
                                select_node.setText(pin_signal_input)
                                select_node.evalImplementation()
                            elif select_type_node == "output" and select_type_port == "digital":
                                # Конфигурируем GPIO как выход
                                GPIO.setup(select_num_port, GPIO.OUT)
                                node_select_value = select_node.evalImplementation()
                                value_bool = bool(node_select_value)
                                # Выводим на GPIO 7 логическую "1" (3.3 V) или логический "0"
                                GPIO.output(select_num_port, value_bool)
                        except Exception as ex:
                            dumpException(ex)
                except Exception as ex:
                    dumpException(ex)
                finally:
                    pass
            except Exception as ex:
                dumpException(ex)
            time.sleep(1)


    def sendDataTW(self):
        self.pool_processing_create()

    def on_success(self, response):
        if response is None: return
        print(f'Response Code: {response.status_code}')
        print(f'Response Content: {response.content}')
        print(f'------------------------------------------------------------')

    def on_error(self, ex):
        print(f'Post requests failed: {ex}')

    def call_api(self):
        while self.ON_OFF_SEND_DATA:
            self.last_node = None
            try:
                list_dict_data = self.getDictDataForSendToServer()
                if len(list_dict_data) < 1: continue

                for dict_data in list_dict_data:
                    url = dict_data["url"]
                    headers = dict_data["headers"]
                    data = dict_data["data"]
                    node = dict_data["node"]
                    node_in = dict_data["node_in"]
                    node_out = dict_data["node_out"]
                    self.last_node = node

                    if node_out is not None:
                        node_out.content_label = url + "\n" + str(data)
                        node_out.markDirty()
                        node_out.eval()

                    response, node_lbl = None, ""
                    node_lbl = node.content_label_objname
                    if "node_thingworx_obj" in node_lbl:
                        response = requests.put(url, headers=headers, json=data)
                    elif "node_fogwing_iiot_obj" in node_lbl:
                        response = requests.post(url, headers=headers, json=data)
                    elif "node_blynkio_obj" in node_lbl:
                        response = requests.get(url, params=data)

                    print(f'Data send: {dict_data}')

                    if response is not None:
                        if "node_blynkio_obj" in node_lbl and "update" in url:
                            pass
                        else:
                            node_in.content_label = "Code:" + str(response.status_code) + "\n" + "Content:" + str(response.content)
                            node_in.value = "Code:" + str(response.status_code) + "\n" + "Content:" + str(response.content)
                            node_in.markDirty()
                            node_in.eval()

                        print(f'Response Code: {response.status_code}')
                        print(f'Response Content: {response.content}')
                        print(f'------------------------------------------------------------')
                    else:
                        node_in.value = "Error"
                        node_in.markDirty()
                        node_in.eval()
            except Exception as ex:
                if self.last_node is not None:
                    self.last_node.value = "Error"
                    self.last_node.markDirty()
                    self.last_node.eval()
                dumpException(ex)
            finally:
                time.sleep(1)

    def getIOTNodes(self, nodes, scene_node, node_lbl):
        node_in, node_out = None, None
        if len(scene_node.inputs) <= 0 and len(scene_node.outputs) > 0:
            node_in = scene_node

            # Ищем вторую ноду
            for scene_node_out in nodes:
                node_lbl_out = scene_node_out.content_label_objname
                if node_lbl_out in iot_list and node_lbl_out == node_lbl:
                    if hasattr(scene_node_out, 'obj_data') and scene_node_out.obj_data is not None \
                            and scene_node_out.obj_data == scene_node.obj_data and scene_node_out != scene_node:
                        node_out = scene_node_out
                        break
        elif len(scene_node.inputs) > 0 and len(scene_node.outputs) <= 0:
            node_out = scene_node
            # Ищем вторую ноду
            for scene_node_in in nodes:
                node_lbl_in = scene_node_in.content_label_objname
                if node_lbl_in in iot_list and node_lbl_in == node_lbl:
                    if hasattr(scene_node_in, 'obj_data') and scene_node_in.obj_data is not None \
                            and scene_node_in.obj_data == scene_node.obj_data and scene_node_in != scene_node:
                        node_in = scene_node_in
                        break

        dict_iot_nodes = ({'node_in': node_in, 'node_out': node_out})
        return dict_iot_nodes

    def getDictDataForSendToServer(self):
        url = None
        outDict = {}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        list_dict_data = []
        for thing_index in THING_NODES:
            thing_node = THING_NODES.get(thing_index)
            if hasattr(thing_node, 'scene') and hasattr(thing_node.scene, 'nodes') and len(thing_node.scene.nodes) > 0:
                for scene_node in thing_node.scene.nodes:
                    node_lbl = scene_node.content_label_objname
                    if node_lbl in iot_list:
                        if hasattr(scene_node, 'obj_data') and scene_node.obj_data is not None:
                            server_name = scene_node.obj_data["server_name"]
                            thing_name = scene_node.obj_data["thing_name"]
                            service_name = scene_node.obj_data["service_name"]
                            appkey_data = scene_node.obj_data["appkey_data"]

                            iot_nodes = self.getIOTNodes(thing_node.scene.nodes, scene_node, node_lbl)
                            node_in = iot_nodes['node_in']
                            node_out = iot_nodes['node_out']

                            if 'node_thingworx_obj' in node_lbl:
                                url = 'https://' + server_name + ':8443/Thingworx/Things/' + thing_name + '/Services/' + service_name

                                headers = {
                                    'Content-Type': 'application/json',
                                    'appkey': appkey_data,
                                    'Accept': 'application/json',
                                    'x-thingworx-session': 'true',
                                    'Cache-Control': 'no-cache',
                                }

                            if 'node_fogwing_iiot_obj' in node_lbl:
                                # curl -X POST "https://portal.fogwing.net/api/v1/iothub/postPayload/withApiKey?accountID=2170&apiKey=b5d4a44eeaa24a5aac02a1c30ec911d2&devEui=581e098c9ac93f07" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"T1\": 2, \"T2\": 1}"
                                url = 'https://' + server_name + '/api/v1/iothub/postPayload/withApiKey?accountID=' + thing_name + '&apiKey=' + appkey_data + '&devEui=' + service_name

                                headers = {
                                    'Content-Type': 'application/json',
                                    'Accept': 'application/json',
                                }

                            if 'node_blynkio_obj' in node_lbl:
                                # https://blynk.cloud/external/api/update?token=ffujYGgbf805tgsf&v1=100
                                if node_out == scene_node:
                                    url = 'https://' + server_name + '/external/api/update?token=' + appkey_data
                                elif node_in == scene_node:
                                    url = 'https://' + server_name + '/external/api/get?token=' + appkey_data

                                headers = {
                                    'Content-Type': 'application/json',
                                    'Accept': 'application/json',
                                }

                            if node_out == scene_node:
                                node_inputs = scene_node.inputs
                                for node_input in node_inputs:
                                    if len(node_input.edges) <= 0:
                                        continue
                                    start_node = node_input.edges[0].start_socket.node
                                    end_node = node_input.edges[0].end_socket.node
                                    if start_node.content_label_objname not in iot_list:
                                        outDict[f'{start_node.obj_title}'] = f"{start_node.value}"
                                    elif end_node.content_label_objname not in iot_list:
                                        outDict[f'{end_node.obj_title}'] = f"{end_node.value}"

                            if node_in == scene_node:
                                pass

                            list_dict_data.append({'url': url, 'headers': headers, 'data': outDict, 'node': scene_node,
                                                   'node_in': node_in, 'node_out': node_out})
                break

        return list_dict_data

    def getDictDataForGPIO(self):
        outDict = {}

        list_dict_data = []
        for thing_index in THING_NODES:
            thing_node = THING_NODES.get(thing_index)
            if hasattr(thing_node, 'scene') and hasattr(thing_node.scene, 'nodes') and len(thing_node.scene.nodes) > 0:
                for scene_node in thing_node.scene.nodes:
                    node_lbl = scene_node.content_label_objname
                    if 'calc_node_some_thing' in node_lbl:
                        if hasattr(scene_node, 'obj_port') and scene_node.obj_port is not None:
                            node_port_str = scene_node.obj_port
                            node_port_lower = str(node_port_str).lower()
                            select_type_port, select_type_node, select_num_port = None, None, None
                            if 'digital' in node_port_lower:
                                if 'calc_node_some_thing_in' in node_lbl:
                                    select_type_node = 'input'
                                if 'calc_node_some_thing_out' in node_lbl:
                                    select_type_node = 'output'
                                select_type_port = "digital"
                                select_num_port = node_port_lower.replace("gpio_digital_", "")

                            list_dict_data.append({'node': scene_node,
                                                   'select_type_node': select_type_node,
                                                   'select_type_port': select_type_port,
                                                   'select_num_port': select_num_port})
                break

        return list_dict_data

    def pool_processing_create(self):
        pool = Pool()
        pool.apply_async(self.call_api, callback=self.on_success, error_callback=self.on_error)

    def addThing_element(self):
        from windows.add_thing_win import thing_window

        elements_count = self.thingListWidget.count()
        name = 'Вещь #' + str(elements_count)
        str_icon = self.DIR_ICONS + 'house-things.png'
        obj_name = "T" + str(elements_count)

        self.thing_window = thing_window(self, name_thing=name, obj_name=obj_name, elements_count=elements_count)
        self.thing_window.login_data[str, str, str, str, str, bool].connect(self.addThing_element_from_thing_window)
        self.thing_window.show()

    def addThing_element_from_thing_window(self, name_thing, icon, elements_count, obj_name, obj_port, obj_bool):
        self.thingListWidget.addMyItem(name=name_thing, icon=icon, op_code=elements_count, obj_title=obj_name, obj_port=obj_port, thing_in=obj_bool)

    def deleteThing_element(self):
        select_item = self.thingListWidget.currentRow()
        if select_item < 0:
            select_item = self.thingListWidget.count() - 1
        self.thingListWidget.takeItem(select_item)
        keys = list(THING_NODES)
        THING_NODES.pop(keys[select_item])
        print("del")

    def addMyItem(self, name='', icon=None, op_code=0, list_widget=None):
        item = QListWidgetItem(name)  # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)

        list_widget.addItem(item)

    def createStatusBar(self):
        self.statusBar().showMessage("Программа готова к работе")

    def createMdiChild(self, child_widget=None):
        nodeeditor = child_widget if child_widget is not None else IOTSubWindow()
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        subwnd.setWindowIcon(self.empty_icon)
        # nodeeditor.scene.addItemSelectedListener(self.updateEditMenu)
        # nodeeditor.scene.addItemsDeselectedListener(self.updateEditMenu)
        nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        nodeeditor.addCloseEventListener(self.onSubWndClose)
        return subwnd

    def onSubWndClose(self, widget, event):
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()


    def findMdiChild(self, filename):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:
                return window
        return None


    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)