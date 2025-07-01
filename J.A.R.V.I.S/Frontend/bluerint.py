from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, 
                            QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, 
                            QLabel, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, 
                        QPixmap, QTextBlockFormat, QLinearGradient, QBrush, QPen,
                        QRadialGradient)
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")
old_chat_message = ""

# Directory paths
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whom', 'can you', "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    try:
        with open(TempDirectoryPath('Mic.data'), 'w', encoding='utf-8') as file:
            file.write(Command)
    except:
        pass

def GetMicrophoneStatus():
    try:
        with open(TempDirectoryPath('Mic.data'), 'r', encoding='utf-8') as file:
            Status = file.read().strip()
        return Status
    except:
        return "True"

def SetAsssistantStatus(Status):
    try:
        with open(rf'{TempDirPath}\Status.data', 'w', encoding='utf-8') as file:
            file.write(Status)
    except:
        pass

def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
            Status = file.read()
        return Status
    except:
        return ""

def MicButtonInitiated():
    print("Mic Button ON - Listening Started")
    SetMicrophoneStatus("True")

def MicButtonClosed():
    print("Mic Button OFF - Listening Stopped") 
    SetMicrophoneStatus("False")

def GraphicsDirectoryPath(Filename):
    path = rf'{GraphicsDirPath}\{Filename}'
    return path

def TempDirectoryPath(Filename):
    path = rf'{TempDirPath}\{Filename}'
    return path

def ShowTextToScreen(Text):
    try:
        with open(rf'{TempDirPath}\Responses.data', 'w', encoding='utf-8') as file:
            file.write(Text)
    except:
        pass

