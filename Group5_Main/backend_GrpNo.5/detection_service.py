import cv2
import numpy as np
from ultralytics import YOLO
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json

class DetectionService:
    """Service for YOLOv8-based crowd detection"""
    
    def __init__(self, model_path: str = 'yolov8n.pt'):
        """
        Initialize YOLOv8 model for person detection
        Using YOLOv8n (nano) for faster inference, can be changed to yolov8s/m/l/x for better accuracy
        """
        try:
            self.model = YOLO(model_path)
            self.model.fuse()  # Fuse model for faster inference
            print(f"YOLOv8 model loaded: {model_path}")
        except Exception as e:
            print(f"Error loading YOLOv8 model: {e}")
            print("Attempting to download model...")
            self.model = YOLO(model_path)
            self.model.fuse()
    
    def detect_persons(self, image_path: str, conf_threshold: float = 0.25) -> Dict:
        """
        Detect persons in an image using YOLOv8
        
        Args:
            image_path: Path to the image file
            conf_threshold: Confidence threshold for detections
            
        Returns:
            Dictionary containing detection results
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")
            
            # Run YOLOv8 inference
            results = self.model(image, conf=conf_threshold, classes=[0])  # class 0 is 'person' in COCO dataset
            
            # Process results
            person_count = 0
            detections = []
            annotated_image = image.copy()
            
            for result in results:
                boxes = result.boxes
                person_count = len(boxes)
                
                for box in boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    detections.append({
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'confidence': confidence,
                        'class_id': class_id
                    })
                    
                    # Draw bounding box on image
                    cv2.rectangle(annotated_image, 
                                (int(x1), int(y1)), 
                                (int(x2), int(y2)), 
                                (0, 255, 0), 2)
                    
                    # Draw confidence score
                    label = f'Person {confidence:.2f}'
                    cv2.putText(annotated_image, label, 
                              (int(x1), int(y1) - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Calculate density percentage (rough estimate based on image area)
            image_area = image.shape[0] * image.shape[1]
            # Estimate: each person occupies roughly 5000-10000 pixels on average
            # This is a simplified calculation - can be improved with actual zone mapping
            estimated_person_area = person_count * 7500
            density_percentage = min(100.0, (estimated_person_area / image_area) * 100)
            
            return {
                'person_count': person_count,
                'density_percentage': round(density_percentage, 2),
                'detections': detections,
                'annotated_image': annotated_image,
                'image_shape': image.shape
            }
        
        except Exception as e:
            print(f"Error in detect_persons: {e}")
            return {
                'person_count': 0,
                'density_percentage': 0.0,
                'detections': [],
                'error': str(e)
            }
    
    def process_video_frame(self, frame: np.ndarray, conf_threshold: float = 0.25) -> Dict:
        """
        Detect persons in a video frame
        
        Args:
            frame: Video frame as numpy array
            conf_threshold: Confidence threshold
            
        Returns:
            Dictionary containing detection results
        """
        try:
            # Run YOLOv8 inference
            results = self.model(frame, conf=conf_threshold, classes=[0], verbose=False)
            
            person_count = 0
            detections = []
            annotated_frame = frame.copy()
            
            for result in results:
                boxes = result.boxes
                person_count = len(boxes)
                
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    detections.append({
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'confidence': confidence
                    })
                    
                    # Draw bounding box
                    cv2.rectangle(annotated_frame,
                                (int(x1), int(y1)),
                                (int(x2), int(y2)),
                                (0, 255, 0), 2)
            
            # Calculate density
            frame_area = frame.shape[0] * frame.shape[1]
            estimated_person_area = person_count * 7500
            density_percentage = min(100.0, (estimated_person_area / frame_area) * 100)
            
            return {
                'person_count': person_count,
                'density_percentage': round(density_percentage, 2),
                'detections': detections,
                'annotated_frame': annotated_frame
            }
        
        except Exception as e:
            print(f"Error in process_video_frame: {e}")
            return {
                'person_count': 0,
                'density_percentage': 0.0,
                'detections': [],
                'error': str(e)
            }
    
    def process_video(self, video_path: str, output_path: str = None, 
                     frame_interval: int = 30, conf_threshold: float = 0.25) -> Dict:
        """
        Process video file and detect persons in frames
        
        Args:
            video_path: Path to input video
            output_path: Path to save annotated video (optional)
            frame_interval: Process every Nth frame
            conf_threshold: Confidence threshold
            
        Returns:
            Dictionary with video processing results
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            frame_detections = []
            total_persons = 0
            frame_count = 0
            
            # Setup video writer if output path is provided
            out = None
            if output_path:
                # Try codecs in order of preference
                # Use codecs that don't require external libraries first
                fourcc_options = [
                    ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),  # MPEG-4 (most compatible, no external deps)
                    ('XVID', cv2.VideoWriter_fourcc(*'XVID')),  # Xvid (good compatibility)
                    ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),  # Motion JPEG (always works)
                    ('avc1', cv2.VideoWriter_fourcc(*'avc1')),  # H.264 (requires codec)
                    ('H264', cv2.VideoWriter_fourcc(*'H264')),  # H.264 alternative
                ]
                
                out = None
                used_codec = None
                for codec_name, fourcc in fourcc_options:
                    try:
                        # Change extension if needed for certain codecs
                        temp_path = output_path
                        if codec_name == 'MJPG' and not output_path.endswith('.avi'):
                            temp_path = output_path.replace('.mp4', '.avi')
                        
                        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
                        if out.isOpened():
                            used_codec = codec_name
                            if temp_path != output_path:
                                # Update output path if we changed extension
                                output_path = temp_path
                            print(f"Video writer initialized with codec: {codec_name}")
                            break
                        else:
                            if out:
                                out.release()
                            out = None
                    except Exception as e:
                        print(f"Failed to initialize codec {codec_name}: {e}")
                        if out:
                            out.release()
                        out = None
                        continue
                
                if not out or not out.isOpened():
                    raise ValueError("Could not initialize video writer with any codec. Please ensure OpenCV is properly installed.")
            
            # Store last detection results to apply to intermediate frames
            last_detections = None
            last_annotated_frame = None
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Process every Nth frame for detection, but annotate every frame
                if frame_count % frame_interval == 0:
                    result = self.process_video_frame(frame, conf_threshold)
                    result['frame_number'] = frame_count
                    result['timestamp'] = frame_count / fps
                    frame_detections.append(result)
                    total_persons += result['person_count']
                    
                    # Store last detection results
                    last_detections = result.get('detections', [])
                    last_annotated_frame = result.get('annotated_frame', frame)
                    
                    if out:
                        # Write annotated frame
                        out.write(last_annotated_frame)
                else:
                    # For intermediate frames, apply last detection if available
                    if out and last_detections is not None and len(last_detections) > 0:
                        # Draw last known detections on current frame
                        annotated_frame = frame.copy()
                        for detection in last_detections:
                            bbox = detection.get('bbox', [])
                            confidence = detection.get('confidence', 0)
                            if len(bbox) == 4:
                                x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                                # Draw bounding box
                                cv2.rectangle(annotated_frame, 
                                            (x1, y1), 
                                            (x2, y2), 
                                            (0, 255, 0), 2)
                                # Draw confidence score
                                label = f'Person {confidence:.2f}'
                                cv2.putText(annotated_frame, label, 
                                          (x1, y1 - 10),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        out.write(annotated_frame)
                    elif out:
                        # If no previous detections, write original frame
                        out.write(frame)
            
            cap.release()
            if out:
                out.release()
                # Verify output file was created
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"Output video created: {output_path}, size: {file_size} bytes")
                    
                    # Re-encode to H.264 for browser compatibility (uses imageio-ffmpeg, no system install needed)
                    if output_path.endswith('.mp4'):
                        output_path = self._reencode_to_h264(output_path, fps, width, height)
                else:
                    print(f"Warning: Output video file not found at {output_path}")
            
            avg_person_count = total_persons / len(frame_detections) if frame_detections else 0
            avg_density = sum(d['density_percentage'] for d in frame_detections) / len(frame_detections) if frame_detections else 0
            
            return {
                'total_frames': total_frames,
                'processed_frames': len(frame_detections),
                'average_person_count': round(avg_person_count, 2),
                'average_density': round(avg_density, 2),
                'frame_detections': frame_detections[:100],  # Limit to first 100 for response size
                'output_video': output_path,
                'output_exists': os.path.exists(output_path) if output_path else False
            }
        
        except Exception as e:
            print(f"Error in process_video: {e}")
            return {
                'error': str(e),
                'total_frames': 0,
                'processed_frames': 0
            }
    
    def save_annotated_image(self, annotated_image: np.ndarray, output_path: str) -> bool:
        """Save annotated image to disk"""
        try:
            cv2.imwrite(output_path, annotated_image)
            return True
        except Exception as e:
            print(f"Error saving annotated image: {e}")
            return False
    
    def _reencode_to_h264(self, input_path: str, fps: int, width: int, height: int) -> str:
        """
        Re-encode video to H.264 using imageio-ffmpeg (no system ffmpeg needed)
        Returns the path to the re-encoded video (or original if encoding fails)
        """
        try:
            import imageio_ffmpeg
            import subprocess
            
            print(f"Re-encoding video to H.264 for browser compatibility using imageio-ffmpeg...")
            
            # Get bundled ffmpeg executable path
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Create temporary output path
            temp_path = input_path.replace('.mp4', '_h264.mp4')
            
            # Use bundled ffmpeg to re-encode
            cmd = [
                ffmpeg_exe,
                '-i', input_path,
                '-c:v', 'libx264',  # H.264 codec
                '-preset', 'medium',  # Encoding speed/quality balance
                '-crf', '23',  # Quality (18-28, lower is better)
                '-pix_fmt', 'yuv420p',  # Pixel format for browser compatibility
                '-movflags', '+faststart',  # Enable streaming
                '-y',  # Overwrite output file
                temp_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0 and os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                # Replace original with re-encoded version
                os.replace(temp_path, input_path)
                print(f"Video successfully re-encoded to H.264: {input_path}")
                return input_path
            else:
                print(f"Re-encoding failed: {result.stderr[:500] if result.stderr else 'Unknown error'}")
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return input_path
                
        except ImportError:
            print("imageio-ffmpeg not installed. Install it with: pip install imageio imageio-ffmpeg")
            print("Video will use original codec (may not work in all browsers).")
            return input_path
        except subprocess.TimeoutExpired:
            print("Re-encoding timed out. Using original video.")
            temp_path = input_path.replace('.mp4', '_h264.mp4')
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return input_path
        except Exception as e:
            print(f"Error during re-encoding: {e}")
            import traceback
            traceback.print_exc()
            # Clean up temp file if it exists
            temp_path = input_path.replace('.mp4', '_h264.mp4')
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return input_path