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

    "text_minimum": "Timeouts must be at least 1 minute.",
    "text_should": "You should {act}\nFor: {mins} minutes",
    "tip_inactive": "Not running",
    "tip_active": "You should {act}\n({mins:.1f} minutes remaining)",
    "title_error": "Error",
    "title_normal": "Sit/Stand Timer",
    "text_sit": "Start Sitting",
    "text_stand": "Start Standing",
    "text_pause": "Pause Timer",
    "text_setup": "Configure...",
    "text_exit": "Exit"
}

ICONS = (
    "res/sit1.png",
    "res/sit2.png",
    "res/stand1.png",
    "res/stand2.png",
    "res/paused.png",
)

POLL_FAST = 0.250
POLL_SLOW = 6.000
ICON_TOGGLES = int(2 * POLL_SLOW / POLL_FAST + 0.5)


class SetupUI(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_Timer()
        self.ui.setupUi(self)
        self.parent = parent
        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.setTimerValues)

    def setValues(self, config):
        self.ui.FirstTime.setValue(config["long_min"])
        self.ui.FirstText.setText(config["long_msg"])
        self.ui.SecondTime.setValue(config["short_min"])
        self.ui.SecondText.setText(config["short_msg"])

    def setTimerValues(self):
        data = {
            "long_min": self.ui.FirstTime.value(),
            "long_msg": str(self.ui.FirstText.text()),
            "short_min": self.ui.SecondTime.value(),
            "short_msg": str(self.ui.SecondText.text())
        }
        self.parent.setValues(**data)
        self.hide()


class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        self.parent = parent
        self.loadConfig()

        def addMenu(key, method):
            self.connect(menu.addAction(self.getText(key)),
                         QtCore.SIGNAL("triggered()"), method)

        menu = QtGui.QMenu(parent)
        addMenu("text_sit", self.startSitting)
        addMenu("text_stand", self.startStanding)
        menu.addSeparator()
        addMenu("text_pause", self.stopTimer)
        menu.addSeparator()
        addMenu("text_setup", self.setup)
        addMenu("text_exit", self.exit)
        self.setContextMenu(menu)

        self.setupDialog = None
        self.timeout = 0
        self.msg = self.getText("tip_inactive")
        self.setToolTip(self.msg)
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.endTimer)
        self.timerID = None

        self.allIcons = [QtGui.QIcon(name) for name in ICONS]

    def exit(self):
        sys.exit(0)

    def error(self, msg):
        QtGui.QMessageBox.warning(None, self.getText("title_error"),
                                  msg, QtGui.QMessageBox.Ok)

    def startSitting(self):
        print("Start sitting timer...")
        self.startTimer(short=False)

    def startStanding(self):
        print("Start standing timer...")
        self.startTimer(short=True)

    def startTimer(self, short):
        ind = 2 if short else 0
        self.short = short
        self.timeout = self.values[ind] * 60
        self.setRemaining(self.timeout)
        self.msg = self.values[ind + 1]
        self.alt = self.values[3 - ind]

        msg = self.getText("text_should")
        msg = msg.format(act=self.msg, mins=self.timeout / 60.0)
        title = self.getText("title_normal")
        QtGui.QMessageBox.information(
            None, title, msg, QtGui.QMessageBox.Ok)

        # Flash the icon 
        self.icons = self.allIcons[ind:ind+2]
        self.setIcon(self.icons[0])
        self.toggles = ICON_TOGGLES
        self.setPolling(POLL_FAST)

    def setRemaining(self, time):
        key = "tip_inactive" if time <= 0 else "tip_active"
        msg = self.getText(key).format(mins=time / 60.0, act=self.msg)
        self.setToolTip(msg)        

    def setPolling(self, sec):
        self.timer.start(sec * 1000)
        self.polling = sec

    def stopTimer(self):
        if self.timer:
            self.timer.stop()
        self.setIcon(self.allIcons[-1])
        self.timeout = 0
        self.setRemaining(self.timeout)
        print("Stopped...")

    def endTimer(self):
        try:
            self.timeout -= self.polling
            self.setRemaining(self.timeout)

            if self.toggles:
                ind = self.toggles % 2
                self.toggles -= 1
                icon = self.icons[ind]
                self.setIcon(icon)
                if not self.toggles:
                    self.setPolling(POLL_SLOW)
                return
            if self.timeout > 0:
                return

            self.startTimer(not self.short)

        except Exception as exc:
            QtGui.QMessageBox.information(None, self.getText("title_error"),
                                          str(exc), QtGui.QMessageBox.Ok)

    def setup(self):
        if self.setupDialog is None:
            self.setupDialog = SetupUI( self)
        self.setupDialog.setValues(self.config)
        self.setupDialog.show()
        self.setupDialog.raise_()

    def getText(self, key):
        return self.config.get(key, DEFAULTS[key])

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
                self.config = json.load(fd, encoding="utf-8")
            # Extend the config
            for key, value in DEFAULTS.items():
                if not key in self.config:
                    self.config[key] = value
        except:
            self.config = dict(DEFAULTS)
            
        self.useConfig = True
        self.configFile = configFile
        self.setValues(**self.config)

    def setValues(self, **config):
        self.config.update(config)
        if self.useConfig:
            saved = dict(self.config)
            for key, value in DEFAULTS.items():
                if value == saved.get(key):
                    saved.pop(key)
            with open(self.configFile, 'w') as fd:
                json.dump(saved, fd, indent=4, sort_keys=True)
        self.values = [val for key, val in sorted(config.items())]
        print("Values: " + ", ".join(("[%s](%s)" % (e.__class__.__name__, e) for e in self.values)))


def main():
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtGui.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon(ICONS[-1]), w)

    trayIcon.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()



    
