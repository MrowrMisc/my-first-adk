from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget


def main() -> None:
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Hello World")
    layout = QVBoxLayout()
    button = QPushButton("Click Me")
    layout.addWidget(button)
    window.setLayout(layout)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
