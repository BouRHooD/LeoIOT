import os
import sys

from PyQt5 import QtGui, QtCore, QtWidgets

DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__))).replace("\\", "/")
DIR_ICONS = DIR_MAIN + "/styles/icons" + "/"
DIR_CSS = DIR_MAIN + "/styles/qss" + "/"


class PopUpDialogThingWorxCountInOut(QtWidgets.QDialog):

    def __init__(self, outputs_enable=True, outputs_value=2):
        super(PopUpDialogThingWorxCountInOut, self).__init__()

        self.returnVal = None
        self.icon = QtGui.QIcon()

        self.setObjectName("self")
        self.resize(400, 150)
        self.setMinimumSize(QtCore.QSize(400, 150))
        self.setMaximumSize(QtCore.QSize(400, 150))
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        self.icon.addPixmap(QtGui.QPixmap(DIR_ICONS + "ask-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(self.icon)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        # 0 0 1 2 - row column rowSpan columnSpan
        self.label_text_info_inout = QtWidgets.QLabel(self)
        self.label_text_info_inout.setObjectName("label_text_inputs")
        self.label_text_info_inout.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_text_info_inout, 0, 0, 1, 2)

        self.label_text_inputs = QtWidgets.QLabel(self)
        self.label_text_inputs.setObjectName("label_text_inputs")
        self.label_text_inputs.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_text_inputs, 1, 0, 1, 1)

        self.label_text_outputs = QtWidgets.QLabel(self)
        self.label_text_outputs.setObjectName("label_text_outputs")
        self.label_text_outputs.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_text_outputs, 1, 1, 1, 1)

        self.text_inputs = QtWidgets.QSpinBox(self)
        self.text_inputs.setObjectName("text_inputs")
        self.text_inputs.setValue(2)
        self.text_inputs.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.text_inputs, 2, 0, 1, 1)

        self.text_outputs = QtWidgets.QSpinBox(self)
        self.text_outputs.setObjectName("text_outputs")
        self.text_outputs.setValue(outputs_value)
        self.text_outputs.setAlignment(QtCore.Qt.AlignCenter)
        self.text_outputs.setEnabled(outputs_enable)
        self.gridLayout.addWidget(self.text_outputs, 2, 1, 1, 1)

        self.add_link = QtWidgets.QPushButton(self)
        self.add_link.setObjectName("accept_link")
        self.gridLayout.addWidget(self.add_link, 3, 0, 1, 1)

        self.cancel_link = QtWidgets.QPushButton(self)
        self.cancel_link.setObjectName("cancel_link")
        self.gridLayout.addWidget(self.cancel_link, 3, 1, 1, 1)

        self.retranslateUi()

        self.cancel_link.clicked.connect(self.reject)
        self.add_link.clicked.connect(self.get_link)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Введите данные"))
        self.label_text_info_inout.setText(_translate("Dialog", "Введите количество входных/выходных данных в ноду"))
        self.label_text_inputs.setText(_translate("Dialog", "Входные"))
        self.label_text_outputs.setText(_translate("Dialog", "Выходные"))
        self.add_link.setText(_translate("Dialog", "Принять"))
        self.cancel_link.setText(_translate("Dialog", "Отменить"))

    def get_link(self):
        text_inputs = self.text_inputs.text()
        text_outputs = self.text_outputs.text()

        array_inputs, array_outputs = [], []
        for int_value in range(int(text_inputs)):
            array_inputs.append(int_value)

        for int_value in range(int(text_outputs)):
            array_outputs.append(int_value)

        self.returnVal = {'inputs': array_inputs, 'outputs': array_outputs}
        self.accept()

    def exec_(self):
        super(PopUpDialogThingWorxCountInOut, self).exec_()
        return self.returnVal


