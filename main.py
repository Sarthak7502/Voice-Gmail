import os
import base64
import pickle
import pyttsx3
import speech_recognition as sr
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google API settings
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'C:/Users/jains/Desktop/AI/client_secret_160992078793-81nsngmssu6b4mg00p5ei02ujtj8v9m3.apps.googleusercontent.com.json'
TOKEN_PICKLE_FILE = 'token.pickle'

# Voice assistant setup
engine = pyttsx3.init()
r = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        print("Recognizing...")
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            return None

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def list_messages(service, user_id='me', label_ids=None):
    results = service.users().messages().list(userId=user_id, labelIds=label_ids).execute()
    messages = results.get('messages', [])
    return messages

def send_message(service, sender, to, subject, body):
    message = create_message(sender, to, subject, body)
    send_message_internal(service, 'me', message)

def create_message(sender, to, subject, body):
    message = {
        'to': to,
        'subject': subject,
        'body': {
            'text': body
        }
    }
    return message

def send_message_internal(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message sent. Message Id: {message['id']}")
    except Exception as error:
        print(f"An error occurred: {error}")

def main():
    speak("Welcome to Gmail Voice Assistant. How can I assist you today?")

    service = get_gmail_service()

    while True:
        speak("Do you want to send an email or check your inbox?")
        command = recognize_speech()

        if command and 'send' in command.lower():
            speak("Who is the recipient?")
            to = recognize_speech()

            speak("What is the subject of the email?")
            subject = recognize_speech()

            speak("What should be the content of the email?")
            body = recognize_speech()

            send_message(service, 'your-email@gmail.com', to, subject, body)
            speak("Email sent successfully!")

        elif command and 'check' in command.lower():
            messages = list_messages(service)
            if messages:
                speak("You have new messages in your inbox.")
            else:
                speak("Your inbox is empty.")

        else:
            speak("I didn't understand. Can you please repeat?")
            
if __name__ == "__main__":
    main()
