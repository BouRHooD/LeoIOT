import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from nodeeditor.node_editor_widget import NodeEditorWidget
from nodeeditor.utils import pp


class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.name_company = 'Surflay'
        self.name_product = 'Home IoT'

        self.initUI()


    def initUI(self):
        self.createActions()
        self.createMenus()

        # create node editor widget
        self.nodeeditor = NodeEditorWidget(self)
        self.nodeeditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeeditor)

        self.createStatusBar()

        # set window properties
        self.setGeometry(200, 200, 800, 600)
        self.setTitle()
        self.show()

    def createStatusBar(self):
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        self.nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)

    def createActions(self):
        self.actNew = QAction('Новый', self, shortcut='Ctrl+N', statusTip="Создать новый график", triggered=self.onFileNew)
        self.actOpen = QAction('Загрузить', self, shortcut='Ctrl+O', statusTip="Загрузить файл", triggered=self.onFileOpen)
        self.actSave = QAction('Сохранить', self, shortcut='Ctrl+S', statusTip="Сохранить файл", triggered=self.onFileSave)
        self.actSaveAs = QAction('Сохранить как', self, shortcut='Ctrl+Shift+S', statusTip="Сохранить файл как...", triggered=self.onFileSaveAs)
        self.actExit = QAction('Выйти', self, shortcut='Ctrl+Q', statusTip="Выйти из приложения", triggered=self.close)

        self.actUndo = QAction('Отменить', self, shortcut='Ctrl+Z', statusTip="Отменить последнюю операцию", triggered=self.onEditUndo)
        self.actRedo = QAction('Повторить', self, shortcut='Ctrl+Shift+Z', statusTip="Повторить отменённую операцию", triggered=self.onEditRedo)
        self.actCut = QAction('Вырезать', self, shortcut='Ctrl+X', statusTip="Вырезать в память", triggered=self.onEditCut)
        self.actCopy = QAction('Копировать', self, shortcut='Ctrl+C', statusTip="Скопировать в память", triggered=self.onEditCopy)
        self.actPaste = QAction('Вставить', self, shortcut='Ctrl+V', statusTip="Вставить из памяти", triggered=self.onEditPaste)
        self.actDelete = QAction('Удалить', self, shortcut='Del', statusTip="Удалить выбранные элементы", triggered=self.onEditDelete)


    def createMenus(self):
        menubar = self.menuBar()

        self.fileMenu = menubar.addMenu('Файл')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

        self.editMenu = menubar.addMenu('Редактировать')
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)

    def setTitle(self):
        title = "Домашний узел устройств"
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()

        self.setWindowTitle(title)


    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def isModified(self):
        return self.getCurrentNodeEditorWidget().scene.isModified()

    def getCurrentNodeEditorWidget(self):
        return self.centralWidget()

    def maybeSave(self):
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "Вы хотите сохранить данные?",
                "Документ был изменён.\nВы хотите сохранить свои изменения?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
              )

        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False

        return True



    def onScenePosChanged(self, x, y):
        self.status_mouse_pos.setText("Позиция сцены: [%d, %d]" % (x, y))

    def onFileNew(self):
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().fileNew()
            self.setTitle()


    def onFileOpen(self):
        if self.maybeSave():
            fname, filter = QFileDialog.getOpenFileName(self, 'Загрузить график из файла')
            if fname != '' and os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)
                self.setTitle()

    def onFileSave(self):
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet(): return self.onFileSaveAs()

            current_nodeeditor.fileSave()
            self.statusBar().showMessage("Успешно сохраненно %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"): current_nodeeditor.setTitle()
            else: self.setTitle()
            return True

    def onFileSaveAs(self):
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            fname, filter = QFileDialog.getSaveFileName(self, 'Сохранить график в файл')
            if fname == '': return False

            current_nodeeditor.fileSave(fname)
            self.statusBar().showMessage("Успешно сохранено как %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"): current_nodeeditor.setTitle()
            else: self.setTitle()
            return True

    def onEditUndo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.getView().deleteSelected()

    def onEditCut(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        if self.getCurrentNodeEditorWidget():
            raw_data = QApplication.instance().clipboard().text()

            try:
                data = json.loads(raw_data)
            except ValueError as e:
                print("Pasting of not valid json data!", e)
                return

            # check if the json data are correct
            if 'nodes' not in data:
                print("JSON does not contain any nodes!")
                return

            self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    def readSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())