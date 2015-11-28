from kivy.uix.label import Label
from kivy.core.image import Image

from kivy.lang import Builder
from kivy.base import runTouchApp


Builder.load_string('''
<RootWidget>:
    text: 'THE BACKGROUND'
    font_size: 150
    Image:
        source: 'colours.png' # same directory as layout.py
        allow_stretch: True
        keep_ratio: False
    Image:
        source: 'colours.png'
        allow_stretch: True
        keep_ratio: False
    Image:
        source: 'colours.png'
        allow_stretch: True
        keep_ratio: False
''')


class RootWidget(Label):
    def do_layout(self, *args):
        self.add_widget(Image('Transparent.png'))
        number_of_children = len(self.children)
        width = self.width
        width_per_child = width/number_of_children
        positions = range(0, width, width_per_child)
        for position, child in zip(positions, self.children):
            child.height = self.height
            child.x = self.x + position
            child.y = self.y
            child.width = width_per_child

    # on_blank means this function will be called whenever blank is changed
    def on_size(self, *args):
        self.do_layout()

    def on_pos(self, *args):
        self.do_layout()

    def add_widget(self, widget):
        super(RootWidget, self).add_widget(widget)
        self.do_layout

    def remove_widget(self, widget):
        super(RootWidget, self).remove_widget(widget)
        self.do_layout()

runTouchApp(RootWidget())
