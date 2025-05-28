
# Multimedia Web Application Collection

This is a collection project that includes three independent web applications, each focusing on specific multimedia and machine learning functionalities. All applications use **Flask** as the backend framework, combined with modern frontend technologies to provide intuitive user interfaces.

---

## Project Structure

This project includes the following three main sub-projects:

1.  **Face Recognition Application** - Real-time face detection and recognition using **MediaPipe**.
2.  **YouTube API Video Content Search** - Utilizes the **YouTube Data API** to search and display video content.
3.  **YOLOv8 Object Detection** - Real-time image object detection using the **YOLOv8** model.

---

## Environment Requirements

This project requires **Python 3.6+** and provides independent dependencies for each sub-project. You can choose to create separate virtual environments for each application or use a unified dependency file in the root directory.

---

## Sub-Project Descriptions

### 1. Face Recognition Application (FaceRecog)

A web application for face recognition built on **MediaPipe**, capable of accessing the camera through a browser for real-time face detection and recognition.

**Key Features:**
* Face detection and landmark extraction
* Face feature vector storage and comparison
* Real-time camera image processing
* User face registration and recognition

**Technology Stack:**
* **Backend**: Flask, MediaPipe
* **Frontend**: HTML, JavaScript
* **Data Storage**: JSON file system

**How to Run:**
```bash
cd FaceRecog
# Create and activate virtual environment
python -m venv face_recog_env
source face_recog_env/bin/activate  # Linux/Mac
# face_recog_env\Scripts\activate  # Windows
# Install dependencies and start
python app.py
```

### 2. YouTube API Video Content Search (YouTube_API)

A video search application built using **YouTube Data API v3**, providing a user-friendly interface for video content retrieval.

**Key Features:**
* Keyword-based video search
* Detailed video information display
* Video thumbnails and previews
* API quota monitoring

**Technology Stack:**
* **Backend**: Flask, Google API Client
* **Frontend**: React
* **External Access**: ngrok (Optional)

**How to Run:**
```bash
cd YouTube_API
# Set up environment
source setup_env.sh  # or bash setup_env.sh
# Install dependencies
bash install_deps.sh
# Start the application
bash start_app.sh
```

### 3. YOLOv8 Object Detection (yolov8_detection)

A real-time object detection web application based on the **YOLOv8 model**, supporting image uploads and live detection.

**Key Features:**
* Object detection and recognition in images
* Real-time object localization
* Detection result visualization
* Supports recognition of multiple object categories

**Technology Stack:**
* **Backend**: Flask, Ultralytics YOLOv8
* **Frontend**: HTML, JavaScript
* **Deep Learning**: YOLOv8 pre-trained model

**How to Run:**
```bash
cd yolov8_detection
# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Start the application
bash start_app.sh  # or ./start_app.sh
```

---

## Unified Dependency Installation

If you wish to install all sub-project dependencies at once, you can use the unified dependency file in the root directory:

```bash
# Create global virtual environment
python -m venv multimedia_apps_env
source multimedia_apps_env/bin/activate  # Linux/Mac
# multimedia_apps_env\Scripts\activate  # Windows

# Generate and install unified dependencies
python -c "import os; open('unified_requirements.txt', 'w').writelines(line for file in ['FaceRecog/requirements.txt', 'YouTube_API/requirements.txt', 'yolov8_detection/requirements.txt'] if os.path.exists(file) for line in open(file))"
pip install -r unified_requirements.txt
```

---

## Development and Contribution

1.  Fork this repository.
2.  Create your feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

## Acknowledgements

* Thanks to **Google MediaPipe** for the face recognition technology.
* Thanks to **YouTube Data API** for providing video search functionality.
* Thanks to **Ultralytics** for providing the **YOLOv8** model.