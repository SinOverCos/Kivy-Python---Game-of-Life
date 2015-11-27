from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

import time
import random

class FirstScreen(Screen):
    pass

class SecondScreen(Screen):
    pass

class ColourScreen(Screen):
    colour = ListProperty([1, 0, 0, 1])

class MyScreenManager(ScreenManager):
    def new_colour_screen(self):
        name = str(time.time())
        # Colour screen inherits from Screen
        # We are dynamically adding one instead of setting it to exist at the start by putting it in the Builder
        s = ColourScreen(name=name,
                         colour = [random.random() for _ in range(3)] + [1])
        self.add_widget(s)
        self.current = name
        # Can set the transition to something different from here
        # Other option is to do it under MyScreenManager in kivy language
        #self.transition = FadeTransition()

# No angle brace for the root widget or else there will be no window created
# widgets with angle braces are just definitions that you can add to the root widget
# Screens can only have one child
# app.root.current: app = running app, root = root widget of running app
# and current = current screen (the one that is displayed)
# * is args and ** is keyword args (kwargs)
# * is also the flatten operator (flattens a list)
# see http://stackoverflow.com/questions/5239856/foggy-on-asterisk-in-python
root_widget = Builder.load_string('''
#:import random random.random
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
MyScreenManager:
    transition: FadeTransition()
    FirstScreen:
    SecondScreen:
    
<FirstScreen>:
    name: 'first'
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'first screen'
            font_size: 30
        Image:
            source: 'colours.png'
            allow_stretch: True
            keep_ratio: False
        BoxLayout:
            Button:
                text: 'goto second screen'
                font_size: 30
                on_release: app.root.current = 'second'
            Button:
                text: 'get random colour screen'
                font_size: 30
                on_release: app.root.new_colour_screen()

<SecondScreen>:
    name: 'second'
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'second screen!!!'
            font_size: 30
        Image:
            source: 'colours.png'
            allow_stretch: True
            keep_ratio: False
        BoxLayout:
            Button:
                text: 'goto first screen'
                font_size: 30
                on_release: app.root.current = 'first'
            Button:
                text: 'get random colour screen'
                font_size: 30
                on_release: app.root.new_colour_screen()

<ColourScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            
            font_size: 30
        Widget:
            canvas:
                Color:
                    rgba: root.colour
                Ellipse:
                    pos: self.pos
                    size: self.size
        BoxLayout:
            Button:
                text: 'goto first screen'
                font_size: 30
                on_release: app.root.current = 'first'
            Button:
                text: 'get random colour screen'
                font_size: 30
                on_release: app.root.new_colour_screen()
''')

class ScreenManagerApp(App):
    def build(self):
        # return value of builder is stored in root_widget instead of being
        # evaluated so root_widget needs to be returned when ScreenManagerApp is run
        return root_widget

if __name__ == "__main__":
    ScreenManagerApp().run()
