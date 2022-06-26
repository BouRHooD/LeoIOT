import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class thing_window(QMainWindow):
    login_data = pyqtSignal(str, str, str, str, str, bool)
    name_thing = "Вещь"
    DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__))).replace("\\", "/")
    DIR_ICONS = DIR_MAIN + "/styles/icons" + "/"
    DIR_SETTINGS = DIR_MAIN + "/settings/"
    icon = DIR_ICONS + "house-things.png"
    obj_port = ""
    obj_name = "T"
    elements_count = 0
    state_type = True

    def __init__(self, parent=None, title="Настройки новой вещи", name_thing="Вещь", obj_name="T", elements_count=0):
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
        self.combo_icon.addItem(QIcon(self.DIR_ICONS + 'mtrf64.png'), "mtrf64.png")
        self.combo_icon.addItem(QIcon(self.DIR_ICONS + 'zigbee.png'), "zigbee.png")

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

        self.combo_port_label = QLabel("Выбирите порт")
        self.combo_port_label.setAlignment(Qt.AlignCenter)
        self.combo_port = QComboBox(self)
        self.combo_port.currentTextChanged.connect(self.select_port_change)
        self.init_port_combo()

        self.saveButton = QPushButton('Сохранить найстройки', clicked=self.save_settings)

        grid = QGridLayout()
        grid.setSpacing(11)

        # saveButton ячейка начинается с нулевой строки нулевой колонки, и занимает 1 строку и 1 колонку.
        grid.addWidget(self.combo_label, 0, 0, 1, 1)
        grid.addWidget(self.combo, 1, 0, 1, 1)
        grid.addWidget(self.combo_icon_label, 2, 0, 1, 1)
        grid.addWidget(self.combo_icon, 3, 0, 1, 1)
        grid.addWidget(self.combo_port_label, 4, 0, 1, 1)
        grid.addWidget(self.combo_port, 5, 0, 1, 1)
        grid.addWidget(self.textEdit_label, 6, 0, 1, 1)
        grid.addWidget(self.textEdit, 7, 0, 1, 1)
        grid.addWidget(self.obj_textEdit_label, 8, 0, 1, 1)
        grid.addWidget(self.obj_textEdit, 9, 0, 1, 1)
        grid.addWidget(self.saveButton, 10, 0, 1, 1)

        self.main_widget = QWidget(self)
        self.main_widget.setLayout(grid)
        self.setCentralWidget(self.main_widget)

    def select_port_change(self, str):
        self.obj_port = str

    def loadjsonDataSettingPorts(self):
        try:
            import json
            with open(self.DIR_SETTINGS + 'used_ports.json.txt', "r") as f:
                self.jsonDataSettingPorts  = json.load(f)
                return self.jsonDataSettingPorts
        except Exception as ex:
            print(ex)

    def init_port_combo(self):
        try:
            self.jsonDataSettingPorts = self.loadjsonDataSettingPorts()
            self.flagErrorLoad = False

            if self.combo.currentText() == "Входное значение":
                self.combo_port.clear()                                                       # delete items of list

                try:
                    for in_port in self.jsonDataSettingPorts["in_ports"]:
                        for port_name in in_port:
                            for port_num in in_port[port_name]:
                                icon = QIcon(self.DIR_ICONS + 'settings.png')
                                low_port_name = str(port_name.lower())
                                if low_port_name.__contains__("digital"):
                                    icon = QIcon(self.DIR_ICONS + 'letter-d.png')
                                if low_port_name.__contains__("analog"):
                                    icon = QIcon(self.DIR_ICONS + 'a.png')
                                self.combo_port.addItem(icon, port_name + "_" + port_num)

                    if self.jsonDataSettingPorts is not None:
                        self.combo_port.addItem(QIcon(self.DIR_ICONS + 'mtrf64.png'), "MTRF-64")
                        self.combo_port.addItem(QIcon(self.DIR_ICONS + 'zigbee.png'), "ZIGBEE")
                except Exception as ex:
                    print(ex)
                    self.flagErrorLoad = True

                if self.jsonDataSettingPorts is None or self.flagErrorLoad:
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_4")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_17")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_27")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_22")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_5")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_6")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_13")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_19")
            elif self.combo.currentText() == "Выходное значение":
                self.combo_port.clear()  # delete items of list

                try:
                    for in_port in self.jsonDataSettingPorts["out_ports"]:
                        for port_name in in_port:
                            for port_num in in_port[port_name]:
                                icon = QIcon(self.DIR_ICONS + 'settings.png')
                                low_port_name = str(port_name.lower())
                                if low_port_name.__contains__("digital"):
                                    icon = QIcon(self.DIR_ICONS + 'letter-d.png')
                                if low_port_name.__contains__("analog"):
                                    icon = QIcon(self.DIR_ICONS + 'a.png')
                                self.combo_port.addItem(icon, port_name + "_" + port_num)

                    if self.jsonDataSettingPorts is not None:
                        self.combo_port.addItem(QIcon(self.DIR_ICONS + 'mtrf64.png'), "MTRF-64")
                        self.combo_port.addItem(QIcon(self.DIR_ICONS + 'zigbee.png'), "ZIGBEE")
                except:
                    pass

                if self.jsonDataSettingPorts is None or self.flagErrorLoad:
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_18")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_23")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_24")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_25")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_12")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_16")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_20")
                    self.combo_port.addItem(QIcon(self.DIR_ICONS + 'house-things.png'), "GPIO_21")
        except:
            pass

    def save_settings(self):
        self.icon = self.DIR_ICONS + self.icon
        print(self.icon)
        self.login_data.emit(str(self.name_thing), str(self.icon), str(self.elements_count), str(self.obj_name),
                             str(self.obj_port), bool(self.state_type))
        self.close()

    def state_type_change(self, str):
        if str == "Входное значение":
            self.state_type = True
        elif str == "Выходное значение":
            self.state_type = False

        # Меняем значение в комбо боксе с портами
        self.init_port_combo()

    def icon_change(self, str):
        self.icon = str

    def textEdit_change(self):
        self.name_thing = self.textEdit.toPlainText()

    def obj_textEdit_change(self):
        self.obj_name = self.obj_textEdit.toPlainText()

