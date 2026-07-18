import os
import eel
import threading
import webbrowser
from engine.features import playAssistantSound, hotword
from engine.command import allCommands, speak, takecommand

def start():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    eel.init(os.path.join(base_dir, "www"))

    playAssistantSound()

    # Run hotword listener in the background of the main process
    t = threading.Thread(target=hotword, daemon=True)
    t.start()

    webbrowser.open("http://localhost:8000/index.html")

    eel.start('index.html', mode=None, host='localhost', block=True)
