import pyttsx3
import speech_recognition as sr
import eel
import time
import json
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import pyjokes
import os
import pygame
from gtts import gTTS

stop_speaking_flag = False

@eel.expose
def stop_speaking():
    global stop_speaking_flag
    stop_speaking_flag = True
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass

# Speak function
def speak(text):
    global stop_speaking_flag
    stop_speaking_flag = False
    
    text = str(text)
    eel.DisplayMessage(text)
    eel.receiverText(text)
    
    try:
        # Detect language based on character script
        lang = 'en'
        
        # Load user preference for English accent
        accent = 'en-in'
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    accent = config.get('voice', 'en-in')
            except Exception:
                pass
            
        if any('\u0900' <= c <= '\u097F' for c in text):  # Devanagari (Hindi)
            lang = 'hi'
            accent = 'hi' # Reset accent for native language
        elif any('\u0A80' <= c <= '\u0AFF' for c in text): # Gujarati
            lang = 'gu'
            accent = 'gu'
            
        # Map accent codes to valid Google TLDs
        tld_map = {
            'en-in': 'co.in',
            'en-gb': 'co.uk',
            'en-au': 'com.au',
            'en-us': 'com'
        }
        
        # Default to 'com' if accent is hi or gu
        target_tld = tld_map.get(accent, 'com')
            
        tts = gTTS(text=text, lang=lang, tld=target_tld, slow=False)
        filename = f"temp_speech_{time.time()}.mp3"
        tts.save(filename)
        
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if stop_speaking_flag:
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
        pygame.mixer.quit()
        
        try:
            os.remove(filename)
        except Exception:
            pass
            
    except Exception as e:
        print(f"gTTS fallback error: {e}")
        # Fallback to pyttsx3
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices') 
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 174)
        engine.say(text)
        engine.runAndWait()

# Take command from microphone
def takecommand():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('Listening....')
        eel.DisplayMessage('Listening....')
        r.pause_threshold = 0.5
        r.adjust_for_ambient_noise(source, duration=0.2)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=6)
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected.")
            eel.DisplayMessage("No speech detected. Returning to home.")
            speak("You didn't say anything, going back to home.")
            eel.ShowHood()
            return ""

    try:
        print('Recognizing.....')
        eel.DisplayMessage('Recognizing....')
        
        # We use hi-IN so the engine picks up Indian languages flawlessly without a translator
        query = r.recognize_google(audio, language='hi-IN')
        query = query.lower().strip()
        print(f"User originally said: {query}")
        
        eel.DisplayMessage(query)
        time.sleep(2)
    except Exception as e:
        return ""
    
    return query

# Handling all commands :

@eel.expose
def allCommands(message=1):
    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)
        
    if not query:
        return

    try:
        from engine.features import chatBot
        chatBot(query)
    except Exception as e:
        print(f"Error in allCommands: {e}")
        speak(f"I can't get it, can you please repeat?")

    eel.ShowHood()
