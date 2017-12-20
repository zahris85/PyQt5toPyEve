import requests
import json
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QMessageBox,
    QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QAbstractItemView, QLineEdit, QDialog, QPushButton,
)

max_results = 10
http = "http://127.0.0.1:5000/people"


class people(QDialog):
    def __init__(self, parent=None):
        super(people, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.tableView()
        self.controlBoxes()
        self.filterName(1)
        self.signals()
        self.setLayout(self.boxLayout())
        self.setFixedSize(254, 380)

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

    def tableView(self):
        self.tview = QTableWidget()
        self.tview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tview.setColumnCount(2)
        self.tview.setHorizontalHeaderItem(0, QTableWidgetItem("Firstname"))
        self.tview.setHorizontalHeaderItem(1, QTableWidgetItem("Lastname"))

    def controlBoxes(self):
        self.pageNum = QComboBox()
        self.firstName = QLineEdit()
        self.firstName.setPlaceholderText("FIRSTNAME")
        self.lastName = QLineEdit()
        self.lastName.setPlaceholderText("LASTNAME")

    def filterName(self, pageNum):
        url = "%s?max_results=%s" % (http, max_results)

        fil = 'like(\\"{v}%\\")'
        fX = fil.format(v=self.firstName.text())
        fY = fil.format(v=self.lastName.text())

        par = {'where': '{"firstname":"%s", "lastname":"%s"}' % (fX, fY),
               'page': pageNum}

        self.genTable(requests.get(url, params=par).json())

    def signals(self):
        self.pageNum.activated.connect(self.tablePage)
        self.firstName.textChanged.connect(self.filterName)
        self.lastName.textChanged.connect(self.filterName)
        self.tview.cellDoubleClicked.connect(self.editRow)

    def tablePage(self):
        pageNum = self.pageNum.currentData()
        self.filterName(pageNum)
        self.pageNum.setCurrentIndex(pageNum - 1)

    def genTable(self, JsonData):
        self.pageCount(JsonData)
        rows = len(JsonData['_items'])
        if rows == 0:
            self.filterName(JsonData['_meta']['page'] - 1)
        else:
            self.tview.setRowCount(rows)
            self.renderTable(JsonData)

    def totalPages(self, JsonData):
        total = JsonData['_meta']['total']
        if total % max_results > 0:
            pages = (total / max_results) + 2
        else:
            pages = total / max_results + 1
        return pages

    def pageCount(self, JsonData):
        self.pageNum.clear()
        for i in range(1, int(self.totalPages(JsonData))):
            self.pageNum.addItem("%s" % i, i)

    def renderTable(self, JsonData):
        row = 0
        for list in JsonData['_items']:
            self.tview.setVerticalHeaderItem(
                row, QTableWidgetItem(str(list["id"])))
            self.tview.setItem(row, 0, QTableWidgetItem(list['firstname']))
            self.tview.setItem(row, 1, QTableWidgetItem(list['lastname']))
            row += 1

    def editRow(self, row):
        id = (self.tview.verticalHeaderItem(row).text())
        data = requests.get(http + '/' + id).json()
        self.editDialogUI(data)

    def editDialogUI(self, JsonData):
        self.editDialog = QDialog()
        self.editDialog.setWindowTitle('Edit ID No. %s' % JsonData['id'])
        self.editDialog.setLayout(self.inputBox(JsonData))
        self.editConn(JsonData)
        self.editDialog.exec()

    def editConn(self, JsonData):
        url = http + '/%s' % JsonData['id']
        headers = {
            "Content-Type": "application/json",
            "If-Match": JsonData['_etag']
        }
        self.editSavButton.clicked.connect(lambda: self.edit(
            JsonData['id'], JsonData['_etag'], url, headers,
            self.editFirstname.text(), self.editLastname.text()
        ))
        self.editDelButton.clicked.connect(lambda: self.delete(url, headers))

    def inputButton(self):
        self.editSavButton = QPushButton('SAVE')
        self.editDelButton = QPushButton('DELETE')
        buttonGroup = QHBoxLayout()
        buttonGroup.addWidget(self.editDelButton)
        buttonGroup.addWidget(self.editSavButton)
        return buttonGroup

    def inputBox(self, JsonData):
        self.editFirstname = QLineEdit(JsonData['firstname'])
        self.editLastname = QLineEdit(JsonData['lastname'])

        firstname = QHBoxLayout()
        firstname.addWidget(QLabel('Firstname :'))
        firstname.addWidget(self.editFirstname)

        lastname = QHBoxLayout()
        lastname.addWidget(QLabel('Lastname :'))
        lastname.addWidget(self.editLastname)

        editGroup = QVBoxLayout()
        editGroup.addLayout(firstname)
        editGroup.addLayout(lastname)
        editGroup.addLayout(self.inputButton())
        return editGroup

    def closeEditDialog(self):
        self.editDialog.close()
        self.tablePage()

    def delete(self, url, headers):
        requests.delete(url, headers=headers)
        self.closeEditDialog()

    def edit(self, id, etag, url, headers, firstname, lastname):
        currentEtag = requests.get(http + '/%s' % id).json()['_etag']
        if currentEtag == etag:
            i = json.dumps({'firstname': firstname, 'lastname': lastname})
            requests.patch(url, data=i, headers=headers)
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
