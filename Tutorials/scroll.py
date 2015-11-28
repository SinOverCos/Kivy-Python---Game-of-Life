from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from kivy.properties import StringProperty

from kivy.base import runTouchApp
from kivy.lang import Builder

Builder.load_string('''
<ScrollableLabel>:
    text: str('some really really long string ' * 100)
    BoxLayout:
        orientation: 'vertical'
        size_hint: 1, 2
        Label:
            text: root.text
            font_size: 50
            text_size: self.width, None # limit width (text wraps around if it's too long)
            size_hint_y: None # no default height
            height: self.texture_size[1] # height follows text's wrapped height
''')

class ScrollableLabel(ScrollView):
    text = StringProperty("")

runTouchApp(ScrollableLabel())
