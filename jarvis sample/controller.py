import eel
import time

eel.init('www')

@eel.expose
def start_jarvis():
    eel.hideStart()()         # 🔥 Trigger animation
    time.sleep(2)

if __name__ == '__main__':
    eel.start('index.html', size=(800, 600), port=8000, block=False)
    time.sleep(2)
    start_jarvis()
    while True:
        eel.sleep(5)