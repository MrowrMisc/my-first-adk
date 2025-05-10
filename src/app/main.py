from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QKeyEvent, QTextOption
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow, QPushButton, QScrollArea, QSizePolicy, QTextEdit, QVBoxLayout, QWidget


class InputTextEdit(QTextEdit):
    def __init__(self, send_callback: Callable[[], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.send_callback = send_callback

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.KeyboardKey.Key_Return, Qt.KeyboardKey.Key_Enter) and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.send_callback()
        else:
            super().keyPressEvent(event)


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
        bubble = QTextEdit(self)
        bubble.setReadOnly(True)
        bubble.setFrameStyle(0)
        bubble.setText(self.message.text)
        bubble.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        bubble.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.addWidget(bubble)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("ChatBubbleUser" if self.message.sender == "user" else "ChatBubbleAI")


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
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Session list
        self.session_list = QListWidget()
        self.session_list.setFixedWidth(150)
        self.session_list.itemClicked.connect(self._on_session_clicked)
        main_layout.addWidget(self.session_list)

        # Chat area with scroll
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        self.scroll_content = QWidget()
        self.scroll_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.scroll_content)
        right_layout.addWidget(scroll, stretch=1)

        # Input row
        input_row = QWidget()
        input_layout = QHBoxLayout(input_row)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_box = InputTextEdit(self._on_send)
        self.input_box.setFixedHeight(60)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.input_box, stretch=1)
        input_layout.addWidget(send_btn)
        right_layout.addWidget(input_row)

        main_layout.addWidget(right, stretch=1)

    def _apply_qss(self) -> None:
        qss = """
        QListWidget {
        }
        QWidget#ChatBubbleUser QTextEdit {
            background-color: #333;
            border-radius: 8px;
            padding: 4px;
        }
        QWidget#ChatBubbleAI QTextEdit {
            border-radius: 8px;
            padding: 4px;
        }
        """
        self.setStyleSheet(qss)

    def _init_sessions(self) -> None:
        # Create multiple sessions with fake data
        self.sessions = [
            Session(id="Session 1", messages=[]),
            Session(
                id="Python Help",
                messages=[
                    Message(sender="user", text="How do I create a virtual environment in Python?"),
                    Message(
                        sender="ai",
                        text="You can create a virtual environment using the `venv` module:\n\n```python\npython -m venv myenv\n```\n\nThen activate it:\n- Windows: `myenv\\Scripts\\activate`\n- Mac/Linux: `source myenv/bin/activate`",
                    ),
                    Message(sender="user", text="Thanks! And how do I install packages?"),
                    Message(sender="ai", text="After activating your virtual environment, use pip:\n\n```\npip install package_name\n```\n\nFor example: `pip install requests`"),
                ],
            ),
            Session(
                id="Travel Ideas",
                messages=[
                    Message(sender="user", text="What are some good places to visit in Japan?"),
                    Message(
                        sender="ai",
                        text="Japan has many amazing places to visit! Here are some highlights:\n\n1. Tokyo - Modern metropolis with districts like Shibuya and Shinjuku\n2. Kyoto - Traditional temples, shrines and gardens\n3. Osaka - Known for food and nightlife\n4. Hokkaido - Beautiful nature and skiing\n5. Hiroshima - Historical sites and peace memorial",
                    ),
                    Message(sender="user", text="Which season is best to visit?"),
                    Message(
                        sender="ai",
                        text="Spring (March-May) for cherry blossoms, Fall (Sept-Nov) for autumn colors, and Winter for skiing in Hokkaido. Summer can be hot and humid but good for festivals. Each season offers a unique experience!",
                    ),
                ],
            ),
        ]

        # Populate the session list
        for session in self.sessions:
            item = QListWidgetItem(session.id)
            self.session_list.addItem(item)

        # Select the first session
        self.session_list.setCurrentItem(self.session_list.item(0))
        self._load_session(0)

    def _on_session_clicked(self, item: QListWidgetItem) -> None:
        idx = self.session_list.row(item)
        self._load_session(idx)

    def _load_session(self, index: int) -> None:
        # Clear current chat
        for i in reversed(range(self.scroll_layout.count())):
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        # Show loading message
        loading_label = QLabel("Loading...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setStyleSheet("color: #888; font-style: italic; margin: 20px 0;")
        self.scroll_layout.addWidget(loading_label)

        # Simulate async loading with a timer
        QTimer.singleShot(800, lambda: self._display_session_messages(index, loading_label))

    def _display_session_messages(self, index: int, loading_label: QLabel) -> None:
        # Remove loading label
        loading_label.setParent(None)

        # Display actual messages
        session = self.sessions[index]
        for msg in session.messages:
            bubble = ChatBubble(msg)

            # Create a wrapper widget to handle alignment and width
            wrapper = QWidget()
            wrapper_layout = QHBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(0, 0, 0, 0)
            wrapper_layout.setSpacing(0)

            # Set up alignment based on sender
            bubble.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            if msg.sender == "user":
                # User messages: right-aligned with left margin
                wrapper_layout.addStretch(1)  # Left margin (flexible)
                wrapper_layout.addWidget(bubble, 9)  # Give bubble 90% of space
            else:
                # AI messages: left-aligned with right margin
                wrapper_layout.addWidget(bubble, 9)  # Give bubble 90% of space
                wrapper_layout.addStretch(1)  # Right margin (flexible)

            # Add the wrapper to the main layout
            self.scroll_layout.addWidget(wrapper)

    def _on_send(self) -> None:
        text = self.input_box.toPlainText().strip()
        if not text:
            return
        user_msg = Message(sender="user", text=text)
        self._add_message(user_msg)
        self.input_box.clear()
        ai_msg = Message(sender="ai", text=f"Echo: {text}")
        self._add_message(ai_msg)

    def _add_message(self, msg: Message) -> None:
        idx = self.session_list.currentRow()
        self.sessions[idx].messages.append(msg)

        bubble = ChatBubble(msg)

        # Create a wrapper widget to handle alignment and width
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)

        # Set up alignment based on sender
        bubble.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        if msg.sender == "user":
            # User messages: right-aligned with left margin
            wrapper_layout.addStretch(1)  # Left margin (flexible)
            wrapper_layout.addWidget(bubble, 9)  # Give bubble 90% of space
        else:
            # AI messages: left-aligned with right margin
            wrapper_layout.addWidget(bubble, 9)  # Give bubble 90% of space
            wrapper_layout.addStretch(1)  # Right margin (flexible)

        # Add the wrapper to the main layout
        self.scroll_layout.addWidget(wrapper)


def main() -> None:
    app = QApplication([])
    window = MainWindow()
    window.resize(QSize(800, 600))
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
