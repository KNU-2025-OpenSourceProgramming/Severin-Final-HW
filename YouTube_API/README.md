
# YouTube API Video Content Search

This is a Flask and React-based web application for searching YouTube video content. The application uses the **YouTube Data API v3** to implement video search functionality and provides external access via **ngrok**.

---

## Features

* **Search YouTube Videos**: Easily find videos by keywords.
* **Responsive User Interface**: Designed to look good on various screen sizes.
* **Detailed Video Information Display**: Shows comprehensive details for each video.
* **Embedded Video Player**: Potentially allows playing videos directly within the app (though the provided React code links out).
* **Real-time Video Preview and Links**: Provides thumbnails and direct links to YouTube.
* **API Quota Monitoring**: Includes mechanisms to track your API usage.
* **Robust Error Handling and Retry Mechanisms**: Ensures more reliable API calls.

---

## Installation and Configuration

### Prerequisites

* **Python 3.6+**
* A **valid YouTube Data API Key**

### Installation Steps

1.  Clone this repository or download the source code.
2.  Install the required Python packages:

    ```bash
    pip install flask google-api-python-client pyngrok flask-cors
    ```

3.  Set up your API Key (choose one of the three methods below):

    a.  **Using a `.env` file (Recommended)**:
        * Copy `.env.example` to `.env`.
        * Add your keys:
            ```
            YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
            NGROK_AUTH_TOKEN=YOUR_NGROK_AUTH_TOKEN
            ```

    b.  **Using a `config.py` file**:
        * Copy `config.template.py` to `config.py`.
        * Add your keys:
            ```python
            YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
            NGROK_AUTH_TOKEN = "YOUR_NGROK_AUTH_TOKEN"
            ```

    c.  **Using Environment Variables**:
        * Set them directly in your terminal:
            ```bash
            export YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY"
            export NGROK_AUTH_TOKEN="YOUR_NGROK_AUTH_TOKEN"
            ```

---

## Running the Application

### Easy Way

Use the provided launch script to automatically handle configuration and startup:

```bash
./start_app.sh
```

The script will check dependencies, configure, and start the application. If no valid API key is found, you will be prompted to enter it.

### Manual Way

1.  Set your API Key via environment variables (recommended):

    ```bash
    source setup_env.sh YOUR_API_KEY
    ```

    Alternatively, edit the `config.py` file to add your API Key.

2.  Execute the following command to start the application:

    ```bash
    python run_server.py
    ```

3.  The application will start, and the **ngrok public URL** will be printed in the console. You can access the application from any device via this URL.

---

## Obtaining a YouTube API Key

1.  Visit the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a **new project**.
3.  Enable **YouTube Data API v3** within your project (search and enable it under "APIs & Services > Library").
4.  Create credentials > **API Key**.
5.  Add the obtained API Key to your `config.py` file or set it as an environment variable.

---

## Technology Stack

* **Backend**: Flask (Python)
* **Frontend**: React (JavaScript)
* **API**: YouTube Data API v3
* **Deployment Tool**: ngrok

---

## Important Notes

* The **YouTube Data API** has daily **quota limits**. Free accounts typically have a daily quota of 10,000 units.
* Each `search.list` call consumes **100 units**.
* **Keep your API Key secure**; do not expose it directly in client-side code.

---

## Developer

* Severin Ye

## License

This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file in the root directory for details.
