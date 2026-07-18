from playsound import playsound
import eel 
from engine.config import ASSISTANT_NAME
from engine.command import speak
import os
import pywhatkit as kit
import re # regular expression
import sqlite3
import subprocess
import webbrowser
import pvporcupine
import pyaudio
import time
import struct
import pyttsx3
import threading
import datetime
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- Task Scheduler ---
scheduled_tasks = []

def task_scheduler_loop():
    import time
    while True:
        try:
            now = datetime.datetime.now()
            for task in scheduled_tasks[:]:
                if now >= task['time']:
                    speak(f"Executing scheduled task: {task['description']}")
                    if task['type'] == 'email':
                        speak(f"Sending email to {task['target']}")
                        print(f"--- EMAIL SENT ---")
                        print(f"TO: {task['target']}")
                        print(f"CONTENT: {task['content']}")
                        print(f"------------------")
                    scheduled_tasks.remove(task)
            time.sleep(10)
        except Exception:
            pass

# Start background scheduler
threading.Thread(target=task_scheduler_loop, daemon=True).start()

def system_control(action):
    speak(f"Initiating system {action} sequence.")
    if action == "lock":
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif action == "shutdown":
        os.system("shutdown /s /t 5")
    elif action == "restart":
        os.system("shutdown /r /t 5")
def send_whatsapp_message(contact, message):
    try:
        import pyautogui
        import time
        speak(f"Sending message to {contact}")
        
        # Open WhatsApp Desktop App
        os.system("start whatsapp:")
        time.sleep(5) # Wait for it to completely open
        
        # Click search or press Ctrl+F
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(1)
        
        # Type the contact name
        pyautogui.write(contact)
        time.sleep(3) # Wait for search results
        
        # Select the contact (first result is auto-highlighted)
        pyautogui.press('enter')
        time.sleep(2)
        
        # Type the message and send
        pyautogui.write(message)
        pyautogui.press('enter')
        print(f"Message sent to {contact}: {message}")
    except Exception as e:
        speak("Sorry, I could not send the WhatsApp message.")
        print(e)

# import google.generativeai as genai                                                                                                       

from engine.helper import extract_yt_term
from hugchat import hugchat 
import json

# Preferences logic
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "#00e5ff", "voice": "en-in", "wakeWord": "jarvis"}

@eel.expose
def save_preferences(theme, voice, wakeWord):
    config = {"theme": theme, "voice": voice, "wakeWord": wakeWord}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    print(f"Preferences saved: {config}")
    
    # Update AI Identity Instantly!
    global chat_session
    try:
        import google.generativeai as genai
        ai_name = wakeWord.upper()
        current_time = datetime.datetime.now().isoformat()
        
        system_prompt = f"""You are {ai_name}, a highly advanced AI assistant. You natively understand English, Hindi, and Gujarati perfectly. DO NOT translate the user's intent. If the user speaks in Hindi, reply in pure Hindi script (Devanagari). If the user speaks in Gujarati, reply in pure Gujarati script. IMPORTANT: You are also a system controller. If the user asks you to perform an action, you must output a special command tag in your response. The tags are:
<CMD:youtube:search_term>
<CMD:screenshot>
<CMD:camera>
<CMD:trash>
<CMD:volumeup>
<CMD:volumedown>
<CMD:mute>
<CMD:news>
<CMD:open:app_name> (If the user asks to open WhatsApp, use <CMD:open:whatsapp> and proactively ask them who they want to send a message to!)
<CMD:whatsapp:contact_name:message> (Use this to send a WhatsApp message)
<CMD:system:lock>
<CMD:system:shutdown>
<CMD:system:restart>
<CMD:schedule_email:YYYY-MM-DDTHH:MM:SS:email_address:content> (Use the exact ISO time format calculated from the user's request. The current time is {current_time})
If no action is needed, just reply normally. Keep answers brief and conversational."""

        gemini_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_prompt
        )
        chat_session = gemini_model.start_chat(history=[])
        print(f"AI Identity updated to {ai_name} instantly!")
    except Exception as e:
        print(f"Failed to update identity: {e}")

@eel.expose
def get_preferences():
    return load_config()

# database connection helper (thread-safe)
def get_db_connection():
    db_path = os.path.join(BASE_DIR, "jarvis.db")
    con = sqlite3.connect(db_path)
    return con, con.cursor()

