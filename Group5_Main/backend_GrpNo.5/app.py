from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit
from datetime import timedelta
import os
from dotenv import load_dotenv

from models import db, User, Camera, Detection, Alert, Zone
from auth import auth_bp
from detection_service import DetectionService
from api import api_bp

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///crowd_monitoring.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize detection service
detection_service = DetectionService()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(api_bp, url_prefix='/api')

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'processed'), exist_ok=True)

def init_db():
    """Initialize database tables and default data"""
    with app.app_context():
        db.create_all()
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(email='admin@crowdsense.ai').first():
            from werkzeug.security import generate_password_hash
            admin = User(
                email='admin@crowdsense.ai',
                password_hash=generate_password_hash('admin123'),
                name='Admin User'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin@crowdsense.ai / admin123")

@app.route('/')
def index():
    return jsonify({'message': 'Crowd Monitoring API', 'status': 'running'})

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to CrowdSense API'})

@socketio.on('subscribe_dashboard')
def handle_subscribe_dashboard():
    """Subscribe to dashboard updates"""
    emit('subscribed', {'message': 'Subscribed to dashboard updates'})

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
