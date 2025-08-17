import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, PushMatrix, PopMatrix, Scale, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.clock import Clock

# Set the window background color for a better look
Window.clearcolor = (0.95, 0.95, 0.95, 1)


class MyLayout(BoxLayout):
    """
    Main application layout that contains the flashcard widgets.
    """
    # Use ObjectProperty to be able to animate the widget within the class
    card_container = ObjectProperty(None)

    # Variables for dynamic card rotation
    rotation_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set the layout orientation to vertical
        self.orientation = 'vertical'
        self.spacing = 30  # Spacing between widgets
        self.padding = 50  # Padding around the content

        # Variable to track which side is visible
        self.is_front_side = True

        # Variables to detect the gesture
        self.touch_start_x = 0
        self.touch_move_x = 0
        self.is_dragging = False

        # 20 words and their translations
        self.words = {
            'dom': 'house',
            'kot': 'cat',
            'pies': 'dog',
            'książka': 'book',
            'drzewo': 'tree',
            'samochód': 'car',
            'woda': 'water',
            'słońce': 'sun',
            'księżyc': 'moon',
            'gwiazda': 'star',
            'jabłko': 'apple',
            'banan': 'banana',
            'stół': 'table',
            'krzesło': 'chair',
            'okno': 'window',
            'drzwi': 'door',
            'telefon': 'phone',
            'komputer': 'computer',
            'szkoła': 'school',
            'praca': 'work',
        }
        self.word_keys = list(self.words.keys())
        self.card_sequence = []  # List to store the card sequence
        self.card_index = -1  # Index of the current card in the sequence
        self.current_word = ''

        # Dictionaries to store correct and incorrect answers
        self.correct_words = {}
        self.incorrect_words = {}

        # Create a container that will look like a physical card
        self.card_container = FloatLayout(
            size_hint=(0.7, 0.8),  # Card proportions
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Centering
        )
        self.add_widget(self.card_container)

        # Draw the card background (rounded rectangle) and transformations
        with self.card_container.canvas.before:
            PushMatrix()
            # Use Scale for card rotation based on rotation_angle
            self.rotate = Scale(1, 1, 1)
            self.rotate.origin = self.card_container.center

            # Shadow under the card
            Color(0.8, 0.8, 0.8, 0.5)
            self.shadow = RoundedRectangle(pos=self.card_container.pos, size=self.card_container.size, radius=[15])

            Color(1, 1, 1, 1)  # White background color
            self.rect = RoundedRectangle(pos=self.card_container.pos, size=self.card_container.size, radius=[20])

            # Draw a blue pattern around the edges
            Color(0, 0.5, 1, 1)  # Blue pattern color
            self.border_lines = [
                Line(width=2, rectangle=(self.card_container.pos[0] + 5, self.card_container.pos[1] + 5,
                                         self.card_container.size[0] - 10, self.card_container.size[1] - 10)),
                Line(width=2, rectangle=(self.card_container.pos[0] + 10, self.card_container.pos[1] + 10,
                                         self.card_container.size[0] - 20, self.card_container.size[1] - 20)),
            ]

        # Widget for the front (face) of the card
        self.word_label = Label(
            text='',  # Set empty text at the beginning
            font_size='60sp',  # Increased font size
            bold=True,
            color=(0, 0, 0, 1),  # Black text color
            size_hint=(1, 1),  # Label takes up the entire space in the container
            text_size=self.card_container.size,
            halign='center',  # Horizontal text alignment
            valign='middle'  # Vertical text alignment
        )
        self.card_container.add_widget(self.word_label)

        # Add a separate Push/Pop matrix and Scale for the back of the card to prevent mirroring
        with self.word_label.canvas.before:
            self.word_text_scale = Scale(1, 1, 1)

        # Widget for the back (reverse) of the card, initially hidden
        self.translation_label = Label(
            text='',  # Set empty text at the beginning
            font_size='60sp',  # Increased font size
            bold=True,
            color=(0, 0, 0, 1),  # Black text color
            size_hint=(1, 1),  # Label takes up the entire space in the container
            text_size=self.card_container.size,
            halign='center',  # Horizontal text alignment
            valign='middle',  # Vertical text alignment
            opacity=0  # Label is invisible
        )
        self.card_container.add_widget(self.translation_label)

        with self.translation_label.canvas.before:
            self.translation_text_scale = Scale(1, 1, 1)

        # Draw the label frame (blue)
        with self.card_container.canvas.after:
            self.label_border = Line(width=2,
                                     rectangle=(self.word_label.pos[0], self.word_label.pos[1], self.word_label.size[0],
                                                self.word_label.size[1]))
            PopMatrix()

        # Add a new BoxLayout for the buttons
        self.button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.5, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0},
            spacing=30,
            opacity=0,  # Initially hidden
        )
        self.add_widget(self.button_layout)

        # "Good" button (thumbs up)
        self.good_button = Button(
            text='OK',
            font_size='40sp',
            background_color=(0, 0.7, 0, 1),  # Green
            size_hint=(0.45, 1),
            disabled=True  # Buttons are disabled by default
        )
        self.good_button.bind(on_release=lambda instance: self.on_button_press(instance, 'correct'))
        self.button_layout.add_widget(self.good_button)

        # "Bad" button (thumbs down)
        self.bad_button = Button(
            text='NOK',
            font_size='40sp',
            background_color=(0.9, 0, 0, 1),  # Red
            size_hint=(0.45, 1),
            disabled=True  # Buttons are disabled by default
        )
        self.bad_button.bind(on_release=lambda instance: self.on_button_press(instance, 'incorrect'))
        self.button_layout.add_widget(self.bad_button)

        # Start the first card sequence
        self.setup_new_sequence()

        # Change touch handling to detect swipe gestures
        self.card_container.bind(on_touch_down=self.on_touch_down_card, on_touch_move=self.on_touch_move_card,
                                 on_touch_up=self.on_touch_up_card)
        self.bind(rotation_angle=self.update_rotation)

        # Update the size and position of all graphic elements
        self.card_container.bind(pos=self.update_graphics, size=self.update_graphics)

    def on_touch_down_card(self, instance, touch):
        """
        Saves the initial touch position if it's on the card.
        """
        if instance.collide_point(*touch.pos):
            self.touch_start_x = touch.x
            self.is_dragging = True
            return True
        return False

    def on_touch_move_card(self, instance, touch):
        """
        Dynamically rotates the card while the finger is being moved.
        """
        if self.is_dragging and instance.collide_point(*touch.pos):
            # Calculate the swipe distance
            swipe_distance = touch.x - self.touch_start_x

            # Map the distance to a rotation angle
            # The card rotates 180 degrees for a distance equal to the card's width
            max_rotation_distance = self.card_container.width * 1.5
            rotation = (swipe_distance / max_rotation_distance) * 180

            # Limit the rotation to 0-180 degrees
            self.rotation_angle = max(0, min(180, rotation))

            # Change text visibility depending on the rotation
            if self.rotation_angle > 90:
                self.word_label.opacity = 0
                self.translation_label.opacity = 1
                # Show buttons after flipping
                anim = Animation(opacity=1, duration=0.2)
                anim.bind(on_complete=self.enable_buttons)
                anim.start(self.button_layout)
            else:
                self.word_label.opacity = 1
                self.translation_label.opacity = 0
                anim = Animation(opacity=0, duration=0.2)
                anim.bind(on_complete=self.disable_buttons)
                anim.start(self.button_layout)

            return True
        return False

    def on_touch_up_card(self, instance, touch):
        """
        Finalizes card rotation or initiates rotation on click.
        """
        if self.is_dragging:
            self.is_dragging = False

            swipe_distance = touch.x - self.touch_start_x
            swipe_threshold = 20  # Threshold to detect a click instead of a gesture

            if abs(swipe_distance) < swipe_threshold:
                # This was a click, not a swipe, so animate the rotation
                if self.is_front_side:
                    Animation(rotation_angle=180, duration=0.25).start(self)
                else:
                    Animation(rotation_angle=0, duration=0.25).start(self)
                self.is_front_side = not self.is_front_side
            else:
                # A swipe gesture, finalize the rotation
                if self.rotation_angle >= 90:
                    Animation(rotation_angle=180, duration=0.25).start(self)
                    self.is_front_side = False
                else:
                    Animation(rotation_angle=0, duration=0.25).start(self)
                    self.is_front_side = True
            return True
        return False

    def update_rotation(self, instance, value):
        """
        Updates the scale based on the rotation_angle to create a 3D rotation effect.
        """
        # Calculate the scale value for the X-axis based on the angle.
        # From 1 (front) to -1 (back), passing through 0.
        scale_x_value = ((180 - value) / 90) - 1
        self.rotate.x = scale_x_value

        # Add a Scale to prevent the mirror effect on the text.
        if value > 90:
            self.word_label.opacity = 0
            self.translation_label.opacity = 1
            # "Un-mirror" the text on the back of the card
            self.translation_text_scale.x = -1
            # Show buttons after flipping
            anim = Animation(opacity=1, duration=0.2)
            anim.bind(on_complete=self.enable_buttons)
            anim.start(self.button_layout)
        else:
            self.word_label.opacity = 1
            self.translation_label.opacity = 0
            self.translation_text_scale.x = 1
            # Hide buttons when the card returns to the front
            anim = Animation(opacity=0, duration=0.2)
            anim.bind(on_complete=self.disable_buttons)
            anim.start(self.button_layout)

    def setup_new_sequence(self):
        """
        Creates a new, random sequence of 5 words.
        """
        # Shuffle the word keys and select the first 5
        random.shuffle(self.word_keys)
        self.card_sequence = self.word_keys[:5]
        self.card_index = 0
        self.next_card()

    def next_card(self):
        """
        Displays the next card in the sequence.
        """
        if self.card_index >= len(self.card_sequence):
            # If the sequence is finished, end the program
            self.show_end_message()
            return

        self.current_word = self.card_sequence[self.card_index]
        self.word_label.text = self.current_word
        self.translation_label.text = self.words[self.current_word]

        # Reset visibility and scale to show the new card
        self.is_front_side = True
        self.word_label.opacity = 1
        self.translation_label.opacity = 0
        self.rotate.x = 1
        self.translation_text_scale.x = 1  # Reset text scale
        self.rotation_angle = 0  # Reset rotation angle for the new card

        # Hide the buttons when a new card appears and disable them
        anim = Animation(opacity=0, duration=0.2)
        anim.bind(on_complete=self.disable_buttons)
        anim.start(self.button_layout)

    def disable_buttons(self, animation, widget):
        """Disables both buttons after the fade-out animation finishes."""
        self.good_button.disabled = True
        self.bad_button.disabled = True

    def enable_buttons(self, animation, widget):
        """Enables both buttons after the fade-in animation finishes."""
        self.good_button.disabled = False
        self.bad_button.disabled = False

    def on_button_press(self, instance, result):
        """
        Handles the "OK" and "NOK" button clicks, disables both,
        and saves the result.
        """
        # Disable both buttons to prevent double-clicking
        self.good_button.disabled = True
        self.bad_button.disabled = True

        # Save the result
        if result == 'correct':
            self.correct_words[self.current_word] = self.words[self.current_word]
        else:
            self.incorrect_words[self.current_word] = self.words[self.current_word]

        # Start the transition animation
        self.animate_next_card_transition()

    def animate_next_card_transition(self):
        """
        Cancels all previous animations and starts the transition animation
        to the next card.
        """
        # Cancel any other animations on the card
        Animation.cancel_all(self.card_container)

        # Slide out animation to the left
        anim_out = Animation(pos_hint={'center_x': -0.5}, duration=0.5, transition='out_quad')
        anim_out.bind(on_complete=self.load_and_slide_in_next_card)
        anim_out.start(self.card_container)

    def load_and_slide_in_next_card(self, animation, widget):
        """
        This method is called after the exit animation is complete.
        It loads a new card and starts the entry animation.
        """
        # Load the next card's data first
        self.card_index += 1
        self.next_card()

        # Reset the card's position off-screen to the right
        self.card_container.pos_hint = {'center_x': 1.5, 'center_y': 0.5}

        # Use Clock.schedule_once to ensure the UI updates before starting the next animation.
        # This prevents the card from "jumping" or starting in the wrong place.
        Clock.schedule_once(self.start_slide_in_animation, 0)

    def start_slide_in_animation(self, dt):
        """
        Starts the slide-in animation for the new card.
        """
        # Slide in animation from the right
        anim_in = Animation(pos_hint={'center_x': 0.5}, duration=0.5, transition='in_quad')
        anim_in.start(self.card_container)

    def update_graphics(self, instance, value):
        # The method updates the position and size of all graphic elements.
        # This unified approach prevents timing issues.

        # Update positions and sizes of the main card elements
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        self.shadow.pos = (instance.pos[0] + 5, instance.pos[1] - 5)
        self.shadow.size = instance.size

        # Update the position of the labels to always fill the container
        self.word_label.pos = instance.pos
        self.word_label.size = instance.size
        self.translation_label.pos = instance.pos
        self.translation_label.size = instance.size

        # Update origins for transformations based on the new center of the card and labels
        self.rotate.origin = instance.center
        self.word_text_scale.origin = self.word_label.center
        self.translation_text_scale.origin = self.translation_label.center

        # Update the position of the border lines
        self.border_lines[0].rectangle = (self.card_container.pos[0] + 5, self.card_container.pos[1] + 5,
                                          self.card_container.size[0] - 10, self.card_container.size[1] - 10)
        self.border_lines[1].rectangle = (self.card_container.pos[0] + 10, self.card_container.pos[1] + 10,
                                          self.card_container.size[0] - 20, self.card_container.size[1] - 20)

        # Update the label frame position
        if self.is_front_side:
            self.label_border.rectangle = (self.word_label.pos[0], self.word_label.pos[1], self.word_label.size[0],
                                           self.word_label.size[1])
        else:
            self.label_border.rectangle = (self.translation_label.pos[0], self.translation_label.pos[1],
                                           self.translation_label.size[0], self.translation_label.size[1])

        # This call is now redundant as we manually update pos/size, but keeping it ensures text_size is always correct.
        self.word_label.text_size = self.card_container.size
        self.translation_label.text_size = self.card_container.size

    def show_end_message(self):
        """
        Displays the end message and summary, including results.
        """
        # Hide the card container and buttons
        self.clear_widgets()

        # Calculate scores
        total_questions = len(self.correct_words) + len(self.incorrect_words)
        correct_count = len(self.correct_words)
        incorrect_count = len(self.incorrect_words)

        # Calculate percentage if there are any questions
        if total_questions > 0:
            percentage = (correct_count / total_questions) * 100
        else:
            percentage = 0

        # Prepare the summary text
        summary_text = "Koniec programu!\n\n"
        summary_text += f"Twój wynik: {correct_count} / {total_questions} poprawnych odpowiedzi.\n"
        summary_text += f"Udział procentowy: {percentage:.2f}%\n\n"

        if self.incorrect_words:
            summary_text += "Słowa, które wymagają powtórki:\n"
            for pl, en in self.incorrect_words.items():
                summary_text += f"    - {pl}: {en}\n"
        else:
            summary_text += "Gratulacje! Wszystkie odpowiedzi były poprawne."

        # Add the end message label
        end_label = Label(
            text=summary_text,
            font_size='30sp',
            color=(0, 0, 0, 1),
            size_hint=(1, 1),
            halign='center',
            valign='middle'
        )
        self.add_widget(end_label)

        # Add an exit button
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