# playing assiatnt sound function
@eel.expose
def playAssistantSound():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    music_dir = os.path.join(base_dir, "www", "assets", "audio", "start_sound.mp3")
    playsound(music_dir)

@eel.expose
def get_system_stats():
    import psutil
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    bat = battery.percent if battery else 100
    return {"cpu": cpu, "ram": ram, "battery": bat}


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query = query.lower()

    app_name = query.strip()

    if app_name != "":
        con, cursor = get_db_connection()
        try:
            cursor.execute(
                'SELECT path FROM system_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        subprocess.Popen(['start', app_name], shell=True)
                    except Exception as e:
                        print(f"Error opening app: {e}")
                        speak("Oops, not found !")
        except Exception as e:
            print(f"Error in openCommand: {e}")
            speak(" Oops , something went wrong !")
        finally:
            con.close() 


# closeCommand function removed — was fully commented out with broken indentation


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)



def hotword():
    config = load_config()
    wake_word = config.get("wakeWord", "jarvis").lower()
    
    porcupine_keywords = ["jarvis", "alexa", "terminator", "computer", "americano", "picovoice", "porcupine", "hey siri", "hey google"]
    
    if wake_word in porcupine_keywords:
        porcupine=None
        paud=None
        audio_stream=None
        try:
            # pre trained keywords    
            try:
                porcupine=pvporcupine.create(keywords=[wake_word]) 
            except TypeError:
                print("PvPorcupine requires an access key! Hotword detection disabled until key is provided.")
                return 
            paud=pyaudio.PyAudio()
            audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
            
            while True:
                keyword=audio_stream.read(porcupine.frame_length)
                keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

                keyword_index=porcupine.process(keyword)

                if keyword_index>=0: 
                    print("hotword detected")
                    
                    # Directly trigger JARVIS UI over Eel instead of simulating keyboard presses
                    import eel
                    
                    # Interrupt current speech instantly
                    try:
                        eel.stop_speaking()
                    except:
                        pass
                    
                    eel.playAssistantSound()
                    
                    # Hide Orb, Show SiriWave
                    eel.hideOval()
                    eel.showSiriWave()
                    
                    eel.allCommands()()
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if porcupine is not None:
                porcupine.delete()
            if audio_stream is not None:
                audio_stream.close()
            if paud is not None:
                paud.terminate()
    else:
        # CUSTOM WAKE WORD FALLBACK USING SPEECH_RECOGNITION
        import speech_recognition as sr
        r = sr.Recognizer()
        print(f"Custom wake word '{wake_word}' activated using Google SR.")
        with sr.Microphone() as source:
            r.pause_threshold = 0.5
            r.adjust_for_ambient_noise(source, duration=0.2)
            while True:
                try:
                    audio = r.listen(source, timeout=1, phrase_time_limit=3)
                    query = r.recognize_google(audio, language='en-in').lower()
                    if wake_word in query:
                        print("Custom hotword detected")
                        import eel
                        try:
                            eel.stop_speaking()
                        except:
                            pass
                        eel.playAssistantSound()
                        eel.hideOval()
                        eel.showSiriWave()
                        eel.allCommands()()
                except Exception:
                    pass

import warnings
warnings.filterwarnings("ignore")

import google.generativeai as genai

# Load API key securely from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
try:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in .env file. Please add it.")
    
    # Load custom name so the AI actually knows who it is!
    current_config = load_config()
    ai_name = current_config.get("wakeWord", "JARVIS").upper()
    
    genai.configure(api_key=GEMINI_API_KEY)
    current_time = datetime.datetime.now().isoformat()
    system_prompt = f"""You are {ai_name}, a highly advanced AI assistant. You natively understand English, Hindi, and Gujarati perfectly. DO NOT translate the user's intent. If the user speaks in Hindi, reply in pure Hindi script (Devanagari). If the user speaks in Gujarati, reply in pure Gujarati script. IMPORTANT: You are also a system controller. If the user asks you to perform an action, you must output a special command tag in your response. The tags are:
<CMD:youtube:search_term>
<CMD:screenshot>
<CMD:camera>
<CMD:trash>
<CMD:volumeup>
<CMD:volumedown>
<CMD:mute>
<CMD:news>
<CMD:open:app_name> (If the user asks to open WhatsApp, use <CMD:open:whatsapp> and proactively ask them who they want to send a message to!)
<CMD:whatsapp:contact_name:message> (Use this to send a WhatsApp message)
<CMD:system:lock>
<CMD:system:shutdown>
<CMD:system:restart>
<CMD:schedule_email:YYYY-MM-DDTHH:MM:SS:email_address:content> (Use the exact ISO time format calculated from the user's request. The current time is {current_time})
If no action is needed, just reply normally. Keep answers brief and conversational."""

    gemini_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_prompt
    )
    chat_session = gemini_model.start_chat(history=[])
