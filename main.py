import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.clock import Clock

# Sets the window's background color for a better look
Window.clearcolor = (0.95, 0.95, 0.95, 1)


class MyLayout(BoxLayout):
    """
    Main application layout that contains the word display and answer buttons.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Sets the layout orientation to vertical
        self.orientation = 'vertical'
        self.spacing = 30  # Spacing between widgets
        self.padding = 50  # Padding around the content

        # Words and their translations
        self.words = {
            '52E': '4x4 BB',
            '56E': '6x6 BB',
            '56J': '6x6 BB',
            '58J': '6x6 BB',
            '96E': '8x8 BB',
            '4PE': '8x8 BL',
        }
        self.word_keys = list(self.words.keys())
        self.word_sequence = []
        self.word_index = -1
        self.current_word = ''

        # Dictionaries to store correct and incorrect answers
        self.correct_words = {}
        self.incorrect_words = {}

        # Variable to store the user's composed answer (without spaces)
        self.composed_answer = ''
        # List of widgets to display individual characters of the answer
        self.answer_widgets = []

        # Main container for the word and buttons
        self.main_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.7, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=20,
            padding=20,
        )
        self.add_widget(self.main_container)

        # Drawing the container background
        with self.main_container.canvas.before:
            Color(0.2, 0.5, 0.8, 1)  # New blue color for the main frame
            self.rect = RoundedRectangle(pos=self.main_container.pos, size=self.main_container.size, radius=[20])

        # Label to display the word
        self.word_label = Label(
            text='',
            font_size='60sp',
            bold=True,
            color=(1, 1, 1, 1),  # White text for better contrast on blue background
            size_hint_y=0.2,
            halign='center',
            valign='middle'
        )
        self.main_container.add_widget(self.word_label)

        # Container for the answer fields (new frames)
        self.answer_display_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.2,
            spacing=10,
            pos_hint={'center_x': 0.5}  # Centering the container
        )
        self.main_container.add_widget(self.answer_display_container)

        # Container for button rows
        self.button_rows_container = BoxLayout(
            orientation='vertical',
            size_hint_y=0.4,
            spacing=10,
        )
        self.main_container.add_widget(self.button_rows_container)

        # First row of buttons (numbers)
        self.row1 = BoxLayout(orientation='horizontal', spacing=10)
        numbers = ['2', '4', '6', '8', '10']
        for num in numbers:
            btn = Button(text=num, font_size='30sp', size_hint=(1, 1), background_color=(0.3, 0.7, 1.0, 1),
                         color=(1, 1, 1, 1))
            btn.bind(on_release=self.compose_answer)
            self.row1.add_widget(btn)
        self.button_rows_container.add_widget(self.row1)

        # Second row of buttons (letters)
        self.row2 = BoxLayout(orientation='horizontal', spacing=10)
        letters = ['x', 'B', 'L']
        for letter in letters:
            btn = Button(text=letter, font_size='30sp', size_hint=(1, 1), background_color=(0.3, 0.7, 1.0, 1),
                         color=(1, 1, 1, 1))
            btn.bind(on_release=self.compose_answer)
            self.row2.add_widget(btn)
        self.button_rows_container.add_widget(self.row2)

        # Container for control buttons
        self.control_buttons_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.2,
            spacing=20,
        )
        self.main_container.add_widget(self.control_buttons_container)

        # "Backspace" button
        self.backspace_button = Button(
            text='<-',
            font_size='30sp',
            background_color=(0.4, 0.2, 0.1, 1),  # Dark brown for the backspace button
            color=(1, 1, 1, 1)
        )
        self.backspace_button.bind(on_release=self.backspace_answer)
        self.control_buttons_container.add_widget(self.backspace_button)

        # "Check" button
        self.check_button = Button(
            text='OK',
            font_size='30sp',
            background_color=(0.2, 0.4, 0.2, 1),  # Dark green for the check button
            color=(1, 1, 1, 1)
        )
        self.check_button.bind(on_release=self.check_answer)
        self.control_buttons_container.add_widget(self.check_button)

        # Feedback label
        self.feedback_label = Label(
            text='',
            font_size='30sp',
            color=(1, 1, 1, 1),  # White text for feedback
            size_hint_y=0.2,
            halign='center',
            valign='middle'
        )
        self.main_container.add_widget(self.feedback_label)

        # Updates the graphics when the container size changes
        self.main_container.bind(pos=self.update_graphics, size=self.update_graphics)

        # Starts a new word sequence
        self.setup_new_sequence()

    def update_graphics(self, instance, value):
        """Updates the position and size of the background graphics."""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def setup_new_sequence(self):
        """
        Creates a new, random sequence of all words.
        """
        self.word_keys = list(self.words.keys())
        random.shuffle(self.word_keys)
        self.word_sequence = self.word_keys
        self.word_index = -1
        self.next_word()

    def next_word(self, *args):
        """
        Displays the next word in the sequence.
        """
        self.word_index += 1
        if self.word_index >= len(self.word_sequence):
            self.show_end_message()
            return

        self.current_word = self.word_sequence[self.word_index]
        self.word_label.text = self.current_word
        self.composed_answer = ''

        # Clears and creates a new layout for the answer fields.
        self.answer_display_container.clear_widgets()
        self.answer_widgets = []

        # Create a container for the first three fields.
        first_group = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=None, width='170dp')

        # Add the first three fields.
        for i in range(3):
            answer_box = BoxLayout(size_hint=(None, None), size=('50dp', '50dp'))
            answer_label = Label(text='', font_size='30sp', bold=True, halign='center', valign='middle',
                                 color=(0, 0, 0, 1))
            answer_box.add_widget(answer_label)
            with answer_box.canvas.before:
                color_ref = Color(0.85, 0.85, 0.85, 1)
                rect_ref = RoundedRectangle(pos=answer_box.pos, size=answer_box.size, radius=[10])
            answer_box.bind(pos=lambda instance, value: setattr(rect_ref, 'pos', instance.pos))
            answer_box.bind(size=lambda instance, value: setattr(rect_ref, 'size', instance.size))
            self.answer_widgets.append({'label': answer_label, 'color': color_ref, 'rect': rect_ref})
            first_group.add_widget(answer_box)

        # Create a container for the last two fields.
        second_group = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=None, width='110dp')

        # Add the last two fields.
        for i in range(2):
            answer_box = BoxLayout(size_hint=(None, None), size=('50dp', '50dp'))
            answer_label = Label(text='', font_size='30sp', bold=True, halign='center', valign='middle',
                                 color=(0, 0, 0, 1))
            answer_box.add_widget(answer_label)
            with answer_box.canvas.before:
                color_ref = Color(0.85, 0.85, 0.85, 1)
                rect_ref = RoundedRectangle(pos=answer_box.pos, size=answer_box.size, radius=[10])
            answer_box.bind(pos=lambda instance, value: setattr(rect_ref, 'pos', instance.pos))
            answer_box.bind(size=lambda instance, value: setattr(rect_ref, 'size', instance.size))
            self.answer_widgets.append({'label': answer_label, 'color': color_ref, 'rect': rect_ref})
            second_group.add_widget(answer_box)

        # Add groups to the main answer container with a spacer between them
        self.answer_display_container.add_widget(BoxLayout())  # Flexible spacer
        self.answer_display_container.add_widget(first_group)
        self.answer_display_container.add_widget(BoxLayout(size_hint_x=None, width='20dp'))  # Fixed spacer
        self.answer_display_container.add_widget(second_group)
        self.answer_display_container.add_widget(BoxLayout())  # Flexible spacer

        self.feedback_label.text = ''

        # Enables the buttons
        self.check_button.disabled = False
        self.backspace_button.disabled = False
        self.set_buttons_state(True)

    def compose_answer(self, instance):
        """
        Adds text from the button to the composed answer and updates the answer field.
        """
        if self.check_button.disabled:
            return

        filled_count = len(self.composed_answer)
        if filled_count < len(self.answer_widgets):
            self.composed_answer += instance.text
            widget_data = self.answer_widgets[filled_count]
            widget_data['label'].text = instance.text

            # Change the color of the rectangle to white
            widget_data['color'].rgb = (1, 1, 1)

    def backspace_answer(self, instance):
        """
        Removes the last typed character from the answer and restores the placeholder field.
        """
        if len(self.composed_answer) > 0:
            last_filled_index = len(self.composed_answer) - 1
            widget_data = self.answer_widgets[last_filled_index]
            self.composed_answer = self.composed_answer[:-1]
            widget_data['label'].text = ''

            # Change the color of the rectangle back to gray
            widget_data['color'].rgb = (0.85, 0.85, 0.85)

    def check_answer(self, instance):
        """
        Checks if the composed answer is correct and displays feedback.
        """
        user_answer = self.composed_answer.strip()
        correct_answer = self.words[self.current_word].replace(' ', '')

        # Disables the buttons
        self.check_button.disabled = True
        self.backspace_button.disabled = True
        self.set_buttons_state(False)

        if user_answer == correct_answer:
            self.feedback_label.text = "Poprawnie!"
            self.feedback_label.color = (0, 0.7, 0, 1)  # Green color
            self.correct_words[self.current_word] = self.words[self.current_word]
        else:
            self.feedback_label.text = f"Źle. Poprawna odpowiedź to: {self.words[self.current_word]}"
            self.feedback_label.color = (0.9, 0, 0, 1)  # Red color
            self.incorrect_words[self.current_word] = self.words[self.current_word]

        # Schedules the display of the next word after a short delay
        Clock.schedule_once(self.next_word, 2)

    def set_buttons_state(self, state):
        """Sets the state (enabled/disabled) for all answer composition buttons."""
        for child in self.row1.children:
            child.disabled = not state
        for child in self.row2.children:
            child.disabled = not state

    def show_end_message(self, *args):
        """
        Displays the final message and a summary of results.
        """
        # Hides the main container
        self.clear_widgets()

        # Calculates the results
        total_questions = len(self.correct_words) + len(self.incorrect_words)
        correct_count = len(self.correct_words)

        # Calculates the percentage if there were any questions
        if total_questions > 0:
            percentage = (correct_count / total_questions) * 100
        else:
            percentage = 0

        # Prepares the summary text
        summary_text = "Koniec programu!\n\n"
        summary_text += f"Twój wynik: {correct_count} / {total_questions} poprawnych odpowiedzi.\n"
        summary_text += f"Udział procentowy: {percentage:.2f}%\n\n"

        if self.incorrect_words:
            summary_text += "Słowa, które wymagają powtórki:\n"
            for pl, en in self.incorrect_words.items():
                summary_text += f"    - {pl}: {en}\n"
        else:
            summary_text += "Gratulacje! Wszystkie odpowiedzi były poprawne."

        # Adds the label with the final message
        end_label = Label(
            text=summary_text,
            font_size='30sp',
            color=(0, 0, 0, 1),
            size_hint=(1, 1),
            halign='center',
            valign='middle'
        )
        self.add_widget(end_label)

        # Adds the exit button
        exit_button = Button(
            text='Zakończ',
            font_size='30sp',
            background_color=(0.5, 0.5, 0.5, 1),
            size_hint=(0.3, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.1}
        )
        exit_button.bind(on_release=lambda x: App.get_running_app().stop())
        self.add_widget(exit_button)


class SampleApp(App):
    """
    Main application class.
    """

    def build(self):
        """
        The build method returns the main application widget.
        """
        return MyLayout()


if __name__ == "__main__":
    SampleApp().run()
