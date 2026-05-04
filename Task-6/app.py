"""
Flask Application for Face Profiling
Main backend server with routes for face detection and personality profiling
"""
from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from base64 import b64decode
import io
from PIL import Image
import traceback

from utils.face_detection import FaceDetector
from utils.feature_measurement import FeatureMeasurement
from utils.personality_profiling import PersonalityProfiler

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize face detector (loaded once at startup)
try:
    face_detector = FaceDetector()
    detector_ready = True
except Exception as e:
    print(f"Warning: Face detector initialization failed: {e}")
    detector_ready = False

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_face():
    """
    Analyze face from image data
    Expects base64 encoded image in JSON body
    """
    try:
        if not detector_ready:
            return jsonify({'error': 'Face detector not initialized'}), 500
        
        # Get image data from request
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        # Remove data URI prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        try:
            img_bytes = b64decode(image_data)
            image = Image.open(io.BytesIO(img_bytes))
            image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            return jsonify({'error': f'Failed to decode image: {str(e)}'}), 400
        
        # Detect faces
        faces = face_detector.detect_faces(image_np)
        
        if len(faces) == 0:
            return jsonify({
                'success': False,
                'message': 'No face detected. Please ensure your face is clearly visible.',
                'faces_detected': 0
            }), 200
        
        # Process the most prominent face (largest)
        largest_face = max(faces, key=lambda f: f[2] * f[3])  # f[2]=width, f[3]=height
        
        # Detect landmarks
        landmarks = face_detector.detect_landmarks(image_np, largest_face)
        
        if landmarks is None:
            return jsonify({
                'success': False,
                'message': 'Could not detect facial landmarks. Please try again with better lighting.',
                'faces_detected': 1
            }), 200
        
        # Measure features
        feature_measurement = FeatureMeasurement(landmarks)
        measurements = feature_measurement.get_measurements()
        normalized_measurements = feature_measurement.get_normalized_measurements()
        feature_summary = feature_measurement.get_summary()
        
        # Profile personality
        profiler = PersonalityProfiler(normalized_measurements)
        personality_profile = profiler.get_full_profile()
        recommendations = profiler.get_recommendations()
        
        # Prepare response
        response = {
            'success': True,
            'faces_detected': len(faces),
            'measurements': {k: round(v, 2) for k, v in measurements.items()},
            'normalized_measurements': {k: round(v, 3) for k, v in normalized_measurements.items()},
            'feature_summary': feature_summary,
            'personality': personality_profile,
            'recommendations': recommendations,
            'landmarks_count': len(landmarks)
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'detector_ready': detector_ready
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    if not detector_ready:
        print("WARNING: Face detector not properly initialized!")
        print("Please ensure OpenCV is properly installed.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
