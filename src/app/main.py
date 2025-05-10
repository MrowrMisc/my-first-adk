from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QKeyEvent, QTextOption
from PySide6.QtWidgets import QApplication, QHBoxLayout, QListWidget, QListWidgetItem, QMainWindow, QPushButton, QScrollArea, QSizePolicy, QTextEdit, QVBoxLayout, QWidget


class InputTextEdit(QTextEdit):
    def __init__(self, send_callback: Callable[[], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.send_callback = send_callback

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
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
        bubble.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
        self.scroll_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

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
        session = Session(id="Session 1", messages=[])
        self.sessions.append(session)
        item = QListWidgetItem(session.id)
        self.session_list.addItem(item)
        self.session_list.setCurrentItem(item)
        self._load_session(0)

    def _on_session_clicked(self, item: QListWidgetItem) -> None:
        idx = self.session_list.row(item)
        self._load_session(idx)

    def _load_session(self, index: int) -> None:
        # clear
        for i in reversed(range(self.scroll_layout.count())):
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        session = self.sessions[index]
        for msg in session.messages:
            bubble = ChatBubble(msg)
            align = Qt.AlignRight if msg.sender == "user" else Qt.AlignLeft
            self.scroll_layout.addWidget(bubble, alignment=align)

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
        align = Qt.AlignRight if msg.sender == "user" else Qt.AlignLeft
        self.scroll_layout.addWidget(bubble, alignment=align)


def main() -> None:
    app = QApplication([])
    window = MainWindow()
    window.resize(QSize(800, 600))
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
