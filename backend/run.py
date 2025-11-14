import os
from flask import Flask
from flask_cors import CORS
from config import Config
from app.models import db
from app.controllers import bp as main_bp
from app.scheduler import init_scheduler
from flask_migrate import Migrate
from app.controllers import set_global_app

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for Next.js frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "https://*.vercel.app",
                "https://your-domain.com"
            ],
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # init db
    db.init_app(app)
    Migrate(app, db)
    # register blueprint controllers
    app.register_blueprint(main_bp)
    return app

app = create_app()
set_global_app(app)

# Only enable scheduler if environment variable ENABLE_SCHEDULER is set or default to True for simplicity
if os.getenv("ENABLE_SCHEDULER", "1") == "1":
    init_scheduler(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)