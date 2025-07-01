from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat, QLinearGradient , QBrush 
from PyQt5.QtCore import Qt, QSize, QTimer , QEvent
from dotenv import dotenv_values
import sys
import os
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
old_chat_message = ""
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
    query_words  = new_query.split()
    question_words = ['how','what','who','where','when','why','which','whom','can you',"what's", "where's","how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(TempDirectoryPath('Mic.data'), 'w', encoding='utf-8') as file:
        file.write(Command)
    
def GetMicrophoneStatus():
    
    with open(TempDirectoryPath('Mic.data'), 'r', encoding='utf-8') as file:
        Status = file.read().strip()
    return Status

def SetAsssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data','w',encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
        Status = file.read()
    return Status
    
def MicButtonInitiated():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    path = rf'{GraphicsDirPath}\{Filename}'
    return path


def TempDirectoryPath(Filename):
    path = rf'{TempDirPath}\{Filename}'
    return path

def ShowTextToScreen(Text):
    with open (rf'{TempDirPath}\Responses.data','w', encoding='utf-8') as file:
        file.write(Text)


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

        
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        
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

        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)  

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
        
        scrollbar = self.chat_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        self.setFixedSize(screen_width, screen_height)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 0, 0, 255),
                    stop:0.3 rgba(5, 5, 15, 255),
                    stop:0.7 rgba(5, 5, 15, 255),
                    stop:1 rgba(0, 0, 0, 255));
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 150)
        main_layout.setSpacing(30)

        # === Title Label ===
        title_label = QLabel(f"Welcome to {Assistantname}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff, stop:1 #0080ff);
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI';
                margin-top: 30px;
            }
        """)

        gif_container = QFrame()
        gif_container.setFixedSize(600, 500)
        gif_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 255, 255, 10),
                    stop:1 rgba(0, 0, 0, 50));
                border: 2px solid rgba(0, 255, 255, 50);
                border-radius: 25px;
            }
        """)
        gif_layout = QVBoxLayout(gif_container)
        gif_layout.setContentsMargins(20, 20, 20, 20)

        self.gif_label = QLabel()
        movie = QMovie(GraphicsDirPath + r'\Jarvis.gif')
        movie.setScaledSize(QSize(550, 550))
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_layout.addWidget(self.gif_label)

        # === Status Label ===
        self.label = QLabel("Status: Loading...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 180);
                font-size: 16px;
                font-family: 'Segoe UI';
            }
        """)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(100, 100)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 255, 255, 30);
                border: 2px solid rgba(0, 255, 255, 80);
                border-radius: 50px;
            }
            QLabel:hover {
                background-color: rgba(0, 255, 255, 60);
                border: 2px solid rgba(0, 255, 255, 150);
            }
        """)

        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

        
        main_layout.addWidget(title_label)
        main_layout.addWidget(gif_container, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

    def SpeechRecogText(self):
        try:
            with open(TempDirPath + r'\Status.data', 'r', encoding='utf-8') as file:
                messages = file.read().strip()
                self.label.setText(messages)
        except FileNotFoundError:
            self.label.setText("Status file not found.")

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirPath + r'\Mic_on.png', 60, 60)
            MicButtonInitiated()
        else:
            self.load_icon(GraphicsDirPath + r'\Mic_off.png', 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()  
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.parent_window = parent
        self.initUI()
        self.installEventFilter(self)

    def initUI(self):
        self.setFixedHeight(60)
        self.setStyleSheet("background-color: transparent;")

       
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 0, 10, 0)
        main_layout.setSpacing(0)

  
        left_layout = QHBoxLayout()
        center_layout = QHBoxLayout()
        right_layout = QHBoxLayout()
        left_layout.setSpacing(10)
        center_layout.setSpacing(15)
        right_layout.setSpacing(10)

        main_layout.addLayout(left_layout)
        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        main_layout.addLayout(right_layout)


        self.addButton("Home", "Home.png", self.showInitialScreen, center_layout)
        self.addButton("Message", "Chats.png", self.showMessageScreen, center_layout)

       
        self.addIconButton("Minimize.png", self.minimizeWindow, right_layout)
        self.maximize_button = self.addIconButton("Maximize.png", self.maximizeWindow, right_layout, is_max=True)
        self.restore_icon = QIcon(GraphicsDirectoryPath('Restore.png'))
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.addIconButton("Close.png", self.closeWindow, right_layout, close_btn=True)

        self.offset = None

    def addButton(self, label, icon_name, callback, layout):
        btn = QPushButton(f"  {label}")
        btn.setIcon(QIcon(GraphicsDirectoryPath(icon_name)))
        btn.clicked.connect(callback)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 255, 255, 40);
                color: white;
                padding: 8px 16px;
                border-radius: 10px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 255, 80);
            }
        """)
        layout.addWidget(btn)

    def addIconButton(self, icon_name, callback, layout, is_max=False, close_btn=False):
        btn = QPushButton()
        btn.setIcon(QIcon(GraphicsDirectoryPath(icon_name)))
        btn.clicked.connect(callback)
        btn.setFlat(True)
        btn.setCursor(Qt.PointingHandCursor)
        if close_btn:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: rgba(255, 0, 0, 100);
                    border-radius: 5px;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: rgba(0, 255, 255, 30);
                    border-radius: 5px;
                }
            """)
        layout.addWidget(btn)
        if is_max:
            return btn

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor(0, 0, 0, 160))
        gradient.setColorAt(1.0, QColor(0, 255, 255, 60))
        painter.fillRect(self.rect(), QBrush(gradient))
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent_window.showMinimized()

    def maximizeWindow(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent_window.showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent_window.close()

    def showMessageScreen(self):
        self.stacked_widget.setCurrentIndex(1)

    def showInitialScreen(self):
        self.stacked_widget.setCurrentIndex(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.parent_window.move(self.parent_window.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter:
            self.setCursor(Qt.OpenHandCursor)
        elif event.type() == QEvent.Leave:
            self.setCursor(Qt.ArrowCursor)
        return super().eventFilter(source, event)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())  