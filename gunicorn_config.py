import multiprocessing

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Worker settings
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
daemon = False
pidfile = "gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = "logs/error.log"
accesslog = "logs/access.log"
loglevel = "info"

# Process naming
proc_name = "promptcrafter"

# Server hooks
def on_starting(server):
    server.log.info("Starting PromptCrafter server")

def on_exit(server):
    server.log.info("Stopping PromptCrafter server")

# SSL (uncomment and modify with your SSL certificate paths for HTTPS)
# keyfile = "/path/to/privkey.pem"
# certfile = "/path/to/fullchain.pem" 