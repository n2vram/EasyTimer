

.SUFFIXES: .py .ui

COMPILE = python2 /usr/lib64/python2.7/site-packages/PyQt4/uic/pyuic.py -x -o $@ $< 


all: ui/timerUI.py timer.py
	@echo ALL Done


run: all
	./timer.py


ui/timerUI.py: timer.ui
	$(COMPILE)

design designer:
	designer-qt5 timer.ui
