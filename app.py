"""
SafeSite AI - Construction Safety Monitoring Application
Powered by Gemini 2.0 Flash Vision
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

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SafeSite AI - Construction Safety Monitor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #1f77b4 0%, #2c3e50 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #1f77b4;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-top: 0.5rem;
    }

    .violation-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }

    .critical-violation {
        background: #ffebee;
        border-left-color: #f44336;
    }

    .warning-violation {
        background: #fff3e0;
        border-left-color: #ff9800;
    }

    .compliant-item {
        background: #e8f5e9;
        border-left-color: #4caf50;
    }

    .risk-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        color: white;
        margin: 0.5rem 0;
    }

    .risk-critical { background: #B71C1C; }
    .risk-high { background: #E53935; }
    .risk-medium { background: #FB8C00; }
    .risk-low { background: #43A047; }

    .action-item {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #1f77b4;
    }

    .stButton>button {
        width: 100%;
        background: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
    }

    .stButton>button:hover {
        background: #155a8a;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'site_info' not in st.session_state:
        st.session_state.site_info = {}


def render_header():
    """Render application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ SafeSite AI - Construction Safety Monitor</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">Powered by Gemini 2.0 Flash Vision</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Preventing 48,000+ annual construction deaths in India</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with site information and BIS standards"""
    with st.sidebar:
        st.header("📋 About SafeSite AI")

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
                st.markdown(f"""
                <div class="violation-card critical-violation">
                    <h4>#{i} {violation.get('violation', 'Unknown')}</h4>
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
                st.markdown(f"""
                <div class="violation-card warning-violation">
                    <h4>#{i} {warning.get('violation', 'Unknown')}</h4>
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
            SafeSite AI Analysis Summary
            ----------------------------
            Compliance Score: {result.get('overall_compliance_score', 0)}%
            Risk Level: {risk_data['risk_level']}
            Critical Violations: {len(result.get('critical_violations', []))}
            Warnings: {len(result.get('warnings', []))}
            Total Workers: {result.get('total_workers', 0)}
            """
            st.code(summary)

    with col3:
        st.info("📄 PDF Report - Coming Soon")


def main():
    """Main application"""
    initialize_session_state()
    render_header()
    render_sidebar()

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
        <p>🏗️ SafeSite AI - Built with ❤️ for BNB Marathon 2025</p>
        <p>Powered by Gemini 2.0 Flash Vision | Google Cloud Platform</p>
        <p style="font-size: 0.8rem; margin-top: 1rem;">
            Making construction sites safer, one analysis at a time
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
