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
from windows.sub_window import CalculatorSubWindow
from widgets.drag_listbox import QDMDragListbox, TWListbox
from nodeeditor.utils import dumpException, pp
from settings.calc_conf import *

# images for the dark skin
import styles.qss.nodeeditor_dark_resources

DEBUG = False

class MainIOTWindow(NodeEditorWindow):
    DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__)))
    DIR_ICONS = DIR_MAIN + "\styles\icons" + "\\"
    DIR_CSS = DIR_MAIN + "\styles\qss" + "\\"

    def initUI(self):
        self.name_company = 'Surflay'
        self.name_product = 'Шлюз интернет вещей'

        self.ON_OFF_SEND_DATA = False

        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), self.DIR_CSS + "nodeeditor.qss")
        loadStylesheets(
            os.path.join(os.path.dirname(__file__), self.DIR_CSS + "nodeeditor.qss"),
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
                        nodeeditor = CalculatorSubWindow()
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

    def createNodesDock(self):
        # "Логические узлы"
        self.nodesListWidget = QDMDragListbox(SOME_NODES=CALC_NODES)

        self.layout_logic = QtWidgets.QBoxLayout(2)
        self.layout_logic.addWidget(self.nodesListWidget)

        self.dockedWidget = QtWidgets.QWidget()
        self.dockedWidget.setLayout(self.layout_logic)

        self.nodesDock = QDockWidget("Логические узлы")
        self.nodesDock.setFloating(True)
        self.nodesDock.setWidget(self.dockedWidget)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodesDock)

        # "Узлы подключенных вещей"
        self.thingListWidget = QDMDragListbox(SOME_NODES=THING_NODES, checkable=True)
        self.thingListWidget.itemClicked.connect(self.state_change)
        self.thingListWidget.addMyItem('Датчик освещенности', self.DIR_ICONS + 'icon-brightness-1758514.png', 11, "T0")
        self.thingListWidget.addMyItem('Датчик температуры', self.DIR_ICONS + 'icon-temperature-sensor-1485456.png', 12, "T1")
        self.thingListWidget.addMyItem('Лампа', self.DIR_ICONS + 'icon-lightbulb-673876.png', 13, "T2", False)
        self.thingListWidget.addMyItem('Вентилятор', self.DIR_ICONS + 'icon-fan-877921.png', 14, "T3", False)

        self.ON_OFFsendButton_tw = QtWidgets.QPushButton("Включить отправку на ThingWorx", clicked=self.ON_OFFsendDataTW)
        self.addButton = QtWidgets.QPushButton(text='Добавить вещь', clicked=self.addThing_element)
        self.delButton = QtWidgets.QPushButton(text='Удалить вещь', clicked=self.deleteThing_element)

        self.layout_things = QtWidgets.QBoxLayout(2)
        self.layout_things.addWidget(self.ON_OFFsendButton_tw)
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
            self.ON_OFFsendButton_tw.setText("Включить отправку на ThingWorx")
        else:
            self.ON_OFF_SEND_DATA = True
            self.ON_OFFsendButton_tw.setText("Отключить отправку на ThingWorx")
            self.sendDataTW()


    def sendDataTW(self):
        url = 'https://PP-2107252209MI.portal.ptc.io:8443/Thingworx/Things/Home_IoT/Services/InOut'

        headers = {
            'Content-Type': 'application/json',
            'appkey': '768cecc2-f48a-4783-b2c6-29fdd734e538',
            'Accept': 'application/json',
            'x-thingworx-session': 'true',
            'Cache-Control': 'no-cache',
        }

        checked_items = []
        _data = ""
        for index in range(self.thingListWidget.count()):
            if self.thingListWidget.item(index).checkState() == Qt.Checked:
                item = self.thingListWidget.item(index)
                checked_items.append(item)

        outDict = {}
        for index in range(len(checked_items)):
            item = checked_items[index]
            index_thing = self.thingListWidget.indexFromItem(item).row()
            keys = list(THING_NODES)
            item_thing = THING_NODES.get(keys[index_thing])
            outDict[f'{item_thing.obj_title}'] = f"{item_thing.value}"

        # JSON форма данных для отправки
        data = outDict
        # data = {"Lamp_Main_Home": "5555", "temp": "1111", "illumination": 1110}

        # Отправили запрос с данными на ThingWorx(TW)
        # print(f'Data send: {data}')
        # response = requests.put(url, headers=headers, json=data)
        self.pool_processing_create(url, data=data, headers=headers)

        # Если код 200, то данные отправлены были успешно
        # print(f'Response Code: {response.status_code}')
        # print(f'Response Content: {response.content}')
        # print(f'------------------------------------------------------------')

    def on_success(self, response):
        print(f'Response Code: {response.status_code}')
        print(f'Response Content: {response.content}')
        print(f'------------------------------------------------------------')

    def on_error(self, ex):
        print(f'Post requests failed: {ex}')

    def call_api(self, url, data, headers):
        while self.ON_OFF_SEND_DATA:
            print(f'Data send: {data}')

            checked_items = []
            _data = ""
            for index in range(self.thingListWidget.count()):
                if self.thingListWidget.item(index).checkState() == Qt.Checked:
                    item = self.thingListWidget.item(index)
                    checked_items.append(item)

            outDict = {}
            for index in range(len(checked_items)):
                item = checked_items[index]
                index_thing = self.thingListWidget.indexFromItem(item).row()
                keys = list(THING_NODES)
                item_thing = THING_NODES.get(keys[index_thing])
                outDict[f'{item_thing.obj_title}'] = f"{item_thing.value}"

            # JSON форма данных для отправки
            print(f'Data send: {data}')
            data = outDict

            response = requests.put(url, headers=headers, json=data)
            print(f'Response Code: {response.status_code}')
            print(f'Response Content: {response.content}')
            print(f'------------------------------------------------------------')
            time.sleep(3)
        return response

    def pool_processing_create(self, url, data, headers):
        pool = Pool()
        pool.apply_async(self.call_api, args=[url, data, headers],
                         callback=self.on_success, error_callback=self.on_error)

    def addThing_element(self):
        from windows.add_thing_win import thing_window

        elements_count = self.thingListWidget.count()
        name = 'Вещь #' + str(elements_count)
        str_icon = self.DIR_ICONS + 'house-things.png'
        obj_name = "T" + str(elements_count)

        self.thing_window = thing_window(self, name_thing=name, obj_name=obj_name, elements_count=elements_count)
        self.thing_window.login_data[str, str, str, str, bool].connect(self.addThing_element_from_thing_window)
        self.thing_window.show()

    def addThing_element_from_thing_window(self, name_thing, icon, elements_count, obj_name, bool):
        self.thingListWidget.addMyItem(name_thing, icon, elements_count, obj_name, bool)

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
        nodeeditor = child_widget if child_widget is not None else CalculatorSubWindow()
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