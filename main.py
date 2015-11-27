##from kivy.app import App
##
### autoclass takes a Java class and produces the same class in Python
##from jnius import autoclass
##
### PythonActivity is the android activity used when kivy is run as an apk
##PythonActivity = autoclass('org.renpy.android.PythonActivity')
##activity = PythonActivity.mActivity
##
##Context = autoclass('android.content.Context')
##vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
##
##import android
##
##class AndroidApp(App):
##    def build(self):
##        vibrator.vibrate(10000)
##
##AndroidApp().run()


# Below is using plyer

from kivy.app import App

from plyer.notification import notify

class AndroidApp(App):
    def build(self):
        vibrator.vibrate(10000)
        notify('Some title', 'Some message text')

AndroidApp().run()
