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
from kivy.uix.settings import SettingsWithSpinner
from gameoflifesettings import logic
from gameoflifesettings import aesthetics
from gameoflifesettings import about_me

## Tools during development
import os


# TODO:

# Load it up with cool stamps! :D

# Fix the default tile size generated - look like long rectangles right now

# Change button texts to images since buttons don't support pictures
# Remember to have both button down and button up pictures

# Document the code

# Separate into modules? E.g. # from buttons import *

# Figure out naming: it might cause problems when compiling (need to name main.py?)
# main.py already exists from tutorial

# Change to Android toasts:
# print "The whole board is empty - there is nothing to save."
# print "No initial state to go back to."
# print "Invalid input given for new tile size."
# print "There is no stamp to paste."
# print "That's ridiculous - let's do size = 1."

# Dynamic word sizes - physical word sizes change depending on screen resolution



## Future TODOs - difficult right now

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
# I have no idea what I'm doing wrong
# To prevent confusion (the app's old settings are loaded in the settings panel but the defaults
#   are actually the rules in effect) gameoflife.ini is being removed every time the app is run
#   so the app is forced to display default selections on the settings panel (conforming to the
#   default rules in effect)


# Make changes persistent
    # Note: external file to toggle between custom and built-in so I know which one to load
    # Note: Split by " = " for gameoflife.ini, and remove the os.remove() line
    # Tile live image
    # Tile dead image
    # Tile size
    # Background image
    # Update speed
    # Life requirement * apply to both game screen and preview screen
    # Birth requirement * apply to both game screen and preview screen


# Save user-defined rules. Not hard to implement but since the Kivy settings panel is given, there's
#   no way for me to add a button that's just used for saving. The alternative is to make yet another
#   button to say "save current rules" but the game screen is already cluttered enough, and it would
#   be a useless button most of the time


# In numeric fields, "0" will be gone if at the beginning with numeric, but using string input is awkward
# And int field that limits the user's keyboard to numbers will also return an int with the leading
#   zeros stripped off

PY_WIDTH = 600
PY_HEIGHT = 1200

TOP_BAR_SCALE = 0.1
GRID_SCALE = 0.8
BOTTOM_BAR_SCALE = 0.1

Config.set("graphics", "width", str(int(0.5*PY_WIDTH)))
Config.set("graphics", "height", str(int(0.5*PY_HEIGHT)))
Window.size = (int(0.5*PY_WIDTH), int(0.5*PY_HEIGHT))

class Juggler(ScreenManager):
    def __init__(self, **kwargs):
        super(Juggler, self).__init__(**kwargs)
        self.fade = FadeTransition()
        self.fall = FallOutTransition()
        self.rise = RiseInTransition()
        self.transition = self.fade

    ## on screen change: change transtion risein/fallout
        
    ## on screen change: need to clear out scroll's widgets


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.name = "game_screen"

    def on_pre_enter(self):        
        print Window.height
        print Window.width



class MasterBox(FloatLayout):
    def __init__(self, **kwargs):
        super(MasterBox, self).__init__(**kwargs)        
        
