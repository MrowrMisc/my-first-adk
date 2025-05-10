from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import QApplication, QHBoxLayout, QListWidget, QListWidgetItem, QMainWindow, QPushButton, QScrollArea, QTextEdit, QVBoxLayout, QWidget


@dataclass
class Message:
    sender: Literal["user", "ai"]
    text: str


@dataclass
class Session:
    id: str
    messages: list[Message]


class ChatBubble(QWidget):
    def __init__(self, message: Message, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.message = message
        self._build_ui()

    def _build_ui(self) -> None:
        text_widget = QTextEdit(self)
        text_widget.setReadOnly(True)
        text_widget.setFrameStyle(0)
        text_widget.setText(self.message.text)
        text_widget.setMinimumWidth(200)
        text_widget.setMaximumWidth(400)
        text_widget.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        layout = QVBoxLayout(self)
        layout.addWidget(text_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # style via objectName and global QSS
        if self.message.sender == "user":
            self.setObjectName("ChatBubbleUser")
        else:
            self.setObjectName("ChatBubbleAI")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Qt Chat Prototype")
        self.sessions: list[Session] = []
        self._build_ui()
        self._apply_qss()
        self._init_sessions()

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        h_layout = QHBoxLayout(central)
        h_layout.setContentsMargins(8, 8, 8, 8)
        h_layout.setSpacing(8)

        # Session list on left
        self.session_list = QListWidget()
        self.session_list.setFixedWidth(150)
        self.session_list.itemClicked.connect(self._on_session_clicked)
        h_layout.addWidget(self.session_list)

        # Chat area on right
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        # Scrollable chat history
        self.chat_area = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_area)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_area.setLayout(self.chat_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.chat_area)
        right_layout.addWidget(scroll, stretch=1)

        # Input area
        input_row = QWidget()
        input_layout = QHBoxLayout(input_row)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(60)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._on_send)
        input_layout.addWidget(self.input_box, stretch=1)
        input_layout.addWidget(self.send_button)
        right_layout.addWidget(input_row)

        h_layout.addWidget(right_widget, stretch=1)

    def _apply_qss(self) -> None:
        qss = """
        QListWidget {
        }
        QTextEdit#ChatBubbleUser, QWidget#ChatBubbleUser {
            background-color: #dcf8c6;
            border-radius: 8px;
            padding: 4px;
        }
        QTextEdit#ChatBubbleAI, QWidget#ChatBubbleAI {
            border-radius: 8px;
            padding: 4px;
        }
        """
        self.setStyleSheet(qss)

    def _init_sessions(self) -> None:
        # create one default session
        session = Session(id="Session 1", messages=[])
        self.sessions.append(session)
        item = QListWidgetItem(session.id)
        self.session_list.addItem(item)
        self.session_list.setCurrentItem(item)
        self._load_session(0)

    def _on_session_clicked(self, item: QListWidgetItem) -> None:
        index = self.session_list.row(item)
        self._load_session(index)

    def _load_session(self, index: int) -> None:
        # clear chat
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        session = self.sessions[index]
        for msg in session.messages:
            bubble = ChatBubble(msg)
            align = Qt.AlignmentFlag.AlignRight if msg.sender == "user" else Qt.AlignmentFlag.AlignLeft
            self.chat_layout.addWidget(bubble, alignment=align)

    def _on_send(self) -> None:
        text = self.input_box.toPlainText().strip()
        if not text:
            return

        # user message
        user_msg = Message(sender="user", text=text)
        self._add_message(user_msg)

        # clear input
        self.input_box.clear()

        # dummy AI response
        ai_text = f"Echo: {text}"
        ai_msg = Message(sender="ai", text=ai_text)
        self._add_message(ai_msg)

    def _add_message(self, msg: Message) -> None:
        # append to current session model
        current_index = self.session_list.currentRow()
        session = self.sessions[current_index]
        session.messages.append(msg)

        # create bubble and add to UI
        bubble = ChatBubble(msg)
        align = Qt.AlignmentFlag.AlignRight if msg.sender == "user" else Qt.AlignmentFlag.AlignLeft
        self.chat_layout.addWidget(bubble, alignment=align)


def main() -> None:
    app = QApplication([])
    window = MainWindow()
    window.resize(QSize(800, 600))
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
