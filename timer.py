#!/usr/bin/env python2
import sys
from PyQt4 import QtGui, QtCore
import datetime
import json
import os

from ui.timerUI import Ui_Timer

# Keys must be in sorted order: long(min,msg), short(min,msg), tip
DEFAULTS = {
    "long_min": 50,
    "long_msg": "Sit Down!",
    "short_min": 10,
    "short_msg": "Stand Up!",
    "tool_tip": "Stand/Sit Timer",
}

ICONS = (
    "res/sit2.png",
    "res/sit1.png",
    "res/stand1.png",
    "res/stand2.png",
    "res/paused.png",
)

POLL_SEC = 2.5


class SetupUI(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_Timer()
        self.ui.setupUi(self)
        self.parent = parent

        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.setTimerValues)

    def setValues(self, config):
        self.ui.FirstTime.setValue(config['long_min'])
        self.ui.FirstText.setText(config['long_msg'])
        self.ui.SecondTime.setValue(config['short_min'])
        self.ui.SecondText.setText(config['short_msg'])

    def setTimerValues(self):
        data = {
            'long_min': self.ui.FirstTime.value(),
            'long_msg': str(self.ui.FirstText.text()),
            'short_min': self.ui.SecondTime.value(),
            'short_msg': str(self.ui.SecondText.text())
        }
        self.parent.setValues(**data)
        self.hide()


class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        self.parent = parent
        menu = QtGui.QMenu(parent)

        startAction = menu.addAction("Start Long")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.startTimerLong)
        self.setContextMenu(menu)

        startAction = menu.addAction("Start Short")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.startTimerShort)
        self.setContextMenu(menu)

        menu.addSeparator()

        startAction = menu.addAction("Pause")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.stopTimer)
        self.setContextMenu(menu)

        menu.addSeparator()

        startAction = menu.addAction("Setup")
        self.connect(startAction, QtCore.SIGNAL("triggered()"), self.setup)
        self.setContextMenu(menu)

        exitAction = menu.addAction("Exit")
        self.connect(exitAction, QtCore.SIGNAL("triggered()"), self.exit)
        self.setContextMenu(menu)

        self.setupDialog = None
        self.timeout = 0
        self.msg = "Default timeout message"
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.endTimer)
        self.timerID = None

        self.allIcons = [QtGui.QIcon(name) for name in ICONS]
        self.loadConfig()

    def getText(self, key):
        return self.config.get(key, DEFAULTS[key])

    def getTime(self, key):
        return float(self.get(key))

    def loadConfig(self):
        configFile = os.path.expanduser(os.path.join("~", ".config", "easytimer.conf"))
        if not os.path.exists(configFile):
            try:
                os.makedirs(os.path.dirname(configFile))
            except:
                self.useConfig = False
                return
        try:
            with open(configFile) as fd:
                self.config = json.load(fd, encoding='utf-8')
            # Extend the config
            for key, value in DEFAULTS.items():
                if not key in self.config:
                    self.config[key] = value
        except:
            self.config = dict(DEFAULTS)
            
        self.useConfig = True
        self.configFile = configFile
        self.setValues(**self.config)

    def exit(self):
        sys.exit(0)

    def error(self, msg):
        QtGui.QMessageBox.warning(None, "Error", (msg),
                                  QtGui.QMessageBox.Ok)
        
    def startTimerLong(self):
        print("Starting LONG timer...")
        self.startTimer(short=False)

    def startTimerShort(self):
        print("Starting SHORT timer...")
        self.startTimer(short=True)

    def startTimer(self, short):
        ind = 2 if short else 0
        self.short = short
        self.timeout = self.values[ind] * 60
        self.msg = self.values[ind + 1]
        self.alt = self.values[3 - ind]

        assert self.timeout >= 60.0, \
            ("A timeout of less than 1 minute (%s sec) is invalid." % self.timeout)

        self.icons = self.allIcons[ind:ind+2]
        self.setIcon(self.icons[0])
        self.toggles = 8

        msg = "You should: %s\nFor: %s minutes" % (
            self.msg, self.timeout / 60.0)
        QtGui.QMessageBox.information(
            None, "Stand/Sit Timer", msg, QtGui.QMessageBox.Ok)

        if not self.timer.isActive():
            self.timerID = self.timer.start(POLL_SEC * 1000)

    def stopTimer(self):
        if self.timer:
            self.timer.stop()
        self.setIcon(self.allIcons[-1])
        print("Stopped...")

    def endTimer(self):
        try:
            print("Time left: %s (to %s) ..." % (self.timeout, self.msg))
            self.timeout -= POLL_SEC
            if self.toggles:
                ind = self.toggles % 2
                self.toggles -= 1
                icon = self.icons[ind]
                self.setIcon(icon)
                return
            if self.timeout > 0:
                return

            self.startTimer(not self.short)

        except Exception as exc:
            QtGui.QMessageBox.information(
                None, "Failed", str(exc), QtGui.QMessageBox.Ok)
            raise

    def setup(self):
        if self.setupDialog is None:
            self.setupDialog = SetupUI( self)

        self.setupDialog.setValues(self.config)
        self.setupDialog.show()
        self.setupDialog.raise_()

    def setValues(self, **config):
        self.config = config
        if self.useConfig:
            with open(self.configFile, 'w') as fd:
                json.dump(self.config, fd, indent=4)
        self.values = [val for key, val in sorted(config.items())]
        print("Values: " + ", ".join(("[%s](%s)" % (e.__class__.__name__, e) for e in self.values)))


def main():
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtGui.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon(ICONS[-1]), w)

    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()



    
