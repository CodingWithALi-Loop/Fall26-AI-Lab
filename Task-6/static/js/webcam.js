/**
 * Webcam Handler JavaScript
 * Manages webcam access, video capture, and file upload
 */

class WebcamHandler {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.stream = null;
        this.capturedImage = null;
        this.uploadedImage = null;
    }

    /**
     * Request permission and start webcam
     */
    async startWebcam() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                },
                audio: false
            });

            this.video.srcObject = this.stream;

            return new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve(true);
                };
            });
        } catch (error) {
            console.error('Error accessing webcam:', error);
            throw new Error('Unable to access webcam. Please check permissions.');
        }
    }

    /**
     * Stop webcam stream
     */
    stopWebcam() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }

    /**
     * Capture current frame from video
     */
    captureFrame() {
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;

        this.ctx.drawImage(this.video, 0, 0);

        // Convert canvas to image data
        this.capturedImage = this.canvas.toDataURL('image/jpeg', 0.95);

        return this.capturedImage;
    }

    /**
     * Get the current captured image
     */
    getCapturedImage() {
        return this.capturedImage;
    }

    /**
     * Set uploaded image
     */
    setUploadedImage(file) {
        if (!file) return false;

        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                this.canvas.width = img.width;
                this.canvas.height = img.height;
                this.ctx.drawImage(img, 0, 0);
                this.uploadedImage = this.canvas.toDataURL('image/jpeg', 0.95);
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);

        return true;
    }

    /**
     * Get the uploaded image
     */
    getUploadedImage() {
        return this.uploadedImage;
    }

    /**
     * Get current image (either captured or uploaded)
     */
    getCurrentImage() {
        return this.capturedImage || this.uploadedImage;
    }

    /**
     * Clear all images
     */
    clearImages() {
        this.capturedImage = null;
        this.uploadedImage = null;
    }
}

// Initialize webcam handler
const webcamHandler = new WebcamHandler();

// DOM Elements
const startBtn = document.getElementById('startBtn');
const captureBtn = document.getElementById('captureBtn');
const stopBtn = document.getElementById('stopBtn');
const selectFileBtn = document.getElementById('selectFileBtn');
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadedImage = document.getElementById('uploadedImage');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Event Listeners - Webcam Controls
startBtn.addEventListener('click', async () => {
    try {
        startBtn.disabled = true;
        startBtn.textContent = 'Starting...';

        await webcamHandler.startWebcam();

        startBtn.style.display = 'none';
        captureBtn.disabled = false;
        stopBtn.disabled = false;
        document.getElementById('analyzeBtn').disabled = false;

        startBtn.textContent = 'Start Camera';
    } catch (error) {
        alert(error.message);
        startBtn.disabled = false;
        startBtn.textContent = 'Start Camera';
    }
});

captureBtn.addEventListener('click', () => {
    try {
        webcamHandler.captureFrame();
        captureBtn.style.background = '#10b981';
        captureBtn.textContent = '✓ Photo Captured';
        document.getElementById('analyzeBtn').disabled = false;

        setTimeout(() => {
            captureBtn.style.background = '';
            captureBtn.textContent = 'Capture Photo';
        }, 2000);
    } catch (error) {
        alert('Error capturing photo: ' + error.message);
    }
});

stopBtn.addEventListener('click', () => {
    webcamHandler.stopWebcam();
    startBtn.show = 'inline-block';
    startBtn.style.display = 'inline-block';
    captureBtn.disabled = true;
    stopBtn.disabled = true;
    document.getElementById('analyzeBtn').disabled = true;
    webcamHandler.clearImages();
});

// Event Listeners - Tab Navigation
tabBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;

        // Update active tab button
        tabBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');

        // Update active tab content
        tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// Event Listeners - File Upload
selectFileBtn.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    handleFileSelect(e.files[0]);
});

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    handleFileSelect(e.dataTransfer.files[0]);
});

/**
 * Handle file selection
 */
function handleFileSelect(file) {
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        alert('File size should be less than 16MB');
        return;
    }

    // Read and display image
    const reader = new FileReader();
    reader.onload = (e) => {
        uploadedImage.src = e.target.result;
        uploadedImage.style.display = 'block';

        // Set image in webcam handler
        const img = new Image();
        img.onload = () => {
            const canvas = webcamHandler.canvas;
            const ctx = canvas.getContext('2d');
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
            webcamHandler.uploadedImage = canvas.toDataURL('image/jpeg', 0.95);
            document.getElementById('analyzeBtn').disabled = false;
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}
