from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from dotenv import dotenv_values
import sys
import os

# ---------------- CONFIG ----------------
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Jarvis")

current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

os.makedirs(TempDirPath, exist_ok=True)

old_chat_message = ""

# ---------------- UTILS ----------------
def GraphicsDirectoryPath(file):
    return rf"{GraphicsDirPath}\{file}"

def TempDirectoryPath(file):
    return rf"{TempDirPath}\{file}"

def ShowTextToScreen(Text):
    with open(TempDirectoryPath("Responses.data"), "w", encoding='utf-8') as file:
        file.write(Text)

def SetMicrophoneStatus(Command):
    with open(TempDirectoryPath("Mic.data"), "w") as file:
        file.write(Command)

def GetMicrophoneStatus():
    try:
        with open(TempDirectoryPath("Mic.data"), "r") as file:
            return file.read()
    except:
        return "False"

def SetAssistantStatus(Status):
    with open(TempDirectoryPath("Status.data"), "w") as file:
        file.write(Status)

def GetAssistantStatus():
    try:
        with open(TempDirectoryPath("Status.data"), "r") as file:
            return file.read()
    except:
        return "Available..."

# ---------------- 🔥 FIXED MISSING FUNCTIONS ----------------
def AnswerModifier(text):
    if not text:
        return ""
    return text.strip()

def QueryModifier(query):
    if not query:
        return ""
    return query.strip().lower()

def GetAssistantStatus():
    try:
        with open(TempDirectoryPath("Status.data"), "r") as file:
            return file.read()
    except:
        return "Available..."

# ---------------- CHAT ----------------
class ChatSection(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setStyleSheet("background:black;color:#00ffff;border:none;")
        layout.addWidget(self.chat_text_edit)

        self.label = QLabel("")
        self.label.setStyleSheet("color:white;font-size:14px;")
        layout.addWidget(self.label)

        self.gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        movie.setScaledSize(QSize(500, 300))
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(300)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath("Responses.data"), "r") as file:
                messages = file.read()
        except:
            return

        if messages and messages != old_chat_message:
            self.chat_text_edit.setText(messages)
            old_chat_message = messages

    def updateStatus(self):
        try:
            with open(TempDirectoryPath("Status.data"), "r") as file:
                self.label.setText(file.read())
        except:
            pass

# ---------------- INITIAL SCREEN ----------------
class InitialScreen(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        gif = QLabel()
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        movie.setScaledSize(QSize(800, 450))
        gif.setMovie(movie)
        movie.start()

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath("Mic_on.png")).scaled(70, 70))
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.toggled = True
        self.icon_label.mousePressEvent = self.toggle_icon

        layout.addWidget(gif, alignment=Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        self.setStyleSheet("background:black;")

    def toggle_icon(self, event):
        self.toggled = not self.toggled

        if self.toggled:
            self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath("Mic_on.png")).scaled(70, 70))
            SetMicrophoneStatus("True")
            SetAssistantStatus("Listening...")
        else:
            self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath("Mic_off.png")).scaled(70, 70))
            SetMicrophoneStatus("False")
            SetAssistantStatus("Paused")

# ---------------- MESSAGE SCREEN ----------------
class MessageScreen(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(ChatSection())
        self.setStyleSheet("background:black;")

# ---------------- TOP BAR ----------------
class CustomTopBar(QWidget):

    def __init__(self, parent, stack):
        super().__init__()
        self.parent = parent
        self.stack = stack

        layout = QHBoxLayout(self)

        title = QLabel(f"{Assistantname} AI")
        title.setStyleSheet("color:black;font-size:18px;")

        home = QPushButton("Home")
        chat = QPushButton("Chat")

        home.clicked.connect(lambda: stack.setCurrentIndex(0))
        chat.clicked.connect(lambda: stack.setCurrentIndex(1))

        min_btn = QPushButton("-")
        max_btn = QPushButton("⬜")
        close_btn = QPushButton("X")

        min_btn.clicked.connect(parent.showMinimized)
        max_btn.clicked.connect(self.toggle_max)
        close_btn.clicked.connect(parent.close)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(home)
        layout.addWidget(chat)
        layout.addStretch()
        layout.addWidget(min_btn)
        layout.addWidget(max_btn)
        layout.addWidget(close_btn)

        self.setStyleSheet("background:white;")

    def toggle_max(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

# ---------------- MAIN WINDOW ----------------
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.stack = QStackedWidget()
        self.stack.addWidget(InitialScreen())
        self.stack.addWidget(MessageScreen())

        self.setCentralWidget(self.stack)

        self.topbar = CustomTopBar(self, self.stack)
        self.setMenuWidget(self.topbar)

        self.setStyleSheet("background:black;")
        self.showMaximized()

# ---------------- RUN ----------------
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()