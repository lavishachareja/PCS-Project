import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import pandas as pd
from difflib import get_close_matches

faq_data = {
    "garbage": "Garbage collection happens every Monday and Thursday. Contact your local municipal office for complaints.",
    "water": "Water supply is available daily. For issues, contact the Jal Board helpline at 1916.",
    "electricity": "Electricity is available 24/7. For outages, contact the local electricity board helpline.",
    "parking": "Parking permits are required for certain areas. Apply via the local municipal website.",
    "library": "Public libraries are open from 9 AM to 6 PM, Monday to Saturday. Closed on Sundays.",
    "buses": "City buses operate every 15 minutes from 6 AM to 10 PM on weekdays.",
    "recycling": "Recyclable waste is collected every Tuesday. Please separate wet and dry waste.",
    "fires": "In case of fire emergencies, dial 101. The fire department operates 24/7.",
    "healthcare": "Government health centers are open from 8 AM to 8 PM. For emergencies, visit the nearest hospital.",
    "schools": "Government schools operate from 8 AM to 2 PM. Check the local education board for holiday schedules.",
    "wifi": "Free Wi-Fi is available in select public parks and metro stations.",
    "police": "For non-emergencies, call the local police station. For emergencies, dial 100.",
    "events": "Visit the city municipal website for details on upcoming local festivals and public events."
}

def closest_match(word, keys):
    matches = get_close_matches(word, keys, n=1, cutoff=0.5)
    return matches[0] if matches else None

def chat(question, citizen_data, citizen_id):
    for keyword, response in faq_data.items():
        if keyword in question.lower():
            return f"Hello {citizen_data.loc[citizen_data['citizen_id'] == citizen_id, 'name'].iloc[0]}, {response}", None
    words = question.lower().split()
    for word in words:
        match = closest_match(word, faq_data.keys())
        if match:
            return f"Did you mean '{match}'? (yes/no)", match
    return f"Hello {citizen_data.loc[citizen_data['citizen_id'] == citizen_id, 'name'].iloc[0]}, I couldn't find information about your question.", None

citizen_data = pd.read_csv("citizen.csv")

class ChatBotApp(App):
    def build(self):
        self.citizen_id = None
        self.citizen_name = ""
        self.pending_confirmation = None

        self.layout = BoxLayout(orientation='vertical')
        self.login_screen()
        return self.layout

    def login_screen(self):
        self.layout.clear_widgets() 
        self.input_id = TextInput(hint_text='Enter your Citizen ID', multiline=False, font_size=40, size_hint=(1, 0.1))  # Adjust size_hint for better scaling
        self.login_button = Button(text='Login', font_size=40, size_hint=(1, 0.1)) 
        self.login_button.bind(on_press=self.validate_citizen)

        self.layout.add_widget(Label(text='Welcome to the City Chatbot', font_size=30))
        self.layout.add_widget(self.input_id)
        self.layout.add_widget(self.login_button) 

    def chat_screen(self):
        self.layout.clear_widgets()
        self.chat_history_layout = GridLayout(cols=1, size_hint_y=None)
        self.chat_history_layout.bind(minimum_height=self.chat_history_layout.setter('height'))

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.scroll.add_widget(self.chat_history_layout)

        input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.input_query = TextInput(hint_text='Ask your question...', multiline=False, size_hint=(0.8, 1))
        self.send_button = Button(text='Send', size_hint=(0.2, 1))
        self.send_button.bind(on_press=self.handle_query)
        input_layout.add_widget(self.input_query)
        input_layout.add_widget(self.send_button)

        self.layout.add_widget(Label(text=f'Hello {self.citizen_name}, ask your question below:'))
        self.layout.add_widget(self.scroll)
        self.layout.add_widget(input_layout)

    def validate_citizen(self, instance):
        try:
            citizen_id = int(self.input_id.text)
            if citizen_id in citizen_data['citizen_id'].values:
                self.citizen_id = citizen_id
                self.citizen_name = citizen_data.loc[citizen_data['citizen_id'] == citizen_id, 'name'].iloc[0]
                self.chat_screen()
            else:
                self.input_id.text = ''
                self.layout.add_widget(Label(text='Invalid ID. Try again.'))
        except ValueError:
            self.input_id.text = ''
            self.layout.add_widget(Label(text='Invalid input. Enter a number.'))

    def handle_query(self, instance):
        query = self.input_query.text.strip().lower()
        if query == 'exit':
            self.layout.clear_widgets()
            self.layout.add_widget(Label(text=f'Thank you, {self.citizen_name}, for using the chatbot.'))
        elif self.pending_confirmation:
            if query == 'yes':
                response = faq_data[self.pending_confirmation]
                self.add_chat_message(f"Bot: {response}")
                self.pending_confirmation = None
            elif query == 'no':
                self.add_chat_message("Bot: Okay, please ask your question again.")
                self.pending_confirmation = None
            else:
                self.add_chat_message("Bot: Please reply with 'yes' or 'no'.")
        else:
            response, match = chat(query, citizen_data, self.citizen_id)
            self.add_chat_message(f"You: {query}")
            self.add_chat_message(f"Bot: {response}")
            self.pending_confirmation = match
        self.input_query.text = ''

    def add_chat_message(self, message):
        self.chat_history_layout.add_widget(Label(text=message, size_hint_y=None, height=30))
        self.scroll.scroll_y = 0

if __name__ == '__main__':
    ChatBotApp().run()
