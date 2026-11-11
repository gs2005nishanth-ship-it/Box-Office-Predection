# 🎬 CineMetric AI — Box Office Prediction & Analytics Platform

An end-to-end Machine Learning and Generative AI platform for worldwide movie box office revenue forecasting, financial risk analysis, and historical film performance analytics.

---

## 🌟 Key Features

- **Advanced Machine Learning Engine**:
  - Compares and benchmarks 6 regression models: **Gradient Boosting**, **Hist Gradient Boosting**, **Random Forest**, **Ridge**, **Lasso**, and **Linear Regression**.
  - Engineered features on TMDB metadata: budget, runtime, holiday season release, franchise/collection indicators, genre distribution, cast star power, and director history.
  - Log-transformed revenue target modeling evaluated with **RMSLE**, **RMSE**, and **R² Score**.
- **Interactive ML Budget Simulator**:
  - Test custom film scenarios with real-time budget, runtime, release timing, and genre combinations.
  - Calculates predicted gross, confidence bounds, ROI percentage, profit multiplier, and commercial verdict (e.g., *All-Time Blockbuster*, *Super Hit*, *Profitable Hit*, *Flop*).
- **Live AI Movie Intelligence (Groq LLM)**:
  - Instant query system retrieving verified worldwide, domestic, and overseas gross, production budget, financial breakdown, and trivia for films worldwide.
- **Interactive Web Dashboard**:
  - Glassmorphic UI with real-time analytics, dataset search and filtering across 3,000+ movies, model comparison cards, and Kaggle `submission.csv` preview & export.
- **Terminal CLI Tools**:
  - Interactive CLI tool (`query_movie.py`) to search film financials directly in your command prompt.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/gs2005nishanth-ship-it/Box-Office-Predection.git
cd <your-repo-name>
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Set Up Environment Variables (Optional)
Copy `.env.example` to `.env` and set your Groq API key:
```bash
copy .env.example .env
```

### 4. Run the Web Dashboard
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 💻 CLI Usage

### Interactive Movie Lookup
```bash
python query_movie.py
```
Or query a film directly:
```bash
python query_movie.py "Oppenheimer"
```

### Run Model Training Standalone
```bash
python ml_engine.py
```

### Run Integration Tests
```bash
python test_app.py
```

---

## 📁 Project Structure

```
├── app.py                      # Flask backend API & routes
├── ml_engine.py                # ML pipeline, feature engineering & model training
├── llm_engine.py               # Live LLM movie intelligence engine (Groq)
├── query_movie.py              # Interactive CLI movie query tool
├── test_app.py                 # Full system integration test suite
├── test_groq.py                # Standalone Groq connectivity test
├── templates/
│   └── index.html              # Modern web dashboard interface
├── static/
│   ├── css/style.css           # Glassmorphism design system & styling
│   └── js/app.js               # Frontend logic, charts & API handlers
├── train.csv                   # Training dataset (TMDB)
├── test.csv                    # Test dataset
├── submission.csv              # Generated Kaggle test predictions
├── box_office_model.joblib     # Persisted best ML model state
├── requirements.txt            # Python dependencies
└── .gitignore                  # Ignored files & environments
```

---

## 📊 Models Benchmarked

| Model | R² Score | RMSLE | RMSE |
|---|---|---|---|
| **Gradient Boosting** (Best) | **0.5878** | **2.0396** | **$83.27M** |
| **Hist Gradient Boosting** | 0.6846 | 2.1110 | $72.84M |
| **Random Forest** | 0.7039 | 2.0748 | $70.57M |
| **Ridge Regression** | -8.9872 | 2.2601 | $409.86M |
| **Lasso Regression** | -0.9852 | 2.2307 | $182.73M |
| **Linear Regression** | -9.0239 | 2.2603 | $410.61M |

---

## 📜 License
MIT License. Free for educational and commercial use.

---

## Docker Deployment

The existing CineMetric AI Flask application is containerized using Docker.

### Docker Architecture

- Docker Image: Packages the application and dependencies.
- Docker Container: Runs the Flask application.
- Docker Volume: Stores datasets and model files persistently.
- Port Mapping: Exposes the application on port 5000.

### Build Docker Image

`docker build -t box-office-prediction .`

### Run Docker Container

`docker run -d --name box-office-app --restart unless-stopped -p 5000:5000 -v box-office-data:/app/data box-office-prediction`

Access the application at http://localhost:5000.

### Persistent Volume Storage

The named volume `box-office-data` is mounted at `/app/data`.

It stores:
- train.csv
- test.csv
- box_office_model.joblib
- submission.csv

The volume preserves data even when the container is removed.

### Backup and Restore

Create a backup directory using `mkdir -p backups`.

Create a compressed volume backup:

`docker run --rm -v box-office-data:/data:ro -v "$PWD/backups":/backup python:3.12-slim tar -czf /backup/box-office-data-backup.tar.gz -C /data .`