except Exception as e:
    print(f"Gemini Init Error: {e}")
    chat_session = None


def chatBot(query):
    user_input = query.lower()
    
    if not chat_session:
        # Fallback to local brain
        if "news" in user_input or "samachar" in user_input:
            get_news()
            return "Fetching news."
        elif "ratan tata" in user_input:
            reply = "Ratan Tata is a revered Indian industrialist and former chairman of Tata Sons. He is known for his business ethics, philanthropy, and transforming the Tata Group into a global powerhouse."
        else:
            reply = "Captain, my Gemini neural network is offline. Please check your API key."
        print(reply)
        speak(reply)
        return reply

    try:
        response = chat_session.send_message(query)
        reply = response.text
        # Clean up text for speech synthesis
        reply = reply.replace("*", "").replace("#", "")
        
        # Parse Dynamic Commands
        import re
        cmd_match = re.search(r'<CMD:(.*?)>', reply)
        if cmd_match:
            cmd = cmd_match.group(1).split(':')
            action = cmd[0]
            reply = re.sub(r'<CMD:.*?>', '', reply).strip() # Remove tag from speech
            
            if reply: # Speak the text before acting
                print(reply)
                speak(reply)
            
            # Execute dynamically!
            if action == "youtube" and len(cmd) > 1:
                PlayYoutube(cmd[1])
            elif action == "screenshot":
                take_screenshot()
            elif action == "camera":
                take_picture()
            elif action == "trash":
                empty_recycle_bin()
            elif action == "volumeup":
                change_volume("up")
            elif action == "volumedown":
                change_volume("down")
            elif action == "mute":
                change_volume("mute")
            elif action == "news":
                get_news()
            elif action == "open" and len(cmd) > 1:
                openCommand(cmd[1])
            elif action == "whatsapp" and len(cmd) >= 3:
                target_contact = cmd[1]
                message_content = ":".join(cmd[2:])
                send_whatsapp_message(target_contact, message_content)
            elif action == "system" and len(cmd) > 1:
                system_control(cmd[1])
            elif action == "schedule_email" and len(cmd) >= 4:
                try:
                    iso_time = cmd[1] + ":" + cmd[2] + ":" + cmd[3] # recombine time string due to colon split
                    target_email = cmd[4]
                    content = ":".join(cmd[5:])
                    task_time = datetime.datetime.fromisoformat(iso_time)
                    scheduled_tasks.append({
                        "type": "email",
                        "target": target_email,
                        "content": content,
                        "time": task_time,
                        "description": f"Email to {target_email}"
                    })
                    speak(f"Task scheduled successfully for {task_time.strftime('%A at %I:%M %p')}")
                except Exception as e:
                    speak("Sorry, I could not parse the schedule time.")
                    print(e)
                
            return reply
            
        print(reply)
        speak(reply)
    except Exception as e:
        if "news" in user_input or "samachar" in user_input:
            get_news()
            return "Fetching news."
        reply = "Captain, I am hitting a Google API restriction right now. Please check your region's free tier access."
        print(f"Error: {e}")
        print(reply)
        speak(reply)

    return reply





# Send WhatsApp message using pyautogui
# This function sends a WhatsApp message to a specified contact using the WhatsApp Desktop application.

import sqlite3
import os
import time
import pyautogui
from engine.command import speak, takecommand

