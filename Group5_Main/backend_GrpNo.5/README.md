# Crowd Monitoring Backend API

Backend API for the AI-Based Crowd Density Monitoring system using YOLOv8 for person detection.

## Features

- **Authentication**: JWT-based user authentication (login/register)
- **YOLOv8 Detection**: Real-time person detection in images and videos
- **Dashboard Metrics**: Real-time crowd metrics (attendance, density, alerts, cameras)
- **Analytics**: Historical data analysis and trends
- **File Upload**: Process images and videos for crowd detection
- **Camera Management**: Manage camera feeds and zones
- **WebSocket Support**: Real-time updates via Socket.IO

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize the database:**
The database will be automatically created on first run. Default admin credentials:
- Email: `admin@crowdsense.ai`
- Password: `admin123`

## Running the Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires JWT)

### Dashboard
- `GET /api/dashboard/metrics` - Get dashboard metrics
- `GET /api/dashboard/heatmap` - Get heatmap data
- `GET /api/dashboard/alerts` - Get recent alerts
- `GET /api/dashboard/cameras` - Get camera list

### Analytics
- `GET /api/analytics/density-trends` - Get density trends by zone
- `GET /api/analytics/zone-stats` - Get zone statistics
- `GET /api/analytics/export` - Export analytics as CSV

### Upload & Processing
- `POST /api/upload/image` - Upload and process image
- `POST /api/upload/video` - Upload and process video

### Camera Management
- `GET /api/cameras` - Get all cameras
- `POST /api/cameras` - Create new camera
- `GET /api/cameras/<id>` - Get camera details

### Zone Management
- `GET /api/zones` - Get all zones
- `POST /api/zones` - Create new zone

## Request/Response Examples

### Login
```json
POST /api/auth/login
{
  "email": "admin@crowdsense.ai",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

### Upload Image
```bash
POST /api/upload/image
Headers: Authorization: Bearer <token>
Form Data:
  - file: <image file>
  - zone_id: 1 (optional)
  - camera_id: 1 (optional)
```

### Get Dashboard Metrics
```bash
GET /api/dashboard/metrics?hours=24
Headers: Authorization: Bearer <token>
```

## YOLOv8 Model

The system uses YOLOv8n (nano) by default for faster inference. The model will be automatically downloaded on first run. You can change the model in `detection_service.py`:
- `yolov8n.pt` - Nano (fastest, less accurate)
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (more accurate)
- `yolov8l.pt` - Large (very accurate)
- `yolov8x.pt` - Extra Large (most accurate, slowest)

## Database Schema

- **Users**: User accounts and authentication
- **Cameras**: Camera configurations and status
- **Zones**: Monitoring zones with thresholds
- **Detections**: Detection results from YOLOv8
- **Alerts**: System alerts and notifications

## Notes

- All endpoints except `/api/auth/register` and `/api/auth/login` require JWT authentication
- File uploads are limited to 500MB
- Supported image formats: PNG, JPG, JPEG, GIF
- Supported video formats: MP4, AVI, MOV, MKV
- Processed files are stored in `uploads/processed/`
