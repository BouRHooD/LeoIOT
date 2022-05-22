import sys
from os import path
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class thing_window(QMainWindow):
    login_data = pyqtSignal(str, str, str, str, bool)
    name_thing = "Вещь"
    DIR_MAIN = path.dirname(path.abspath(str(sys.modules['__main__'].__file__)))
    DIR_ICONS = DIR_MAIN + "\styles\icons" + "\\"
    icon = DIR_ICONS + "house-things.png"
    obj_name = "T"
    elements_count = 0
    state_type = True

    def __init__(self, parent=None, title="Настройки новой вещи", name_thing="Вещь", obj_name = "T", elements_count=0):
        super(thing_window, self).__init__(parent)
        print(self.icon)
        self.title = title
        self.name_thing = name_thing
        self.obj_name = obj_name
        self.elements_count = elements_count
        self.initUI()

    def initUI(self):
        # Настройки окна (x,y, width, height)
        self.setGeometry(600, 400, 400, 200)
        self.setWindowTitle(self.title)

        # "Настройки виджетов для вещей"
        self.combo_label = QLabel("Выбирите тип вещи")
        self.combo_label.setAlignment(Qt.AlignCenter)
        self.combo = QComboBox(self)
        self.combo.addItem("Входное значение")
        self.combo.addItem("Выходное значение")
        self.combo.currentTextChanged.connect(self.state_type_change)

        self.combo_icon_label = QLabel("Выбирите изображение для вещи")
        self.combo_icon_label.setAlignment(Qt.AlignCenter)
        self.combo_icon = QComboBox(self)
        self.combo_icon.currentTextChanged.connect(self.icon_change)
        self.combo_icon.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "house-things.png")
        self.combo_icon.addItem(QIcon(self.DIR_ICONS + 'icon-brightness-1758514.png'), "icon-brightness-1758514.png")
        self.combo_icon.addItem(QIcon(self.DIR_ICONS + 'icon-fan-877921.png'), "icon-fan-877921.png")
        self.combo_icon.addItem(QIcon(self.DIR_ICONS + 'icon-lightbulb-673876.png'), "icon-lightbulb-673876.png")
        self.combo_icon.addItem(QIcon(self.DIR_ICONS + 'icon-temperature-sensor-1485456.png'), "icon-temperature-sensor-1485456.png")
        self.combo_icon.addItem(QIcon(self.DIR_ICONS + 'settings.png'), "settings.png")

        self.textEdit_label = QLabel("Введите название вещи")
        self.textEdit_label.setAlignment(Qt.AlignCenter)
        self.textEdit = QTextEdit(self)
        self.textEdit.textChanged.connect(self.textEdit_change)
        self.textEdit.setFixedSize(self.width(), 26)
        self.textEdit.setText(self.name_thing)

        self.obj_textEdit_label = QLabel("Введите название параметра (для отправки на ThingWorx)")
        self.obj_textEdit_label.setAlignment(Qt.AlignCenter)
        self.obj_textEdit = QTextEdit(self)
        self.obj_textEdit.textChanged.connect(self.obj_textEdit_change)
        self.obj_textEdit.setFixedSize(self.width(), 26)
        self.obj_textEdit.setText(self.obj_name)

        self.saveButton = QPushButton('Сохранить найстройки', clicked=self.save_settings)

        grid = QGridLayout()
        grid.setSpacing(9)

        # saveButton ячейка начинается с нулевой строки нулевой колонки, и занимает 1 строку и 1 колонку.
        grid.addWidget(self.combo_label, 0, 0, 1, 1)
        grid.addWidget(self.combo, 1, 0, 1, 1)
        grid.addWidget(self.combo_icon_label, 2, 0, 1, 1)
        grid.addWidget(self.combo_icon, 3, 0, 1, 1)
        grid.addWidget(self.textEdit_label, 4, 0, 1, 1)
        grid.addWidget(self.textEdit, 5, 0, 1, 1)
        grid.addWidget(self.obj_textEdit_label, 6, 0, 1, 1)
        grid.addWidget(self.obj_textEdit, 7, 0, 1, 1)
        grid.addWidget(self.saveButton, 8, 0, 1, 1)

        self.main_widget = QWidget(self)
        self.main_widget.setLayout(grid)
        self.setCentralWidget(self.main_widget)

    def save_settings(self):
        self.login_data.emit(str(self.name_thing), str(self.icon), str(self.elements_count), str(self.obj_name),
                             bool(self.state_type))
        self.close()

    def state_type_change(self, str):
        if str == "Входное значение":
            self.state_type = True
        elif str == "Выходное значение":
            self.state_type = False

    def icon_change(self, str):
        self.icon = str

    def textEdit_change(self):
        self.name_thing = self.textEdit.toPlainText()

    def obj_textEdit_change(self):
        self.obj_name = self.obj_textEdit.toPlainText()

