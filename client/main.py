import sys
from PyQt5.QtWidgets import (
    QPushButton, QApplication, QDesktopWidget, QMainWindow
)
from people import people


class main(QMainWindow):
    def __init__(self, parent=None):
        super(main, self).__init__(parent)
        self.initUI()
        self.center()
        self.show()

    def initUI(self):
        self.center()
        button = QPushButton('open', self)
        button.clicked.connect(self.clickopen)

    def clickopen(self):
        self.dialog = people(self)
        self.dialog.exec()

    def center(self):
        self.setFixedSize(800, 600)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    x = main()
    sys.exit(app.exec_())
