# PyQt wrapper for the Flask app
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from threading import Thread
import socket
from app import app  # Import your Flask app

class FlaskThread(Thread):
    def run(self):
        # Using port 5002 to match the one in app.py
        app.run(port=5002, debug=False, use_reloader=False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PromptCrafter Desktop")
        self.setGeometry(100, 100, 1024, 768)
        
        # Check if port is available
        if not self.is_port_free(5002):
            QMessageBox.critical(self, "Error", "Port 5002 is already in use!")
            sys.exit(1)
        
        # Start Flask in background
        self.flask_thread = FlaskThread(daemon=True)
        self.flask_thread.start()
        
        # Set up Qt WebEngine
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://127.0.0.1:5002"))
        
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def is_port_free(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) != 0

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Quit", "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(qt_app.exec_()) 