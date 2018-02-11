__all__ = ['WIDGET_DATE_RANGE','BASE_DATE_RANGE']

from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis import gui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 67)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_start = QtWidgets.QLabel(Form)
        self.label_start.setObjectName("label_start")
        self.gridLayout.addWidget(self.label_start, 0, 0, 1, 1)
        self.label_end = QtWidgets.QLabel(Form)
        self.label_end.setObjectName("label_end")
        self.gridLayout.addWidget(self.label_end, 0, 1, 1, 1)
        self.date_start = gui.QgsDateTimeEdit(Form)
        self.date_start.setMinimumDateTime(QtCore.QDateTime(QtCore.QDate(1971, 12, 31), QtCore.QTime(13, 0, 0)))
        self.date_start.setMinimumDate(QtCore.QDate(1971, 12, 31))
        self.date_start.setCurrentSection(QtWidgets.QDateTimeEdit.YearSection)
        self.date_start.setTimeSpec(QtCore.Qt.UTC)
        self.date_start.setObjectName("date_start")
        self.gridLayout.addWidget(self.date_start, 1, 0, 1, 1)
        self.date_end = gui.QgsDateTimeEdit(Form)
        self.date_end.setMinimumDateTime(QtCore.QDateTime(QtCore.QDate(1972, 1, 1), QtCore.QTime(0, 0, 0)))
        self.date_end.setMinimumDate(QtCore.QDate(1972, 1, 1))
        self.date_end.setCurrentSection(QtWidgets.QDateTimeEdit.YearSection)
        self.date_end.setObjectName("date_end")
        self.gridLayout.addWidget(self.date_end, 1, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_start.setText(_translate("Form", "Start Date"))
        self.label_end.setText(_translate("Form", "End Date"))
        self.date_start.setDisplayFormat(_translate("Form", "yyyy-MM-dd"))
        self.date_end.setDisplayFormat(_translate("Form", "yyyy-MM-dd"))


WIDGET_DATE_RANGE, BASE_DATE_RANGE = (Ui_Form, QtWidgets.QWidget)