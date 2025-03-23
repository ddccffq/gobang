from PyQt6 import QtWidgets
from Ui_MainWindow import Ui_MainWindow

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()