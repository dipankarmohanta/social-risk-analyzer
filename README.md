# Social Risk Analyzer

Social Risk Analyzer is a Python-based application that analyzes social media content and evaluates potential risk using machine learning techniques. The project extracts features from social data and classifies profiles or content based on risk indicators.

This project is designed to be usable both as an academic project and as a real-world prototype for social risk analysis systems.

---

## Features

* Social media content feature extraction
* Machine learning–based risk prediction
* Pre-trained model support
* Simple local execution
* Modular code structure

---

## Project Structure

```
social-risk-analyzer/
│
├── app.py                  # Main application entry point
├── extractor.py            # Data extraction logic
├── features.py             # Feature engineering
├── model.py                # Model loading and prediction
├── model.pkl               # Trained ML model (may vary)
├── risk_model.joblib       # Alternative trained model
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## Requirements

* Python 3.8 or higher
* pip (Python package manager)
* Git

---

## Installation & Setup

### Step 1: Clone the Repository

```
git clone https://github.com/dipankarmohanta/social-risk-analyzer.git
cd social-risk-analyzer
```

---

### Step 2: Create a Virtual Environment (Recommended)

**Windows**

```
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running the Application

Start the application using:

```
python app.py
```

If the application starts successfully, you should see a message indicating the local server is running.

---

## Accessing the Application

Open your browser and visit:

```
http://127.0.0.1:5000
```

or

```
http://localhost:5000
```

---

## Stopping the Application

Press the following keys in the terminal:

```
CTRL + C
```

---

## Common Issues & Solutions

**ModuleNotFoundError**

* Ensure the virtual environment is activated
* Ensure all dependencies are installed using `requirements.txt`

**Model file not found**

* Verify that `model.pkl` or `risk_model.joblib` exists in the project root
* Ensure the model filename matches the one used in `model.py`

**Port already in use**

* Stop other running Python servers
* Change the port number inside `app.py`

---

## How It Works (High Level)

1. Social media input is provided to the application
2. Text or profile data is extracted using `extractor.py`
3. Features are generated via `features.py`
4. The trained ML model predicts a risk score or category
5. Results are returned to the user interface or API response

---

## Use Cases

* Fake profile detection
* Social media risk assessment
* Content moderation research
* Academic ML projects

---

## Future Improvements

* Add real-time social media API integration
* Improve model accuracy with deep learning
* Add authentication and dashboards
* Deploy as a cloud-based service

---

## Author

**Dipankar Mohanta**
GitHub: [https://github.com/dipankarmohanta](https://github.com/dipankarmohanta)

---

## License

This project is for educational and research purposes.
You may modify and use it with proper attribution.

---

⭐ If you find this project useful, please consider giving it a star on GitHub!
