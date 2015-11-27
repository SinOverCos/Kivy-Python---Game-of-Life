from kivy.app import App
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import SettingsWithSidebar

from settingsjson import settings_json
from settingsjson import settings_json2

Builder.load_string('''
<Interface>:
    orientation: 'vertical'
    Button:
        text: 'open the settings'
        font_size: 150
        on_release: app.open_settings() # app refers to currently running app
''')

class Interface(BoxLayout):
    pass

class SettingsApp(App):
    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False # kivy settings panel won't show up
        # pull out all settings:
        # self.config.items('example')
        # can pull out individual settings like this but it is read-only
        # changing this doesn't change the actual setting
        #setting = self.config.get('example', 'boolexample')
        return Interface()

    def build_config(self, config):
        config.setdefaults('example', {
            'boolexample': True,
            'numericexample': 10,
            'optionsexample': 'option2',
            'stringexample': 'some_string',
            'pathexample': '/'})
        config.setdefaults('my example 2', {'myboolexample': True})
    

    # self.config is the default config parser
    # 
    def build_settings(self, settings):
        settings.add_json_panel('Panel Name', self.config, data=settings_json)
        settings.add_json_panel('My New Pan', self.config, data=settings_json2)

    # automatically called on config change
    def on_config_change(self, config, section, key, value):
        print "CONFIG: ", config, "SECTION: ", section, "KEY: ", key, "VALUE: ", value

SettingsApp().run()
