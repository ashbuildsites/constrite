"""
Site Analytics Page
A page for site owners to view historical data and analytics for their sites.
"""

import streamlit as st
import pandas as pd
from utils.bigquery_logger import BigQueryLogger

def show_analytics():
    """
    Displays the analytics for a given site ID.
    """
    st.header("Site Analytics")

    site_id = st.text_input("Enter your Site ID to view analytics:", key="analytics_site_id")

    if site_id:
        st.session_state.site_id_for_analytics = site_id

    if 'site_id_for_analytics' in st.session_state and st.session_state.site_id_for_analytics:
        site_id = st.session_state.site_id_for_analytics
        st.subheader(f"Analytics for Site: {site_id}")

        # Initialize BigQueryLogger
        if 'bigquery_logger' not in st.session_state:
            st.session_state.bigquery_logger = BigQueryLogger()

        bq_logger = st.session_state.bigquery_logger

        if not bq_logger.client:
            st.warning("BigQuery is not configured. Please set the GCP_PROJECT_ID environment variable.")
            return

        with st.spinner(f"Fetching data for site {site_id}..."):
            # Get site history
            history = bq_logger.get_site_history(site_id)

            if history:
                st.subheader("Analysis History")
                df = pd.DataFrame(history)
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                st.dataframe(df)
            else:
                st.info("No analysis history found for this site.")

            # Get most common violations for this site
            # Note: get_most_common_violations in the original file is global.
            # We need a site-specific version. For now, we'll just show global common violations.
            st.subheader("Most Common Violations (All Sites)")
            common_violations = bq_logger.get_most_common_violations()

            if common_violations:
                st.table(common_violations)
            else:
                st.info("No common violations found.")


def main():
    """
    Main function for the Site Analytics page.
    """
    st.set_page_config(
        page_title="Site Analytics - ConStrite",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Site Analytics")
    st.write("View historical safety data for your construction sites.")

    # Simple password protection
    password = st.text_input("Enter password to access analytics", type="password")

    # Hardcoded password for demonstration purposes
    if password == "safesite":
        show_analytics()
    elif password:
        st.error("Incorrect password.")

if __name__ == "__main__":
    main()