class MicrophoneButton(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.setCursor(Qt.PointingHandCursor)
        self.is_listening = False
        self.glow_intensity = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 255, 255, 150))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Outer glow rings
        for i in range(3):
            glow_radius = 45 + i * 10
            glow_alpha = int((30 - i * 10) * (self.glow_intensity / 100))
            if self.is_listening:
                glow_color = QColor(0, 255, 100, glow_alpha)
            else:
                glow_color = QColor(0, 150, 255, glow_alpha)
            
            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.rect().center().x() - glow_radius//2, 
                              self.rect().center().y() - glow_radius//2, 
                              glow_radius, glow_radius)
        
        # Main button circle
        if self.is_listening:
            # Active state - Green gradient
            gradient = QRadialGradient(self.rect().center(), 35)
            gradient.setColorAt(0, QColor(0, 255, 100, 220))
            gradient.setColorAt(0.7, QColor(0, 200, 80, 255))
            gradient.setColorAt(1, QColor(0, 150, 60, 255))
            border_color = QColor(0, 255, 100, 200)
        else:
            # Inactive state - Blue gradient
            gradient = QRadialGradient(self.rect().center(), 35)
            gradient.setColorAt(0, QColor(0, 150, 255, 220))
            gradient.setColorAt(0.7, QColor(0, 100, 200, 255))
            gradient.setColorAt(1, QColor(0, 50, 150, 255))
            border_color = QColor(0, 150, 255, 200)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(border_color, 3))
        painter.drawEllipse(self.rect().center().x() - 35, self.rect().center().y() - 35, 70, 70)
        
        # Microphone icon
        painter.setPen(QPen(QColor(255, 255, 255), 4))
        center = self.rect().center()
        
        # Mic body
        painter.drawRoundedRect(center.x() - 10, center.y() - 20, 20, 25, 10, 10)
        # Mic stand
        painter.drawLine(center.x(), center.y() + 5, center.x(), center.y() + 20)
        # Mic base
        painter.drawLine(center.x() - 12, center.y() + 20, center.x() + 12, center.y() + 20)
        
        # Status text
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        status_text = "ON" if self.is_listening else "OFF"
        painter.drawText(center.x() - 10, center.y() + 35, status_text)
    
    def update_animation(self):
        if self.is_listening:
            self.glow_intensity = (self.glow_intensity + 8) % 100
        else:
            self.glow_intensity = max(0, self.glow_intensity - 5)
        self.update()
    
    def mousePressEvent(self, event):
        self.is_listening = not self.is_listening
        print(f"Microphone button clicked - Status: {'ON' if self.is_listening else 'OFF'}")
        
        if self.is_listening:
            MicButtonInitiated()
        else:
            MicButtonClosed()
        
        self.update()
        super().mousePressEvent(event)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 40, 100)
        layout.setSpacing(20)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        
        # Modern chat styling
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 15, 25, 200),
                    stop:1 rgba(25, 25, 40, 200));
                border: 2px solid rgba(0, 255, 255, 50);
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-family: 'Consolas';
                font-size: 14px;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 100);
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 255, 255, 150),
                    stop:1 rgba(0, 150, 255, 150));
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 255, 255, 200),
                    stop:1 rgba(0, 150, 255, 200));
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        layout.addWidget(self.chat_text_edit)

        # Bottom section with GIF and status
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # GIF section
        gif_frame = QFrame()
        gif_frame.setFixedSize(220, 220)
        gif_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 150);
                border: 2px solid rgba(0, 255, 255, 80);
                border-radius: 20px;
            }
        """)
        
        gif_layout = QVBoxLayout(gif_frame)
        gif_layout.setContentsMargins(15, 15, 15, 15)
        
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        
        # Load GIF
        gif_path = rf"{GraphicsDirPath}\Jarvis.gif"
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(180, 150))
            self.gif_label.setAlignment(Qt.AlignCenter)
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setText("GIF\nNot Found")
            self.gif_label.setStyleSheet("color: white; font-size: 14px; text-align: center;")
            self.gif_label.setAlignment(Qt.AlignCenter)
        
        gif_layout.addWidget(self.gif_label)

        self.status_label = QLabel("Ready...")
        self.status_label.setStyleSheet("""
            color: rgba(0, 255, 255, 200); 
            font-size: 14px; 
            font-weight: bold;
            text-align: center;
            border: none;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        gif_layout.addWidget(self.status_label)

        bottom_layout.addStretch()
        bottom_layout.addWidget(gif_frame)
        layout.addLayout(bottom_layout)

        self.setStyleSheet("background-color: black;")
        font = QFont("Consolas", 13)
        self.chat_text_edit.setFont(font)

        # Timers for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)  # Check every 100ms

    def loadMessages(self):
        global old_chat_message
        try:
            with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            if messages and messages != old_chat_message:
                self.addMessage(message=messages, color='White')
                old_chat_message = messages
        except FileNotFoundError:
            pass

    def updateStatus(self):
        try:
            with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
                messages = file.read().strip()
            if messages:
                self.status_label.setText(messages)
        except FileNotFoundError:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        cursor.movePosition(cursor.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        
        # Auto scroll to bottom
        scrollbar = self.chat_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(50, 100, 50, 150)
        content_layout.setSpacing(30)

        # Title
        title_label = QLabel(f"Welcome to {Assistantname}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff, stop:1 #0080ff);
                font-size: 32px;
                font-weight: bold;
                font-family: 'Segoe UI';
                margin: 20px;
            }
        """)
        content_layout.addWidget(title_label)

        # GIF container
        gif_container = QFrame()
        gif_container.setFixedSize(600, 450)
        gif_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 255, 15),
                    stop:1 rgba(0, 0, 0, 80));
                border: 3px solid rgba(0, 255, 255, 100);
                border-radius: 30px;
            }
        """)
        
        gif_layout = QVBoxLayout(gif_container)
        gif_layout.setContentsMargins(25, 25, 25, 25)
        
        self.gif_label = QLabel()
        gif_path = rf"{GraphicsDirPath}\Jarvis.gif"
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(540, 380))
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setText("GIF Not Found\nPlace Jarvis.gif in Graphics folder")
            self.gif_label.setStyleSheet("color: white; font-size: 18px; text-align: center;")
        
        self.gif_label.setAlignment(Qt.AlignCenter)
        gif_layout.addWidget(self.gif_label)
        
        content_layout.addWidget(gif_container, alignment=Qt.AlignCenter)

        # Status label
        self.status_label = QLabel("Ready to assist...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 200);
                font-size: 18px;
                font-family: 'Segoe UI';
                margin: 15px;
            }
        """)
        content_layout.addWidget(self.status_label)

        # Microphone button
        self.mic_button = MicrophoneButton()
        content_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        
        # Timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)

    def updateStatus(self):
        try:
            with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
                messages = file.read().strip()
            if messages:
                self.status_label.setText(messages)
        except FileNotFoundError:
            pass

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        chat_section = ChatSection()  
        layout.addWidget(chat_section)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.parent_window = parent
        self.initUI()
        self.offset = None

    def initUI(self):
        self.setFixedHeight(70)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 10)
        main_layout.setSpacing(20)

        # Navigation buttons
        left_layout = QHBoxLayout()
        left_layout.setSpacing(15)
        
        self.home_btn = self.createButton("🏠 Home", self.showInitialScreen)
        self.chat_btn = self.createButton("💬 Chat", self.showMessageScreen)
        
        left_layout.addWidget(self.home_btn)
        left_layout.addWidget(self.chat_btn)

        # Window controls
        right_layout = QHBoxLayout()
        right_layout.setSpacing(10)
        
        self.min_btn = self.createControlButton("–", self.minimizeWindow)
        self.max_btn = self.createControlButton("⬜", self.maximizeWindow)
        self.close_btn = self.createControlButton("✕", self.closeWindow, is_close=True)
        
        right_layout.addWidget(self.min_btn)
        right_layout.addWidget(self.max_btn)
        right_layout.addWidget(self.close_btn)

        main_layout.addLayout(left_layout)
        main_layout.addStretch()
        main_layout.addLayout(right_layout)

    def createButton(self, text, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 100),
                    stop:1 rgba(0, 150, 255, 150));
                color: white;
                padding: 12px 20px;
                border-radius: 15px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 14px;
                border: 2px solid rgba(0, 255, 255, 50);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 150),
                    stop:1 rgba(0, 150, 255, 200));
                border: 2px solid rgba(0, 255, 255, 100);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 150, 255, 200),
                    stop:1 rgba(0, 100, 200, 250));
            }
        """)
        return btn

    def createControlButton(self, text, callback, is_close=False):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(40, 40)
        
        if is_close:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 50, 50, 150);
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 16px;
                    border: 2px solid rgba(255, 100, 100, 100);
                }
                QPushButton:hover {
                    background: rgba(255, 50, 50, 200);
                    border: 2px solid rgba(255, 100, 100, 150);
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(100, 100, 100, 150);
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 14px;
                    border: 2px solid rgba(150, 150, 150, 100);
                }
                QPushButton:hover {
                    background: rgba(100, 100, 100, 200);
                    border: 2px solid rgba(150, 150, 150, 150);
                }
            """)
        return btn

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Glassmorphism background
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(0, 0, 0, 180))
        gradient.setColorAt(0.5, QColor(0, 255, 255, 50))
        gradient.setColorAt(1, QColor(0, 0, 0, 180))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 255, 255, 100), 2))
        painter.drawRoundedRect(self.rect().adjusted(5, 5, -5, -5), 25, 25)

    def minimizeWindow(self):
        self.parent_window.showMinimized()

    def maximizeWindow(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

    def closeWindow(self):
        print("Application closing...")
        self.parent_window.close()

    def showMessageScreen(self):
        print("Switching to Message Screen")
        self.stacked_widget.setCurrentIndex(1)

    def showInitialScreen(self):
        print("Switching to Initial Screen")
        self.stacked_widget.setCurrentIndex(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.parent_window.move(self.parent_window.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Create stacked widget
        stacked_widget = QStackedWidget(self)
        
        # Add screens
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 0, 0, 255),
                    stop:0.3 rgba(10, 10, 20, 255),
                    stop:0.7 rgba(10, 10, 20, 255),
                    stop:1 rgba(0, 0, 0, 255));
            }
        """)
        
        # Add top bar
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        
        print("GUI Initialized Successfully!")
        print("Mic button ready - Click to toggle ON/OFF")

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Ensure directories exist
    os.makedirs(TempDirPath, exist_ok=True)
    os.makedirs(GraphicsDirPath, exist_ok=True)
    
    # Initialize files
    try:
        SetMicrophoneStatus("False")
        SetAsssistantStatus("Ready...")
    except:
        pass
    
    window = MainWindow()
    window.show()
    
    print("Application started - Backend connections active!")
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()