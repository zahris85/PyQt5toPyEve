import sys, requests, json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QAbstractItemView, QLineEdit, QDialog, QPushButton,
    QDesktopWidget, QMessageBox
)

max_results = 10
http = "http://127.0.0.1:5000/people"

class main(QWidget):
    def __init__(self, parent=None):
        super(main, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.tableView()
        self.paginate()
        self.searchBoxes()
        self.filterName(1)
        self.signals()
        self.setLayout(self.boxLayout())
        self.setFixedSize(254, 380)
        self.center()
        self.show()

    def boxLayout(self):
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.firstName)
        hbox.addWidget(self.lastName)
        hbox.addWidget(QLabel('Page :'))
        hbox.addWidget(self.pageNum)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.tview)
        return vbox

    def signals(self):
        self.pageNum.activated.connect(self.tablePage)
        self.firstName.textChanged.connect(self.filterName)
        self.lastName.textChanged.connect(self.filterName)
        self.tview.cellDoubleClicked.connect(self.editRow)

    def editRow(self, row):
        id = (self.tview.verticalHeaderItem(row).text())
        data = requests.get(http + '/' + id).json()
        self.editRowDialog(data)

    def tablePage(self):
        z = self.pageNum.currentData()
        self.filterName(z)
        self.pageNum.setCurrentIndex(z - 1)

    def tableView(self):
        self.tview = QTableWidget()
        self.tview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tview.setColumnCount(2)
        self.tview.setHorizontalHeaderItem(0, QTableWidgetItem("Firstname"))
        self.tview.setHorizontalHeaderItem(1, QTableWidgetItem("Lastname"))

    def genTable(self, JsonData):
        self.pageCount(JsonData)
        self.tview.setRowCount(len(JsonData['_items']))
        self.renderTable(JsonData)

    def paginate(self):
        self.pageNum = QComboBox()

    def searchBoxes(self):
        self.firstName = QLineEdit()
        self.lastName = QLineEdit()
        self.firstName.setPlaceholderText("FIRSTNAME")
        self.lastName.setPlaceholderText("LASTNAME")

    def filterName(self, pageNum):
        url = "%s?max_results=%s" % (http, max_results)

        fil = 'like(\\"{v}%\\")'
        fX = fil.format(v=self.firstName.text())
        fY = fil.format(v=self.lastName.text())

        par = {'where': '{"firstname":"%s", "lastname":"%s"}' % (fX, fY),
               'page': pageNum}

        self.genTable(requests.get(url, params=par).json())

    def pageCount(self, JsonData):
        total = JsonData['_meta']['total']
        if total % max_results > 0:
            pages = (total / max_results) + 2
        else:
            pages = total / max_results + 1

        self.pageNum.clear()
        for i in range(1, int(pages)):
            self.pageNum.addItem("%s" % i, i)

    def renderTable(self, JsonData):
        row = 0
        for list in JsonData['_items']:
            self.tview.setVerticalHeaderItem(row, QTableWidgetItem(str(list["id"])))
            self.tview.setItem(row, 0, QTableWidgetItem(list['firstname']))
            self.tview.setItem(row, 1, QTableWidgetItem(list['lastname']))
            row += 1

    def editRowDialog(self, JsonData):
        url = http + '/%s' % JsonData['id']
        headers = {"Content-Type": "application/json", "If-Match": JsonData['_etag']}

        self.editDialog = QDialog()
        self.editDialog.setWindowTitle('Edit ID No. %s' % JsonData['id'])

        editSavButton = QPushButton('SAVE', self.editDialog)
        editDelButton = QPushButton('DELETE', self.editDialog)

        editSavButton.clicked.connect(lambda: self.save(
            JsonData['id'], JsonData['_etag'], url, headers, editFirstname.text(), editLastname.text()
        ))
        editDelButton.clicked.connect(lambda: self.delete(url, headers))

        buttonGroup = QHBoxLayout()
        buttonGroup.addWidget(editDelButton)
        buttonGroup.addWidget(editSavButton)

        editFirstname = QLineEdit(JsonData['firstname'])
        editLastname = QLineEdit(JsonData['lastname'])

        firstname = QHBoxLayout()
        firstname.addWidget(QLabel('Firstname :'))
        firstname.addWidget(editFirstname)

        lastname = QHBoxLayout()
        lastname.addWidget(QLabel('Lastname :'))
        lastname.addWidget(editLastname)

        inputGroup = QVBoxLayout()
        inputGroup.addLayout(firstname)
        inputGroup.addLayout(lastname)

        editGroup = QVBoxLayout()
        editGroup.addLayout(inputGroup)
        editGroup.addLayout(buttonGroup)

        self.editDialog.setLayout(editGroup)
        self.editDialog.exec()

    def closeEditDialog(self):
        self.editDialog.close()
        self.tablePage()

    def delete(self, url, headers):
        e = requests.delete(url, headers=headers)
        self.closeEditDialog()

    def save(self, id, etag, url, headers, firstname, lastname):
        currentEtag = requests.get(http + '/%s' % id).json()['_etag']
        if currentEtag == etag:
            i = json.dumps({'firstname': firstname, 'lastname': lastname})
            e = requests.patch(url, data=i, headers=headers)
            self.closeEditDialog()
        else:
            err = QMessageBox()
            err.setIcon(QMessageBox.Information)
            err.setText(
                'Cannot running the update '
                'someone has already changed the data \n\n'
                'click OK to update the Table')
            err.setWindowTitle('Data Missmatch')
            err.buttonClicked.connect(self.closeEditDialog)
            err.exec()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    x = main()
    sys.exit(app.exec_())
