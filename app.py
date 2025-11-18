"""
ConStrite - Construction Safety Monitoring Application
Powered by Gemini 2.5 Pro
"""

import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import json
from datetime import datetime

# Import custom modules
from utils.gemini_vision import ConstructionSafetyAnalyzer
from utils.bis_standards import BISDatabase
from utils.risk_scoring import calculate_risk_score, prioritize_actions, calculate_financial_impact
from utils.pdf_generator import SafetyReportPDF
from utils.firestore_manager import FirestoreManager
from utils.cloud_storage import CloudStorageManager
from utils.bigquery_logger import BigQueryLogger

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ConStrite - Construction Safety Monitor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Modern Design & Typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .main {
        background: linear-gradient(to bottom, #f8fafc 0%, #f1f5f9 100%);
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 2.5rem;
        box-shadow: 0 20px 60px -15px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
    }

    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        position: relative;
    }

    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 400;
        position: relative;
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 10px 30px -5px rgba(0, 0, 0, 0.08);
        text-align: center;
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
    }

    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e293b 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }

    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        margin-top: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Violation Cards */
    .violation-card {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }

    .violation-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .violation-card h4 {
        font-size: 1.125rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
        line-height: 1.4;
    }

    .violation-card p {
        margin: 0.5rem 0;
        font-size: 0.9375rem;
        line-height: 1.6;
    }

    .violation-card strong {
        font-weight: 600;
        color: #1e293b;
    }

    .critical-violation {
        background: linear-gradient(to right, #fef2f2 0%, #ffffff 100%);
        border-color: #fecaca;
    }

    .critical-violation h4 {
        color: #dc2626;
    }

    .warning-violation {
        background: linear-gradient(to right, #fffbeb 0%, #ffffff 100%);
        border-color: #fed7aa;
    }

    .warning-violation h4 {
        color: #ea580c;
    }

    .compliant-item {
        background: linear-gradient(to right, #f0fdf4 0%, #ffffff 100%);
        border-color: #bbf7d0;
    }

    .compliant-item h4 {
        color: #16a34a;
    }

    /* Risk Badges */
    .risk-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.625rem 1.25rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        letter-spacing: 0.025em;
    }

    .risk-critical {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
    }
    .risk-high {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
    }
    .risk-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    .risk-low {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
    }

    /* Action Items */
    .action-item {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        position: relative;
        padding-left: 1.75rem;
    }

    .action-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        border-radius: 12px 0 0 12px;
        background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
        padding: 0.875rem 1.5rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transition: all 0.2s ease;
        font-size: 1rem;
        letter-spacing: 0.025em;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    /* Download Button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
    }

    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #15803d 0%, #166534 100%);
        box-shadow: 0 6px 20px rgba(22, 163, 74, 0.4);
    }

    /* Section Headers */
    h2 {
        font-size: 1.875rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 2rem;
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
    }

    h3 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        letter-spacing: -0.015em;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #ffffff 0%, #f8fafc 100%);
    }

    [data-testid="stSidebar"] .element-container {
        margin-bottom: 1rem;
    }

    /* File Uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        background: white;
        transition: all 0.2s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background: #f8fafc;
    }

    /* Stats Container */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }

    /* Icon Styles */
    .icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    /* Code Blocks */
    code {
        font-family: 'JetBrains Mono', monospace;
        background: #1e293b;
        color: #e2e8f0;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-size: 0.875rem;
    }

    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    """Render application header"""
    st.markdown("""
    <div class="main-header">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🏗️</div>
        <h1>ConStrite</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem; font-weight: 500;">AI-Powered Construction Safety Monitoring</p>
        <p style="font-size: 0.95rem; margin-top: 0.75rem; opacity: 0.85;">
            <span style="display: inline-block; margin: 0 0.5rem;">⚡ Powered by Gemini 2.5 Pro</span>
            <span style="display: inline-block; margin: 0 0.5rem;">•</span>
            <span style="display: inline-block; margin: 0 0.5rem;">🛡️ BIS Standards Compliant</span>
            <span style="display: inline-block; margin: 0 0.5rem;">•</span>
            <span style="display: inline-block; margin: 0 0.5rem;">🎯 Real-time Analysis</span>
        </p>
    </div>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'site_info' not in st.session_state:
        st.session_state.site_info = {}
    if 'firestore_manager' not in st.session_state:
        st.session_state.firestore_manager = FirestoreManager()
    if 'cloud_storage' not in st.session_state:
        st.session_state.cloud_storage = CloudStorageManager()
    if 'bigquery_logger' not in st.session_state:
        st.session_state.bigquery_logger = BigQueryLogger()
    if 'pdf_generator' not in st.session_state:
        st.session_state.pdf_generator = SafetyReportPDF()
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False


def render_login():
    """Render the login form."""
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            # Hardcoded credentials for demonstration
            if username == "site_owner" and password == "safesite":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password")

def render_sidebar():
    """Render sidebar with site information and BIS standards"""
    with st.sidebar:
        if st.session_state.logged_in:
            st.header("📋 About ConStrite")

            with st.expander("❓ The Problem"):
                st.write("""
                **48,000 construction workers die annually in India**

                - 130+ deaths every day
                - Most are preventable
                - Manual inspections are inadequate
                - BIS standards often not enforced
                """)

            with st.expander("✨ Our Solution"):
                st.write("""
                **AI-Powered Safety Monitoring**

                - Instant safety analysis (5 seconds)
                - BIS standards compliance checking
                - Real-time violation detection
                - Actionable recommendations
                - Cost vs fine analysis
                """)

            with st.expander("🎯 Impact"):
                st.write("""
                **Potential to save thousands of lives**

                - Early hazard detection
                - Prevent accidents before they happen
                - Ensure regulatory compliance
                - Reduce financial penalties
                - Create safer work environments
                """)

            st.divider()

            st.header("🏗️ Site Information")

            site_id = st.text_input("Site ID", placeholder="e.g., BLR-SITE-001")
            location = st.text_input("Location", placeholder="e.g., Bangalore, Karnataka")
            contractor = st.text_input("Contractor Name", placeholder="e.g., ABC Constructions")
            project_type = st.selectbox(
                "Project Type",
                ["Residential", "Commercial", "Infrastructure", "Industrial", "Mixed-Use"]
            )

            st.session_state.site_info = {
                'site_id': site_id,
                'location': location,
                'contractor': contractor,
                'project_type': project_type,
                'timestamp': datetime.now().isoformat()
            }

            st.divider()

            # BIS Standards Reference
            st.header("📚 BIS Standards Reference")

            with st.expander("View All Standards"):
                bis_db = BISDatabase()
                standards = bis_db.get_all_standards()

                for std in standards[:5]:  # Show first 5
                    st.markdown(f"**{std.code}**")
                    st.caption(std.title)
                    st.write(f"Penalty: {std.penalty}")
                    st.divider()

                st.caption(f"Total: {len(standards)} BIS standards loaded")

            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()
        else:
            render_login()


def render_upload_section():
    """Render image upload section"""
    st.header("📸 Upload Construction Site Image")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear photo of the construction site"
        )

        if uploaded_file is not None:
            st.session_state.uploaded_image = uploaded_file

            # Display image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Site Image", use_column_width=True)

            return True

    with col2:
        st.info("""
        **📷 Tips for Best Results:**

        ✅ Clear, well-lit image
        ✅ Wide angle showing work area
        ✅ Workers visible
        ✅ Safety equipment visible
        ✅ Minimum 1MP resolution
        """)

    return False


def render_analysis_results():
    """Render analysis results"""
    if st.session_state.analysis_result is None:
        return

    result = st.session_state.analysis_result

    st.header("📊 Safety Analysis Results")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{result.get('total_workers', 0)}</div>
            <div class="metric-label">Total Workers</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #4caf50;">{result.get('workers_compliant', 0)}</div>
            <div class="metric-label">Compliant Workers</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #f44336;">{result.get('workers_non_compliant', 0)}</div>
            <div class="metric-label">Non-Compliant</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        score = result.get('overall_compliance_score', 0)
        score_color = '#4caf50' if score >= 80 else '#ff9800' if score >= 50 else '#f44336'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {score_color};">{score}%</div>
            <div class="metric-label">Compliance Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Risk Assessment
    risk_data = calculate_risk_score(result)

    col1, col2 = st.columns([1, 2])

    with col1:
        risk_class = f"risk-{risk_data['risk_level'].lower()}"
        st.markdown(f"""
        <div style="text-align: center;">
            <h3>Risk Assessment</h3>
            <div class="risk-badge {risk_class}">
                {risk_data['risk_level']} RISK
            </div>
            <p style="font-size: 2rem; font-weight: bold; margin: 1rem 0;">
                {risk_data['risk_score']}/100
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: #f5f5f5; padding: 1.5rem; border-radius: 8px;">
            <h4>Recommendation</h4>
            <p>{risk_data['recommendation']}</p>
            <p><strong>Action Required:</strong> {risk_data['action_urgency'].replace('_', ' ')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Financial Impact
    financial = calculate_financial_impact(result)

    st.subheader("💰 Financial Impact Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Potential Fine",
            f"₹{financial['potential_fine']:,.0f}",
            delta=None,
            delta_color="inverse"
        )

    with col2:
        st.metric(
            "Compliance Cost",
            f"₹{financial['compliance_cost']:,.0f}",
            delta=None
        )

    with col3:
        st.metric(
            "Potential Savings",
            f"₹{financial['potential_savings']:,.0f}",
            delta=f"ROI: {financial['roi_percentage']:.0f}%",
            delta_color="normal"
        )

    st.divider()

    # Violations Section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚨 Critical Violations")
        critical_violations = result.get('critical_violations', [])

        if critical_violations:
            for i, violation in enumerate(critical_violations, 1):
                confidence = violation.get('confidence', 85)
                confidence_color = '#4caf50' if confidence >= 80 else '#ff9800' if confidence >= 60 else '#f44336'
                st.markdown(f"""
                <div class="violation-card critical-violation">
                    <h4>#{i} {violation.get('violation', 'Unknown')}
                        <span style="float: right; color: {confidence_color}; font-size: 0.9em;">
                            🎯 {confidence}% confidence
                        </span>
                    </h4>
                    <p><strong>Location:</strong> {violation.get('location', 'Unknown')}</p>
                    <p><strong>BIS Code:</strong> {violation.get('bis_code', 'N/A')}</p>
                    <p><strong>Recommendation:</strong> {violation.get('recommendation', 'Fix immediately')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No critical violations detected!")

        st.subheader("⚠️ Warnings")
        warnings = result.get('warnings', [])

        if warnings:
            for i, warning in enumerate(warnings, 1):
                confidence = warning.get('confidence', 85)
                confidence_color = '#4caf50' if confidence >= 80 else '#ff9800' if confidence >= 60 else '#f44336'
                st.markdown(f"""
                <div class="violation-card warning-violation">
                    <h4>#{i} {warning.get('violation', 'Unknown')}
                        <span style="float: right; color: {confidence_color}; font-size: 0.9em;">
                            🎯 {confidence}% confidence
                        </span>
                    </h4>
                    <p><strong>Location:</strong> {warning.get('location', 'Unknown')}</p>
                    <p><strong>BIS Code:</strong> {warning.get('bis_code', 'N/A')}</p>
                    <p><strong>Risk Level:</strong> {warning.get('risk_level', 'MEDIUM')}</p>
                    <p><strong>Recommendation:</strong> {warning.get('recommendation', 'Address soon')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No warnings!")

    with col2:
        st.subheader("✅ Compliant Items")
        compliant_items = result.get('compliant_items', [])

        if compliant_items:
            for item in compliant_items:
                st.markdown(f"""
                <div class="violation-card compliant-item">
                    <p>✓ {item}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No compliant items detected")

    st.divider()

    # Action Plan
    st.subheader("📋 Immediate Action Plan")

    actions = prioritize_actions(result)

    for action in actions[:10]:  # Show top 10 actions
        urgency_color = {
            'IMMEDIATE': '#f44336',
            'HIGH': '#ff9800',
            'MEDIUM': '#2196f3'
        }.get(action['urgency'], '#757575')

        st.markdown(f"""
        <div class="action-item">
            <h4 style="color: {urgency_color};">
                Priority {action['priority']} - [{action['urgency']}]
            </h4>
            <p><strong>Action:</strong> {action['action']}</p>
            <p><strong>Violation:</strong> {action['violation']}</p>
            <p><strong>Location:</strong> {action['location']}</p>
            <p><strong>BIS Code:</strong> {action['bis_code']}</p>
            <p><strong>Estimated Time:</strong> {action['estimated_time']} |
               <strong>Est. Cost:</strong> {action['estimated_cost']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Download options
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Download JSON Report"):
            json_data = json.dumps(result, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"safety_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    with col2:
        if st.button("📋 Copy Summary"):
            summary = f"""
            ConStrite Analysis Summary
            ----------------------------
            Compliance Score: {result.get('overall_compliance_score', 0)}%
            Risk Level: {risk_data['risk_level']}
            Critical Violations: {len(result.get('critical_violations', []))}
            Warnings: {len(result.get('warnings', []))}
            Total Workers: {result.get('total_workers', 0)}
            """
            st.code(summary)

    with col3:
        if st.button("📄 Generate PDF Report"):
            with st.spinner("Generating professional PDF report..."):
                try:
                    # Get necessary data
                    financial = calculate_financial_impact(result)
                    actions = prioritize_actions(result)

                    # Generate PDF
                    pdf_generator = st.session_state.pdf_generator
                    pdf_buffer = pdf_generator.generate_report(
                        result,
                        st.session_state.site_info,
                        risk_data,
                        financial,
                        actions
                    )

                    # Offer download
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"ConStrite_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ PDF report generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")


def main():
    """Main application"""
    initialize_session_state()
    render_sidebar()

    if st.session_state.logged_in:
        render_header()

        # Check for API key
        api_key = os.getenv('GEMINI_API_KEY')

        if not api_key:
            st.error("""
            ⚠️ **Gemini API Key Not Found**

            Please set your GEMINI_API_KEY in the .env file.

            Get your free API key at: https://ai.google.dev
            """)

            with st.expander("📖 Setup Instructions"):
                st.code("""
# 1. Get API key from https://ai.google.dev
# 2. Create .env file in project root
# 3. Add the following line:
GEMINI_API_KEY=your_api_key_here

# 4. Restart the application
                """)
            return

        # Upload section
        has_image = render_upload_section()

        # Analyze button
        if has_image:
            st.divider()

            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                if st.button("🔍 Analyze Safety Compliance", type="primary"):
                    with st.spinner("🤖 AI is analyzing the construction site... This may take 10-15 seconds..."):
                        try:
                            # Save uploaded file temporarily
                            temp_path = "temp_upload.jpg"
                            image = Image.open(st.session_state.uploaded_image)
                            image.save(temp_path)

                            # Analyze image
                            analyzer = ConstructionSafetyAnalyzer(api_key)
                            result = analyzer.analyze_image(temp_path)

                            # Store result
                            st.session_state.analysis_result = result

                            # Upload image to Cloud Storage (optional)
                            image_url = None
                            if st.session_state.cloud_storage.client:
                                with st.spinner("Uploading image to cloud..."):
                                    site_id = st.session_state.site_info.get('site_id', 'unknown')
                                    image_url = st.session_state.cloud_storage.upload_image(
                                        temp_path,
                                        site_id=site_id
                                    )
                                    if image_url:
                                        st.session_state.image_url = image_url

                            # Calculate additional data
                            risk_data = calculate_risk_score(result)
                            financial_data = calculate_financial_impact(result)

                            # Save to Firestore (optional)
                            if st.session_state.firestore_manager.db:
                                with st.spinner("Saving to database..."):
                                    doc_id = st.session_state.firestore_manager.save_analysis(
                                        result,
                                        st.session_state.site_info,
                                        risk_data,
                                        financial_data,
                                        image_url
                                    )
                                    if doc_id:
                                        st.session_state.analysis_id = doc_id

                            # Log to BigQuery (optional)
                            if st.session_state.bigquery_logger.client:
                                st.session_state.bigquery_logger.log_analysis(
                                    result,
                                    st.session_state.site_info
                                )

                            # Clean up
                            os.remove(temp_path)

                            st.success("✅ Analysis complete!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error during analysis: {str(e)}")
                            st.info("Please check your API key and try again.")

        # Render results if available
        if st.session_state.analysis_result is not None:
            st.divider()
            render_analysis_results()

        # Footer
        st.divider()
        st.markdown("""
        <div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
            <p>🏗️ ConStrite - Built with ❤️ for BNB Marathon 2025</p>
            <p>Powered by Gemini 2.5 Pro | Google Cloud Platform</p>
            <p style="font-size: 0.8rem; margin-top: 1rem;">
                Making construction sites safer, one analysis at a time
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.title("Welcome to ConStrite")
        st.write("Please log in to access the application.")
        st.info("Use the sidebar to log in.")


if __name__ == "__main__":
    main()
