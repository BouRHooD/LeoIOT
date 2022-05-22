import os
import sys
from PyQt5.QtWidgets import *
from windows.main_iot_window import MainIOTWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wnd = MainIOTWindow()
    wnd.show()
    sys.exit(app.exec_())
