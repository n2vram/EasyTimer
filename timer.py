#!/usr/bin/env python2
import datetime
import json
import logging
import os
from PyQt4 import QtGui, QtCore
from subprocess import call
import sys
from threading import Thread, Lock

from ui.timerUI import Ui_Timer

logger = logging.getLogger('__name__')
logging.basicConfig(level=logging.DEBUG)

DEFAULTS = {
    "sitting_min": 50,
    "sitting_msg": "Sit Down!",
    "sitting_sound": '',
    "standing_min": 10,
    "standing_msg": "Stand Up!",
    "standing_sound": '',

    "text_minimum": "Timeouts must be at least 1 minute.",
    "text_should": "You should {act}\nFor: {mins} minutes",
    "tip_inactive": "Not running",
    "tip_active": "You should {act}\n({mins:.1f} minutes remaining)",
    "title_error": "Error",
    "title_normal": "Sit/Stand Timer",
    "files_audio": "Audio Files (*.mp3 *.ogg *.flc *.flac *.wav)",
    "files_all": "All Files (*)",
    "sound_standing": "Standing Sound",
    "sound_sitting": "Sitting Sound",
    "text_sit": "Start Sitting",
    "text_stand": "Start Standing",
    "text_cancel": "Cancel Timer",
    "text_pause": "Pause Timer",
    "text_paused": "(PAUSE)",
    "error_resume": "Not paused.",
    "error_pause": "Already paused.",
    "text_resume": "Resume Timer",
    "text_setup": "Configure...",
    "text_exit": "Exit",

    "play_cmd": ["xdg-open"]
}

TIME_KEYS = ("sitting_min", "sitting_msg", "standing_min", "standing_msg")

ICONS = (
    "res/sit1.png",
    "res/sit2.png",
    "res/stand1.png",
    "res/stand2.png",
    "res/paused.png",
    "res/clock.png",
)

POLL_FAST = 0.250
POLL_SLOW = 6.000
ICON_TOGGLES = int(2 * POLL_SLOW / POLL_FAST + 0.5)


class SetupUI(QtGui.QDialog):
    def __init__(self, parent, sounds):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_Timer()
        self.ui.setupUi(self)
        self.parent = parent
        self.sounds = sounds
        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.setTimerValues)
        self.connect(self.ui.StandingFileBtn, QtCore.SIGNAL("clicked()"), self.standingFile)
        self.connect(self.ui.StandingPlayBtn, QtCore.SIGNAL("clicked()"), self.playStanding)
        self.connect(self.ui.SittingFileBtn, QtCore.SIGNAL("clicked()"), self.sittingFile)
        self.connect(self.ui.SittingPlayBtn, QtCore.SIGNAL("clicked()"), self.playSitting)

    def soundFile(self, key, ui):
        current = str(ui.text())
        caption = self.config.get(key, DEFAULTS[key])
        filters = ";;".join((self.config.get('files_audio', DEFAULTS['files_audio']),
                             self.config.get('files_all', DEFAULTS['files_all'])))
        value = QtGui.QFileDialog.getOpenFileName(parent=self, caption=caption, filter=filters,
                                                  directory=os.path.dirname(current))
        if value:
            ui.setText(value)
        
    def standingFile(self):
        self.soundFile('sound_standing', self.ui.StandingFile)

    def sittingFile(self):
        self.soundFile('sound_sitting', self.ui.SittingFile)

    def playSitting(self):
        fname = str(self.ui.SittingFile.text())
        self.sounds.playSound(fname)

    def playStanding(self):
        fname = str(self.ui.StandingFile.text())
        self.sounds.playSound(fname)

    def setValues(self, config):
        self.config = config
        self.ui.FirstTime.setValue(config["sitting_min"])
        self.ui.FirstText.setText(config["sitting_msg"])
        self.ui.SittingFile.setText(config["sitting_sound"])
        self.ui.SecondTime.setValue(config["standing_min"])
        self.ui.SecondText.setText(config["standing_msg"])
        self.ui.StandingFile.setText(config["standing_sound"])

    def setTimerValues(self):
        self.parent.setValues(
            sitting_min=self.ui.FirstTime.value(),
            sitting_msg=str(self.ui.FirstText.text()),
            sitting_sound=str(self.ui.SittingFile.text()),
            standing_min=self.ui.SecondTime.value(),
            standing_msg=str(self.ui.SecondText.text()),
            standing_sound=str(self.ui.StandingFile.text())
        )
        self.hide()


