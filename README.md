# 🏗️ ConStrite - AI-Powered Construction Safety Monitor

[![Gemini 2.5 Pro](https://img.shields.io/badge/Gemini-2.5%20Pro-4285F4?logo=google)](https://ai.google.dev)
[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Ready-4285F4?logo=google-cloud)](https://cloud.google.com/run)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-FF4B4B?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)

> **Real-time AI safety analysis to prevent construction site accidents and ensure BIS compliance**

ConStrite uses Google's Gemini 2.5 Pro vision AI to analyze construction site photos and detect safety violations in real-time, helping prevent the 48,000+ annual construction deaths in India.

---

## 🎯 Problem

Every day in India, **130 construction workers die** due to preventable safety violations. Manual safety inspections are:
- Slow and infrequent
- Inconsistent in enforcement
- Reactive rather than proactive
- Resource-intensive

## ✨ Solution

ConStrite provides **instant AI-powered safety analysis** in just 5 seconds:

✅ **Instant Violation Detection** - AI identifies safety hazards in real-time
✅ **BIS Compliance Checking** - Validates against 15+ Indian safety standards
✅ **Risk Assessment** - 0-100 risk scoring with urgency classification
✅ **Financial Impact** - Calculate potential fines vs compliance costs
✅ **Actionable Insights** - Prioritized recommendations with timeline and budget
✅ **Analytics Dashboard** - Track safety trends across sites and contractors

---

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/ashbuildsites/constrite.git
cd constrite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run application
streamlit run app.py
```

Visit `http://localhost:8501`

### Docker Deployment

```bash
# Build image
docker build -t constrite .

# Run container
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_api_key \
  constrite
```

### Google Cloud Run

```bash
# Deploy directly from source
gcloud run deploy constrite \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key
```

---

## 🎨 Key Features

### 1. AI Vision Analysis
Upload construction site photos and receive comprehensive safety analysis powered by Gemini 2.5 Pro multimodal AI.

### 2. BIS Standards Validation
Automatic checking against 15+ Bureau of Indian Standards safety codes:
- **IS 2925:1984** - Safety Helmets
- **IS 3696:1966** - Safety Harnesses
- **IS 4014:1967** - Scaffolding Safety
- **IS 14489:1998** - Ladder Safety
- **IS 2190:2010** - Fire Safety Equipment
- And more...

### 3. Intelligent Risk Scoring
Four-tier risk assessment system:
- 🟢 **LOW (0-24)**: Good compliance, routine monitoring
- 🟠 **MEDIUM (25-49)**: Minor violations, 48-hour action
- 🔴 **HIGH (50-74)**: Serious violations, 24-hour action
- ⚫ **CRITICAL (75-100)**: Life-threatening, immediate halt required

### 4. Financial Impact Analysis
- Potential regulatory fines
- Estimated compliance costs
- ROI calculations
- Cost-benefit analysis

### 5. Professional PDF Reports
Generate comprehensive safety reports with:
- Executive summary
- Detailed violation breakdowns
- Photographic evidence
- Actionable recommendations
- Compliance checklist

### 6. Cloud Integration (Optional)
- **BigQuery**: Historical analytics and trend analysis
- **Firestore**: Real-time data synchronization
- **Cloud Storage**: Secure image archival

---

## 🏗️ Architecture

```
┌──────────────┐
│   User       │
│  (Browser)   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Streamlit Frontend  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐      ┌─────────────────┐
│  Gemini 2.5 Pro API  │◄─────│ BIS Standards   │
│  Vision Analysis     │      │ Database        │
└──────┬───────────────┘      └─────────────────┘
       │
       ▼
┌──────────────────────┐
│  Risk Scoring Engine │
│  Financial Calculator│
└──────┬───────────────┘
       │
       ├──────────┬──────────┬──────────┐
       ▼          ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │BigQuery│ │Firestore│ │Storage│ │  PDF   │
   └────────┘ └────────┘ └────────┘ └────────┘
```

Deployed on **Google Cloud Run** for automatic scaling and serverless execution.

---

## 📁 Project Structure

```
constrite/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── .env.example             # Environment template
├── README.md                # Documentation
├── LICENSE                  # MIT License
│
├── utils/
│   ├── gemini_vision.py     # Gemini API integration
│   ├── bis_standards.py     # BIS standards database
│   ├── risk_scoring.py      # Risk calculation engine
│   ├── pdf_generator.py     # PDF report generation
│   ├── firestore_manager.py # Firestore integration
│   ├── cloud_storage.py     # GCS integration
│   └── bigquery_logger.py   # BigQuery analytics
│
├── pages/
│   ├── live_monitoring.py   # Real-time dashboard
│   └── site_analytics.py    # Historical analytics
│
├── .streamlit/
│   └── config.toml          # Streamlit configuration
│
└── samples/                 # Sample construction images
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **AI/ML** | Google Gemini 2.5 Pro (Multimodal) |
| **Frontend** | Streamlit 1.29.0 |
| **Backend** | Python 3.9+ |
| **Database** | BigQuery, Firestore |
| **Storage** | Google Cloud Storage |
| **Deployment** | Cloud Run (Serverless) |
| **Container** | Docker |
| **PDF Generation** | ReportLab |

---

## 📊 Usage

1. **Upload Photo**: Take or upload construction site image
2. **Enter Details**: Site ID, location, contractor information
3. **Analyze**: AI processes image in 5-10 seconds
4. **Review Results**:
   - Compliance score
   - Critical violations
   - Risk assessment
   - Financial impact
5. **Download Report**: Professional PDF with recommendations
6. **Track Progress**: Monitor improvements over time

---

## 🎯 Use Cases

### Construction Site Managers
- Daily safety inspections
- Contractor compliance monitoring
- Risk mitigation planning

### Safety Officers
- Real-time violation detection
- Compliance documentation
- Audit trail generation

### Government Inspectors
- Multi-site monitoring
- Regulatory compliance verification
- Violation tracking

### Contractors & Builders
- Pre-inspection checks
- Safety training tool
- Cost optimization

---

## 📚 BIS Standards Covered

| Code | Description | Severity |
|------|-------------|----------|
| IS 2925:1984 | Safety Helmets | CRITICAL |
| IS 3696:1966 | Safety Harnesses & Belts | CRITICAL |
| IS 4014:1967 | Scaffolding Safety | CRITICAL |
| IS 14489:1998 | Portable Ladders | HIGH |
| IS 2190:2010 | Fire Extinguishers | HIGH |
| IS 4081:1996 | Safety Nets | CRITICAL |
| IS 3764:1992 | Safety Signs | MEDIUM |
| IS 1646:1997 | Excavation Safety | CRITICAL |
| IS 5216:1982 | Safety Footwear | HIGH |
| IS 15750:2008 | High-Visibility Clothing | MEDIUM |
| IS 694:1990 | PVC Insulated Cables | CRITICAL |
| IS 3043:1987 | Earthing Code | CRITICAL |
| IS 7205:1974 | First Aid | HIGH |
| IS 4756:1978 | Building Demolition | CRITICAL |
| IS 7293:1984 | Welding Safety | HIGH |

---

## 🔐 Environment Variables

Create a `.env` file with:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional - for cloud features
GCP_PROJECT_ID=your_project_id
GCP_REGION=asia-south1
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# BigQuery
BIGQUERY_DATASET=construction_safety
BIGQUERY_TABLE=violations

# Firestore
FIRESTORE_COLLECTION=site_analyses

# Cloud Storage
GCS_BUCKET=your_bucket_name
```

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Google Gemini Team for the powerful vision AI
- Bureau of Indian Standards for comprehensive safety codes
- Construction workers everywhere who inspire safer workplaces

---

## 📧 Contact

**Developer**: [@ashbuildsites](https://github.com/ashbuildsites)

**Project**: [https://github.com/ashbuildsites/constrite](https://github.com/ashbuildsites/constrite)

**Issues**: [Report bugs or request features](https://github.com/ashbuildsites/constrite/issues)

---

## 🚦 Project Status

✅ **Core Features**: Complete
✅ **Testing**: Validated
✅ **Deployment**: Cloud Run ready
✅ **Documentation**: Comprehensive
🚧 **Mobile App**: Planned
🚧 **Multi-language**: Planned

---

## 💡 Impact

**Target Audience**: 70,000+ active construction sites in India

**Potential Impact**:
- Reduce construction deaths by up to 70%
- Save billions in accident costs and fines
- Improve worker safety awareness
- Enable proactive safety management

---

<div align="center">

### 🏗️ ConStrite - Safer Construction Sites Through AI

**[Get Started](#-quick-start)** • **[Documentation](#-key-features)** • **[Deploy](#-docker-deployment)**

*Making construction sites safer, one image at a time.*

</div>
