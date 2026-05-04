/**
 * Main Application JavaScript
 * Handles API calls and results display
 */

const analyzeBtn = document.getElementById('analyzeBtn');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const downloadResultsBtn = document.getElementById('downloadResultsBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');
const statusMessage = document.getElementById('statusMessage');

let analysisResults = null;

/**
 * Main analyze function - sends image to backend
 */
async function analyzeImage() {
    try {
        // Get current image
        const imageData = webcamHandler.getCurrentImage();

        if (!imageData) {
            alert('Please capture or upload an image first');
            return;
        }

        // Show loading spinner
        loadingSpinner.style.display = 'flex';
        resultsSection.style.display = 'none';
        analyzeBtn.disabled = true;
        statusMessage.textContent = '';

        // Send to backend
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData
            }),
            timeout: 60000
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // Handle results
        if (result.success) {
            analysisResults = result;
            displayResults(result);
            resultsSection.style.display = 'block';
        } else {
            statusMessage.textContent = result.message || 'Analysis failed. Please try again.';
            statusMessage.style.color = '#ef4444';
        }

        loadingSpinner.style.display = 'none';
        analyzeBtn.disabled = false;

    } catch (error) {
        console.error('Error:', error);
        statusMessage.textContent = 'Error: ' + error.message;
        statusMessage.style.color = '#ef4444';
        loadingSpinner.style.display = 'none';
        analyzeBtn.disabled = false;
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    // Personality Profile
    const personality = data.personality;
    document.getElementById('typeBadge').textContent = personality.type;
    document.getElementById('typeName').textContent = personality.name;
    document.getElementById('typeDescription').textContent = personality.description;

    // Confidence
    const confidence = parseFloat(personality.confidence);
    document.getElementById('confidenceFill').style.width = `${confidence}%`;
    document.getElementById('confidenceText').textContent = personality.confidence;

    // Traits
    const traitsList = document.getElementById('traitsList');
    traitsList.innerHTML = '';
    personality.traits.forEach(trait => {
        const li = document.createElement('li');
        li.textContent = trait;
        traitsList.appendChild(li);
    });

    // Feature Summary
    const summary = data.feature_summary;
    document.getElementById('eyesSummary').textContent = summary.eyes || 'N/A';
    document.getElementById('noseSummary').textContent = summary.nose || 'N/A';
    document.getElementById('mouthSummary').textContent = summary.mouth || 'N/A';
    document.getElementById('jawSummary').textContent = summary.jaw || 'N/A';

    // Measurements Table
    const measurementsList = document.getElementById('measurementsList');
    measurementsList.innerHTML = '';
    
    const measurements = data.measurements;
    const measurementLabels = {
        'left_eye_width': 'Left Eye Width',
        'left_eye_height': 'Left Eye Height',
        'left_eye_ratio': 'Left Eye Ratio',
        'right_eye_width': 'Right Eye Width',
        'right_eye_height': 'Right Eye Height',
        'right_eye_ratio': 'Right Eye Ratio',
        'eye_distance': 'Eye Distance',
        'nose_length': 'Nose Length',
        'nose_width': 'Nose Width',
        'mouth_width': 'Mouth Width',
        'mouth_height': 'Mouth Height',
        'mouth_ratio': 'Mouth Ratio',
        'jaw_length': 'Jaw Length',
        'jaw_width': 'Jaw Width',
        'jaw_ratio': 'Jaw Ratio',
        'face_height': 'Face Height',
        'face_width': 'Face Width',
        'face_ratio': 'Face Ratio',
        'left_eyebrow_angle': 'Left Eyebrow Angle (°)',
        'right_eyebrow_angle': 'Right Eyebrow Angle (°)'
    };

    Object.entries(measurements).forEach(([key, value]) => {
        const label = measurementLabels[key] || key.replace(/_/g, ' ').toUpperCase();
        const row = document.createElement('tr');
        row.innerHTML = `<td>${label}</td><td>${value}</td>`;
        measurementsList.appendChild(row);
    });

    // Recommendations
    const recommendations = data.recommendations;
    document.getElementById('strengthsText').textContent = recommendations.strengths;
    document.getElementById('growthText').textContent = recommendations.growth_areas;
    document.getElementById('communicationText').textContent = recommendations.communication_style;
    document.getElementById('workText').textContent = recommendations.work_preferences;

    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

/**
 * New Analysis - Clear everything and reset
 */
function newAnalysis() {
    // Clear images
    webcamHandler.clearImages();
    
    // Reset UI
    resultsSection.style.display = 'none';
    statusMessage.textContent = '';
    analysisResults = null;
    
    // Reset camera
    webcamHandler.stopWebcam();
    document.getElementById('startBtn').style.display = 'inline-block';
    document.getElementById('captureBtn').disabled = true;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('analyzeBtn').disabled = true;
    
    // Clear uploaded image
    document.getElementById('uploadedImage').style.display = 'none';
    
    // Hide results section with animation
    document.querySelector('.camera-section').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Download results as JSON
 */
function downloadResults() {
    if (!analysisResults) {
        alert('No results to download');
        return;
    }

    const dataStr = JSON.stringify(analysisResults, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = `face-profile-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
}

/**
 * Download results as PDF (text format)
 */
function downloadResultsText() {
    if (!analysisResults) {
        alert('No results to download');
        return;
    }

    const personality = analysisResults.personality;
    const recommendations = analysisResults.recommendations;

    let text = 'FACE PROFILING ANALYSIS REPORT\n';
    text += '=' .repeat(50) + '\n\n';

    text += 'PERSONALITY TYPE: ' + personality.type + '\n';
    text += 'Name: ' + personality.name + '\n';
    text += 'Confidence: ' + personality.confidence + '\n';
    text += 'Description: ' + personality.description + '\n\n';

    text += 'Key Traits:\n';
    personality.traits.forEach(trait => {
        text += '  • ' + trait + '\n';
    });

    text += '\nPERSONALITY INSIGHTS\n';
    text += '-' .repeat(50) + '\n';
    text += 'Strengths: ' + recommendations.strengths + '\n';
    text += 'Growth Areas: ' + recommendations.growth_areas + '\n';
    text += 'Communication Style: ' + recommendations.communication_style + '\n';
    text += 'Work Preferences: ' + recommendations.work_preferences + '\n';

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = `face-profile-${new Date().toISOString().slice(0, 10)}.txt`;
    link.click();
    
    URL.revokeObjectURL(url);
}

// Event Listeners
analyzeBtn.addEventListener('click', analyzeImage);
newAnalysisBtn.addEventListener('click', newAnalysis);
downloadResultsBtn.addEventListener('click', downloadResults);

// Initial state
document.getElementById('analyzeBtn').disabled = true;

// Health check on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        if (!data.detector_ready) {
            console.warn('Face detector not ready. Please ensure dlib is properly installed.');
            statusMessage.textContent = '⚠️ Face detector not initialized. Please check installation.';
            statusMessage.style.color = '#f59e0b';
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
});