class Sounds(object):
    """Provides a multi-platform way to play sounds through the native OS."""
    def __init__(self, cmd):
        self.cmd = tuple(cmd)
        self.lock = Lock()

    def playSound(self, fname):
        def playThread():
            cmd = self.cmd + (fname,)
            with self.lock:
                try:
                    logger.info("Running: '%s' ...", fname)
                    with open(os.devnull) as rd:
                        with open(os.devnull, 'wb') as wr:
                            call(cmd, stdin=rd, stdout=wr, stderr=wr)
                    logger.info("Played: %s", fname)
                except:
                    logger.exception("Error playing: %s", fname)
                    
        thread = Thread(target=playThread)
        thread.start()


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
        addMenu("text_pause", self.pauseTimer)
        addMenu("text_resume", self.resumeTimer)
        menu.addSeparator()
        addMenu("text_cancel", self.stopTimer)
        menu.addSeparator()
        addMenu("text_setup", self.setup)
        addMenu("text_exit", self.exit)
        self.setContextMenu(menu)

        self.setupDialog = None
        self.timeout = 0
        self.paused = 0
        self.msg = self.getText("tip_inactive")
        self.setToolTip(self.msg)
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.endTimer)
        self.timerID = None
        self.sounds = Sounds(self.config.get('play_cmd'))

        self.allIcons = [QtGui.QIcon(name) for name in ICONS]

    def exit(self):
        sys.exit(0)

    def error(self, msg):
        QtGui.QMessageBox.warning(None, self.getText("title_error"),
                                  msg, QtGui.QMessageBox.Ok)

    def startSitting(self):
        self.startTimer(stand=False)

    def startStanding(self):
        self.startTimer(stand=True)

    def startTimer(self, stand):
        sound = self.config.get('standing_sound' if stand else 'sitting_sound')
        if sound:
            self.sounds.playSound(sound)

        ind = 2 if stand else 0
        self.paused = 0
        self.stand = stand
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
        if self.paused:
            msg += '\n' + self.getText('text_paused')
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

    def pauseTimer(self):
        if self.paused:
            self.popUp('title_error', 'error_pause', 3)
            return
        self.paused = 1
        self.setRemaining(self.timeout)
        self.popUp('title_normal', 'text_pause')

    def resumeTimer(self):
        if not self.paused:
            self.popUp('title_error', 'error_resume', 3)
            return
        self.paused = 0
        self.setRemaining(self.timeout)
        self.toggles = 1
        self.endTimer()

    def endTimer(self):
        try:
            if self.paused:
                self.paused += 1
                icon = self.icons[1] if (self.paused & 1) else self.allIcons[-2]
                self.setIcon(icon)
                return

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

            self.startTimer(not self.stand)

        except Exception as exc:
            self.popUp('title_error', str(exc), 15)

    def setup(self):
        if self.setupDialog is None:
            self.setupDialog = SetupUI(self, self.sounds)
        self.setupDialog.setValues(self.config)
        self.setupDialog.show()
        self.setupDialog.raise_()

    def getText(self, key, default=None):
        return self.config.get(key, DEFAULTS.get(key, default))

    def loadConfig(self):
        configFile = os.path.expanduser(
            os.path.join("~", ".config", "easytimer.conf"))
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
        self.values = [config[key] for key in TIME_KEYS]

    def popUp(self, title, message, timeout=None, modal=False):
        mbox = QtGui.QMessageBox()
        mbox.setWindowTitle(self.getText(title))
        mbox.setIcon(QtGui.QMessageBox.Information)
        if message in DEFAULTS:
            message = self.getText(message)
        mbox.setText(message)
        mbox.setStandardButtons(QtGui.QMessageBox.Cancel)
        if timeout:
            timer = QtCore.QTimer(self)
            def timedout():
                mbox.hide()
                timer.stop()
            self.connect(timer, QtCore.SIGNAL("timeout()"), timedout)
            timer.start(timeout * 1000)
        if modal:
            mbox.exec_()
        else:
            mbox.show()


def main():
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtGui.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon(ICONS[-1]), w)

    trayIcon.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()



    
