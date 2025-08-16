
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class MyLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.label = Label(text='Hello World')
        self.add_widget(self.label)

        self.button = Button(text='Kliknij mnie')
        self.button.bind(on_press=self.on_button_click)
        self.add_widget(self.button)

    def on_button_click(self, instance):
        self.label.text = 'Przycisk został kliknięty!'

class SampleApp(App):
    def build(self):
        return MyLayout()

if __name__ == "__main__":
    SampleApp().run()