class TileGrid(GridLayout):
    def __init__(self, **kwargs):
        super(TileGrid, self).__init__(**kwargs)

        self.side_len = 30
        print "self.side_len:", self.side_len, ", PY_HEIGHT:", PY_HEIGHT, "GRID_SCALE*PY_HEIGHT:", GRID_SCALE*PY_HEIGHT,
        print ", GRID_SCALE*PY_HEIGHT/self.side_len", int(GRID_SCALE*PY_HEIGHT/self.side_len)
        print "self.side_len:", self.side_len, ", PY_WIDTH:", PY_WIDTH,
        print ", PY_WIDTH/self.side_len", PY_WIDTH/self.side_len
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

    def build_self(self):
        for i in range(self.tiles):
            self.add_widget(Tile(self.tiles - i - 1))

    ## Need to update rows, cols, tiles when self.side_len changes
    def update_rct(self):
        self.rows = int(GRID_SCALE*Window.height/self.side_len)
        self.cols = Window.width/self.side_len
        self.tiles = self.rows*self.cols

    def clear_board(self):
        for child in self.children:
            child.die()

    def randomize(self):
        self.stop()
        for child in self.children:
            if random() < 0.5:
                child.live()
            else:
                child.die()
        
    # True for alive, False for dead, None for out of bounds
    def determine_state(self, row, col):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return None
        else:
            tile_num = row*self.cols + col
            return self.children[tile_num].alive
    
    # Return list of neighbour states
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

    def number_alive(self, tile_num):
        neighbour_states = self.find_neighbour_states(tile_num)
        living_neighbours = 0
        
        for s in neighbour_states:
            if s:
                living_neighbours += 1

        return living_neighbours

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


    ## *args needed - Clock will pass what I assume is time
    def update_board(self, *args):
        next_frame = self.get_life_list()
        for i, j in zip(next_frame, self.children):
            if i:
                j.live()
            else:
                j.die()
                

    def toggle(self):
        if not self.playing:
            self.running = Clock.schedule_interval(self.update_board, 1.0/self.updates_per_second)
            self.playing = True
        else:
            Clock.unschedule(self.running)
            self.running = None
            self.playing = False


    def stop(self):
        if self.running != None:
            Clock.unschedule(self.running)
            self.running = None
            self.playing = False

    def save_state(self):
        self.initial_state = []
        for child in self.children:
            self.initial_state.append(child.alive)

    def load_initial_state(self):
        if self.initial_state == None:
            print "No initial state to go back to."
        else:
            self.stop()
            root.ids["play_pause_button"].stop()
            n_children = len(self.children)
            for i in range(n_children):
                if self.initial_state[i] == True:
                    self.children[i].live()
                else:
                    self.children[i].die()

    ## Keeps only the outer consecutive patterns: e.g.
    ## [0, 1, 2, 3, 6, 7, 12, 13] -> [0, 1, 2, 3, 12, 13]
    ## Assumes non-empty list
    ## Assumes no duplicates in the list
    ## Assumes the consecutive patterns are ascending
    ## A consecutive list is returned as-is
    def keep_outer_consecutives(self, seq):
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
            return
        
        ## print "The whole board, up-down, left-right flipped:"
        ## self.print_binary_matrix(state_matrix)
        
        ## Trim rows with all dead tiles
        dead_rows = []
        dead_row = []

        for i in range(self.cols):
            dead_row.append(False)

        for i in range(self.rows):
            if state_matrix[i] == dead_row:
                dead_rows.append(i)

        ## Keep inner empty rows (they are intentional)
        dead_rows = self.keep_outer_consecutives(dead_rows)
        ## Reverse order so they can be removed
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


    def enforce_life(self, row, col, state):

        ## If out of bounds, do nothing
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return

        if state == False:
            return
        
        child_number = row*self.cols + col
        self.children[child_number].live()

    ## Takes a midpoint (child #) and draws stamp (list of lists) around the midpoint
    def paste_stamp(self, midpoint, stamp):

        if stamp == None:
            print "There is no stamp to paste."
            return

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

        print "stamp rows:", stamp_rows, "stamp cols:", stamp_cols
        print "mid row:", mid_row, "mid_col:", mid_col
        print "least_row:", least_row, "least_col:", least_col

        for r in range(stamp_rows):
            for c in range(stamp_cols):
                self.enforce_life(least_row + r, least_col + c, stamp[r][c])

    def update_tile_size(self, new_tile_size):
        print new_tile_size
        new_tile_size = str(new_tile_size)
        clean_number = ""
        str_numbers = ['.', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        for char in new_tile_size:
            if char in str_numbers:
                clean_number += char

        print "NEW TILE SIZE:" + clean_number
        print int(clean_number)

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
        Tile.update_rc()

        self.build_self()
        
        # Any saved state would be invalid now
        self.initial_state = None        

    
    def wave(self):
        for i in range(len(self.children)):
            print "child number:", i
            self.children[i].blink()
            print "\n"

    def print_binary_matrix(self, matrix):
        for row in matrix:
            for col in row:
                if col:
                    print "1",
                else:
                    print "0",
            print


class PlayPauseButton(Button):
    def __init__(self, **kwargs):
        super(PlayPauseButton, self).__init__(**kwargs)
        self.text = "Play"
        self.font_size = 20
        self.playing = False

    def stop(self):
        self.text = "Play"
        self.playing = False

    def on_release(self):
        if not self.playing:
            root.ids["grid"].save_state()
        
        if not self.playing:
            self.playing = True
            self.text = "Stop"
        else:
            self.playing = False
            self.text = "Play"
            
        root.ids["grid"].toggle()
        

class NextButton(Button):
    def __init__(self, **kwargs):
        super(NextButton, self).__init__(**kwargs)
        self.text = "Next"
        self.font_size = 20

    def on_release(self):
        root.ids["grid"].update_board()
        print "width:", Window.width
        print "height:", Window.height


class RestoreButton(Button):
    def __init__(self, **kwargs):
        super(RestoreButton, self).__init__(**kwargs)
        self.text = "Restore"
        self.font_size = 20

    def on_release(self):
        root.ids["grid"].load_initial_state()


class SaveButton(Button):
    def __init__(self, **kwargs):
        super(SaveButton, self).__init__(**kwargs)
        self.text = "Save"
        self.font_size = 20

    def on_release(self):
        root.ids["grid"].record_stamp()
        root.current = "save_stamp_screen"


class RandomButton(Button):
    def __init__(self, **kwargs):
        super(RandomButton, self).__init__(**kwargs)
        self.text = "Random"
        self.font_size = 20
    def on_release(self):
        root.ids["play_pause_button"].stop()
        root.ids["grid"].randomize()


class ClearButton(Button):
    def __init__(self, **kwargs):
        super(ClearButton, self).__init__(**kwargs)
        self.text = "Clear"
        self.font_size = 20

    def on_release(self):
        root.ids["grid"].clear_board()
        root.ids["grid"].stop()
        root.ids["play_pause_button"].stop()
        print root.ids["grid"].tiles
        print len(root.ids["grid"].children)

class PenButton(Button):
    def __init__(self, **kwargs):
        super(PenButton, self).__init__(**kwargs)
        self.text = "Pen"
        self.font_size = 20

    def on_release(self):
        Tile.to_draw_mode()
 

class StampButton(Button):
    def __init__(self, **kwargs):
        super(StampButton, self).__init__(**kwargs)
        self.text = "Stamp"
        self.font_size = 20

    def on_release(self):
        Tile.to_stamp_mode()
        

class ChooseStampButton(Button):
    def __init__(self, **kwargs):
        super(ChooseStampButton, self).__init__(**kwargs)
        self.text = "Choose Stamp"
        self.font_size = 20

    def on_release(self):
        root.current = "stamp_screen"


class SettingsButton(Button):
    def __init__(self, **kwargs):
        super(SettingsButton, self).__init__(**kwargs)
        self.text = "Settings"
        self.font_size = 20


# Touch: parent receives signal. If return False (default), then pass to
# most recently added child, then second most recent, etc.
# Root widget receives touch first

class Tile(Image):

    live_source = "./Images/GreenFade.png"
    dead_source = "./Images/Transparent.png"
    side_len = 30

    ## In retrospect, keeping row and cols in the Tile was useless,
    ##  and trying to keep it updated with the grid's numbers was a pain

    ##rows = int(GRID_SCALE*Window.height/side_len)
    ##cols = Window.width/side_len

    draw_mode = True

    def __init__(self, index, **kwargs):
        super(Tile, self).__init__(**kwargs)

        self.source = Tile.dead_source
        self.allow_stretch = True
        self.keep_ratio = False

        self.index = index

        ## In retrospect, keeping row and cols in the Tile was useless,
        ##  and trying to keep it updated with the grid's numbers was a pain
        ##self.row_num = index/Tile.cols
        ##self.col_num = index%Tile.cols

        self.alive = False
        self.departed = True

    ## Update rows and cols after side_len has changed
    @staticmethod
    def update_rc():
        ## In retrospect, keeping row and cols in the Tile was useless,
        ##  and trying to keep it updated with the grid's numbers was a pain
        ##Tile.rows = int(GRID_SCALE*Window.height/Tile.side_len)
        ##Tile.cols = Window.width/Tile.side_len
        pass
    
    ## Changes tile behaviour to draw mode
    @staticmethod
    def to_draw_mode():
        Tile.draw_mode = True

    ## Changes tile behaviour to stamp mode
    @staticmethod
    def to_stamp_mode():
        Tile.draw_mode = False

    def get_bounds(self):
        self.left = self.pos[0]
        self.right = self.pos[0] + self.size[0]
        self.bottom = self.pos[1]
        self.top = self.pos[1] + self.size[1]

    def print_bounds(self):
        print self.left, self.right, self.bottom, self.top

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
    # Status should only be updated if the user is returning (i.e. departed, then came back)
    # Should not continuously shift back and forth because user's finger stayed too long
    def on_touch_move(self, touch):

        ## If coming back to this tile and in draw mode:
        if self.departed and Tile.draw_mode == True and (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            if self.alive == True:
                self.die()
            else:
                self.live()

            self.departed = False

        ## If touch wasn't on this tile, then departed is True
        if (not (self.left <= touch.x <= self.right)) or (not (self.bottom <= touch.y <= self.top)):
            self.departed = True


    def on_touch_down(self, touch):

        self.get_bounds()

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

    def on_touch_up(self, touch):

        self.get_bounds()

        ## If touch up was on this dot, the departed is True
        if (self.left <= touch.x <= self.right) and (self.bottom <= touch.y <= self.top):
            self.departed = True

    def blink(self):
        print "tile id:", self.index
        

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

    def read_tiles_from_file(self, filename):
        tiles = {}
        tile_file = open(filename, "r")
        for line in tile_file:
            tile = line.split(":")
            tiles[tile[0]] = tile[1][:-1] ## Get rid of the newline character at the end
        return tiles

    def build_grid(self):
        self.grid.build_self()

    
    def build(self):
        self.root = Juggler()
        self.grid = self.root.children[0].children[0].children[2].children[0].children[0]
            
        self.build_grid()

        ## Settings panel
        self.settings_cls = SettingsWithSpinner
        #self.use_kivy_settings = False

        ## Make root accessible to all
        global root
        root = self.root
        return self.root

    def build_config(self, config):
        config.setdefaults("logic", {
            "updates_per_second" : 10,
            "req_to_live" : "2, 3",
            "req_to_birth" : "3",
            "rule_to_use" : "Conway",})
        config.setdefaults("aesthetics", {
            "live_tile" : "Green Fade",
            "dead_tile" : "Transparent",
            "tile_size" : 30,
            "background" : "Black",
            "custom_live_tile" : "/",
            "custom_dead_tile" : "/"})


    def build_settings(self, settings):
        settings.add_json_panel("Gameplay", self.config, data=logic)
        settings.add_json_panel("Aesthetics", self.config, data=aesthetics)

    def on_config_change(self, config, section, key, value):
        self.settings_functions.get(key, self.setting_not_found)(config, value)

    def setting_not_found(self, value, *args):
        print "Can't do anything about %s, setting not found!" % str(value)

    def update_updates_per_second(self, config, new_updates_per_second):
        new_updates_per_second = float(new_updates_per_second)
        self.grid.updates_per_second = new_updates_per_second

    def to_single_digits(self, single_digits):
        string = str(single_digits)
        str_numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '0']
        new_numbers = []

        for char in string:
            if char in str_numbers:
                new_numbers.append(int(char))
        return new_numbers

    def update_req_to_live(self, config, new_req_to_live):
        new_numbers = self.to_single_digits(new_req_to_live)
        print "New list of allowable neighbours to stay alive: ", new_numbers
        self.grid.req_to_live = new_numbers
        
        new_live_str = ""
        for char in new_numbers:
            new_live_str += str(char)
            new_live_str += ", "
        new_live_str = new_live_str[:-2]

                
    def update_req_to_birth(self, config, new_req_to_birth):
        new_numbers = self.to_single_digits(new_req_to_birth)
        print "New list of neighbours needed to come to live: ", new_numbers
        self.grid.req_to_birth = new_numbers

    def update_rule_to_use(self, config, new_rule_to_use):
        new_rule_set = self.rules[new_rule_to_use]
        self.update_req_to_live(config, new_rule_set[0])
        self.update_req_to_birth(config, new_rule_set[1])

    def update_live_tile(self, config, new_live_tile):
        Tile.live_source = self.tiles[str(new_live_tile)]
        print "Tile.live_source is updated to: ", Tile.live_source
        for child in self.root.ids["grid"].children:
            if child.alive:
                child.source = Tile.live_source
    
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

    def update_custom_live_tile(self, config, new_live_tile):
        new_path = str(new_live_tile)
        print "New path for live tiles: ", new_path
        Tile.live_source = new_path
        for child in self.root.ids["grid"].children:
            if child.alive:
                child.source = new_path

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


## Just a screen
class StampScreen(Screen):
    def __init__(self, **kwargs):
        super(StampScreen, self).__init__(**kwargs)
        self.name = "stamp_screen"
        self.tile_side_len = None

    def on_pre_enter(self):
        self.children[0].list_stamps()
        self.orig_tile_side_len = Tile.side_len
        self.orig_tile_mode = Tile.draw_mode
        Tile.to_draw_mode()

    def on_pre_leave(self):
        Tile.side_len = self.orig_tile_side_len
        Tile.update_rc()
        if self.orig_tile_mode == True:
            Tile.to_draw_mode()
        else:
            Tile.to_stamp_mode()
        self.children[0].children[2].stop()


class ViewStampButton(ListItemButton):
    def __init__(self, **kwargs):
        super(ViewStampButton, self).__init__(**kwargs)
        self.font_size = 20

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
        print self.selection
        Tile.to_stamp_mode()

    
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
        ## Also hides the fact that the UI still displays the to-be-deleted stamp, lol
        root.current = "game_screen"
        Tile.to_draw_mode()


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

    def update_rct(self):
        self.rows = int(0.4*Window.height/self.side_len) ## 0.4 is scale of the demo grid
        self.cols = Window.width/self.side_len
        self.tiles = self.rows*self.cols

    def start_demo(self):
        ## Stop previous animation (if any)
        self.stop()
        ## Resize tiles so grid matches pattern
        print "Cells are stretched this way. Reconfigure and use paste_stamp()"
        self.stamp_rows = len(self.stamp)
        self.stamp_cols = len(self.stamp[0])
        self.side_len = min((0.4*Window.height)/(1.3*self.stamp_rows),
                            (Window.width)/(1.3*self.stamp_cols))
        print "New side length from preview: ", self.side_len
        self.update_tile_size(str(int(self.side_len)))
        ## Paste pattern into middle
        print "Pasting stamp. self.tiles/2: ", self.tiles/2
        self.paste_stamp(self.tiles/2, self.stamp)

        ## Start animation
        ##self.toggle()
        


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


class StampViewer(GridLayout):
    ## Will be called by .kv at app start because it's in the widget tree
    def __init__(self, **kwargs):
        kwargs['cols'] = 1 # One column of buttons, has to come before super()
        super(StampViewer, self).__init__(**kwargs)
        self.orientation = "vertical"
        
        ## Here for testing only, replace with real dictionary
        ## from the read_stamps_from_file() method
        self.stamp_dict = {}
        self.already_set_up = False

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

    def print_binary_matrix(self, matrix):
        for row in matrix:
            for col in row:
                if col:
                    print "1",
                else:
                    print "0",
            print


class NameBox(TextInput):
    def __init__(self, **kwargs):
        super(NameBox, self).__init__(**kwargs)
        self.font_size = 150
        self.size_hint_y = 0.3
        self.text = "New Stamp"
        

class SaveNameButton(Button):
    def __init__(self, **kwargs):
        super(SaveNameButton, self).__init__(**kwargs)
        self.font_size = 20
        self.size_hint_y = 0.7
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
        print "Implement save to file"
        self.stamp_name = root.ids["save_stamp_screen"].children[0].children[1].text
        self.stamp_grid = root.ids["grid"].stamp
        self.append_stamp_to_file("gameoflifestamps.txt", self.stamp_name, self.stamp_grid)
        root.current = "game_screen"


## Just a screen
class SaveStampScreen(Screen):
    def __init__(self, **kwargs):
        super(SaveStampScreen, self).__init__(**kwargs)
        self.name = "save_stamp_screen"
        self.already_set_up = False
        
    def on_pre_enter(self):
        if not self.already_set_up:
           nameSaver = GridLayout(size_hint=(1,1), rows=2, cols=1)
           nameSaver.add_widget(NameBox())
           nameSaver.add_widget(SaveNameButton())
           self.add_widget(nameSaver)
           self.already_set_up = True
    

class AboutMeScreen(Screen):
    def __init__(self, **kwargs):
        super(AboutMeScreen, self).__init__(**kwargs)
        self.name = "about_me_screen"


if __name__ == "__main__":
    try:
        os.remove("gameoflife.ini")
    except:
        pass
    GameOfLifeApp().run()
