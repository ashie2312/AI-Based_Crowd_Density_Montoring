# Setup Guide - AI-Based Crowd Density Monitoring System

This guide will help you set up both the frontend and backend of the Crowd Monitoring system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser
- (Optional) A web server for serving the frontend (or use a simple HTTP server)

## Backend Setup

1. **Navigate to the backend directory:**
```bash
cd Group5_Main/backend_GrpNo.5
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
# Copy the example .env file (if it exists)
# Or create a .env file with:
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///crowd_monitoring.db
UPLOAD_FOLDER=uploads
```

5. **Run the backend server:**
```bash
python run.py
# or
python app.py
```

The backend API will be available at `http://localhost:5000`

**Default Admin Credentials:**
- Email: `admin@crowdsense.ai`
- Password: `admin123`

## Frontend Setup

1. **Navigate to the frontend directory:**
```bash
cd Group5_Main/frontend_GrpNo.5
```

2. **Serve the frontend using a local web server:**

   **Option 1: Using Python's built-in HTTP server:**
   ```bash
   # Python 3
   python -m http.server 8000
   ```

   **Option 2: Using Node.js http-server:**
   ```bash
   npx http-server -p 8000
   ```

   **Option 3: Using VS Code Live Server extension**

3. **Open your browser and navigate to:**
```
http://localhost:8000/login.html
```

## Configuration

### Backend API URL

If your backend is running on a different port or host, update the `API_BASE_URL` in `frontend_GrpNo.5/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### CORS Configuration

The backend is configured to allow CORS from any origin. For production, update the CORS settings in `backend_GrpNo.5/app.py`:

```python
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8000"]}})
```

## First Steps

1. **Start the backend server** (see Backend Setup above)
2. **Start the frontend server** (see Frontend Setup above)
3. **Open the login page** in your browser
4. **Login with default credentials** or create a new account
5. **Upload an image or video** to test the YOLOv8 detection

## Testing the System

1. **Test Authentication:**
   - Login with `admin@crowdsense.ai` / `admin123`
   - Or create a new account via the signup page

2. **Test File Upload:**
   - Go to "Upload & Connect" page
   - Upload an image or video file
   - The system will process it using YOLOv8 and show detection results

3. **View Dashboard:**
   - Check the dashboard for real-time metrics
   - View heatmap and alerts

4. **View Analytics:**
   - Check the analytics page for historical data
   - Export data as CSV

## Troubleshooting

### Backend Issues

- **Port already in use:** Change the port in `app.py` or `run.py`
- **YOLOv8 model download fails:** The model will be downloaded automatically on first use. Ensure you have internet connection.
- **Database errors:** Delete `crowd_monitoring.db` and restart the server to recreate the database

### Frontend Issues

- **CORS errors:** Ensure the backend is running and CORS is properly configured
- **API connection errors:** Check that `API_BASE_URL` in `api.js` matches your backend URL
- **Authentication errors:** Clear browser localStorage and login again

## Production Deployment

For production deployment:

1. **Backend:**
   - Use a production WSGI server (gunicorn, uWSGI)
   - Set up proper environment variables
   - Use a production database (PostgreSQL recommended)
   - Configure proper CORS origins
   - Set up SSL/HTTPS

2. **Frontend:**
   - Build and minify JavaScript files
   - Serve via a production web server (Nginx, Apache)
   - Configure proper caching headers

## API Documentation

See `backend_GrpNo.5/README.md` for detailed API documentation.

## Support

For issues or questions, refer to the project documentation or contact the development team.
