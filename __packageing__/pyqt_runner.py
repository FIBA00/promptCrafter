# PyQt wrapper for the Flask app
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from threading import Thread
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import after loading .env to ensure correct configuration
from app import create_app, run_development_server, run_production_server

class FlaskThread(Thread):
    def run(self):
        # Check if we should use production server
        env = os.environ.get('FLASK_ENV', 'production')
        
        if env.lower() == 'development':
            # In development mode, set debug to False to avoid reloader conflicts with PyQt
            os.environ['FLASK_DEBUG'] = 'False'
            run_development_server()
        else:
            run_production_server()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PromptCrafter Desktop")
        self.setGeometry(100, 100, 1024, 768)
        
        # Get port from environment
        app_config = create_app().config
        self.port = app_config.get('PORT', 5002)
        
        # Check if port is available
        if not self.is_port_free(self.port):
            QMessageBox.critical(self, "Error", f"Port {self.port} is already in use!")
            sys.exit(1)
        
        # Start Flask in background
        self.flask_thread = FlaskThread(daemon=True)
        self.flask_thread.start()
        
        # Set up Qt WebEngine
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(f"http://127.0.0.1:{self.port}"))
        
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Show server information
        self.setStatusTip(f"Connected to PromptCrafter on port {self.port} ({os.environ.get('FLASK_ENV', 'production')} mode)")

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