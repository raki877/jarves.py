import os
import webbrowser
import pyttsx3
import pyautogui
import ctypes
import time
import keyboard
import speech_recognition as sr
from datetime import datetime
import wave
import pyaudio
import threading
import sys
import psutil
import pygetwindow as gw
from enum import Enum
import json
import screeninfo
import random
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Tuple, Union

class ScreenCommands(Enum):
    MOVE = ["move", "go to", "position"]
    CLICK = ["click", "select", "press"]
    RIGHT_CLICK = ["right click", "context menu"]
    DOUBLE_CLICK = ["double click"]
    MIDDLE_CLICK = ["middle click"]
    DRAG = ["drag", "move this"]
    SCROLL = ["scroll", "move up", "move down"]
    TYPE = ["type", "write", "enter"]
    KEYPRESS = ["press key", "hit key"]
    PRECISION = ["precision mode", "accurate mode"]
    WINDOW_CONTROL = ["window", "application"]
    CLOSE_WINDOW = ["close window", "terminate window"]
    MINIMIZE_WINDOW = ["minimize window", "hide window"]
    MAXIMIZE_WINDOW = ["maximize window", "fullscreen window"]
    RESTORE_WINDOW = ["restore window", "normal window"]
    SWITCH_WINDOW = ["switch window", "change window"]
    MOVE_WINDOW = ["move window", "position window"]
    RESIZE_WINDOW = ["resize window", "adjust window"]
    CLEAR_LINE = ["clear line", "erase line"]
    CLEAR_SENTENCE = ["clear sentence", "erase sentence"]
    SELECT_ALL = ["select all", "highlight all"]
    COPY = ["copy", "copy selection"]
    PASTE = ["paste", "paste clipboard"]
    CUT = ["cut", "cut selection"]
    UNDO = ["undo", "reverse action"]
    REDO = ["redo", "repeat action"]
    SAVE = ["save", "save file"]
    NEW_LINE = ["new line", "line break"]
    TAB = ["insert tab", "press tab"]
    ESCAPE = ["press escape", "exit mode"]
    FUNCTION_KEYS = [f"press f{i}" for i in range(1, 13)] + ["function key"]
    LOCK = ["lock computer", "secure workstation"]
    SHUTDOWN = ["shutdown computer", "turn off computer"]
    RESTART = ["restart computer", "reboot system"]

DEFAULT_CONFIG = {
    "wake_word": "jarvis",
    "user_name": os.getenv("USERNAME", "Sir"),
    "voice_effects": True,
    "sensitivity": {
        "screen_control": 25,
        "scroll": 100,
        "default_pixel_move": 100,
        "drag_speed": 0.5
    },
    "mouse": {
        "acceleration": 1.2,
        "precision_mode_multiplier": 0.5,
        "screen_edge_threshold": 50
    },
    "window_management": {
        "minimize_hotkey": "win+down",
        "maximize_hotkey": "win+up",
        "close_hotkey": "alt+f4",
        "restore_hotkey": "win+shift+up"
    },
    "applications": {
        "default": {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "camera": "microsoft.windows.camera:",
            "paint": "mspaint.exe",
            "file explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "vs code": r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME')),
            "pycharm": r"C:\Program Files\JetBrains\PyCharm Community Edition\bin\pycharm64.exe",
            "photoshop": r"C:\Program Files\Adobe\Adobe Photoshop {version}\Photoshop.exe",
            "premiere": r"C:\Program Files\Adobe\Adobe Premiere Pro {version}\Adobe Premiere Pro.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "teams": r"C:\Users\{}\AppData\Local\Microsoft\Teams\current\Teams.exe".format(os.getenv('USERNAME')),
            "zoom": r"C:\Users\{}\AppData\Roaming\Zoom\bin\Zoom.exe".format(os.getenv('USERNAME')),
            "instagram": "https://www.instagram.com/",
            "chatgpt": "https://chat.openai.com/",
            "deepseek": "https://www.deepseek.com/",
            "google": "https://www.google.com/"
        },
        "custom": {}
    },
    "web_services": {
        "google_search": "https://www.google.com/search?q={query}",
        "google_maps": "https://www.google.com/maps?q={query}",
        "youtube": "https://www.youtube.com/results?search_query={query}",
        "wikipedia": "https://en.wikipedia.org/wiki/{query}"
    },
    "voice_settings": {
        "rate": 170,
        "volume": 1.0,
        "voice_preference": ["david", "zira"],
        "response_style": "formal"
    },
    "security": {
        "require_confirmation": False,
        "confirmation_phrases": ["confirm", "proceed", "execute"]
    }
}

