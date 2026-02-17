# Project Summary - AI-Based Crowd Density Monitoring System

## Overview

This project is a complete full-stack web application for monitoring and analyzing crowd density using AI (YOLOv8) for person detection. The system consists of a modern frontend and a robust Python Flask backend.

## Architecture

### Frontend (`frontend_GrpNo.5/`)
- **Technology:** HTML5, CSS3, JavaScript (Vanilla)
- **Styling:** Tailwind CSS
- **Pages:**
  - Login/Signup (Authentication)
  - Dashboard (Real-time metrics, heatmap, alerts, cameras)
  - Analytics (Historical data, trends, zone statistics)
  - Upload & Connect (File upload for processing)
  - Settings (Configuration)

### Backend (`backend_GrpNo.5/`)
- **Technology:** Python Flask
- **AI Model:** YOLOv8 (Ultralytics) for person detection
- **Database:** SQLite (can be upgraded to PostgreSQL)
- **Authentication:** JWT (JSON Web Tokens)
- **Real-time:** WebSocket support via Flask-SocketIO

## Key Features

### 1. Authentication System
- User registration and login
- JWT-based session management
- Protected API endpoints

### 2. AI-Powered Detection
- **YOLOv8 Integration:** Uses YOLOv8n (nano) model for fast person detection
- **Image Processing:** Detects persons in uploaded images
- **Video Processing:** Processes video files frame-by-frame
- **Real-time Analysis:** Calculates person count and density percentage

### 3. Dashboard
- **Real-time Metrics:**
  - Total attendance
  - Average density
  - Active alerts
  - Active cameras status
- **Live Heatmap:** Visual representation of crowd density by zone
- **Recent Alerts:** Latest system alerts and notifications
- **Camera Status:** Monitor connected cameras

### 4. Analytics
- **Density Trends:** Historical density data by zone
- **Zone Statistics:** Detailed statistics per zone
- **Data Export:** Export analytics as CSV
- **Peak Time Analysis:** Identify peak crowd times

### 5. File Upload & Processing
- **Image Upload:** Upload and process images
- **Video Upload:** Upload and process videos
- **Annotated Output:** View processed images/videos with bounding boxes
- **Automatic Detection:** Automatic person counting and density calculation

### 6. Zone & Camera Management
- **Zone Configuration:** Define monitoring zones with thresholds
- **Camera Management:** Add and manage camera feeds
- **Alert Thresholds:** Configure warning and critical density levels

## File Structure

```
Group5_Main/
├── frontend_GrpNo.5/
│   ├── dashboard.html          # Main dashboard page
│   ├── analytics.html          # Analytics page
│   ├── login.html              # Login page
│   ├── signup.html             # Signup page
│   ├── upload-connect.html     # File upload page
│   ├── settings.html           # Settings page
│   ├── styles.css              # Stylesheet
│   ├── api.js                  # API client library
│   └── app.js                  # Main application logic
│
├── backend_GrpNo.5/
│   ├── app.py                  # Main Flask application
│   ├── models.py               # Database models
│   ├── auth.py                 # Authentication endpoints
│   ├── api.py                  # Main API endpoints
│   ├── detection_service.py    # YOLOv8 detection service
│   ├── requirements.txt        # Python dependencies
│   ├── run.py                  # Application entry point
│   ├── README.md               # Backend documentation
│   └── .gitignore              # Git ignore rules
│
├── SETUP.md                    # Setup instructions
└── PROJECT_SUMMARY.md          # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Dashboard
- `GET /api/dashboard/metrics` - Get dashboard metrics
- `GET /api/dashboard/heatmap` - Get heatmap data
- `GET /api/dashboard/alerts` - Get recent alerts
- `GET /api/dashboard/cameras` - Get camera list

### Analytics
- `GET /api/analytics/density-trends` - Get density trends
- `GET /api/analytics/zone-stats` - Get zone statistics
- `GET /api/analytics/export` - Export analytics as CSV

### Upload & Processing
- `POST /api/upload/image` - Upload and process image
- `POST /api/upload/video` - Upload and process video

### Management
- `GET /api/cameras` - Get all cameras
- `POST /api/cameras` - Create camera
- `GET /api/zones` - Get all zones
- `POST /api/zones` - Create zone

## Database Schema

### Users
- User accounts and authentication credentials

### Cameras
- Camera configurations, locations, and status

### Zones
- Monitoring zones with density thresholds

### Detections
- Detection results from YOLOv8 processing
- Stores person count, density, timestamps, and metadata

### Alerts
- System alerts triggered by density thresholds
- Tracks alert type, severity, and resolution status

## Technology Stack

### Backend
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-JWT-Extended** - JWT authentication
- **Flask-SQLAlchemy** - Database ORM
- **Flask-SocketIO** - WebSocket support
- **Ultralytics YOLOv8** - AI model for person detection
- **OpenCV** - Image/video processing
- **SQLite** - Database (default)

### Frontend
- **HTML5/CSS3** - Markup and styling
- **JavaScript (ES6+)** - Application logic
- **Tailwind CSS** - Utility-first CSS framework
- **Fetch API** - HTTP requests

## Getting Started

1. **Setup Backend:**
   ```bash
   cd backend_GrpNo.5
   pip install -r requirements.txt
   python run.py
   ```

2. **Setup Frontend:**
   ```bash
   cd frontend_GrpNo.5
   python -m http.server 8000
   ```

3. **Access Application:**
   - Open `http://localhost:8000/login.html`
   - Login with: `admin@crowdsense.ai` / `admin123`

## Default Credentials

- **Email:** admin@crowdsense.ai
- **Password:** admin123

## YOLOv8 Model

The system uses YOLOv8n (nano) by default for fast inference. The model is automatically downloaded on first use. You can change the model in `detection_service.py`:
- `yolov8n.pt` - Nano (fastest)
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (more accurate)
- `yolov8l.pt` - Large (very accurate)
- `yolov8x.pt` - Extra Large (most accurate, slowest)

## Future Enhancements

- Real-time camera feed processing
- Advanced analytics with machine learning predictions
- Mobile app integration
- Multi-tenant support
- Advanced alerting system (email, SMS, push notifications)
- Integration with external camera systems
- Advanced zone mapping and calibration
- Historical data visualization with charts
- User role management
- API rate limiting
- Production-ready deployment configurations

## License

[Specify your license here]

## Contributors

[Add contributor information]
