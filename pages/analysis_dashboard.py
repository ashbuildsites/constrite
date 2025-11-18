"""
Analysis Dashboard
Historical safety analysis and insights across all sites
"""

import streamlit as st
import os
from datetime import datetime, timedelta
import time
import pandas as pd
from typing import Dict, List

# Import custom modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.firestore_manager import FirestoreManager
from utils.bigquery_logger import BigQueryLogger


# Page configuration
st.set_page_config(
    page_title="Analysis Dashboard - ConStrite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #1f77b4;
        height: 100%;
    }

    .critical-card {
        border-left-color: #f44336;
        background: #ffebee;
    }

    .warning-card {
        border-left-color: #ff9800;
        background: #fff3e0;
    }

    .success-card {
        border-left-color: #4caf50;
        background: #e8f5e9;
    }

    .site-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .pulse {
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .refresh-indicator {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: #4caf50;
        color: white;
        border-radius: 20px;
        font-size: 0.9rem;
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)


def initialize_connections():
    """Initialize Firebase and BigQuery connections"""
    if 'firestore_manager' not in st.session_state:
        st.session_state.firestore_manager = FirestoreManager()

    if 'bigquery_logger' not in st.session_state:
        st.session_state.bigquery_logger = BigQueryLogger()


def render_header():
    """Render dashboard header"""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title("📊 Safety Analysis Dashboard")
        st.caption("Historical safety insights and analytics across all sites")

    with col2:
        st.markdown(
            '<div class="refresh-indicator">📈 ANALYTICS</div>',
            unsafe_allow_html=True
        )


def render_overview_metrics(firestore_manager: FirestoreManager):
    """Render overview metrics"""
    st.subheader("📈 Overview Metrics")

    # Get statistics
    stats = firestore_manager.get_statistics()

    if not stats:
        st.info("No data available yet. Perform some analyses to see statistics.")
        return

    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #1f77b4; margin: 0;">{stats['total_analyses']}</h3>
            <p style="color: #666; margin: 0.5rem 0 0 0;">Total Analyses</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #2196f3; margin: 0;">{stats['total_workers']}</h3>
            <p style="color: #666; margin: 0.5rem 0 0 0;">Total Workers</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        score = stats['avg_compliance_score']
        score_color = '#4caf50' if score >= 80 else '#ff9800' if score >= 50 else '#f44336'
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {score_color}; margin: 0;">{score}%</h3>
            <p style="color: #666; margin: 0.5rem 0 0 0;">Avg Compliance</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card critical-card">
            <h3 style="color: #f44336; margin: 0;">{stats['total_violations']}</h3>
            <p style="color: #666; margin: 0.5rem 0 0 0;">Total Violations</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card warning-card">
            <h3 style="color: #ff9800; margin: 0;">{stats['total_warnings']}</h3>
            <p style="color: #666; margin: 0.5rem 0 0 0;">Total Warnings</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Risk distribution
    st.subheader("🎯 Risk Distribution")
    risk_dist = stats['risk_distribution']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Critical Risk", risk_dist.get('CRITICAL', 0), delta=None, delta_color="inverse")

    with col2:
        st.metric("High Risk", risk_dist.get('HIGH', 0), delta=None, delta_color="inverse")

    with col3:
        st.metric("Medium Risk", risk_dist.get('MEDIUM', 0), delta=None)

    with col4:
        st.metric("Low Risk", risk_dist.get('LOW', 0), delta=None, delta_color="normal")


def render_critical_alerts(firestore_manager: FirestoreManager):
    """Render critical alerts section"""
    st.subheader("🚨 Critical Alerts")

    critical_sites = firestore_manager.get_critical_sites(limit=5)

    if not critical_sites:
        st.success("✅ No critical alerts! All sites are operating safely.")
        return

    for site in critical_sites:
        risk_level = site.get('risk_level', 'UNKNOWN')
        risk_colors = {
            'CRITICAL': '#B71C1C',
            'HIGH': '#E53935',
            'MEDIUM': '#FB8C00',
            'LOW': '#43A047'
        }
        border_color = risk_colors.get(risk_level, '#757575')

        timestamp = site.get('created_at', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_ago = get_time_ago(dt)
            except:
                time_ago = 'Unknown time'
        else:
            time_ago = 'Unknown time'

        st.markdown(f"""
        <div class="site-card" style="border-left-color: {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h4 style="margin: 0; color: {border_color};">{site.get('site_id', 'Unknown Site')}</h4>
                    <p style="margin: 0.3rem 0; color: #666;">
                        📍 {site.get('location', 'Unknown')} |
                        🏢 {site.get('contractor', 'Unknown')}
                    </p>
                    <p style="margin: 0.3rem 0;">
                        <strong>Risk Level:</strong> <span style="color: {border_color};">{risk_level}</span> |
                        <strong>Score:</strong> {site.get('risk_score', 0)}/100
                    </p>
                    <p style="margin: 0.3rem 0;">
                        <strong>Compliance:</strong> {site.get('compliance_score', 0)}% |
                        <strong>Workers:</strong> {site.get('total_workers', 0)}
                        ({site.get('workers_compliant', 0)} compliant, {site.get('workers_non_compliant', 0)} non-compliant)
                    </p>
                    <p style="margin: 0.3rem 0; color: #999; font-size: 0.9rem;">
                        🕐 {time_ago}
                    </p>
                </div>
                <div style="text-align: right;">
                    <div style="background: {border_color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                        {len(site.get('critical_violations', []))} Critical<br/>
                        {len(site.get('warnings', []))} Warnings
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_recent_analyses(firestore_manager: FirestoreManager):
    """Render recent analyses table"""
    st.subheader("📋 Recent Analyses")

    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        risk_filter = st.selectbox(
            "Filter by Risk Level",
            ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
        )

    with col2:
        limit = st.slider("Number of results", 5, 50, 20)

    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()

    # Get analyses
    risk_level = None if risk_filter == "All" else risk_filter
    analyses = firestore_manager.get_recent_analyses(limit=limit, risk_level=risk_level)

    if not analyses:
        st.info("No analyses found.")
        return

    # Convert to DataFrame
    data = []
    for analysis in analyses:
        data.append({
            'Time': get_time_ago_short(analysis.get('created_at', '')),
            'Site ID': analysis.get('site_id', 'N/A'),
            'Location': analysis.get('location', 'N/A'),
            'Contractor': analysis.get('contractor', 'N/A'),
            'Risk': analysis.get('risk_level', 'N/A'),
            'Score': f"{analysis.get('compliance_score', 0)}%",
            'Workers': f"{analysis.get('total_workers', 0)}",
            'Critical': len(analysis.get('critical_violations', [])),
            'Warnings': len(analysis.get('warnings', []))
        })

    df = pd.DataFrame(data)

    # Style the dataframe
    def color_risk(val):
        colors_map = {
            'CRITICAL': 'background-color: #ffebee; color: #B71C1C; font-weight: bold',
            'HIGH': 'background-color: #fff3e0; color: #E53935; font-weight: bold',
            'MEDIUM': 'background-color: #e3f2fd; color: #FB8C00; font-weight: bold',
            'LOW': 'background-color: #e8f5e9; color: #43A047; font-weight: bold'
        }
        return colors_map.get(val, '')

    styled_df = df.style.applymap(color_risk, subset=['Risk'])
    st.dataframe(styled_df, use_container_width=True, height=400)


def get_time_ago(dt: datetime) -> str:
    """Convert datetime to human-readable 'time ago' format"""
    now = datetime.utcnow()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"


def get_time_ago_short(timestamp: str) -> str:
    """Get short time ago string"""
    if not timestamp:
        return 'N/A'

    try:
        dt = datetime.fromisoformat(timestamp)
        now = datetime.utcnow()
        diff = now - dt
        seconds = diff.total_seconds()

        if seconds < 60:
            return "now"
        elif seconds < 3600:
            return f"{int(seconds/60)}m"
        elif seconds < 86400:
            return f"{int(seconds/3600)}h"
        else:
            return f"{int(seconds/86400)}d"
    except:
        return 'N/A'


def main():
    """Main dashboard"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.warning("Please log in from the main page to view the analysis dashboard.")
        return

    initialize_connections()
    render_header()

    firestore_manager = st.session_state.firestore_manager

    if not firestore_manager.db:
        st.warning("""
        ⚠️ **Firestore Not Connected**

        The analysis dashboard requires Firestore to be configured.
        Please set up your Google Cloud credentials and configure Firestore.

        See the documentation for setup instructions.
        """)
        return

    # Auto-refresh toggle
    col1, col2 = st.columns([4, 1])
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)

    st.divider()

    # Overview metrics
    render_overview_metrics(firestore_manager)

    st.divider()

    # Two columns for alerts and recent analyses
    col1, col2 = st.columns([1, 1])

    with col1:
        render_critical_alerts(firestore_manager)

    with col2:
        # Site selector for history
        st.subheader("🏗️ Site History")

        recent = firestore_manager.get_recent_analyses(limit=100)
        site_ids = list(set([a.get('site_id', '') for a in recent if a.get('site_id')]))

        if site_ids:
            selected_site = st.selectbox("Select Site", ["All Sites"] + site_ids)

            if selected_site != "All Sites":
                site_history = firestore_manager.get_site_analyses(selected_site, limit=10)

                if site_history:
                    for analysis in site_history:
                        risk_level = analysis.get('risk_level', 'UNKNOWN')
                        risk_colors = {
                            'CRITICAL': '#B71C1C',
                            'HIGH': '#E53935',
                            'MEDIUM': '#FB8C00',
                            'LOW': '#43A047'
                        }
                        color = risk_colors.get(risk_level, '#757575')

                        time_ago = get_time_ago_short(analysis.get('created_at', ''))

                        st.markdown(f"""
                        <div style="background: white; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0;
                                    border-left: 3px solid {color};">
                            <strong>{time_ago}</strong> -
                            Score: {analysis.get('compliance_score', 0)}% |
                            <span style="color: {color};">{risk_level}</span>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No sites available yet.")

    st.divider()

    # Recent analyses table
    render_recent_analyses(firestore_manager)

    # Footer with last update time
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    # Auto-refresh
    if auto_refresh:
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main()
