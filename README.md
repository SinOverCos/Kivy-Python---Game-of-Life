# GUIPython
First GUI project, implemented Conway's Game of Life with Kivy.

Premise of the game:
====================

**Basic premise of the game:**
- On this grid, cells are either living or dead, you decide at the beginning
- If a cell has strictly fewer than 2 neighbours, it dies in the next frame, as if by loneliness
- If a cell has strictly more than 3 neighbours, it dies in the next frame, as if by overpopulation
- If a cell has exactly 2 or 3 neighbours, it lives to the next frame
- If a dead cell has exactly 3 neighbours, it comes alive the next frame, as if by reproduction or migration

**Bonus material:**
- There are many initial circumstances that can lead the board to evolve to some fascinating results, a few of these are included in this game
- To use these patterns, tap on the icon with 4 stamps to choose a stamp and return, then tap on the single stamp icon to go to stamp mode, and tap anywhere on the screen to paste the stamp
- Certain aesthetic and logical settings can be adjusted, such as the appearance of the cells and survival requirements, in the settings panel
- The board's original state can be restored
- The board can be scrambled
- User-defined patterns can be saved

Installation instructions:
==========================

The packaged version on OS X is 1.1GB and isn't really practical to put on GitHub, since part of its bulk include a python interpreter and such so that the app can work out of the box.

The safest route would be to follow instructions [here](http://kivy.org/docs/installation/installation.html).

**OS X Instructions:**
- ```brew install Caskroom/cask/kivy```
- ```sudo pip install cython```

**Ubuntu / Other Linux Distros:**
- ```sudo apt-get install python-kivy```
- ```sudo pip install cython```

**Finally:**
- ```kivy gameoflife.py```

Some issues encountered along the way:
======================================

- Read the comments at the top of gameoflife.py for more detail.

- Number one issue: I did not separate this project into different modules from the beginning. It's too late to un-clutter all my classes into different files now.

- Kivy's widget tree is constructed at the beginning, but can't rely on the whole tree to exist when trying to initialize other widgets though ```__init__()```. Sometimes there will be conflicts where an ```__init__()``` constructor is expecting something to be there but it's not constructed by the widget tree yet.

- The dictionary holding the list of stamps becomes None after an item is popped, don't know why.

- Tried to make images that behave like buttons, but caused a bug where touches from Settings get passesd to my image buttons. This is due to the settings screen covers the game screen instead of replacing it, so the touches still get through to the image buttons. Considering changing the buttons back to actual buttons instead of images that just act as buttons.

- The widget tree from the .kv file is hard-coded, and trying to access a certain widget requires either giving the widget an ID or doing something to the effect of grid = root.children[0].children[1]...children[0]. Both methods look messy, the ID less so. Sometimes in constructors I can't rely on the ID from the .kv file being ready.

- Config.set() is unavailable outside of the build_config() method, and settings that depend on each other can't be updated in the settings panel when one of them is changed, which can be misleading (settings shown on settings panel can be different from what is actually in effect).

- Similarly, user settings can't be made permanent because although the settings panel will load from the gameoflife.ini file, the actual settings in effect are the defaults. Since I can't change what is displayed on the settings panel, the gameoflife.ini is removed on each run to force the settings panel to display the defaults.

- Buildozer (the tool Kivy devs made to compile Kivy projects onto Android/iOS) always has issues. I couldn't get it to work on my Mac. A few months before I bought the Mac I was running a Windows machine dual booting Ubuntu. After literally days of Googling I managed to get Buildozer to build a simple Android app, but then I spilled water on my old laptop. Couldn't get Buildozer to work on my Mac or Kivy's provided VM even after retracing my old steps.

- So far I've only been able to package an app for Mac.
