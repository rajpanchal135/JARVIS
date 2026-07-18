import multiprocessing
import subprocess
import os

# To run Jarvis
def startJarvis():
    print("Process 1 is running.")
    from main import start
    start()

# To run Flask backend
def startBackend():
    print("Process 3 (Flask Backend) is running.")
    from www.backend import app
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

# Start all processes
if __name__ == '__main__':
    p1 = multiprocessing.Process(target=startJarvis)
    p3 = multiprocessing.Process(target=startBackend)

    p1.start()
    p3.start()

    p1.join()

    if p3.is_alive():
        p3.terminate()
        p3.join()

    print("System Terminated !!!")
    
    



# 