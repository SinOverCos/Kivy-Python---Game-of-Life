from kivy.config import Config # For settings
from kivy.core.window import Window # To determine window size

## The app
from kivy.app import App # To run the app
from kivy.uix.screenmanager import ScreenManager, Screen # Manage screens
from kivy.uix.screenmanager import FadeTransition, FallOutTransition, RiseInTransition # Transitions
from kivy.uix.boxlayout import BoxLayout # Options pane and Scatter container
from kivy.uix.floatlayout import FloatLayout # Root widget
from kivy.uix.button import Button # For options
from kivy.uix.scatter import Scatter # Movable and zoomable space
from kivy.uix.gridlayout import GridLayout # Grid for the tiles
from kivy.uix.image import Image # Image to act as tiles
from kivy.properties import StringProperty # Test for image source
from random import random # For shuffling the tiles
from kivy.clock import Clock # For scheduling functions
from kivy.uix.listview import ListView, ListItemButton # For selecting stamps
from kivy.adapters.dictadapter import DictAdapter # For selecting stamps
from kivy.uix.textinput import TextInput # For saving stamps

## Settings panel
from kivy.config import ConfigParser
from kivy.uix.settings import SettingsWithSidebar
from gameoflifesettings import logic
from gameoflifesettings import aesthetics
from gameoflifesettings import about_me

## Tools during development
import os



# TODO:

# Dynamic word sizes - physical word sizes change depending on screen resolution

# Package for OS X and Windows

# upgrade android sdk from VM and try to build again!
# upgrade android sdk from VM and try to build again!
# Package for Android - upgrade android sdk from VM and try to build again!
# Package for iOS



## Future TODOs - difficult right now

## Compile for Android
## Used to work on my Ubuntu machine, but I broke the computer.
## Getting it to work on Ubuntu still took a lot of Googling - Buildozer never worked right out of the box
## Rename to main.py and main.kv, of course

# Change to Android toasts:
# print "The whole board is empty - there is nothing to save."
# print "No initial state to go back to."
# print "Invalid input given for new tile size."
# print "There is no stamp to paste."
# print "That's ridiculous - let's do size = 5."


# Given up:
# Use Config.set() to set the living and birth requirements in the settings panel to reflect
#   the new set of rules that the user chose
# E.g. living requirement was "1, 2, 3, 4, 5". User chooses "Conway" as the rule set to use
# The game should automatically change living requirement to say "2, 3" to reflect that
# After about two hours to trying things and reading documentation, I just can't get it to work
# I don't know what I'm doing wrong
# It seems that Config.set only works from within the build_config() method. Even if I save
#   that Config reference and use it to set a field by calling Config.set from another method,
#   it will not work (but works fine if I use Config.set() from within build_config)


# Similarly, this is also difficult due to Config being unusable outside of build_config()
# To prevent confusion (the app's old settings are loaded in the settings panel but the default
#   rules are actually the ones in effect), gameoflife.ini is being removed every time the app is run
#   so the app is forced to display default selections on the settings panel (conforming to the
#   default rules in effect)
# Want to changes persistent
    # Note: external file to toggle between custom and built-in so I know which one to load
    # Note: Split by " = " for gameoflife.ini, and remove the os.remove() line
    # Tile live image
    # Tile dead image
    # Tile size
    # Background image
    # Update speed
    # Life requirement * apply to both game screen and preview screen
    # Birth requirement * apply to both game screen and preview screen


# Save user-defined rules. Not hard to implement but since the Kivy settings panel is provided, there's
#   no way for me to add a button that's just used for saving. The alternative is to make yet another
#   button to say "save current rules" but the game screen is already cluttered enough, and it would
#   be a useless button most of the time


# In numeric fields, "0" will be gone if at the beginning with numeric, but using string input is awkward
# And int field that limits the user's keyboard to numbers will also return an int with the leading
#   zeros stripped off


# Can't figure out kivy's touch propagation
# Root passes the touch to its children and the touch is propagated recursively
# Make the images behave more like buttons
#   i.e. When the user touches down on a button (like pause), but drags it to the tile grid (as if changing their mind)
#   then the game should know the touch started from a button and should not react


## Settings the screen to a big size
PY_WIDTH = 1600
PY_HEIGHT = 1200

TOP_BAR_SCALE = 0.1
GRID_SCALE = 0.8
BOTTOM_BAR_SCALE = 0.1

Config.set("graphics", "width", str(int(0.5*PY_WIDTH)))
Config.set("graphics", "height", str(int(0.5*PY_HEIGHT)))
Window.size = (int(0.5*PY_WIDTH), int(0.5*PY_HEIGHT))



## Updates the bounds of a widget
def get_bounds(bounded):
    bounded.left = bounded.pos[0]
    bounded.right = bounded.pos[0] + bounded.size[0]
    bounded.bottom = bounded.pos[1]
    bounded.top = bounded.pos[1] + bounded.size[1]



## Master widget, it juggles between the different screens
class Juggler(ScreenManager):
    def __init__(self, **kwargs):
        super(Juggler, self).__init__(**kwargs)
        self.fade = FadeTransition()
        self.fall = FallOutTransition()
        self.rise = RiseInTransition()
        self.transition = self.fade



