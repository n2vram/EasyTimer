# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timer.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Timer(object):
    def setupUi(self, Timer):
        Timer.setObjectName(_fromUtf8("Timer"))
        Timer.resize(474, 178)
        self.buttonBox = QtGui.QDialogButtonBox(Timer)
        self.buttonBox.setGeometry(QtCore.QRect(140, 140, 176, 27))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.layoutWidget = QtGui.QWidget(Timer)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 431, 124))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.FirstTime = QtGui.QSpinBox(self.layoutWidget)
        self.FirstTime.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.FirstTime.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.FirstTime.setMinimum(1)
        self.FirstTime.setMaximum(1500)
        self.FirstTime.setSingleStep(5)
        self.FirstTime.setObjectName(_fromUtf8("FirstTime"))
        self.gridLayout.addWidget(self.FirstTime, 0, 1, 1, 1)
        self.FirstTextLabel = QtGui.QLabel(self.layoutWidget)
        self.FirstTextLabel.setObjectName(_fromUtf8("FirstTextLabel"))
        self.gridLayout.addWidget(self.FirstTextLabel, 1, 0, 1, 1)
        self.SecondTimeLabel = QtGui.QLabel(self.layoutWidget)
        self.SecondTimeLabel.setObjectName(_fromUtf8("SecondTimeLabel"))
        self.gridLayout.addWidget(self.SecondTimeLabel, 3, 0, 1, 1)
        self.FirstTimeLabel = QtGui.QLabel(self.layoutWidget)
        self.FirstTimeLabel.setObjectName(_fromUtf8("FirstTimeLabel"))
        self.gridLayout.addWidget(self.FirstTimeLabel, 0, 0, 1, 1)
        self.SecondTime = QtGui.QSpinBox(self.layoutWidget)
        self.SecondTime.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.SecondTime.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.SecondTime.setMinimum(1)
        self.SecondTime.setMaximum(1500)
        self.SecondTime.setSingleStep(5)
        self.SecondTime.setObjectName(_fromUtf8("SecondTime"))
        self.gridLayout.addWidget(self.SecondTime, 2, 1, 1, 1)
        self.SecondText = QtGui.QLineEdit(self.layoutWidget)
        self.SecondText.setText(_fromUtf8(""))
        self.SecondText.setObjectName(_fromUtf8("SecondText"))
        self.gridLayout.addWidget(self.SecondText, 3, 1, 1, 1)
        self.SecondTextLabel = QtGui.QLabel(self.layoutWidget)
        self.SecondTextLabel.setObjectName(_fromUtf8("SecondTextLabel"))
        self.gridLayout.addWidget(self.SecondTextLabel, 2, 0, 1, 1)
        self.FirstText = QtGui.QLineEdit(self.layoutWidget)
        self.FirstText.setText(_fromUtf8(""))
        self.FirstText.setObjectName(_fromUtf8("FirstText"))
        self.gridLayout.addWidget(self.FirstText, 1, 1, 1, 1)
        self.FirstTextLabel.setBuddy(self.FirstText)
        self.SecondTimeLabel.setBuddy(self.FirstText)
        self.FirstTimeLabel.setBuddy(self.FirstTime)
        self.SecondTextLabel.setBuddy(self.FirstTime)

        self.retranslateUi(Timer)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Timer.hide)
        QtCore.QMetaObject.connectSlotsByName(Timer)

    def retranslateUi(self, Timer):
        Timer.setWindowTitle(_translate("Timer", "EasyTimer Setup", None))
        self.FirstTextLabel.setText(_translate("Timer", "Long Interval Name", None))
        self.SecondTimeLabel.setText(_translate("Timer", "Short Interval Name", None))
        self.FirstTimeLabel.setText(_translate("Timer", "Long Interval (minutes)", None))
        self.SecondTextLabel.setText(_translate("Timer", "Short Interval (minutes)", None))

