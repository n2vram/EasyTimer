Easytimer
---------

A simple desktop-tray timer to remind you to sit or stand on a regular basis.

This is my first PyQt project, and my first Qt project in years; it's configurable
and all user strings can be overridden within ~/.config/easytimer.conf

Requirements
============
* Python2
* PyQt4

HOWTO
=====
Either start the "timer.py" script manually or add it to your "startup
applications" per your desktop environment.  Note that, for now, it must be
launched within the project directory to find the icon resources.

When launched, right click the system tray icon and **Configure** to set your
timer intervals and custom messages.

Once setup, right click again and select your option, the icon will show the
expected status, and the tooltip will show the status.  *Pause Timer* will keep
the current status until *Resume Timer*, while *Stop Timer* will simply put the
timer into standby mode.

If sounds don't work, exit the timer and edit the ~/.config/easytimer.conf file
and add a "play_cmd" key, with an array of strings that get executed to play
the sound.

Thanks
======
Thanks to Sven Steinbauer for his Svenito/EasyTimer project on Github.
