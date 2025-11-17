# 🚀 SafeSite AI - Complete Setup Guide

This guide will walk you through setting up SafeSite AI from scratch.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] Git installed
- [ ] Google account (for Gemini API)
- [ ] GCP account (optional, for Cloud Run deployment)
- [ ] Text editor or IDE

---

## 🔑 Step 1: Get Gemini API Key (5 minutes)

1. Visit [https://ai.google.dev](https://ai.google.dev)
2. Click "Get API Key in Google AI Studio"
3. Sign in with your Google account
4. Click "Create API Key"
5. Copy the key (starts with `AIza...`)
6. Save it securely - you'll need it in Step 4

---

## 📥 Step 2: Clone and Setup Project (5 minutes)

```bash
# Clone the repository (or download ZIP)
git clone <your-repo-url>
cd safesite-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Step 3: Configure Environment Variables (2 minutes)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your favorite editor
# On Windows:
notepad .env

# On macOS:
open .env

# On Linux:
nano .env
```

**Add your Gemini API key:**

```env
GEMINI_API_KEY=AIza...your_actual_key_here
GCP_PROJECT_ID=safesite-ai-bnb-2025
GCP_REGION=us-central1
```

Save and close the file.

---

## ▶️ Step 4: Run the Application (1 minute)

```bash
# Make sure virtual environment is activated
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

**That's it! You're ready to analyze construction sites!** 🎉

---

## 🧪 Step 5: Test the Application

1. **Upload a sample image**
   - Use any construction site photo
   - Recommended: Clear, well-lit image showing workers and site

2. **Fill in site information** (in sidebar)
   - Site ID: TEST-001
   - Location: Your City
   - Contractor: Test Contractor
   - Project Type: Residential

3. **Click "Analyze Safety Compliance"**
   - Wait 5-10 seconds for AI analysis
   - Review the results

4. **Explore the results**
   - Check compliance score
   - Review violations and warnings
   - See financial impact
   - Read action recommendations

---

## 🐳 Optional: Docker Setup

If you prefer running with Docker:

```bash
# Build the image
docker build -t safesite-ai:local .

# Run the container
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_api_key_here \
  safesite-ai:local

# Access at http://localhost:8080
```

---

## ☁️ Optional: Deploy to Cloud Run

### Prerequisites for Cloud Run

1. **Install Google Cloud CLI**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk

   # Linux
   curl https://sdk.cloud.google.com | bash

   # Windows: Download from https://cloud.google.com/sdk/docs/install
   ```

2. **Initialize gcloud**
   ```bash
   gcloud init
   ```

3. **Create GCP Project**
   ```bash
   # Create project
   gcloud projects create safesite-ai-bnb-2025 --name="SafeSite AI"

   # Set as active project
   gcloud config set project safesite-ai-bnb-2025

   # Enable billing (use your billing account)
   # Visit: https://console.cloud.google.com/billing
   ```

4. **Enable Required APIs**
   ```bash
   gcloud services enable \
     aiplatform.googleapis.com \
     run.googleapis.com \
     cloudbuild.googleapis.com \
     bigquery.googleapis.com \
     storage.googleapis.com
   ```

### Deploy

```bash
# Make deploy script executable (macOS/Linux)
chmod +x deploy.sh

# Set environment variables
export GEMINI_API_KEY=your_api_key_here
export GCP_PROJECT_ID=safesite-ai-bnb-2025

# Deploy
./deploy.sh
```

On Windows, use Git Bash or WSL to run the script.

---

## 📊 Optional: Setup BigQuery Analytics

1. **Create BigQuery Dataset**
   ```bash
   bq mk --dataset ${GCP_PROJECT_ID}:construction_safety
   ```

2. **Create Table with Schema**
   ```bash
   bq mk --table \
     construction_safety.violations \
     config/bigquery_schema.json
   ```

3. **Test BigQuery Logging**
   ```bash
   python utils/bigquery_logger.py
   ```

---

## 🔧 Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Gemini API key not found"

**Solution:**
- Check that `.env` file exists in project root
- Verify `GEMINI_API_KEY=` line has your actual key
- Restart the Streamlit app

### Issue: "Permission denied" when running deploy.sh

**Solution:**
```bash
chmod +x deploy.sh
```

### Issue: Streamlit won't start

**Solution:**
```bash
# Check if port 8501 is already in use
# Kill the process using the port, or use a different port:
streamlit run app.py --server.port 8502
```

### Issue: Docker build fails

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker build --no-cache -t safesite-ai:local .
```

---

## 📚 Project Structure

```
safesite-ai/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Dependencies
├── Dockerfile               # Container config
├── deploy.sh                # Deployment script
├── .env                     # Your config (not in git)
├── .env.example            # Template
├── README.md               # Main documentation
├── SETUP_GUIDE.md          # This file
├── utils/                  # Python modules
│   ├── gemini_vision.py    # AI integration
│   ├── bis_standards.py    # Standards database
│   ├── risk_scoring.py     # Risk calculation
│   └── bigquery_logger.py  # Analytics
├── config/                 # Configuration files
│   ├── bis_codes.json      # BIS standards data
│   └── bigquery_schema.json
└── .streamlit/            # Streamlit config
    └── config.toml
```

---

## 🎯 Next Steps

Once everything is working:

1. **Test with different images** - Try various construction scenarios
2. **Customize BIS standards** - Edit `config/bis_codes.json`
3. **Deploy to Cloud Run** - Make it accessible online
4. **Setup BigQuery** - Track analytics over time
5. **Write blog post** - Document your journey
6. **Demo preparation** - Practice your pitch

---

## 📖 Additional Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error message carefully
3. Check environment variables are set correctly
4. Ensure all dependencies are installed
5. Verify API key is valid

---

## ✅ Verification Checklist

Before considering setup complete:

- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] `.env` file created with valid Gemini API key
- [ ] Streamlit app runs successfully
- [ ] Can upload and analyze an image
- [ ] Results display correctly
- [ ] No error messages in terminal

**If all boxes are checked, you're ready to go!** 🚀

---

## 🎉 Success!

You've successfully set up SafeSite AI!

Now you can:
- Analyze construction site safety
- Detect BIS violations
- Generate compliance reports
- Save lives through AI

**Happy building!** 🏗️
