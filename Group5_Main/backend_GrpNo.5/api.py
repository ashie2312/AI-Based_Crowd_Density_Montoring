from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, Camera, Detection, Alert, Zone
from detection_service import DetectionService
from datetime import datetime, timedelta
import os
import json

api_bp = Blueprint('api', __name__)
detection_service = DetectionService()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== Dashboard Endpoints ====================

@api_bp.route('/dashboard/metrics', methods=['GET'])
@jwt_required()
def get_dashboard_metrics():
    """Get dashboard metrics (total attendance, avg density, alerts, cameras)"""
    try:
        # Get time range (default: last 24 hours)
        hours = request.args.get('hours', 24, type=int)
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Total attendance (sum of all person counts in last period)
        recent_detections = Detection.query.filter(
            Detection.timestamp >= time_threshold
        ).all()
        
        total_attendance = sum(d.person_count for d in recent_detections)
        
        # Previous period for comparison
        prev_threshold = time_threshold - timedelta(hours=hours)
        prev_detections = Detection.query.filter(
            Detection.timestamp >= prev_threshold,
            Detection.timestamp < time_threshold
        ).all()
        prev_attendance = sum(d.person_count for d in prev_detections)
        
        attendance_delta = 0
        if prev_attendance > 0:
            attendance_delta = ((total_attendance - prev_attendance) / prev_attendance) * 100
        
        # Average density
        if recent_detections:
            avg_density = sum(d.density_percentage for d in recent_detections) / len(recent_detections)
            prev_avg_density = sum(d.density_percentage for d in prev_detections) / len(prev_detections) if prev_detections else avg_density
            density_delta = avg_density - prev_avg_density if prev_detections else 0
        else:
            avg_density = 0
            density_delta = 0
        
        # Active alerts
        active_alerts = Alert.query.filter_by(is_resolved=False).count()
        new_alerts = Alert.query.filter(
            Alert.timestamp >= time_threshold,
            Alert.is_resolved == False
        ).count()
        
        # Active cameras
        active_cameras = Camera.query.filter_by(is_active=True).count()
        total_cameras = Camera.query.count()
        
        return jsonify({
            'total_attendance': total_attendance,
            'attendance_delta': round(attendance_delta, 1),
            'avg_density': round(avg_density, 1),
            'density_delta': round(density_delta, 1),
            'active_alerts': active_alerts,
            'new_alerts': new_alerts,
            'active_cameras': f"{active_cameras}/{total_cameras}",
            'cameras_status': 'Online' if active_cameras == total_cameras and total_cameras > 0 else 'Offline'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dashboard/heatmap', methods=['GET'])
@jwt_required()
def get_heatmap_data():
    """Get heatmap data for zones"""
    try:
        zones = Zone.query.all()
        heatmap_data = []
        
        for zone in zones:
            # Get latest detection for zone
            latest_detection = Detection.query.filter_by(zone_id=zone.id)\
                .order_by(Detection.timestamp.desc()).first()
            
            density = latest_detection.density_percentage if latest_detection else 0
            
            # Determine heat level
            if density >= zone.threshold_critical * 100:
                level = 'crit'
            elif density >= zone.threshold_warning * 100:
                level = 'high'
            elif density >= 30:
                level = 'med'
            elif density > 0:
                level = 'low'
            else:
                level = 'empty'
            
            heatmap_data.append({
                'zone_id': zone.id,
                'zone_name': zone.name,
                'density': round(density, 1),
                'level': level
            })
        
        return jsonify({
            'zones': heatmap_data,
            'updated': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dashboard/alerts', methods=['GET'])
@jwt_required()
def get_recent_alerts():
    """Get recent alerts"""
    try:
        limit = request.args.get('limit', 10, type=int)
        alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dashboard/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    """Get list of cameras"""
    try:
        cameras = Camera.query.all()
        return jsonify({
            'cameras': [camera.to_dict() for camera in cameras]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Analytics Endpoints ====================

@api_bp.route('/analytics/density-trends', methods=['GET'])
@jwt_required()
def get_density_trends():
    """Get density trends by zone over time"""
    try:
        hours = request.args.get('hours', 24, type=int)
        zone_id = request.args.get('zone_id', type=int)
        
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        query = Detection.query.filter(Detection.timestamp >= time_threshold)
        if zone_id:
            query = query.filter_by(zone_id=zone_id)
        
        detections = query.order_by(Detection.timestamp.asc()).all()
        
        # Group by hour and zone
        trends = {}
        for detection in detections:
            hour_key = detection.timestamp.replace(minute=0, second=0, microsecond=0)
            zone_name = detection.zone.name if detection.zone else 'Unknown'
            
            if zone_name not in trends:
                trends[zone_name] = {}
            
            if hour_key not in trends[zone_name]:
                trends[zone_name][hour_key] = {'count': 0, 'total_density': 0}
            
            trends[zone_name][hour_key]['count'] += 1
            trends[zone_name][hour_key]['total_density'] += detection.density_percentage
        
        # Calculate averages
        result = {}
        for zone_name, hours_data in trends.items():
            result[zone_name] = [
                {
                    'time': hour.isoformat(),
                    'density': round(data['total_density'] / data['count'], 2)
                }
                for hour, data in sorted(hours_data.items())
            ]
        
        return jsonify({'trends': result}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/zone-stats', methods=['GET'])
@jwt_required()
def get_zone_stats():
    """Get detailed zone statistics"""
    try:
        hours = request.args.get('hours', 24, type=int)
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        zones = Zone.query.all()
        stats = []
        
        for zone in zones:
            detections = Detection.query.filter(
                Detection.zone_id == zone.id,
                Detection.timestamp >= time_threshold
            ).all()
            
            if detections:
                avg_density = sum(d.density_percentage for d in detections) / len(detections)
                peak_detection = max(detections, key=lambda x: x.density_percentage)
                peak_time = peak_detection.timestamp
            else:
                avg_density = 0
                peak_time = None
            
            alerts_count = Alert.query.filter(
                Alert.zone_id == zone.id,
                Alert.timestamp >= time_threshold
            ).count()
            
            # Determine status
            if avg_density >= zone.threshold_critical * 100:
                status = 'Critical'
            elif avg_density >= zone.threshold_warning * 100:
                status = 'Warning'
            else:
                status = 'Normal'
            
            stats.append({
                'zone_id': zone.id,
                'zone_name': zone.name,
                'avg_density': round(avg_density, 1),
                'peak_time': peak_time.strftime('%H:%M') if peak_time else 'N/A',
                'alerts_triggered': alerts_count,
                'status': status
            })
        
        return jsonify({'zones': stats}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/export', methods=['GET'])
@jwt_required()
def export_analytics():
    """Export analytics data as CSV"""
    try:
        hours = request.args.get('hours', 24, type=int)
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        detections = Detection.query.filter(
            Detection.timestamp >= time_threshold
        ).order_by(Detection.timestamp.asc()).all()
        
        # Generate CSV
        csv_lines = ['Timestamp,Zone,Camera,Person Count,Density Percentage\n']
        for detection in detections:
            zone_name = detection.zone.name if detection.zone else 'Unknown'
            camera_name = detection.camera.name if detection.camera else 'Unknown'
            csv_lines.append(
                f"{detection.timestamp.isoformat()},{zone_name},{camera_name},"
                f"{detection.person_count},{detection.density_percentage}\n"
            )
        
        return jsonify({
            'csv': ''.join(csv_lines),
            'filename': f'analytics_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Upload & Processing Endpoints ====================

@api_bp.route('/upload/image', methods=['POST'])
@jwt_required()
def upload_image():
    """Upload and process an image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join('uploads', 'images', f'{timestamp}_{filename}')
        file.save(filepath)
        
        # Process with YOLOv8
        result = detection_service.detect_persons(filepath)
        
        # Check if processing failed
        if 'error' in result:
            return jsonify({'error': f'Image processing failed: {result["error"]}'}), 500
        
        # Save annotated image
        annotated_filename = f'processed_{timestamp}_{filename}'
        annotated_path = os.path.join('uploads', 'processed', annotated_filename)
        if 'annotated_image' in result:
            detection_service.save_annotated_image(result['annotated_image'], annotated_path)
        else:
            annotated_path = None
        
        # Get zone from request (optional)
        zone_id = request.form.get('zone_id', type=int)
        camera_id = request.form.get('camera_id', type=int)
        
        # Save detection to database
        detection = Detection(
            camera_id=camera_id,
            zone_id=zone_id,
            person_count=result.get('person_count', 0),
            density_percentage=result.get('density_percentage', 0.0),
            image_path=filepath,
            processed_image_path=annotated_path,
            detection_metadata=json.dumps(result.get('detections', []))
        )
        db.session.add(detection)
        
        # Check for alerts
        if zone_id:
            zone = Zone.query.get(zone_id)
            density = result.get('density_percentage', 0.0)
            if zone and density >= zone.threshold_critical * 100:
                alert = Alert(
                    zone_id=zone_id,
                    detection_id=detection.id,
                    alert_type='density',
                    severity='critical',
                    message=f'Critical density detected in {zone.name}: {density:.1f}%'
                )
                db.session.add(alert)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Image processed successfully',
            'detection': detection.to_dict(),
            'result': {
                'person_count': result.get('person_count', 0),
                'density_percentage': result.get('density_percentage', 0.0),
                'processed_image_url': f'/api/files/{annotated_filename}'
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Image upload error: {str(e)}")
        print(f"Traceback: {error_trace}")
        return jsonify({'error': str(e), 'details': error_trace}), 500

@api_bp.route('/upload/video', methods=['POST'])
@jwt_required()
def upload_video():
    """Upload and process a video"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join('uploads', 'videos', f'{timestamp}_{filename}')
        file.save(filepath)
        
        # Process video (this may take time)
        # frame_interval=5 processes every 5th frame and applies to intermediate frames (good balance)
        # frame_interval=10 processes every 10th frame (faster)
        # Lower values = more accurate but slower
        output_path = os.path.join('uploads', 'processed', f'processed_{timestamp}_{filename}')
        print(f"Processing video: {filepath}")
        print(f"Output path: {output_path}")
        print("This may take a while for longer videos...")
        # Use frame_interval=5 for good balance of speed and accuracy
        # The code will apply detections to intermediate frames for smooth boxes
        result = detection_service.process_video(filepath, output_path, frame_interval=5, conf_threshold=0.25)
        
        # Check if processing failed
        if 'error' in result:
            return jsonify({'error': f'Video processing failed: {result["error"]}'}), 500
        
        if result.get('processed_frames', 0) == 0:
            return jsonify({'error': 'No frames were processed from the video'}), 500
        
        # Verify output file exists
        output_exists = result.get('output_exists', False) or os.path.exists(output_path)
        if not output_exists:
            print(f"Warning: Processed video file not found at {output_path}")
            # Still return success but note that file may not be available
        
        # Get zone and camera from request
        zone_id = request.form.get('zone_id', type=int)
        camera_id = request.form.get('camera_id', type=int)
        
        # Save detection summary
        detection = Detection(
            camera_id=camera_id,
            zone_id=zone_id,
            person_count=int(result.get('average_person_count', 0)),
            density_percentage=result.get('average_density', 0.0),
            video_path=filepath,
            processed_image_path=output_path if os.path.exists(output_path) else None,
            detection_metadata=json.dumps({
                'total_frames': result.get('total_frames', 0),
                'processed_frames': result.get('processed_frames', 0)
            })
        )
        db.session.add(detection)
        db.session.commit()
        
        return jsonify({
            'message': 'Video processed successfully',
            'detection': detection.to_dict(),
            'result': {
                'average_person_count': result.get('average_person_count', 0),
                'average_density': result.get('average_density', 0.0),
                'total_frames': result.get('total_frames', 0),
                'processed_frames': result.get('processed_frames', 0),
                'processed_video_url': f'/api/files/{os.path.basename(output_path)}' if output_exists else None,
                'output_file_exists': output_exists,
                'output_filename': os.path.basename(output_path) if output_exists else None
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Video upload error: {str(e)}")
        print(f"Traceback: {error_trace}")
        return jsonify({'error': str(e), 'details': error_trace}), 500

# ==================== Camera Management ====================

@api_bp.route('/cameras', methods=['POST'])
@jwt_required()
def create_camera():
    """Create a new camera"""
    try:
        data = request.get_json()
        
        camera = Camera(
            name=data.get('name'),
            location=data.get('location'),
            zone=data.get('zone'),
            stream_url=data.get('stream_url'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(camera)
        db.session.commit()
        
        return jsonify({
            'message': 'Camera created successfully',
            'camera': camera.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/cameras/<int:camera_id>', methods=['GET'])
@jwt_required()
def get_camera(camera_id):
    """Get camera details"""
    try:
        camera = Camera.query.get_or_404(camera_id)
        return jsonify({'camera': camera.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Zone Management ====================

@api_bp.route('/zones', methods=['GET'])
@jwt_required()
def get_zones():
    """Get all zones"""
    try:
        zones = Zone.query.all()
        return jsonify({'zones': [zone.to_dict() for zone in zones]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/zones', methods=['POST'])
@jwt_required()
def create_zone():
    """Create a new zone"""
    try:
        data = request.get_json()
        
        zone = Zone(
            name=data.get('name'),
            description=data.get('description'),
            max_capacity=data.get('max_capacity'),
            threshold_warning=data.get('threshold_warning', 0.6),
            threshold_critical=data.get('threshold_critical', 0.8)
        )
        
        db.session.add(zone)
        db.session.commit()
        
        return jsonify({
            'message': 'Zone created successfully',
            'zone': zone.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== File Serving ====================

@api_bp.route('/files/<filename>', methods=['GET'])
@jwt_required()
def get_file(filename):
    """Serve processed files (images and videos)"""
    try:
        file_path = os.path.join('uploads', 'processed', filename)
        if os.path.exists(file_path):
            # Determine content type based on file extension
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                from flask import Response
                # For video files, use proper headers for streaming
                return send_file(
                    file_path, 
                    mimetype='video/mp4',
                    as_attachment=False,
                    conditional=True
                )
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                return send_file(file_path, mimetype='image/jpeg')
            elif filename.lower().endswith('.png'):
                return send_file(file_path, mimetype='image/png')
            elif filename.lower().endswith('.gif'):
                return send_file(file_path, mimetype='image/gif')
            else:
                return send_file(file_path)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        import traceback
        print(f"File serving error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