class SystemJarvis:
    def __init__(self, config: dict = None):
        self.config = config or self._load_config()
        self._init_audio_systems()
        self.engine = self._init_tts_engine()
        self.sound_effects = self._load_sound_effects()
        self.applications = self._load_applications()
        self.screen_control_active = False
        self.precision_mode = False
        self.drag_start = None
        self.monitors = screeninfo.get_monitors()
        self.current_monitor = 0
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01
        self.responses = self._init_responses()
        self.last_command = None
        self.awaiting_confirmation = False
        self.pending_command = None

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path) as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
            return DEFAULT_CONFIG
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG

    def _init_audio_systems(self):
        try:
            self.audio = pyaudio.PyAudio()
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception as e:
            print(f"Audio initialization failed: {e}")
            raise

    def _init_tts_engine(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.config["voice_settings"]["rate"])
            engine.setProperty('volume', self.config["voice_settings"]["volume"])
            voices = engine.getProperty('voices')
            for voice in voices:
                if any(vp.lower() in voice.name.lower() 
                      for vp in self.config["voice_settings"]["voice_preference"]):
                    engine.setProperty('voice', voice.id)
                    break
            return engine
        except Exception as e:
            print(f"TTS initialization failed: {e}")
            engine = pyttsx3.init()
            engine.say = lambda x: print(f"TTS would say: {x}")
            engine.runAndWait = lambda: None
            return engine

    def _restart_tts_engine(self):
        try:
            if hasattr(self.engine, '_inLoop') and self.engine._inLoop:
                self.engine.endLoop()
        except Exception:
            pass
        self.engine = self._init_tts_engine()

    def _load_sound_effects(self):
        effects = {}
        sound_files = {
            'startup': 'startup.wav',
            'processing': 'processing.wav',
            'error': 'error.wav',
            'screen_control': 'screen_control.wav'
        }
        for name, filename in sound_files.items():
            try:
                if os.path.exists(filename):
                    effects[name] = wave.open(filename, 'rb')
                else:
                    effects[name] = None
            except Exception as e:
                print(f"Error loading sound {filename}: {e}")
                effects[name] = None
        return effects

    def _play_sound(self, sound_name: str):
        if not self.config["voice_effects"] or not self.sound_effects.get(sound_name):
            return
            
        def play():
            try:
                sound = self.sound_effects[sound_name]
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(sound.getsampwidth()),
                    channels=sound.getnchannels(),
                    rate=sound.getframerate(),
                    output=True
                )
                data = sound.readframes(1024)
                while data:
                    stream.write(data)
                    data = sound.readframes(1024)
                stream.stop_stream()
                stream.close()
            except Exception as e:
                print(f"Error playing sound: {e}")
                
        threading.Thread(target=play, daemon=True).start()

    def _load_applications(self):
        apps = self.config["applications"]["default"].copy()
        apps.update(self.config["applications"]["custom"])
        if self.config.get("auto_discover_apps", True):
            program_dirs = [
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                os.path.expandvars("%APPDATA%"),
                os.path.expandvars("%LOCALAPPDATA%")
            ]
            for dir in program_dirs:
                if os.path.exists(dir):
                    for root, _, files in os.walk(dir):
                        for file in files:
                            if file.endswith(".exe"):
                                name = os.path.splitext(file)[0].lower()
                                if name not in apps:
                                    apps[name] = os.path.join(root, file)
        return apps

    def _init_responses(self) -> Dict[str, List[str]]:
        style = self.config["voice_settings"].get("response_style", "formal")
        
        if style == "formal":
            return {
                'acknowledgments': [
                    "Right away, sir.", 
                    "Executing your command immediately.",
                    "I'll handle that right now."
                ],
                'humor': [
                    "Why don't scientists trust atoms? Because they make up everything.",
                    "I'm reading a book about anti-gravity. It's impossible to put down."
                ],
                'compliments': [
                    "An excellent decision, sir.",
                    "Your command was most efficiently formulated."
                ],
                'errors': [
                    "I'm experiencing some technical difficulties with that request.",
                    "My systems are encountering unexpected resistance."
                ],
                'system_status': [
                    "All systems operating at peak efficiency.",
                    "Diagnostics show 99.9% operational capacity."
                ],
                'confirmations': [
                    "Please confirm you want me to proceed with this action.",
                    "This is a security-sensitive command. Say 'confirm' to proceed."
                ],
                'window_actions': [
                    "Window operation completed successfully.",
                    "The window has been adjusted as requested."
                ]
            }
        else:
            return {
                'acknowledgments': [
                    "You got it!", 
                    "On it!",
                    "Consider it done."
                ],
                'humor': [
                    "I'd tell you a UDP joke, but you might not get it.",
                    "Why was the robot angry? Because someone kept pushing its buttons!"
                ],
                'compliments': [
                    "Nice one!",
                    "You're really good at this!"
                ],
                'errors': [
                    "Oops, that didn't work.",
                    "My bad, I couldn't do that."
                ],
                'system_status': [
                    "Everything's running smoothly!",
                    "All systems go!"
                ],
                'confirmations': [
                    "You sure about that?",
                    "This seems important. Want me to go ahead?"
                ],
                'window_actions': [
                    "Done!",
                    "Window handled!"
                ]
            }

    def _jarvis_response(self, action: str, command: str = None) -> str:
        base_response = random.choice(self.responses.get(action, [""]))
        
        if action == "acknowledgments":
            if self.last_command and "thank" in self.last_command.lower():
                return random.choice([
                    "You're most welcome, sir.",
                    "My pleasure to assist.",
                    "Always at your service."
                ])
            
            if random.random() < 0.15:
                base_response += " " + random.choice(self.responses['compliments'])
        
        return base_response

    def speak(self, text: str, is_error: bool = False):
        print(f"JARVIS: {text}")
        
        if not is_error:
            self._play_sound('processing')
        
        pause = min(0.5, max(0.1, len(text.split()) * 0.05))
        time.sleep(pause)
        
        if not text.lower().startswith(self.config["user_name"].lower()):
            honorific = "sir" if self.config["voice_settings"]["response_style"] == "formal" else ""
            text = f"{self.config['user_name']}, {text}" if honorific else text
        
        try:
            if len(text.split()) > 20:
                sentences = [s.strip() for s in text.split('.') if s.strip()]
                for sentence in sentences[:-1]:
                    self._safe_speak(sentence + ".")
                    time.sleep(0.2)
                text = sentences[-1]
            
            self._safe_speak(text)
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            time.sleep(0.2)

    def _safe_speak(self, text: str):
        try:
            self.engine.stop()
            self.engine.say(text)
            self.engine.runAndWait()
        except RuntimeError as e:
            if "run loop already started" in str(e):
                self._restart_tts_engine()
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                raise

    def listen(self, timeout: int = 5) -> Optional[str]:
        with self.microphone as source:
            print("\nListening...")
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"{self.config['user_name']}: {command}")
                return command
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                self.speak("I didn't quite catch that.", is_error=True)
                return None
            except sr.RequestError as e:
                self.speak(f"Speech service unavailable: {e}", is_error=True)
                return None

    def _get_active_monitor(self):
        pos = pyautogui.position()
        for i, monitor in enumerate(self.monitors):
            if (monitor.x <= pos.x < monitor.x + monitor.width and 
                monitor.y <= pos.y < monitor.y + monitor.height):
                self.current_monitor = i
                return {
                    'x': monitor.x,
                    'y': monitor.y,
                    'width': monitor.width,
                    'height': monitor.height,
                    'center_x': monitor.x + monitor.width // 2,
                    'center_y': monitor.y + monitor.height // 2
                }
        return self.monitors[0].__dict__

    def _calculate_movement(self, command: str) -> Tuple[int, int]:
        words = command.split()
        numbers = [int(word) for word in words if word.isdigit()]
        amount = numbers[0] if numbers else self.config["sensitivity"]["default_pixel_move"]
        if self.precision_mode:
            amount = int(amount * self.config["mouse"]["precision_mode_multiplier"])
        if any(word in command for word in ["keep", "hold", "continuous"]):
            amount = int(amount * self.config["mouse"]["acceleration"])
        x_offset, y_offset = 0, 0
        if "left" in command: x_offset = -amount
        elif "right" in command: x_offset = amount
        elif "up" in command: y_offset = -amount
        elif "down" in command: y_offset = amount
        return x_offset, y_offset

    def _handle_edge_detection(self, x: int, y: int) -> Tuple[int, int]:
        monitor = self._get_active_monitor()
        edge_threshold = self.config["mouse"]["screen_edge_threshold"]
        near_left = x <= monitor['x'] + edge_threshold
        near_right = x >= monitor['x'] + monitor['width'] - edge_threshold
        near_top = y <= monitor['y'] + edge_threshold
        near_bottom = y >= monitor['y'] + monitor['height'] - edge_threshold
        if near_left and self.current_monitor > 0:
            self.current_monitor -= 1
            new_mon = self.monitors[self.current_monitor]
            x = new_mon.x + new_mon.width - edge_threshold
            y = min(max(y, new_mon.y), new_mon.y + new_mon.height)
        elif near_right and self.current_monitor < len(self.monitors) - 1:
            self.current_monitor += 1
            new_mon = self.monitors[self.current_monitor]
            x = new_mon.x + edge_threshold
            y = min(max(y, new_mon.y), new_mon.y + new_mon.height)
        return x, y

    def _handle_window_management(self, command: str) -> Optional[str]:
        try:
            if any(word in command for word in ScreenCommands.MINIMIZE_WINDOW.value):
                keyboard.press_and_release(self.config["window_management"]["minimize_hotkey"])
                return f"{random.choice(self.responses['window_actions'])} Window minimized."
                
            elif any(word in command for word in ScreenCommands.MAXIMIZE_WINDOW.value):
                keyboard.press_and_release(self.config["window_management"]["maximize_hotkey"])
                return f"{random.choice(self.responses['window_actions'])} Window maximized."
                
            elif any(word in command for word in ScreenCommands.CLOSE_WINDOW.value):
                keyboard.press_and_release(self.config["window_management"]["close_hotkey"])
                return f"{random.choice(self.responses['window_actions'])} Window closed."
                
            elif any(word in command for word in ScreenCommands.RESTORE_WINDOW.value):
                keyboard.press_and_release(self.config["window_management"]["restore_hotkey"])
                return f"{random.choice(self.responses['window_actions'])} Window restored."
                
            return None
        except Exception as e:
            return f"{self._jarvis_response('errors')} Window operation failed: {str(e)}"

    def _handle_web_services(self, command: str) -> Optional[str]:
        try:
            if "instagram" in command:
                if "post" in command or "upload" in command:
                    webbrowser.open("https://www.instagram.com/create/story")
                    return f"{self._jarvis_response('acknowledgments')} Opening Instagram story."
                elif "messages" in command or "dm" in command:
                    webbrowser.open("https://www.instagram.com/direct/inbox/")
                    return f"{self._jarvis_response('acknowledgments')} Opening Instagram DMs."
                else: 
                    webbrowser.open(self.applications["instagram"])
                    return f"{self._jarvis_response('acknowledgments')} Launching Instagram."

            elif "chatgpt" in command or "chat gpt" in command:
                if "new chat" in command: 
                    webbrowser.open("https://chat.openai.com/?model=text-davinci-002-render-sha")
                else: 
                    webbrowser.open(self.applications["chatgpt"])
                return f"{self._jarvis_response('acknowledgments')} Opening ChatGPT."

            elif "deepseek" in command or "deep seek" in command:
                webbrowser.open(self.applications["deepseek"])
                return f"{self._jarvis_response('acknowledgments')} Accessing DeepSeek."

            elif any(word in command for word in ["search", "look up", "find"]):
                query = command.split("for")[-1].strip() if "for" in command else command.split("search")[-1].strip()
                if not query: 
                    return "What should I search for, sir?"
                if "on youtube" in command:
                    url = self.config["web_services"]["youtube"].format(query=query.replace("on youtube", "").strip())
                    webbrowser.open(url)
                    return f"{self._jarvis_response('acknowledgments')} Searching YouTube: {query}."
                elif "on wikipedia" in command:
                    url = self.config["web_services"]["wikipedia"].format(query=query.replace("on wikipedia", "").strip())
                    webbrowser.open(url)
                    return f"{self._jarvis_response('acknowledgments')} Searching Wikipedia: {query}."
                elif "on maps" in command or "location" in command:
                    url = self.config["web_services"]["google_maps"].format(query=query.replace("on maps", "").strip())
                    webbrowser.open(url)
                    return f"{self._jarvis_response('acknowledgments')} Searching maps: {query}."
                else:
                    url = self.config["web_services"]["google_search"].format(query=query)
                    webbrowser.open(url)
                    return f"{self._jarvis_response('acknowledgments')} Searching Google: {query}."
            return None
        except Exception as e:
            return f"{self._jarvis_response('error')} Web error: {str(e)}"

    def _handle_text_deletion(self, command: str) -> str:
        try:
            count = 1
            words = command.split()
            for word in words:
                if word.isdigit(): 
                    count = int(word)
                    break
            if "word" in command:
                for _ in range(count): 
                    keyboard.press_and_release('ctrl+backspace')
                return f"{self._jarvis_response('acknowledgments')} Deleted {count} word{'s' if count > 1 else ''}."
            elif "line" in command:
                keyboard.press_and_release('end, shift+home, backspace')
                return f"{self._jarvis_response('acknowledgments')} Line erased."
            elif "all" in command or "everything" in command:
                keyboard.press_and_release('ctrl+a, backspace')
                return f"{self._jarvis_response('acknowledgments')} All content deleted."
            elif "forward" in command:
                for _ in range(count): 
                    keyboard.press_and_release('delete')
                return f"{self._jarvis_response('acknowledgments')} Removed {count} character{'s' if count > 1 else ''} forward."
            else:
                for _ in range(count): 
                    keyboard.press_and_release('backspace')
                return f"{self._jarvis_response('acknowledgments')} Deleted {count} character{'s' if count > 1 else ''}."
        except Exception as e:
            return f"{self._jarvis_response('error')} Deletion failed: {str(e)}"

    def _handle_applications(self, command: str) -> Optional[str]:
        action = None
        if any(word in command for word in ["open", "launch", "start"]): 
            action = "open"
        elif any(word in command for word in ["close", "terminate", "exit"]): 
            action = "close"
        elif any(word in command for word in ["switch", "change", "go to"]): 
            action = "switch"
        if not action: 
            return None
            
        for app_name, app_path in self.applications.items():
            if app_name in command:
                try:
                    if action == "open":
                        if app_path.startswith("http"): 
                            webbrowser.open(app_path)
                        elif "{" in app_path:
                            formatted_path = app_path.format(version="2023")
                            if os.path.exists(formatted_path):
                                os.startfile(os.path.expandvars(formatted_path))
                            else:
                                base_dir = os.path.dirname(formatted_path.split("{")[0])
                                if os.path.exists(base_dir):
                                    versions = [d for d in os.listdir(base_dir) if d.startswith("20")]
                                    if versions:
                                        latest = sorted(versions)[-1]
                                        final_path = app_path.format(version=latest)
                                        os.startfile(os.path.expandvars(final_path))
                        else:
                            os.startfile(os.path.expandvars(app_path))
                        return f"{self._jarvis_response('acknowledgments')} Opening {app_name}."
                    elif action == "close":
                        for proc in psutil.process_iter(attrs=['pid', 'name']):
                            if app_name.lower() in proc.info['name'].lower():
                                proc.kill()
                                return f"{self._jarvis_response('acknowledgments')} Closed {app_name}."
                        return f"{app_name} is not running, sir."
                    elif action == "switch":
                        windows = gw.getWindowsWithTitle(app_name)
                        if windows: 
                            windows[0].activate()
                            return f"{self._jarvis_response('acknowledgments')} Switched to {app_name}."
                        return f"Couldn't find {app_name} window."
                except Exception as e:
                    return f"{self._jarvis_response('error')} Failed to {action} {app_name}: {str(e)}"
        return f"Application not recognized, sir."

    def _handle_special_app_commands(self, command: str) -> Optional[str]:
        try:
            if "file explorer" in command or "explorer" in command:
                path = None
                if "desktop" in command: path = os.path.expanduser("~/Desktop")
                elif "documents" in command: path = os.path.expanduser("~/Documents")
                elif "downloads" in command: path = os.path.expanduser("~/Downloads")
                elif "pictures" in command: path = os.path.expanduser("~/Pictures")
                
                if path:
                    os.startfile(path)
                    return f"{self._jarvis_response('acknowledgments')} Opening {os.path.basename(path)} folder."
            
            if "camera" in command:
                os.system("start microsoft.windows.camera:")
                return f"{self._jarvis_response('acknowledgments')} Launching Camera."
            
            if "vs code" in command or "visual studio code" in command:
                if "open project" in command or "open folder" in command:
                    folder = command.split("project")[-1].strip() if "project" in command else command.split("folder")[-1].strip()
                    if folder and os.path.exists(folder):
                        os.system(f'code "{folder}"')
                        return f"{self._jarvis_response('acknowledgments')} Opening VS Code with {folder}."
            
            if "photoshop" in command:
                if "open" in command and ("image" in command or "photo" in command):
                    file_path = command.split("open")[-1].strip()
                    if os.path.exists(file_path):
                        os.startfile(file_path)
                        return f"{self._jarvis_response('acknowledgments')} Opening {file_path} in Photoshop."
            
            return None
        except Exception as e:
            return f"{self._jarvis_response('error')} Special app command failed: {str(e)}"

    def _handle_file_operations(self, command: str) -> Optional[str]:
        try:
            if "open file" in command:
                file_path = command.split("open file")[-1].strip()
                if os.path.exists(file_path):
                    os.startfile(file_path)
                    return f"{self._jarvis_response('acknowledgments')} Opening {os.path.basename(file_path)}."
            
            if "delete file" in command:
                file_path = command.split("delete file")[-1].strip()
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return f"{self._jarvis_response('acknowledgments')} Deleted {os.path.basename(file_path)}."
            
            if "rename file" in command:
                parts = command.split("rename file")[-1].strip().split(" to ")
                if len(parts) == 2:
                    old_path, new_name = parts[0].strip(), parts[1].strip()
                    if os.path.exists(old_path):
                        dir_name = os.path.dirname(old_path)
                        new_path = os.path.join(dir_name, new_name)
                        os.rename(old_path, new_path)
                        return f"{self._jarvis_response('acknowledgments')} Renamed to {new_name}."
            
            return None
        except Exception as e:
            return f"{self._jarvis_response('error')} File operation failed: {str(e)}"

    def _execute_screen_command(self, command: str) -> Optional[str]:
        try:
            if any(word in command for word in ScreenCommands.PRECISION.value):
                self.precision_mode = not self.precision_mode
                status = "activated" if self.precision_mode else "deactivated"
                return f"Precision mode {status}. {self._jarvis_response('acknowledgments')}"

            if any(word in command for word in ScreenCommands.MOVE.value):
                if "to" in command:
                    coord_part = command.split("to")[1].strip()
                    monitor = self._get_active_monitor()
                    if "center" in coord_part:
                        x, y = monitor['center_x'], monitor['center_y']
                        pyautogui.moveTo(x, y, duration=0.3)
                        return f"{self._jarvis_response('acknowledgments')} Cursor centered."
                    elif "corner" in coord_part:
                        if "top left" in coord_part: x, y = monitor['x'] + 10, monitor['y'] + 10
                        elif "top right" in coord_part: x, y = monitor['x'] + monitor['width'] - 10, monitor['y'] + 10
                        elif "bottom left" in coord_part: x, y = monitor['x'] + 10, monitor['y'] + monitor['height'] - 10
                        elif "bottom right" in coord_part: x, y = monitor['x'] + monitor['width'] - 10, monitor['y'] + monitor['height'] - 10
                        pyautogui.moveTo(x, y, duration=0.3)
                        return f"{self._jarvis_response('acknowledgments')} Positioned at {coord_part.strip()}."
                    else:
                        coords = [int(p) for p in coord_part.split() if p.isdigit()]
                        if len(coords) >= 2:
                            x = min(max(coords[0], monitor['x']), monitor['x'] + monitor['width'])
                            y = min(max(coords[1], monitor['y']), monitor['y'] + monitor['height'])
                            x, y = self._handle_edge_detection(x, y)
                            pyautogui.moveTo(x, y, duration=0.3)
                            return f"{self._jarvis_response('acknowledgments')} Moved to {x}, {y}."
                x_offset, y_offset = self._calculate_movement(command)
                if x_offset or y_offset:
                    directions = []
                    if x_offset < 0: directions.append(f"{abs(x_offset)} pixels left")
                    elif x_offset > 0: directions.append(f"{abs(x_offset)} pixels right")
                    if y_offset < 0: directions.append(f"{abs(y_offset)} pixels up")
                    elif y_offset > 0: directions.append(f"{abs(y_offset)} pixels down")
                    pyautogui.moveRel(x_offset, y_offset, duration=0.1)
                    return f"{self._jarvis_response('acknowledgments')} Movement: {', '.join(directions)}."

            if any(word in command for word in ScreenCommands.RIGHT_CLICK.value): 
                pyautogui.rightClick()
                return f"{self._jarvis_response('acknowledgments')} Right click executed."
            elif any(word in command for word in ScreenCommands.DOUBLE_CLICK.value): 
                pyautogui.doubleClick()
                return f"{self._jarvis_response('acknowledgments')} Double click initiated."
            elif any(word in command for word in ScreenCommands.MIDDLE_CLICK.value): 
                pyautogui.middleClick()
                return f"{self._jarvis_response('acknowledgments')} Middle click activated."
            elif any(word in command for word in ScreenCommands.CLICK.value): 
                pyautogui.click()
                return f"{self._jarvis_response('acknowledgments')} Primary click executed."

            if any(word in command for word in ScreenCommands.DRAG.value):
                if self.drag_start is None:
                    self.drag_start = pyautogui.position()
                    return f"{self._jarvis_response('acknowledgments')} Drag sequence initialized."
                pyautogui.dragTo(*pyautogui.position(), duration=self.config["sensitivity"]["drag_speed"], button='left')
                self.drag_start = None
                return f"{self._jarvis_response('acknowledgments')} Drag operation completed."

            if any(word in command for word in ScreenCommands.SCROLL.value):
                scroll_amount = self.config["sensitivity"]["scroll"]
                if "up" in command: 
                    pyautogui.scroll(scroll_amount)
                    return f"{self._jarvis_response('acknowledgments')} Scrolled up {scroll_amount} units."
                elif "down" in command: 
                    pyautogui.scroll(-scroll_amount)
                    return f"{self._jarvis_response('acknowledgments')} Scrolled down {scroll_amount} units."

            if any(word in command for word in ScreenCommands.TYPE.value):
                text = command.split("type")[1].strip()
                if text: 
                    pyautogui.write(text, interval=0.1)
                    return f"{self._jarvis_response('acknowledgments')} Text entered: '{text}'."

            if any(word in command for word in ScreenCommands.KEYPRESS.value):
                key = command.split("key")[1].strip()
                if key: 
                    pyautogui.press(key)
                    return f"{self._jarvis_response('acknowledgments')} {key.capitalize()} key pressed."

            return None
        except Exception as e:
            return f"{self._jarvis_response('error')} {str(e)}"

    def execute_command(self, command: str) -> Optional[str]:
        if not command:
            return None
            
        self.last_command = command
        
        if self.config["wake_word"] in command:
            command = command.replace(self.config["wake_word"], "").strip()
        
        if self.awaiting_confirmation:
            if any(phrase in command for phrase in self.config["security"]["confirmation_phrases"]):
                self.awaiting_confirmation = False
                return self._execute_confirmed_command(self.pending_command)
            else:
                self.awaiting_confirmation = False
                return "Command canceled."
        
        sensitive_commands = [
            "lock computer", "shutdown computer", 
            "restart computer", "delete file"
        ]
        
        if (any(cmd in command for cmd in sensitive_commands) and 
            self.config["security"]["require_confirmation"]):
            self.pending_command = command
            self.awaiting_confirmation = True
            return random.choice(self.responses['confirmations'])
        
        window_result = self._handle_window_management(command)
        if window_result:
            return window_result

        if "screen control" in command:
            self.screen_control_active = not self.screen_control_active
            return (self._jarvis_response('screen_control') 
                    if self.screen_control_active 
                    else "Screen control deactivated.")

        if self.screen_control_active:
            result = self._execute_screen_command(command)
            if result: 
                return result
            elif "stop screen control" in command: 
                self.screen_control_active = False
                return "Screen control deactivated."

        web_result = self._handle_web_services(command)
        if web_result: 
            return web_result

        if any(word in command for word in ["erase", "delete"]): 
            return self._handle_text_deletion(command)

        app_result = self._handle_applications(command)
        if app_result: 
            return app_result

        special_app_result = self._handle_special_app_commands(command)
        if special_app_result: 
            return special_app_result

        file_op_result = self._handle_file_operations(command)
        if file_op_result: 
            return file_op_result

        if any(word in command for word in ScreenCommands.LOCK.value): 
            ctypes.windll.user32.LockWorkStation()
            return f"{self._jarvis_response('acknowledgments')} Workstation secured."
            
        elif any(word in command for word in ScreenCommands.SHUTDOWN.value): 
            os.system("shutdown /s /t 5")
            return f"{self._jarvis_response('acknowledgments')} Initiating shutdown sequence."
            
        elif any(word in command for word in ScreenCommands.RESTART.value): 
            os.system("shutdown /r /t 5")
            return f"{self._jarvis_response('acknowledgments')} Preparing system reboot."

        elif "what is the time" in command: 
            return f"The current time is {datetime.now().strftime('%I:%M %p')}."
            
        elif "what is today's date" in command: 
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

        elif "increase volume" in command: 
            keyboard.press_and_release("volume up")
            return f"{self._jarvis_response('acknowledgments')} Volume increased."
            
        elif "decrease volume" in command: 
            keyboard.press_and_release("volume down")
            return f"{self._jarvis_response('acknowledgments')} Volume decreased."
            
        elif "mute volume" in command: 
            keyboard.press_and_release("volume mute")
            return f"{self._jarvis_response('acknowledgments')} Audio muted."

        elif any(cmd in command for cmd in ["terminate", "exit", "quit", "goodbye"]):
            self._shutdown()
            return None

        return None

    def _execute_confirmed_command(self, command: str) -> str:
        if any(word in command for word in ScreenCommands.LOCK.value): 
            ctypes.windll.user32.LockWorkStation()
            return f"{self._jarvis_response('acknowledgments')} Workstation locked as requested."
            
        elif any(word in command for word in ScreenCommands.SHUTDOWN.value): 
            os.system("shutdown /s /t 5")
            return f"{self._jarvis_response('acknowledgments')} Confirmed. System will shutdown in 5 seconds."
            
        elif any(word in command for word in ScreenCommands.RESTART.value): 
            os.system("shutdown /r /t 5")
            return f"{self._jarvis_response('acknowledgments')} Confirmed. Rebooting system."
            
        elif "delete file" in command:
            file_path = command.split("delete file")[-1].strip()
            if os.path.exists(file_path):
                os.remove(file_path)
                return f"{self._jarvis_response('acknowledgments')} Permanently deleted {os.path.basename(file_path)}."
            return "File not found."

        return "Confirmed command executed."

    def _shutdown(self):
        try: 
            self.engine.stop()
        except: 
            pass
        self.speak(self._jarvis_response('shutdown'))
        sys.exit(0)

    def process_input(self, command: str):
        if not command:
            return
        response = self.execute_command(command)
        if response:
            self.speak(response)
        elif self.screen_control_active:
            self.speak("Screen command not recognized", is_error=True)
        else:
            self.speak("Command not recognized", is_error=True)

    def run_screen_control_listener(self):
        self.speak("Screen control active. Awaiting commands.")
        while self.screen_control_active:
            command = self.listen(timeout=1)
            if command:
                self.process_input(command)
            time.sleep(0.1)

    def run(self):
        self._play_sound('startup')
        self.speak(self._jarvis_response('startup'))
        while True:
            try:
                command = self.listen()
                if command:
                    if "how are you" in command.lower():
                        self.speak("All systems optimal, sir.")
                    elif "joke" in command.lower():
                        self.speak(random.choice(self.responses['humor']))
                    elif any(word in command.lower() for word in ["thank you", "thanks"]):
                        self.speak("You're welcome, sir.")
                    elif "status" in command.lower():
                        self.speak(random.choice(self.responses['system_status']))
                    else:
                        self.process_input(command)
                    
                    if random.random() < 0.05:
                        remarks = ["System temperature optimal.", "Response time at 98.7% efficiency."]
                        threading.Timer(1.5, lambda: self.speak(random.choice(remarks))).start()
                
                if self.screen_control_active:
                    self.run_screen_control_listener()
                
                time.sleep(0.5)
            except KeyboardInterrupt:
                self.speak(self._jarvis_response('shutdown'))
                sys.exit(0)
            except Exception as e:
                self.speak(f"{self._jarvis_response('errors')} Error: {str(e)}", is_error=True)
                continue

if __name__ == "__main__":
    try:
        assistant = SystemJarvis()
        assistant.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)