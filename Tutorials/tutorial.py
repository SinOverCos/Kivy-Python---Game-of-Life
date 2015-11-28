## ATTENTION TO FILE NAMES!!!
## Must be named main.py - when staring android app, main.py is called
## Must be named tutorial.py and tutorial.kv in lowercase for the files to connect

import random

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.graphics.vertex_instructions import (Rectangle, Ellipse, Line)
from kivy.graphics.context_instructions import Color

## This inherits from BoxLayout and is edited in main.kv
## In the .kv file, everything on the right is Python
class ScatterTextWidget(BoxLayout):

    text_colour = ListProperty([1, 0, 0 ,1])

    def __init__(self, **kwargs):
        super(ScatterTextWidget, self).__init__(**kwargs)
##        with self.canvas.before: #.before means draw this first (and the words second, so shapes are below)
##            Color(0, 1, 0, 1)
##            Rectangle(pos=(0, 100), size=(300, 100))
##            Ellipse(pos=(0, 400), size=(300, 100))
##            Line(points=[0, 0, 500, 600, 400, 300], close=True, width=3)    
    def change_label_colour(self, *args):
        colour = [random.random() for i in xrange(3)] + [1]
        self.text_colour = colour
        
##        # Kivy widgets have dictionary of labels
##        # Below is manually setting all colours
##        label = self.ids['my_label']
##        label1 = self.ids['label1']
##        label2 = self.ids['label2']
##        label.color = colour
##        label1.color = colour
##        label2.color = colour
        

## Whatever build() returns becomes the top-level widget
## Kivy will resize it to fit the window and all other widgets are
## sub-widget of that one

class TutorialApp(App):
    def build(self):
        return ScatterTextWidget()


    
        ## Commented out code is replaced by main.kv's use
##        b = BoxLayout(orientation='vertical')
##        t = TextInput(font_size=150,
##                      size_hint_y=None, # If has size_hint (default 1) box layout sizes children according to the hint
##                      height=200,
##                      text='text input default') 
##        
##        f = FloatLayout()
##        s = Scatter()
##        l = Label(text="label default", font_size=150)
##
##        # All kivy widget have the bind method
##        t.bind(text=l.setter('text')) # i.e. whenever the text changes, some function, l.setter('text'), which returns a function whose purpose is to update the text, is called
##        
##        f.add_widget(s)
##        s.add_widget(l)
##
##        # Order of using add_widget determines the order children appear in
##        b.add_widget(t)
##        b.add_widget(f)
##        
##        return b


def some_function(*args):
    print 'text changed'

if __name__ == "__main__":
    TutorialApp().run()
