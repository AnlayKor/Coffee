import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableWidgetItem

from main_ui_file import Ui_MainWindow
from addEditCoffeeForm import Ui_Form


class DBSample(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect("coffee.sqlite")
        self.pushButton.clicked.connect(self.open)
        # По умолчанию будем выводить все данные из таблицы films
        self.select_data()

    def select_data(self):
        # Получим результат запроса,
        # который ввели в текстовое поле
        query = "SELECT * FROM coffee"
        res = self.connection.cursor().execute(query).fetchall()
        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def closeEvent(self, event):
        # При закрытии формы закроем и наше соединение
        # с базой данных
        self.connection.close()

    def open(self):
        self.new_form = AddWidget()
        self.new_form.show()


class AddWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.pushButton.clicked.connect(self.update_result)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.pushButton_2.clicked.connect(self.save_results)
        self.pushButton_3.clicked.connect(self.insert_results)
        self.modified = {}
        self.titles = None

    def update_result(self):
        cur = self.con.cursor()
        # Получили результат запроса, который ввели в текстовое поле
        result = cur.execute("SELECT * FROM coffee WHERE id=?",
                             (item_id := self.spinBox.text(),)).fetchall()
        # Заполнили размеры таблицы
        self.tableWidget.setRowCount(len(result))
        # Если запись не нашлась, то не будем ничего делать
        if not result:
            self.label_2.setText('Ничего не нашлось')
            return
        else:
            self.label_2.setText(f"Нашлась запись с id = {item_id}")
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        # Если значение в ячейке было изменено,
        # то в словарь записывается пара: название поля, новое значение
        self.modified[self.titles[item.column()]] = item.text()

    def save_results(self):
        if self.modified:
            cur = self.con.cursor()
            que = "UPDATE coffee SET "
            que += ", ".join([f"{key} = '{self.modified.get(key)}'"
                              for key in self.modified.keys()])
            que += f" WHERE id = ?"
            cur.execute(que, (self.spinBox.text(),))
            self.con.commit()
            self.modified.clear()

    def insert_results(self):
        for i in range(1, 7):
            self.modified[self.titles[i]] = self.tableWidget.item(0, i).text()
        cur = self.con.cursor()
        cur.execute(f'''INSERT INTO coffee({','.join(list(self.modified))}) VALUES({','.join(list(self.modified.values()))})''')
        self.con.commit()
        self.modified.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec())
