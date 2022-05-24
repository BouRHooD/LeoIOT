import os
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtWidgets import *
from windows.main_iot_window import MainIOTWindow

wnd = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wnd = MainIOTWindow()
    wnd.show()
    sys.exit(app.exec_())
