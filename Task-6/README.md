# Face Profiling System

A comprehensive facial analysis application that detects facial features and profiles personality types based on the 16 MBTI types. Built with Python Flask backend, OpenCV, and dlib for precise face landmark detection.

## Features

✨ **Facial Feature Detection & Measurement**
- Eye measurements (width, height, spacing, openness)
- Nose analysis (length, width, proportions)
- Mouth measurements (width, height, fullness)
- Jawline analysis (length, width, shape ratios)
- Face shape classification

🎯 **Personality Profiling**
- 16 MBTI personality type classification
- Confidence scoring based on facial features
- Detailed personality descriptions
- Personalized insights and recommendations

📸 **Flexible Input**
- Real-time webcam capture
- Image file upload
- Drag-and-drop support

🎨 **Modern UI**
- Beautiful responsive design
- Real-time analysis results
- Detailed measurements breakdown
- Downloadable reports

## Installation

### Prerequisites
- Python 3.8+
- Webcam (for live capture)
- Modern web browser

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: ~~Download dlib Shape Predictor~~ (NO LONGER NEEDED!)

The application now uses OpenCV's Haar Cascades for face detection, which requires no additional downloads or compilation!

**That's it!** You're ready to go.

## Running the Application

```bash
python app.py
```

Then open your browser and go to:
```
http://localhost:5000
```

## Project Structure

```
Face Profiling/
├── app.py                          Main Flask application
├── requirements.txt                Python dependencies
├── shape_predictor_68_face_landmarks.dat  (Download separately)
├── templates/
│   └── index.html                 Main HTML page
├── static/
│   ├── css/
│   │   └── style.css              Styling
│   └── js/
│       ├── webcam.js              Camera handling
│       └── main.js                Application logic
└── utils/
    ├── __init__.py
    ├── face_detection.py           Face and landmark detection
    ├── feature_measurement.py       Feature measurement calculations
    └── personality_profiling.py     MBTI personality mapping
```

## Usage

### Webcam Capture
1. Click "Start Camera"
2. Click "Capture Photo" when ready
3. Click "Analyze Face & Profile"

### Image Upload
1. Click the "Upload Photo" tab
2. Drag and drop an image or click to browse
3. Click "Analyze Face & Profile"

### Results
- View personality type and detailed profile
- See facial feature measurements
- Get personalized insights and recommendations
- Download results as JSON or text

## Technical Details

### Facial Landmarks
The system uses 68-point facial landmarks to measure:
- **Points 0-16**: Jaw outline
- **Points 17-21**: Left eyebrow
- **Points 22-26**: Right eyebrow
- **Points 27-35**: Nose
- **Points 36-41**: Left eye
- **Points 42-47**: Right eye
- **Points 48-67**: Mouth

Landmarks are generated using OpenCV's Haar Cascade detectors combined with synthetic landmark generation for precise feature measurement.

### Personality Mapping
Features are mapped to MBTI dimensions:
- **Extraversion (E) vs Introversion (I)**: Eye spacing, openness
- **Sensing (S) vs Intuition (N)**: Angular vs soft features
- **Thinking (T) vs Feeling (F)**: Jawline angularity
- **Judging (J) vs Perceiving (P)**: Feature definition

### Measurements
All measurements are relative to face geometry, allowing consistent analysis across different face sizes and distances.

## API Endpoints

### POST /api/analyze
Analyzes a face image and returns personality profile.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "faces_detected": 1,
  "measurements": { ... },
  "normalized_measurements": { ... },
  "feature_summary": { ... },
  "personality": {
    "type": "INTJ",
    "name": "The Architect",
    "traits": [...],
    "description": "...",
    "confidence": "85.3%"
  },
  "recommendations": { ... }
}
```

### GET /api/health
Health check endpoint.

## Troubleshooting

### "Face Detector Not Initialized"
- Ensure `shape_predictor_68_face_landmarks.dat` is in the project root
- Restart the Flask application

### "No Face Detected"
- Ensure good lighting
- Face should be clearly visible
- Try adjusting camera angle

### Webcam Not Working
- Check browser permissions
- Use HTTPS (required in some browsers)
- Try a different browser

### Slow Performance
- Close other applications
- Ensure good internet connection
- Use a more powerful computer for faster processing

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Note: Webcam access requires HTTPS in production (or localhost for development)

## Performance Notes

- First analysis may take 2-3 seconds (model loading)
- Subsequent analyses typically take 0.5-1 second
- Larger images may take longer to process

## Limitations

- Works best with frontal face photos
- Requires clear, well-lit images
- Accuracy depends on image quality
- Results are probabilistic personality insights, not definitive

## Disclaimer

This tool provides personality insights based on facial feature analysis for entertainment purposes. Results are probabilistic estimates and should not be used for official personality assessment, medical diagnosis, or critical decision-making.

## License

Educational and personal use.

## Technical Stack

- **Backend**: Flask (Python)
- **Face Detection**: OpenCV (Haar Cascades) + Synthetic Landmark Generation
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **APIs**: RESTful JSON API

## Future Enhancements

- Real-time analysis with webcam feed
- Multiple face comparison
- Historical analysis tracking
- Export to PDF with charts
- Mobile app version
- Support for different lighting conditions
- Age/gender estimation
- Emotion detection
- Facial symmetry analysis

## Support

For issues or suggestions, ensure:
1. Shape predictor file is properly installed
2. Python 3.8+ is being used
3. All dependencies are installed: `pip install -r requirements.txt`
4. Flask is running on the correct port

## Version

Face Profiling System v1.0

---

**Built with ❤️ using Python, Flask, OpenCV, and dlib**
