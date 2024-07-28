import pyttsx3 as p
import speech_recognition as sr
from playwright.sync_api import sync_playwright
import time

# Function to initialize text-to-speech engine
def init_tts():
    engine = p.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', 130)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    return engine

# Function to speak text
def speak(engine, text):
    engine.say(text)
    engine.runAndWait()

# Infow class to handle browser automation
class Infow:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)  # Set headless=False for debugging

    def search_wikipedia(self, query):
        self.page = self.browser.new_page()
        self.page.goto("https://www.wikipedia.org/")
        self.page.fill('input[name="search"]', query)
        self.page.click('button[type="submit"]')
        self.page.wait_for_selector('div#mw-content-text', timeout=10000)  # Wait for the content to load
        time.sleep(60)  # Allow some time for the user to see the page

    def play_youtube_video(self, query):
        self.page = self.browser.new_page()
        self.page.goto("https://www.youtube.com/")
        self.page.fill('input#search', query)
        self.page.click('button#search-icon-legacy')
        self.page.wait_for_selector('ytd-video-renderer', timeout=10000)  # Wait for search results to load
        self.page.click('ytd-video-renderer a#thumbnail')  # Click on the first video result
        time.sleep(60)  # Allow some time for the video to start playing

    def play_spotify_song(self, query):
        self.page = self.browser.new_page()
        self.page.goto("https://accounts.spotify.com/en/login")
        self.page.fill('input#login-username', 'your_spotify_username')
        self.page.fill('input#login-password', 'your_spotify_password')
        self.page.click('button#login-button')
        self.page.wait_for_selector('input[data-testid="search-input"]', timeout=20000)  # Wait for search input to load
        self.page.fill('input[data-testid="search-input"]', query)
        self.page.press('input[data-testid="search-input"]', 'Enter')
        self.page.wait_for_selector('div[data-testid="tracklist-row"]', timeout=10000)  # Wait for search results to load
        self.page.click('div[data-testid="tracklist-row"]')  # Click on the first song result
        time.sleep(60)  # Allow some time for the song to start playing

    def close(self):
        self.browser.close()
        self.playwright.stop()

# Function to handle speech recognition
def recognize_speech(recognizer, source, prompt):
    speak(engine, prompt)
    try:
        recognizer.adjust_for_ambient_noise(source, duration=1.2)
        print("Listening...")
        audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        speak(engine, "Sorry, I could not understand what you said.")
        print("UnknownValueError: Could not understand audio")
        return None
    except sr.RequestError:
        speak(engine, "Sorry, there was an issue with the speech recognition service.")
        print("RequestError: Issue with the speech recognition service")
        return None
    except sr.WaitTimeoutError:
        speak(engine, "Listening timed out. Please try again.")
        print("WaitTimeoutError: Listening timed out")
        return None

# Main function to handle voice recognition and interaction
def main():
    global engine
    engine = init_tts()
    speak(engine, "Welcome, I am your assistant.")
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        text = recognize_speech(recognizer, source, "Hello sir, I'm your voice assistant. How are you?")
        if text and "what" in text and "about" in text and "you" in text:
            speak(engine, "I am having a good day.")

        text2 = recognize_speech(recognizer, source, "What can I do for you?")
        if text2:
            print("You said:", text2)
            assist = Infow()
            if "information" in text2.lower() or "wikipedia" in text2.lower():
                infor = recognize_speech(recognizer, source, "Which information do you want?")
                speak(engine, "Searching Wikipedia for {}".format(infor))
                if infor:
                    assist.search_wikipedia(infor)
            elif "youtube" in text2.lower() or "video" in text2.lower():
                infor = recognize_speech(recognizer, source, "What do you want to search for on YouTube?")
                speak(engine, "Searching YouTube for {}".format(infor))
                if infor:
                    assist.play_youtube_video(infor)
            elif " spotify" in text2.lower() or "song" in text2.lower():
                infor = recognize_speech(recognizer, source, "What do you want to search for on Spotify?")
                speak(engine, "Searching Spotify for {}".format(infor))
                if infor:
                    assist.play_spotify_song(infor)
            else:
                speak(engine, "Sorry, I couldn't understand your request.")
                print("The request did not include a recognized platform.")
            assist.close()

if __name__ == "__main__":
    main()
