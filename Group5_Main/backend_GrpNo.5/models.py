from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Camera(db.Model):
    __tablename__ = 'cameras'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    zone = db.Column(db.String(100), nullable=True)
    stream_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_heartbeat = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'zone': self.zone,
            'stream_url': self.stream_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None
        }

class Zone(db.Model):
    __tablename__ = 'zones'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    max_capacity = db.Column(db.Integer, nullable=True)
    threshold_warning = db.Column(db.Float, default=0.6)  # 60% density
    threshold_critical = db.Column(db.Float, default=0.8)  # 80% density
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'max_capacity': self.max_capacity,
            'threshold_warning': self.threshold_warning,
            'threshold_critical': self.threshold_critical
        }

class Detection(db.Model):
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('cameras.id'), nullable=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    person_count = db.Column(db.Integer, nullable=False)
    density_percentage = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(500), nullable=True)
    video_path = db.Column(db.String(500), nullable=True)
    processed_image_path = db.Column(db.String(500), nullable=True)
    detection_metadata = db.Column(db.JSON, nullable=True)  # Store bounding boxes, confidence scores, etc.
    
    camera = db.relationship('Camera', backref='detections')
    zone = db.relationship('Zone', backref='detections')
    
    def to_dict(self):
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'zone_id': self.zone_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'person_count': self.person_count,
            'density_percentage': self.density_percentage,
            'image_path': self.image_path,
            'video_path': self.video_path,
            'processed_image_path': self.processed_image_path,
            'metadata': self.detection_metadata  # Keep 'metadata' in API response for compatibility
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('cameras.id'), nullable=True)
    detection_id = db.Column(db.Integer, db.ForeignKey('detections.id'), nullable=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 'density', 'movement', 'camera', etc.
    severity = db.Column(db.String(20), nullable=False)  # 'info', 'warning', 'critical', 'success'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    zone = db.relationship('Zone', backref='alerts')
    camera = db.relationship('Camera', backref='alerts')
    detection = db.relationship('Detection', backref='alerts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'zone_id': self.zone_id,
            'camera_id': self.camera_id,
            'detection_id': self.detection_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_resolved': self.is_resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