## Primary screen holding the menu options and grid
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.name = "game_screen"



## Holds the top and bottom menu bars plus the game screen
class MasterBox(FloatLayout):
    def __init__(self, **kwargs):
        super(MasterBox, self).__init__(**kwargs)        



## Holds all the individual tiles
class TileGrid(GridLayout):
    def __init__(self, **kwargs):
        super(TileGrid, self).__init__(**kwargs)

        self.side_len = 20
        self.rows = int((GRID_SCALE)*PY_HEIGHT/self.side_len) ## GRID_SCALE is proportion of screen height used for grid
        self.cols = PY_WIDTH/self.side_len
        self.tiles = self.rows*self.cols

        self.req_to_live = [2, 3]
        self.req_to_birth = [3]

        self.updates_per_second = 10.0
        self.playing = False
        self.running = None

        self.initial_state = None

        self.stamp = None

    ## Adds appropriate number of tiles to itself
    def build_self(self):
        for i in range(self.tiles):
            self.add_widget(Tile(self.tiles - i - 1))

    ## Need to update rows, cols, tiles when self.side_len changes
    def update_rct(self):
        self.rows = int(GRID_SCALE*Window.height/self.side_len)
        self.cols = Window.width/self.side_len
        self.tiles = self.rows*self.cols

    ## Kills all the tiles
    def clear_board(self):
        for child in self.children:
            child.die()

    ## Scrambles the tiles
    def randomize(self):
        self.stop()
        for child in self.children:
            if random() < 0.5:
                child.live()
            else:
                child.die()

    ## Determines the state of the cell at the specified coordinates
    ## True for alive, False for dead, None for out of bounds
    def determine_state(self, row, col):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return None
        else:
            tile_num = row*self.cols + col
            return self.children[tile_num].alive

    ## Return list of neighbour states
    def find_neighbour_states(self, tile_num):
        # Coordinates are in row, col
        tile_coords = [tile_num/self.cols, tile_num%self.cols]
        r = tile_coords[0]
        c = tile_coords[1]

        ## I thought it was:
        ## [----->n]
        ## [------>]
        ## [0 1 -->]
        ## Actually:
        ## [n<-----]
        ## [<------]
        ## [<-- 1 0]
        ## Not going to change the code since I am only counting neighbours,
        ## and left/right doesn't matter here
        ## Shouldn't matter anywhere - orientation is irrelevant - just need to be consistent.
        ## Be abstract - go to "next" row/col is still next row/col no matter the orientation.
        top_left = [r+1, c-1]
        top_centre = [r+1, c]
        top_right = [r+1, c+1]
        left = [r, c-1]
        right = [r, c+1]
        bottom_left = [r-1, c-1]
        bottom_centre = [r-1, c]
        bottom_right = [r-1, c+1]

        neighbours = [top_left, top_centre, top_right, left, right, bottom_left, bottom_centre, bottom_right]
        state_list = []
        for n in neighbours:
            state_list.append(self.determine_state(n[0], n[1]))

        return state_list

    ## Counts the number of living neighbours a tile has
    def number_alive(self, tile_num):
        neighbour_states = self.find_neighbour_states(tile_num)
        living_neighbours = 0
        
        for s in neighbour_states:
            if s:
                living_neighbours += 1

        return living_neighbours

    ## Determines the next state of the board (who lives, who dies)
    def get_life_list(self):
        next_frame = []
        for child in self.children:
            living_neighbours = self.number_alive(child.index)
            if child.alive:
                if living_neighbours in self.req_to_live:
                    next_frame.append(True)
                else:
                    next_frame.append(False)
            else:
                if living_neighbours in self.req_to_birth:
                    next_frame.append(True)
                else:
                    next_frame.append(False)

        return next_frame

    ## Updates the board using the list returned by get_life_list()
    ## *args needed - Clock will pass additional arguments (interval?)
    def update_board(self, *args):
        next_frame = self.get_life_list()
        for i, j in zip(next_frame, self.children):
            if i:
                j.live()
            else:
                j.die()

    ## Toggles the state of the board - switches between constantly updating the board and stopping
    def toggle(self):
        if not self.playing:
            self.running = Clock.schedule_interval(self.update_board, 1.0/self.updates_per_second)
            self.playing = True
        else:
            Clock.unschedule(self.running)
            self.running = None
            self.playing = False

    ## Stops updating the board
    def stop(self):
        if self.running != None:
            Clock.unschedule(self.running)
            self.running = None
            self.playing = False

    ## Saves the state of the board
    ## Called before the board starts animating in case the user wants to restart
    def save_state(self):
        self.initial_state = []
        for child in self.children:
            self.initial_state.append(child.alive)

    ## Stops the animation and restores the board to its initial state
    def load_initial_state(self):
        if self.initial_state == None:
            print "No initial state to go back to."
        else:
            self.stop()
            root.ids["play_pause_button"].stop()
            for i, j in zip(self.initial_state, self.children):
                if i == True:
                    j.live()
                else:
                    j.die()
                    
    ## Keeps only the outer consecutive patterns: e.g.
    ## [0, 1, 2, 3, 6, 7, 12, 13] -> [0, 1, 2, 3, 12, 13]
    ## Assumes non-empty list
    ## Assumes no duplicates in the list
    ## Assumes the consecutive patterns are ascending
    ## A consecutive list is returned as-is
    def keep_outer_consecutives(self, seq):
        ## Counting consecutives from the front
        beginning = []
        end = []
        head = seq[0]
        for n in seq:
            if n == head:
                beginning.append(n)
                head += 1
            else:
                break

        ## Flip the seq so I can iterate forward
        seq_rev = seq[::-1]
        tail = seq[-1]
        for n in seq_rev:
            if n == tail:
                end.append(n)
                tail -= 1
            else:
                break

        ## Flip the ending portion back to it is ascending order
        end = end[::-1]
        
        if beginning == end:
            return beginning
        else:
            return beginning + end

    ## Takes the current state, trims away outer dead rows/columns to save
    ## the smallest possible grid that contains the current pattern
    def record_stamp(self):

        ## Save everything in a grid
        state_matrix = []
        row_state = []
        counter = 0
        empty = True
        for child in self.children:
            counter += 1
            row_state.append(child.alive)
            if child.alive:
                empty = False
            if counter%self.cols == 0:
                state_matrix.append(row_state)
                row_state = []

        ## Out-of-bounds error if continuing with empty board
        if empty:
            print "The whole board is empty - there is nothing to save."
            self.stamp = None
            return
        
        ## Trim rows with all dead tiles
        dead_rows = [] # Holds the indices of the dead rows in state_matrix
        dead_row = [] # Definition of a dead row

        ## Defining a row of all dead tiles
        for i in range(self.cols):
            dead_row.append(False)

        for i in range(self.rows):
            if state_matrix[i] == dead_row:
                dead_rows.append(i)

        ## Keep inner empty rows (they are intentional)
        dead_rows = self.keep_outer_consecutives(dead_rows)
        ## Reverse order so they can be removed safely (not removing elements as I iterate forward)
        dead_rows = dead_rows[::-1]
        ## print "Dead rows to remove, in this order:", dead_rows
        for row in dead_rows:
            state_matrix.pop(row)
            
        ## print "Empty rows removed, up-down, left-right flipped:"
        ## self.print_binary_matrix(state_matrix)
        
        ## Trim columns with all dead tiles
        dead_cols = []
        for col in range(self.cols):
            col_is_dead = True
            for row in state_matrix:
                if row[col] == True:
                    col_is_dead = False
                    break
            if col_is_dead:
                dead_cols.append(col)

        ## Keep inner empty columns (they are intentional)
        dead_cols = self.keep_outer_consecutives(dead_cols)
        ## Reverse order so they can be removed
        dead_cols = dead_cols[::-1]
        
        ## print "Columns to remove, in this order: ", dead_cols
        for col in dead_cols:
            for row in state_matrix:
                row.pop(col)
        ## print "Empty rows and columns removed, up-down, left-right flipped:"
        ## self.print_binary_matrix(state_matrix)

        self.stamp = state_matrix

    ## If the given state is True, make the tile at the given coordinates live
    ## Used to help with paste_stamp()
    def enforce_life(self, row, col, state):

        ## If out of bounds, do nothing
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return

        ## If trying to enforce death, skip
        if state == False:
            return
        
        child_number = row*self.cols + col
        self.children[child_number].live()

    ## Takes a midpoint (child #) and draws stamp (list of lists) around the midpoint
    def paste_stamp(self, midpoint, stamp):

        if stamp == None:
            print "There is no stamp to paste."
            return

        ## Find the middle coordinate
        stamp_rows = len(stamp)
        stamp_cols = len(stamp[0])
        mid_row = midpoint/self.cols
        mid_col = midpoint%self.cols
        least_row = mid_row - stamp_rows/2
        least_col = mid_col - stamp_cols/2
        if least_row < 0:
            least_row = 0
        if least_col < 0:
            least_col = 0

        ## Paste each of the stamp's tiles onto the board
        for r in range(stamp_rows):
            for c in range(stamp_cols):
                self.enforce_life(least_row + r, least_col + c, stamp[r][c])

    ## Letters are possible inputs, so non-numeric characters are filtered out
    ## If the remaining string is a valid number, the tile size is updated to that size
    def update_tile_size(self, new_tile_size):
        ## Filter out non-numeric characters
        new_tile_size = str(new_tile_size)
        clean_number = ""
        str_numbers = ['.', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        for char in new_tile_size:
            if char in str_numbers:
                clean_number += char

        try:
            ## Try statement in case no user enters no numeric character
            new_tile_size = int(clean_number)
            if new_tile_size < 5:
                print "That's ridiculous - let's do size = 5."
                new_tile_size = 5
        except:
            ## Does nothing in the app.
            print "Invalid input given for new tile size."
            return

        self.clear_widgets()
        self.side_len = new_tile_size
        self.update_rct()
        Tile.side_len = new_tile_size
        
        self.build_self()
        
        # Any saved state would be invalid now
        self.initial_state = None        



## Base class for the picture buttons
class ImageButton(Image):
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        ## Hack fix. Need to get bounds for the image at construction/on first touch down
        ##  or game will crash, saying there are no left/right/top/bottom fields in this class
        ## I created the left/right/top/bottom fields and they are used when comparing touch coordinates
        ## It appears that a touch is applied right when the app starts up, but before get_bounds is first called
        ## This hack fix can be avoided if I just used self.pos[1] + self.size[1] instead of self.top
        ##  but self.top just feels so much cleaner
        get_bounds(self)

    ## If the touch is within this widget's bounds, the touch_down image is displayed, instead
    def on_touch_down(self, touch):
        get_bounds(self)
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.down_source

    ## If the touch movement is within this widget's bounds, the down_source is applied
    ## Otherwise the up_source is applied
    def on_touch_move(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.down_source
        else:
            self.source = self.up_source


## Switches the game to draw mode
class PenButton(ImageButton):
    def __init__(self, **kwargs):
        super(PenButton, self).__init__(**kwargs)
        self.up_source = "./Images/PenUp.png"
        self.down_source = "./Images/PenDown.png"
        self.source = self.up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.up_source
            Tile.to_draw_mode()



## Switches the game to stamp mode
class StampButton(ImageButton):
    def __init__(self, **kwargs):
        super(StampButton, self).__init__(**kwargs)
        self.up_source = "./Images/StampUp.png"
        self.down_source = "./Images/StampDown.png"
        self.source = self.up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.up_source
            Tile.to_stamp_mode()



## Swaps the game to the choose stamp screen
class ChooseStampButton(ImageButton):
    def __init__(self, **kwargs):
        super(ChooseStampButton, self).__init__(**kwargs)
        self.up_source = "./Images/ChooseStampUp.png"
        self.down_source = "./Images/ChooseStampDown.png"
        self.source = self.up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.up_source
            root.ids["grid"].stop()
            root.ids["play_pause_button"].stop()
            root.current = "stamp_screen"



## Swaps the game to the settings screen
class SettingsButton(ImageButton):
    def __init__(self, **kwargs):
        super(SettingsButton, self).__init__(**kwargs)
        get_bounds(self)
        self.up_source = "./Images/SettingsUp.png"
        self.down_source = "./Images/SettingsDown.png"
        self.source = self.up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.up_source
            root.ids["play_pause_button"].stop()
            root.ids["grid"].stop()
            app.open_settings()



## Swaps the game between playing and stopping the animation
## on_touch_down and on_touch_move are overridden because this button has two images
class PlayPauseButton(ImageButton):
    def __init__(self, **kwargs):
        super(PlayPauseButton, self).__init__(**kwargs)
        self.play_down_source = "./Images/PlayDown.png"
        self.play_up_source = "./Images/PlayUp.png"
        self.pause_down_source = "./Images/PauseDown.png"
        self.pause_up_source = "./Images/PauseUp.png"
        self.source = self.play_up_source
        self.playing = False

    def stop(self):
        self.source = self.play_up_source
        self.playing = False

    def on_touch_down(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            if self.source == self.play_up_source:
                self.source = self.play_down_source
            elif self.source == self.pause_up_source:
                self.source = self.pause_down_source

    def on_touch_move(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            if self.playing:
                self.source = self.pause_down_source
            else:
                self.source = self.play_down_source
        else:
            if self.playing:
                self.source = self.pause_up_source
            else:
                self.source = self.play_up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            if not self.playing:
                root.ids["grid"].save_state()
                self.playing = True
                self.source = self.pause_up_source
            else:
                self.playing = False
                self.source = self.play_up_source

            root.ids["grid"].toggle()



## Stops the animation, if any, and goes to the next frame
class NextButton(ImageButton):
    def __init__(self, **kwargs):
        super(NextButton, self).__init__(**kwargs)
        get_bounds(self)
        self.up_source = "./Images/NextUp.png"
        self.down_source = "./Images/NextDown.png"
        self.source = self.up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.up_source
            root.ids["grid"].stop()
            root.ids["play_pause_button"].stop()
            root.ids["grid"].update_board()



## Stops the animation, if any, and restores the grid to its original state
class RestoreButton(ImageButton):
    def __init__(self, **kwargs):
        super(RestoreButton, self).__init__(**kwargs)
        get_bounds(self)
        self.up_source = "./Images/RestoreUp.png"
        self.down_source = "./Images/RestoreDown.png"
        self.source = self.up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.up_source
            root.ids["grid"].load_initial_state()



## Saves the board's current state and takes the user to the save stamp screen
## Does nothing if the board is empty
class SaveButton(ImageButton):
    def __init__(self, **kwargs):
        super(SaveButton, self).__init__(**kwargs)
        get_bounds(self)
        self.up_source = "./Images/SaveUp.png"
        self.down_source = "./Images/SaveDown.png"
        self.source = self.up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.up_source
            root.ids["grid"].stop()
            root.ids["play_pause_button"].stop()
            root.ids["grid"].record_stamp()
            ## grid.stamp is set to None if user tried to save blank screen
            if root.ids["grid"].stamp == None:
                return
            root.current = "save_stamp_screen"



## Scrambles the tiles
class RandomButton(ImageButton):
    def __init__(self, **kwargs):
        super(RandomButton, self).__init__(**kwargs)
        get_bounds(self)
        self.up_source = "./Images/RandomUp.png"
        self.down_source = "./Images/RandomDown.png"
        self.source = self.up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.up_source
            root.ids["play_pause_button"].stop()
            root.ids["grid"].randomize()



## Clears the tiles
class ClearButton(ImageButton):
    def __init__(self, **kwargs):
        super(ClearButton, self).__init__(**kwargs)
        get_bounds(self)
        self.up_source = "./Images/ClearUp.png"
        self.down_source = "./Images/ClearDown.png"
        self.source = self.up_source

    def on_touch_up(self, touch):
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.source = self.up_source
            root.ids["grid"].clear_board()
            root.ids["grid"].stop()
            root.ids["play_pause_button"].stop()



# Touch: parent receives signal. If return False (default), then pass to
# most recently added child, then second most recent, etc.
# Root widget receives touch first
## Class representing tiles in the game
class Tile(Image):

    live_source = "./Images/GreenFade.png"
    dead_source = "./Images/Transparent.png"
    side_len = 20

    draw_mode = True

    def __init__(self, index, **kwargs):
        super(Tile, self).__init__(**kwargs)

        self.source = Tile.dead_source
        self.allow_stretch = True
        self.keep_ratio = False

        self.index = index

        self.alive = False
        self.departed = True
    
    ## Changes tile behaviour to draw mode
    @staticmethod
    def to_draw_mode():
        Tile.draw_mode = True

    ## Changes tile behaviour to stamp mode
    @staticmethod
    def to_stamp_mode():
        Tile.draw_mode = False

    ## Enforces that this tile uses the live source
    ## If already alive, don't bother reassigning the source
    def live(self):
        if self.alive and self.source == Tile.live_source:
            return
        self.alive = True
        self.source = Tile.live_source

    ## Same as live. Enforces that the tile uses the dead source
    ## If already dead, don't bother reassigning the source
    def die(self):
        if not self.alive and self.source == Tile.dead_source:
            return
        self.alive = False
        self.source = Tile.dead_source

    # self.departed: true if the touch has left this tile.
    def on_touch_down(self, touch):

        get_bounds(self)

        ## If touching this tile:
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            ## If draw mode: then draw a dot
            if Tile.draw_mode == True:
                if self.alive:
                    self.die()
                else:
                    self.live()
            ## If stamp mode: draw the stamp
            else:
                self.parent.paste_stamp(self.index, self.parent.stamp)

            ## Either way, departed is now False
            self.departed = False

    # Status should only be updated if the user is returning (i.e. departed, then came back)
    # Should not continuously shift back and forth because user's finger stayed too long
    def on_touch_move(self, touch):

        get_bounds(self)

        ## If coming back to this tile and in draw mode:
        if self.departed and Tile.draw_mode and (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            if self.alive == True:
                self.die()
            else:
                self.live()

            self.departed = False

        ## If touch wasn't on this tile, then departed is True
        if (not (self.left <= touch.x <= self.right)) or (not (self.bottom <= touch.y <= self.top)):
            self.departed = True

        ## No consideration for stamps because user shouldn't be able to accidentally
        ##  paste the same stamp mutiple times next to each other (ruins the stamp)

    def on_touch_up(self, touch):

        get_bounds(self)

        ## If touch up was on this dot, the departed is True
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.departed = True

        

## The app itself
class GameOfLifeApp(App):

    def __init__(self, **kwargs):
        super(GameOfLifeApp, self).__init__(**kwargs)
        
        self.settings_functions = {
            u'updates_per_second' : self.update_updates_per_second,
            u'req_to_live' : self.update_req_to_live,
            u'req_to_birth' : self.update_req_to_birth,
            u'rule_to_use' : self.update_rule_to_use,

            u'live_tile' : self.update_live_tile,
            u'dead_tile' : self.update_dead_tile,
            u'tile_size' : self.update_tile_size,
            u'background' : self.update_background,
            u'custom_live_tile' : self.update_custom_live_tile,
            u'custom_dead_tile' : self.update_custom_dead_tile,
            u'custom_background' : self.update_custom_background }

        self.rules = self.read_rules_from_file("gameofliferules.txt")
        self.tiles = self.read_tiles_from_file("gameoflifetiles.txt")

        global app
        app = self

    ## Takes a file name and updates the rules dictionary with definitions from the file
    def read_rules_from_file(self, filename):
        rules = {}
        rule_file = open(filename, "r")
        for line in rule_file:
            rule = line.split(":")
            
            living_req_str = rule[1]
            living_req_list = []
            living_req_len = len(living_req_str)
            for i in range(living_req_len):
                living_req_list.append(int(living_req_str[i]))

            birth_req_str = rule[2][:-1] ## Get rid of newline character at the end
            birth_req_list = []
            birth_req_len = len(birth_req_str)
            for i in range(birth_req_len):
                birth_req_list.append(int(birth_req_str[i]))

            rules[rule[0]] = (living_req_list, birth_req_list)

        return rules

    ## Takes a file name and updates the tiles dictionary with paths from the file
    def read_tiles_from_file(self, filename):
        tiles = {}
        tile_file = open(filename, "r")
        for line in tile_file:
            tile = line.split(":")
            tiles[tile[0]] = tile[1][:-1] ## Get rid of the newline character at the end
        return tiles

    ## Calls the grid's build_self function
    def build_grid(self):
        self.grid.build_self()

    ## Sets everything up
    def build(self):
        self.root = Juggler()
        self.grid = self.root.children[0].children[0].children[2].children[0].children[0]
            
        self.build_grid()

        ## Settings panel
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False

        ## Make root accessible to all
        global root
        root = self.root
        return self.root

    ## Sets up default settings in the settings panel
    def build_config(self, config):
        config.setdefaults("logic", {
            "updates_per_second" : 10,
            "req_to_live" : "2, 3",
            "req_to_birth" : "3",
            "rule_to_use" : "Conway",})
        config.setdefaults("aesthetics", {
            "live_tile" : "Green Fade",
            "dead_tile" : "Transparent",
            "tile_size" : 20,
            "background" : "Black",
            "custom_live_tile" : "/",
            "custom_dead_tile" : "/"})

    ## Adds the two settings panels
    def build_settings(self, settings):
        settings.add_json_panel("Gameplay", self.config, data=logic)
        settings.add_json_panel("Aesthetics", self.config, data=aesthetics)

    ## Calls corresponding function to the setting that is changed
    def on_config_change(self, config, section, key, value):
        self.settings_functions.get(key, self.setting_not_found)(config, value)

    ## Should never be called, but here in case
    def setting_not_found(self, value, *args):
        print "Can't do anything about %s, setting not found!" % str(value)

    ## Changes the update frequency
    def update_updates_per_second(self, config, new_updates_per_second):
        new_updates_per_second = float(new_updates_per_second)
        self.grid.updates_per_second = new_updates_per_second

    ## Converts string input to individual digits
    def to_single_digits(self, single_digits):
        string = str(single_digits)
        str_numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '0']
        new_numbers = []

        for char in string:
            if char in str_numbers:
                new_numbers.append(int(char))
        return new_numbers

    ## Updates the requirement to living
    def update_req_to_live(self, config, new_req_to_live):
        new_numbers = self.to_single_digits(new_req_to_live)
        self.grid.req_to_live = new_numbers
        
        new_live_str = ""
        for char in new_numbers:
            new_live_str += str(char)
            new_live_str += ", "
        new_live_str = new_live_str[:-2]

    ## Updates the requirement to come alive
    def update_req_to_birth(self, config, new_req_to_birth):
        new_numbers = self.to_single_digits(new_req_to_birth)
        print "New list of neighbours needed to come to live: ", new_numbers
        self.grid.req_to_birth = new_numbers

    ## Updates the set of rules to use, e.g. Conway is 2, 3 to live, 3 to come alive
    def update_rule_to_use(self, config, new_rule_to_use):
        new_rule_set = self.rules[new_rule_to_use]
        self.update_req_to_live(config, new_rule_set[0])
        self.update_req_to_birth(config, new_rule_set[1])

    ## Updates live tile with new picture
    def update_live_tile(self, config, new_live_tile):
        Tile.live_source = self.tiles[str(new_live_tile)]
        print "Tile.live_source is updated to: ", Tile.live_source
        for child in self.root.ids["grid"].children:
            if child.alive:
                child.source = Tile.live_source

    ## Updates dead tile with new picture    
    def update_dead_tile(self, config, new_dead_tile):
        Tile.dead_source = self.tiles[str(new_dead_tile)]
        print "Tile.dead_source is updated to: ", Tile.dead_source
        for child in self.root.ids["grid"].children:
            if not child.alive:
                child.source = Tile.dead_source

    ## Delete all tiles, update tile size, add new number of tiles back
    ## This takes a while...
    def update_tile_size(self, config, new_tile_size):
        self.grid.update_tile_size(new_tile_size)

    ## Not going to implement
    def update_background(self, config, new_background):
        pass

    ## Updates the live tile with a custom image (path specified by the user)
    def update_custom_live_tile(self, config, new_live_tile):
        new_path = str(new_live_tile)
        print "New path for live tiles: ", new_path
        Tile.live_source = new_path
        for child in self.root.ids["grid"].children:
            if child.alive:
                child.source = new_path

    ## Updates the dead tile with a custom image (path specified by the user)
    def update_custom_dead_tile(self, config, new_dead_tile):
        new_path = str(new_dead_tile)
        print "New path for dead tiles: ", new_path
        Tile.dead_source = new_path
        for child in self.root.ids["grid"].children:
            if not child.alive:
                child.source = new_path

    ## Not going to implement
    def update_custom_background(self, config, new_background):
        pass



## Screen for selecting stamps
class StampScreen(Screen):
    def __init__(self, **kwargs):
        super(StampScreen, self).__init__(**kwargs)
        self.name = "stamp_screen"
        self.tile_side_len = None

    ## Tracks the original Tile settings (they are changed later for the stamp previews)
    def on_pre_enter(self):
        self.children[0].list_stamps()
        self.orig_tile_side_len = Tile.side_len
        self.orig_tile_mode = Tile.draw_mode
        Tile.to_draw_mode()

    ## Changes Tile settings to the screen's pre-enter state
    def on_pre_leave(self):
        Tile.side_len = self.orig_tile_side_len
        if self.orig_tile_mode == True:
            Tile.to_draw_mode()
        else:
            Tile.to_stamp_mode()
        self.children[0].children[2].stop()



## Custom button to use for selectable scrollview
class ViewStampButton(ListItemButton):
    def __init__(self, **kwargs):
        super(ViewStampButton, self).__init__(**kwargs)
        self.font_size = 20

    ## When this button is clicked, the stamp that this button represents will be
    ##  put up on the preview
    def on_release(self):
        stamp_dict = root.ids["stamp_select_viewer"].children[0].stamp_dict
        returnDeleteButtons = root.ids["stamp_select_viewer"].children[1]
        previewGrid = root.ids["stamp_select_viewer"].children[2]
        for key in stamp_dict:
            if self.text == stamp_dict[key]["name"]:
                previewGrid.stamp = stamp_dict[key]["grid"]
                previewGrid.start_demo()
                ## Delete was added first, return second
                ## But: return is child 0, delete is child 1
                returnDeleteButtons.children[1].selection = self.text
                returnDeleteButtons.children[0].selection = stamp_dict[key]["grid"]
                break



## Button to return to the game screen
class ReturnButton(Button):
    def __init__(self, **kwargs):
        super(ReturnButton, self).__init__(**kwargs)
        self.font_size = 20
        self.text = "Return"
        self.size_hint = (1.0, 0.05)
        self.selection = None

    def on_release(self):
        root.current = "game_screen"
        root.ids["grid"].stamp = self.selection



## Button to delete a stamp    
class DeleteStampButton(Button):
    def __init__(self, **kwargs):
        super(DeleteStampButton, self).__init__(**kwargs)
        self.font_size = 20
        self.text = "Delete"
        self.selection = None

    def on_release(self):
        viewer = root.ids["stamp_select_viewer"]
        if self.selection == None:
            return
        print self.selection
        del viewer.stamp_dict[self.selection]
        viewer.write_stamps_to_file("gameoflifestamps.txt", viewer.stamp_dict)
        print "Stamp will be gone on next load"

        ## Hack. The list view dictionary turns to None after one deletion
        ## Not sure how that works in kivy (or if I'm doing something wrong)
        ## For now: return user to screen after one deletion
        ## Also hides the fact that the UI still displays the to-be-deleted stamp
        ##  and will only update the next time the user enters this screen, lol
        root.current = "game_screen"
        Tile.to_draw_mode()



## A smaller grid that is just big enough to display the stamp selected in the stamp screen
class StampThumbnail(TileGrid):
    def __init__(self, rows, cols, live, birth, stamp, **kwargs):
        super(StampThumbnail, self).__init__(**kwargs)

        self.size_hint = (1.0, 0.4)

        ## Number of tiles depends on size of stamp, needs to be large
        ## enough to play it out
        ## Adjust to make it as much of a square as possible
        self.rows = rows*3
        self.cols = cols*3
        self.tiles = self.rows*self.cols

        self.req_to_live = live
        self.req_to_birth = birth

        self.updates_per_second = 10.0
        self.playing = False
        self.running = None

        ## List - will become list representation of self.stamp
        self.initial_state = None

        ## Matrix
        self.stamp = stamp

        self.build_self()

    ## Updates the grid according the to tile sizes (changes with each stamp)
    def update_rct(self):
        self.rows = int(0.4*Window.height/self.side_len) ## 0.4 is scale of the demo grid
        self.cols = Window.width/self.side_len
        self.tiles = self.rows*self.cols

    ## Reconfigures the grid to fit the current stamp
    ## Line to start the animation (preview the stamp's animation before selecting it)
    ##  is disabled. Not sure if user would want to only see what the initial stamp looks like
    ## In addition, depending on the stamp, the size of the grid would have to be adjusted
    ##  to accomodate for the full size of the resulting animation, which is impossible to
    ##  determine for an arbitrary pattern, according to Conway himself!
    def start_demo(self):
        ## Stop previous animation (if any)
        self.stop()
        ## Resize tiles so grid matches pattern
        self.stamp_rows = len(self.stamp)
        self.stamp_cols = len(self.stamp[0])
        self.side_len = min((0.4*Window.height)/(1.3*self.stamp_rows),
                            (Window.width)/(1.3*self.stamp_cols))
        self.update_tile_size(str(int(self.side_len)))
        ## Paste pattern into middle
        self.paste_stamp(self.tiles/2, self.stamp)

        ## Start animation
        ##self.toggle()
        


## A scrollable list view with clickable buttons
## This is mostly copy-pasted code from kivy examples
## I still don't quite understand how this list things works
class StampList(ListView):
    def __init__(self, stamp_dict, **kwargs):
        super(StampList, self).__init__(**kwargs)

        self.size_hint = (1.0, 0.55)
    
        self.stamp_dict = stamp_dict
        
        list_item_args_converter = \
            lambda row_index, rec: {'text': rec['name'],
                                    'size_hint_y': None,
                                    'height': Window.height * 0.6 / 5}

        dict_adapter = DictAdapter(sorted_keys = sorted(self.stamp_dict.keys()),
                                   data = self.stamp_dict,
                                   args_converter = list_item_args_converter,
                                   selection_mode = 'single',
                                   allow_empty_selection = False,
                                   cls = ViewStampButton)

        self.adapter = dict_adapter



## A smaller grid used to preview stamps
class StampViewer(GridLayout):
    ## Will be called by .kv at app start because it's in the widget tree
    def __init__(self, **kwargs):
        kwargs['cols'] = 1 # One column of buttons, has to come before super(), don't know why
        super(StampViewer, self).__init__(**kwargs)
        self.orientation = "vertical"
        
        self.stamp_dict = {}
        self.already_set_up = False


    ## For whatever reason, most of this setup work can't be done in __init__()
    ## My guess is that there'a conflict when the .kv file's tree is constructed
    ##  at the same time that the __init__() method is running, but not sure
    def list_stamps(self):
        ## Initiate the preview
        ## Reread every time in case user added new stamp and is trying it out
        self.clear_widgets()
        self.stamp_dict = self.read_stamps_from_file("gameoflifestamps.txt")
        self.add_widget(StampThumbnail(1, 1, [2, 3], [3], None))
        Buttons = GridLayout(rows=1, cols=2, size_hint=(1.0, 0.05))
        Buttons.add_widget(DeleteStampButton())
        Buttons.add_widget(ReturnButton())
        self.add_widget(Buttons)
        self.add_widget(StampList(self.stamp_dict))
        self.already_set_up = True

    ## Reads stamps and their definitions from file
    def read_stamps_from_file(self, stamp_file):
        stamps = open(stamp_file, "r")

        stamp_dict = {}
        skipped_first = False

        for line in stamps:
            if not skipped_first:
                skipped_first = True
                continue
            
            stamp = line.split(":")
            stamp_name = stamp[0]
            stamp_matrix = []
            stamp = stamp[1:]
            for row in stamp:
                stamp_row = []
                for col in row:
                    if col == "0":
                        stamp_row.append(False)
                    elif col == "1": ## elif in case it's a newline character
                        stamp_row.append(True)
                stamp_matrix.append(stamp_row)
            stamp_dict[stamp_name] = {"name" : stamp_name,
                                      "grid" : stamp_matrix}
        stamps.close()
        return stamp_dict

    ## Takes a stamp file name and a dictionary of stamps and writes it to file
    def write_stamps_to_file(self, stamp_file, stamp_dict):
        stamps = open(stamp_file, "w")

        stamps.write("# Name : row : row : ...\n")
        
        for stamp in stamp_dict:
            stamp_matrix = stamp_dict[stamp]["grid"]
            line = stamp + ":"
            for row in stamp_matrix:
                str_row = ""
                for col in row:
                    if col == True:
                        str_row += "1"
                    else:
                        str_row += "0"
                str_row += ":"
                line += str_row
            line = line[:-1] ## Get rid of last colon
            line += "\n" ## Append new line
            stamps.write(line)

        stamps.close()

        self.stamp_dict = None



## Simple text input for saving stamp names
class NameBox(TextInput):
    def __init__(self, **kwargs):
        super(NameBox, self).__init__(**kwargs)
        self.font_size = 50
        self.size_hint_y = 0.3
        self.text = "New Stamp"



## Saves a stamp with the text in the text input as its name
class SaveNameButton(Button):
    def __init__(self, **kwargs):
        super(SaveNameButton, self).__init__(**kwargs)
        self.font_size = 20
        self.size_hint_y = 0.35
        self.text = "Save"
        self.stamp_name = None
        self.stamp_grid = None

    def append_stamp_to_file(self, stamp_file, stamp_name, stamp_matrix):
        stamps = open(stamp_file, "a")

        line = stamp_name + ":"
        for row in stamp_matrix:
            str_row = ""
            for col in row:
                if col == True:
                    str_row += "1"
                else:
                    str_row += "0"
            str_row += ":"
            line += str_row
        line = line[:-1] ## Get rid of last colon
        line += "\n" ## End of line
        stamps.write(line)
        stamps.close()
        
    def on_release(self):
        self.stamp_name = root.ids["save_stamp_screen"].children[0].children[2].text
        self.stamp_grid = root.ids["grid"].stamp
        self.append_stamp_to_file("gameoflifestamps.txt", self.stamp_name, self.stamp_grid)
        root.current = "game_screen"



## Returns the user to the main game screen without saving the stamp
class CancelButton(Button):
    def __init__(self, **kwargs):
        super(CancelButton, self).__init__(**kwargs)
        self.font_size = 20
        self.size_hint_y = 0.35
        self.text = "Cancel"

    def on_release(self):
        root.current = "game_screen"



## Screen used to save stamps - consists of a text input and two buttons
class SaveStampScreen(Screen):
    def __init__(self, **kwargs):
        super(SaveStampScreen, self).__init__(**kwargs)
        self.name = "save_stamp_screen"
        self.already_set_up = False
        
    def on_pre_enter(self):
        if not self.already_set_up:
           nameSaver = GridLayout(size_hint=(1,1), rows=3, cols=1)
           nameSaver.add_widget(NameBox())
           nameSaver.add_widget(SaveNameButton())
           nameSaver.add_widget(CancelButton())
           self.add_widget(nameSaver)
           self.already_set_up = True



## Not implemented yet
class AboutMeScreen(Screen):
    def __init__(self, **kwargs):
        super(AboutMeScreen, self).__init__(**kwargs)
        self.name = "about_me_screen"



if __name__ == "__main__":
    ## Hack/hotfix/ugly patch. See comments at the top
    try:
        os.remove("gameoflife.ini")
    except:
        pass
    
    GameOfLifeApp().run()