class PopUpDialogThingWorx(QtWidgets.QDialog):

    def __init__(self, server_name_exp_lbl="PP-2107252209MI.portal.ptc.io",
                 server_name="", thing_name="", service_name="", appkey_data="",
                 thing_name_lbl="Введите название вещи",
                 service_name_lbl="Введите название сервиса",
                 appkey_data_lbl="Введите ваш AppKey"):
        super(PopUpDialogThingWorx, self).__init__()

        self.server_name_exp = server_name_exp_lbl
        self.thing_name_lbl = thing_name_lbl
        self.service_name_lbl = service_name_lbl
        self.appkey_data_lbl = appkey_data_lbl

        self.returnVal = None
        self.icon = QtGui.QIcon()

        self.setObjectName("self")
        self.resize(400, 300)
        self.setMinimumSize(QtCore.QSize(400, 300))
        self.setMaximumSize(QtCore.QSize(400, 300))
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        self.icon.addPixmap(QtGui.QPixmap(DIR_ICONS + "ask-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(self.icon)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        # 0 0 1 2 - row column rowSpan columnSpan
        self.label_server_name = QtWidgets.QLabel(self)
        self.label_server_name.setObjectName("label_server_name")
        self.label_server_name.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_server_name, 0, 0, 1, 2)

        self.label_server_name_example = QtWidgets.QLabel(self)
        self.label_server_name_example.setObjectName("label_server_name_example")
        self.label_server_name_example.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_server_name_example, 1, 0, 1, 2)

        self.text_server_name = QtWidgets.QTextEdit(self)
        self.text_server_name.setObjectName("text_server_name")
        self.text_server_name.setAlignment(QtCore.Qt.AlignCenter)
        self.text_server_name.setText(server_name)
        self.gridLayout.addWidget(self.text_server_name, 2, 0, 1, 2)

        self.label_thing_name = QtWidgets.QLabel(self)
        self.label_thing_name.setObjectName("label_thing_name")
        self.label_thing_name.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_thing_name, 3, 0, 1, 2)

        self.text_thing_name = QtWidgets.QTextEdit(self)
        self.text_thing_name.setObjectName("text_thing_name")
        self.text_thing_name.setAlignment(QtCore.Qt.AlignCenter)
        self.text_thing_name.setText(thing_name)
        self.gridLayout.addWidget(self.text_thing_name, 4, 0, 1, 2)

        self.label_service_name = QtWidgets.QLabel(self)
        self.label_service_name.setObjectName("label_service_name")
        self.label_service_name.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_service_name, 5, 0, 1, 2)

        self.text_service_name = QtWidgets.QTextEdit(self)
        self.text_service_name.setObjectName("text_service_name")
        self.text_service_name.setAlignment(QtCore.Qt.AlignCenter)
        self.text_service_name.setText(service_name)
        self.gridLayout.addWidget(self.text_service_name, 6, 0, 1, 2)

        self.label_appkey_data = QtWidgets.QLabel(self)
        self.label_appkey_data.setObjectName("label_appkey_data")
        self.label_appkey_data.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label_appkey_data, 7, 0, 1, 2)

        self.text_appkey_data = QtWidgets.QTextEdit(self)
        self.text_appkey_data.setObjectName("text_appkey_data")
        self.text_appkey_data.setAlignment(QtCore.Qt.AlignCenter)
        self.text_appkey_data.setText(appkey_data)
        self.gridLayout.addWidget(self.text_appkey_data, 8, 0, 1, 2)

        self.add_link = QtWidgets.QPushButton(self)
        self.add_link.setObjectName("accept_link")
        self.gridLayout.addWidget(self.add_link, 9, 0, 1, 1)

        self.cancel_link = QtWidgets.QPushButton(self)
        self.cancel_link.setObjectName("cancel_link")
        self.gridLayout.addWidget(self.cancel_link, 9, 1, 1, 1)

        self.retranslateUi()

        self.cancel_link.clicked.connect(self.reject)
        self.add_link.clicked.connect(self.get_link)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Введите данные"))

        self.label_server_name.setText(_translate("Dialog", "Введите ваш адрес сервера"))
        self.label_server_name_example.setText(_translate("Dialog", "Пример: " + self.server_name_exp))

        self.label_thing_name.setText(_translate("Dialog", self.thing_name_lbl))
        self.label_service_name.setText(_translate("Dialog", self.service_name_lbl))
        self.label_appkey_data.setText(_translate("Dialog", self.appkey_data_lbl))

        self.add_link.setText(_translate("Dialog", "Принять"))
        self.cancel_link.setText(_translate("Dialog", "Отменить"))

    def get_link(self):
        server_name = self.text_server_name.toPlainText()
        thing_name = self.text_thing_name.toPlainText()
        service_name = self.text_service_name.toPlainText()
        appkey_data = self.text_appkey_data.toPlainText()
        self.returnVal = {'server_name': server_name, 'thing_name': thing_name,
                          'service_name': service_name, 'appkey_data': appkey_data}
        self.accept()

    def exec_(self):
        super(PopUpDialogThingWorx, self).exec_()
        return self.returnVal