# FFmpeg Setup for Video Encoding

## Problem
Videos processed with OpenCV's `mp4v` codec are not compatible with web browsers. They need to be re-encoded to H.264 format.

## Solution: Install FFmpeg

### Windows:
1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Download the "ffmpeg-release-essentials.zip" file
3. Extract it to a folder (e.g., `C:\ffmpeg`)
4. Add FFmpeg to your system PATH:
   - Open System Properties → Environment Variables
   - Edit the "Path" variable
   - Add: `C:\ffmpeg\bin` (or wherever you extracted it)
5. Restart your terminal/IDE
6. Verify installation: `ffmpeg -version`

### Alternative: Use Chocolatey
```powershell
choco install ffmpeg
```

### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# Mac
brew install ffmpeg
```

## After Installation
Once FFmpeg is installed, the backend will automatically re-encode videos to H.264 format, making them compatible with all browsers.

## Manual Conversion (if FFmpeg not available)
If you can't install FFmpeg, you can manually convert videos using:
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 23 -c:a aac -movflags +faststart output.mp4
```