Verify the backup using:

`tar -tzf backups/box-office-data-backup.tar.gz`

Restore into a separate test volume:

`docker volume create box-office-restore-test`

`docker run --rm -v "$PWD/backups":/backup:ro -v box-office-restore-test:/data python:3.12-slim tar -xzf /backup/box-office-data-backup.tar.gz -C /data`

### Useful Docker Commands

| Command | Purpose |
|---|---|
| `docker ps` | View running containers |
| `docker logs box-office-app` | View application logs |
| `docker stop box-office-app` | Stop the container |
| `docker start box-office-app` | Start the container |
| `docker volume ls` | List Docker volumes |
| `docker images` | List Docker images |

### Testing and Validation

The following operations were tested successfully:

- Docker image built successfully.
- Flask application launched inside the container.
- Website accessed through port 5000.
- Volume data persisted after container removal.
- Backup archive created and verified.
- Backup restored into a separate test volume.


---

## Docker Deployment

The existing CineMetric AI Flask application is containerized using Docker.

### Docker Architecture

- Docker Image: Packages the application and dependencies.
- Docker Container: Runs the Flask application.
- Docker Volume: Stores datasets and model files persistently.
- Port Mapping: Exposes the application on port 5000.

### Build Docker Image

`docker build -t box-office-prediction .`

### Run Docker Container

`docker run -d --name box-office-app --restart unless-stopped -p 5000:5000 -v box-office-data:/app/data box-office-prediction`

Access the application at http://localhost:5000.

### Persistent Volume Storage

The named volume `box-office-data` is mounted at `/app/data`.

It stores:
- train.csv
- test.csv
- box_office_model.joblib
- submission.csv

The volume preserves data even when the container is removed.

### Backup and Restore

Create a backup directory using `mkdir -p backups`.

Create a compressed volume backup:

`docker run --rm -v box-office-data:/data:ro -v "$PWD/backups":/backup python:3.12-slim tar -czf /backup/box-office-data-backup.tar.gz -C /data .`

Verify the backup using:

`tar -tzf backups/box-office-data-backup.tar.gz`

Restore into a separate test volume:

`docker volume create box-office-restore-test`

`docker run --rm -v "$PWD/backups":/backup:ro -v box-office-restore-test:/data python:3.12-slim tar -xzf /backup/box-office-data-backup.tar.gz -C /data`

### Useful Docker Commands

| Command | Purpose |
|---|---|
| `docker ps` | View running containers |
| `docker logs box-office-app` | View application logs |
| `docker stop box-office-app` | Stop the container |
| `docker start box-office-app` | Start the container |
| `docker volume ls` | List Docker volumes |
| `docker images` | List Docker images |

### Testing and Validation

The following operations were tested successfully:

- Docker image built successfully.
- Flask application launched inside the container.
- Website accessed through port 5000.
- Volume data persisted after container removal.
- Backup archive created and verified.
- Backup restored into a separate test volume.


---

## Docker Deployment

The existing CineMetric AI Flask application is containerized using Docker.

### Docker Architecture

- Docker Image: Packages the application and dependencies.
- Docker Container: Runs the Flask application.
- Docker Volume: Stores datasets and model files persistently.
- Port Mapping: Exposes the application on port 5000.

### Build Docker Image

`docker build -t box-office-prediction .`

### Run Docker Container

`docker run -d --name box-office-app --restart unless-stopped -p 5000:5000 -v box-office-data:/app/data box-office-prediction`

Access the application at http://localhost:5000.

### Persistent Volume Storage

The named volume `box-office-data` is mounted at `/app/data`.

It stores:
- train.csv
- test.csv
- box_office_model.joblib
- submission.csv

The volume preserves data even when the container is removed.

### Backup and Restore

Create a backup directory using `mkdir -p backups`.

Create a compressed volume backup:

`docker run --rm -v box-office-data:/data:ro -v "$PWD/backups":/backup python:3.12-slim tar -czf /backup/box-office-data-backup.tar.gz -C /data .`

Verify the backup using:

`tar -tzf backups/box-office-data-backup.tar.gz`

Restore into a separate test volume:

`docker volume create box-office-restore-test`

`docker run --rm -v "$PWD/backups":/backup:ro -v box-office-restore-test:/data python:3.12-slim tar -xzf /backup/box-office-data-backup.tar.gz -C /data`

### Useful Docker Commands

| Command | Purpose |
|---|---|
| `docker ps` | View running containers |
| `docker logs box-office-app` | View application logs |
| `docker stop box-office-app` | Stop the container |
| `docker start box-office-app` | Start the container |
| `docker volume ls` | List Docker volumes |
| `docker images` | List Docker images |

### Testing and Validation

The following operations were tested successfully:

- Docker image built successfully.
- Flask application launched inside the container.
- Website accessed through port 5000.
- Volume data persisted after container removal.
- Backup archive created and verified.
- Backup restored into a separate test volume.

