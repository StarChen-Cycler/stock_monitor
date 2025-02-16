
# Stock Analytics Web App
[![License MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

1. Description
2. Requirements
3. Installation & Setup with Miniconda
4. Running the Application
5. Deployment Guide
6. Git Workflow

## 1. Description
A Flask-based stock visualization and analysis tool with user authentication and interactive charts using ECharts. Users can display historical stock data, apply technical indicators, and save custom strategies.

## 2. Requirements
- Python 3.8+
- Node.js (for frontend dependencies, if needed)
- Miniconda/Anaconda (recommended for dependency management)
- Required Python packages: `pip install -r requirements.txt`
- Parquet file processing dependencies (PyArrow or Fastparquet)
- Database: SQLite (default) or PostgreSQL (optional)

## 3. Installation & Setup Using Miniconda
### Step 1: Install Miniconda
Download Miniconda from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html) and follow the installation instructions for your OS.

### Step 2: Create a Conda Environment
```bash
conda create --name stock_env python=3.8
conda activate stock_env
```

### Step 3: Install Project Dependencies
```bash
pip install -r flask_app/requirements.txt
```

### Step 4: Prepare Environment Variables
Configure your environment with the secret key and database URI:
```bash
export FLASK_APP=flask_app/app.py  # Linux/Mac
set FLASK_APP=flask_app/app.py     # Windows
```

## 4. Running the Application
### Step 1: Initialize Database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Step 2: Start the Flask Application
```bash
python flask_app/app.py
```
The app will be available at `http://localhost:5000`.

### Step 3: Load Sample Data (if using merged_data.parquet)
Ensure the `data/merged_data.parquet` file is present or replace it with your dataset.

## 5. Deployment Guide
### Production Deployment
1. **Use a Production-Grade WSGI Server**: Gunicorn or uWSGI
2. **Database**: Migrate to PostgreSQL for production
3. **Reverse Proxy**: Set up Nginx or Apache
4. **Session Management**: Configure Redis for sessions

### Example Dockerfile
```Dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install -r flask_app/requirements.txt
EXPOSE 5000
CMD ["gunicorn", "flask_app/app:app", "-b", "0.0.0.0:5000", "--workers", "3"]
```

## 6. Git Workflow
### Workflow Overview
1. **Local Development**: Code and commit changes locally
2. **Version Control**: Push to a remote repository (GitHub/Bitbucket)
3. **Collaboration**: Use pull requests and issue tracking

### Basic Git Commands
1. **Initialize Repository**
   ```bash
   git init
   ```

2. **Add Files**
   ```bash
   git add .
   # Or specific files:
   git add file1.py file2.py
   ```

3. **Commit Changes**
   ```bash
   git commit -m "Your descriptive commit message"
   ```

4. **Push to Remote**
   ```bash
   git remote add origin <repository_url>
   git push -u origin main
   ```

5. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

### Local vs. Remote Git
- **Local Repository**: Stores commits and history on your machine
- **Remote Repository**: Hosted on services like GitHub (e.g., `origin/main`)
- **Workflow**:
1. Clone the remote repository to create a local copy
2. Branch to create a new feature or fix
3. Commit and push branches for review
4. Merge changes into the main branch

---

