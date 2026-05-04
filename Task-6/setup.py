#!/usr/bin/env python3
"""
Setup script for Face Profiling System
Helps with environment setup and dependency installation
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_step(step_num, text):
    """Print step information"""
    print(f"\n📌 Step {step_num}: {text}")
    print("-" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python Version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required packages"""
    print_step(2, "Installing Python Dependencies")
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def download_dlib_predictor():
    """Download dlib face landmark predictor"""
    print_step(3, "Setting Up dlib Face Predictor")
    
    predictor_name = "shape_predictor_68_face_landmarks.dat"
    predictor_path = Path(predictor_name)
    
    # Check if already exists
    if predictor_path.exists():
        print(f"✅ {predictor_name} already found")
        return True
    
    print("The dlib predictor file needs to be downloaded separately.")
    print("File: shape_predictor_68_face_landmarks.dat")
    print("Size: ~100 MB (compressed), ~200 MB (uncompressed)")
    print("\nDownload from:")
    print("  http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
    print("\nSteps:")
    print("  1. Download the .bz2 file")
    print("  2. Extract it (7-Zip, WinRAR, or bunzip2)")
    print("  3. Place the .dat file in the project root directory")
    
    try_download = input("\nWould you like to attempt automatic download? (y/n): ").lower().strip()
    
    if try_download == 'y':
        try:
            print("\nDownloading predictor file...")
            print("(This may take a few minutes...)")
            
            url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
            compressed_file = "shape_predictor.bz2"
            
            # Download
            print("Downloading...")
            urllib.request.urlretrieve(url, compressed_file)
            
            # Extract
            print("Extracting...")
            import bz2
            with bz2.open(compressed_file, 'rb') as f_in:
                with open(predictor_name, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Clean up
            os.remove(compressed_file)
            
            print(f"✅ {predictor_name} downloaded and extracted successfully")
            return True
        except Exception as e:
            print(f"❌ Automatic download failed: {e}")
            print("Please download manually using the instructions above")
            return False
    else:
        print("⚠️  Please download the predictor manually and place it in the project root")
        return False

def check_opencv_dlib():
    """Verify OpenCV and dlib installation"""
    print_step(4, "Verifying Critical Libraries")
    
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__} installed")
    except ImportError:
        print("❌ OpenCV not found")
        return False
    
    try:
        import dlib
        print(f"✅ dlib installed")
    except ImportError:
        print("❌ dlib not found")
        print("   Note: dlib installation can take time on some systems")
        return False
    
    return True

def verify_predictor():
    """Verify predictor file exists and is valid"""
    print_step(5, "Verifying Predictor File")
    
    predictor_name = "shape_predictor_68_face_landmarks.dat"
    predictor_path = Path(predictor_name)
    
    if not predictor_path.exists():
        print(f"❌ {predictor_name} not found")
        print(f"   Location: {predictor_path.absolute()}")
        return False
    
    file_size = predictor_path.stat().st_size
    expected_size = 100000000  # Approximately 100 MB
    
    if file_size < expected_size * 0.9:
        print(f"⚠️  File size seems small ({file_size} bytes)")
        print("   The file may not be complete")
        return False
    
    print(f"✅ {predictor_name} found ({file_size / (1024*1024):.1f} MB)")
    return True

def display_usage():
    """Display usage instructions"""
    print_header("Face Profiling System - Setup Complete!")
    
    print("✅ All checks passed! You're ready to run the application.")
    print("\n" + "=" * 60)
    print("  GETTING STARTED")
    print("=" * 60)
    print("\n1. Start the Flask server:")
    print("   python app.py")
    print("\n2. Open your browser:")
    print("   http://localhost:5000")
    print("\n3. Capture or upload a face image")
    print("\n4. Click 'Analyze Face & Profile' to get results")
    print("\n" + "=" * 60)
    print("  FEATURES")
    print("=" * 60)
    print("  • Real-time webcam capture")
    print("  • Facial feature measurement")
    print("  • 16 MBTI personality type classification")
    print("  • Detailed analysis and recommendations")
    print("  • Result export")
    print("\n" + "=" * 60)

def display_optional_steps():
    """Display optional configuration steps"""
    print("\n" + "=" * 60)
    print("  OPTIONAL: Advanced Configuration")
    print("=" * 60)
    print("\nFor production deployment:")
    print("  1. Change debug mode in app.py")
    print("  2. Set up proper web server (Gunicorn, uWSGI)")
    print("  3. Configure SSL/TLS for HTTPS")
    print("  4. Set up proper logging")
    print("  5. Use environment variables for configuration")

def main():
    """Main setup function"""
    print_header("Face Profiling System - Setup Wizard")
    
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    # Run all checks
    if not check_python_version():
        print("\n❌ Setup failed: Python version requirement not met")
        sys.exit(1)
    
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        sys.exit(1)
    
    if not check_opencv_dlib():
        print("\n❌ Setup failed: Critical libraries not properly installed")
        sys.exit(1)
    
    download_dlib_predictor()
    
    if not verify_predictor():
        print("\n⚠️  Warning: Predictor file not found or incomplete")
        print("   The application will not work without this file")
        print("   Please download it from:")
        print("   http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
    
    display_usage()
    display_optional_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
