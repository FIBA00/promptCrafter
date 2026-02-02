# PromptCrafter Environment Configuration

# Application Environment: development or production
FLASK_ENV=production

# Debug mode (True/False) - only used in development
FLASK_DEBUG=False

# Secret key for sessions and security
# In production, change this to a strong random value
SECRET_KEY=change-me-in-production-qj89$@#$9dh

# Database URI
# SQLite database by default
DATABASE_URL=postgresql://postgres:123456789@localhost/promptcrafter_db

# Server port (used by both Flask and Waitress)
PORT=5002

# Waitress server settings
WAITRESS_THREADS=4
WAITRESS_HOST=0.0.0.0 
MY_IP=196.189.12.161
# ssh -i azure-remote-ollama_key.pem \-L 11434:127.0.0.1:11434 \azureuser@172.209.217.71
OLLAMA_HOST=http://127.0.0.1:5000
OLLAMA_MODEL=phi3:mini
OLLAMA_TIMEOUT=300