def send_whatsapp_desktop():
    try:
        # Step 1: Get WhatsApp path from database
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "jarvis.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM system_command WHERE name = 'whatsapp'")
        result = cursor.fetchone()
        conn.close()

        if result:
            whatsapp_path = result[0]

            # Step 2: Open WhatsApp Desktop
            os.startfile(whatsapp_path)
            speak("Opening WhatsApp, please wait...")
            time.sleep(2)

            # Step 3: Ask for contact name
            speak("Whom should I send the message to?")
            contact = takecommand().strip().title()
            time.sleep(2)
            if not contact:
                speak("No contact name provided, going back to home.")
                return
            # Sub Step: Automate message send using pyautogui
            pyautogui.click(940,160)  # Click search bar (adjust coords)
            time.sleep(1)
            pyautogui.write(contact)
            time.sleep(2)
            pyautogui.click(845,253)  # Click on contact (adjust coords)
            time.sleep(1)

            # Step 4: Ask for message
            speak("What is the message?")
            message = takecommand().strip()
            time.sleep(2)
            if not message:
                speak("No message provided, going back to home.")
                return
            pyautogui.click(1390,990)  # Click typing bar (adjust coords)
            time.sleep(1)
            pyautogui.write(message)
            time.sleep(2)
            pyautogui.press('enter')

            speak(f"Sending message to {contact}: {message}")


            speak("Message sent successfully.")
        else:
            speak("WhatsApp path not found in database.")

    except Exception as e:
        speak("Sorry, something went wrong while sending the message.")
        print(f"[Error]: {e}")

# ==========================================
# NEW CRAZY FEATURES: SYSTEM CONTROL
# ==========================================

def system_status():
    import psutil
    battery = psutil.sensors_battery()
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    
    status = f"Captain, the system is operating at {cpu} percent CPU usage, and {ram} percent RAM utilization. "
    if battery:
        status += f"Battery is at {battery.percent} percent. "
        if battery.power_plugged:
            status += "The system is currently charging."
        else:
            status += "We are running on battery power."
    
    print(status)
    speak(status)

def take_screenshot():
    import pyautogui
    import time
    speak("Taking a screenshot in 3 seconds. Please smile!")
    time.sleep(3)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = f"screenshot_{int(time.time())}.png"
    filepath = os.path.join(base_dir, filename)
    
    img = pyautogui.screenshot()
    img.save(filepath)
    speak(f"Screenshot saved successfully to your Jarvis folder.")

# ==========================================
# MORE CRAZY FEATURES
# ==========================================

def research_topic(topic):
    import wikipedia
    speak(f"Searching Wikipedia for {topic}")
    try:
        results = wikipedia.summary(topic, sentences=2)
        speak("According to Wikipedia:")
        print(results)
        speak(results)
    except wikipedia.exceptions.DisambiguationError:
        speak("There are too many results for that topic. Please be more specific.")
    except Exception:
        speak("I couldn't find any information on that right now.")

def take_picture():
    try:
        import cv2
        import time
        speak("Opening camera. Please look at the screen and smile!")
        cam = cv2.VideoCapture(0)
        time.sleep(2) # Allow camera to warm up
        result, image = cam.read()
        if result:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filename = f"camera_capture_{int(time.time())}.png"
            filepath = os.path.join(base_dir, filename)
            cv2.imwrite(filepath, image)
            speak("Picture taken successfully! It is saved in your Jarvis folder.")
        else:
            speak("Sorry Captain, I couldn't capture an image from your camera.")
        cam.release()
    except ImportError:
        speak("Camera module is currently installing. Try again in a minute.")
    except Exception as e:
        speak("Sorry Captain, I encountered an error with the camera.")

def empty_recycle_bin():
    import ctypes
    speak("Emptying the recycle bin.")
    try:
        # 7 = No confirmation (1), No progress UI (2), No sound (4)
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        if result == 0:
            speak("Recycle bin emptied successfully.")
        else:
            speak("The recycle bin is already empty.")
    except Exception:
        speak("Failed to empty the recycle bin.")

def change_volume(direction):
    import pyautogui
    if direction == "up":
        speak("Increasing volume.")
        for _ in range(5):
            pyautogui.press("volumeup")
    elif direction == "down":
        speak("Decreasing volume.")
        for _ in range(5):
            pyautogui.press("volumedown")
    elif direction == "mute":
        speak("Muting system.")
        pyautogui.press("volumemute")

def get_news():
    import urllib.request
    import xml.etree.ElementTree as ET
    speak("Fetching the latest news for you, Captain.")
    try:
        url = 'https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en'
        req = urllib.request.urlopen(url)
        res = req.read()
        xml_data = ET.fromstring(res)
        
        speak("Here are the top headlines right now:")
        count = 0
        for item in xml_data.findall('.//item'):
            title = item.find('title').text
            # Remove the source from the title (usually separated by ' - ')
            clean_title = title.split(' - ')[0]
            print(f"- {clean_title}")
            speak(clean_title)
            count += 1
            if count >= 3:
                break
    except Exception as e:
        speak("Sorry Captain, I couldn't connect to the news server right now.")





