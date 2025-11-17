"""
BigQuery Logger Module
Logs safety analyses to Google BigQuery for analytics
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from google.cloud import bigquery
from google.api_core import exceptions


class BigQueryLogger:
    """Logger for construction safety analyses to BigQuery"""

    def __init__(self, project_id: str = None, dataset: str = None, table: str = None):
        """
        Initialize BigQuery logger

        Args:
            project_id: GCP project ID
            dataset: BigQuery dataset name
            table: BigQuery table name
        """
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.dataset = dataset or os.getenv('BIGQUERY_DATASET', 'construction_safety')
        self.table = table or os.getenv('BIGQUERY_TABLE', 'violations')

        if not self.project_id:
            print("⚠️ Warning: GCP_PROJECT_ID not set. BigQuery logging disabled.")
            self.client = None
            return

        try:
            self.client = bigquery.Client(project=self.project_id)
            self.table_ref = f"{self.project_id}.{self.dataset}.{self.table}"
            print(f"✅ BigQuery logger initialized: {self.table_ref}")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize BigQuery client: {e}")
            self.client = None

    def log_analysis(self, analysis_data: Dict, site_info: Dict) -> Optional[str]:
        """
        Log safety analysis to BigQuery

        Args:
            analysis_data: Analysis result from Gemini
            site_info: Site information dictionary

        Returns:
            Analysis ID if successful, None otherwise
        """
        if not self.client:
            print("⚠️ BigQuery client not initialized. Skipping logging.")
            return None

        try:
            # Generate unique analysis ID
            analysis_id = str(uuid.uuid4())

            # Prepare row data
            row = {
                'analysis_id': analysis_id,
                'timestamp': datetime.utcnow().isoformat(),
                'site_id': site_info.get('site_id', 'UNKNOWN'),
                'location': site_info.get('location', 'UNKNOWN'),
                'contractor': site_info.get('contractor', 'UNKNOWN'),
                'project_type': site_info.get('project_type', 'UNKNOWN'),
                'total_workers': analysis_data.get('total_workers', 0),
                'workers_compliant': analysis_data.get('workers_compliant', 0),
                'workers_non_compliant': analysis_data.get('workers_non_compliant', 0),
                'compliance_score': analysis_data.get('overall_compliance_score', 0),
                'risk_level': analysis_data.get('risk_assessment', 'UNKNOWN'),
                'critical_violations': analysis_data.get('critical_violations', []),
                'warnings': analysis_data.get('warnings', []),
                'compliant_items': analysis_data.get('compliant_items', []),
                'estimated_fine': analysis_data.get('potential_fine_if_inspected', '₹0'),
                'compliance_cost': analysis_data.get('estimated_compliance_cost', '₹0'),
            }

            # Insert row
            errors = self.client.insert_rows_json(self.table_ref, [row])

            if errors:
                print(f"❌ Errors inserting to BigQuery: {errors}")
                return None

            print(f"✅ Logged analysis to BigQuery: {analysis_id}")
            return analysis_id

        except exceptions.NotFound:
            print(f"⚠️ Table not found: {self.table_ref}. Please create the dataset and table first.")
            return None
        except Exception as e:
            print(f"❌ Error logging to BigQuery: {e}")
            return None

    def get_analytics(self, days: int = 30) -> Optional[Dict]:
        """
        Get analytics for the last N days

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with analytics data
        """
        if not self.client:
            return None

        try:
            query = f"""
            SELECT
                COUNT(*) as total_analyses,
                AVG(compliance_score) as avg_compliance_score,
                COUNT(DISTINCT site_id) as unique_sites,
                COUNT(DISTINCT contractor) as unique_contractors,
                SUM(ARRAY_LENGTH(critical_violations)) as total_critical_violations,
                SUM(ARRAY_LENGTH(warnings)) as total_warnings,
                COUNTIF(risk_level = 'CRITICAL') as critical_risk_count,
                COUNTIF(risk_level = 'HIGH') as high_risk_count,
                COUNTIF(risk_level = 'MEDIUM') as medium_risk_count,
                COUNTIF(risk_level = 'LOW') as low_risk_count
            FROM `{self.table_ref}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            """

            query_job = self.client.query(query)
            results = list(query_job.result())

            if results:
                row = results[0]
                return {
                    'total_analyses': row.total_analyses,
                    'avg_compliance_score': round(row.avg_compliance_score, 1) if row.avg_compliance_score else 0,
                    'unique_sites': row.unique_sites,
                    'unique_contractors': row.unique_contractors,
                    'total_critical_violations': row.total_critical_violations or 0,
                    'total_warnings': row.total_warnings or 0,
                    'risk_distribution': {
                        'CRITICAL': row.critical_risk_count or 0,
                        'HIGH': row.high_risk_count or 0,
                        'MEDIUM': row.medium_risk_count or 0,
                        'LOW': row.low_risk_count or 0
                    }
                }

            return None

        except Exception as e:
            print(f"❌ Error getting analytics: {e}")
            return None

    def get_site_history(self, site_id: str, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get analysis history for a specific site

        Args:
            site_id: Site identifier
            limit: Maximum number of results

        Returns:
            List of analysis records
        """
        if not self.client:
            return None

        try:
            query = f"""
            SELECT
                analysis_id,
                timestamp,
                compliance_score,
                risk_level,
                total_workers,
                ARRAY_LENGTH(critical_violations) as critical_count,
                ARRAY_LENGTH(warnings) as warning_count
            FROM `{self.table_ref}`
            WHERE site_id = @site_id
            ORDER BY timestamp DESC
            LIMIT {limit}
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("site_id", "STRING", site_id)
                ]
            )

            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())

            history = []
            for row in results:
                history.append({
                    'analysis_id': row.analysis_id,
                    'timestamp': row.timestamp.isoformat() if row.timestamp else None,
                    'compliance_score': row.compliance_score,
                    'risk_level': row.risk_level,
                    'total_workers': row.total_workers,
                    'critical_violations': row.critical_count,
                    'warnings': row.warning_count
                })

            return history

        except Exception as e:
            print(f"❌ Error getting site history: {e}")
            return None

    def get_most_common_violations(self, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get most common violations across all analyses

        Args:
            limit: Number of violations to return

        Returns:
            List of violations with counts
        """
        if not self.client:
            return None

        try:
            query = f"""
            WITH violations_unnested AS (
                SELECT violation.violation as violation_text,
                       violation.bis_code as bis_code
                FROM `{self.table_ref}`,
                UNNEST(critical_violations) as violation
                UNION ALL
                SELECT warning.violation as violation_text,
                       warning.bis_code as bis_code
                FROM `{self.table_ref}`,
                UNNEST(warnings) as warning
            )
            SELECT
                violation_text,
                bis_code,
                COUNT(*) as occurrence_count
            FROM violations_unnested
            GROUP BY violation_text, bis_code
            ORDER BY occurrence_count DESC
            LIMIT {limit}
            """

            query_job = self.client.query(query)
            results = list(query_job.result())

            violations = []
            for row in results:
                violations.append({
                    'violation': row.violation_text,
                    'bis_code': row.bis_code,
                    'count': row.occurrence_count
                })

            return violations

        except Exception as e:
            print(f"❌ Error getting common violations: {e}")
            return None

    def create_dataset_and_table(self):
        """Create BigQuery dataset and table if they don't exist"""
        if not self.client:
            print("⚠️ BigQuery client not initialized")
            return False

        try:
            # Create dataset
            dataset_id = f"{self.project_id}.{self.dataset}"
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US"

            try:
                dataset = self.client.create_dataset(dataset, exists_ok=True)
                print(f"✅ Dataset created or already exists: {dataset_id}")
            except Exception as e:
                print(f"⚠️ Dataset creation: {e}")

            # Create table schema
            schema = [
                bigquery.SchemaField("analysis_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("site_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("contractor", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("project_type", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("total_workers", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("workers_compliant", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("workers_non_compliant", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("compliance_score", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("risk_level", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("critical_violations", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("warnings", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("compliant_items", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("estimated_fine", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("compliance_cost", "STRING", mode="NULLABLE"),
            ]

            table = bigquery.Table(self.table_ref, schema=schema)

            try:
                table = self.client.create_table(table, exists_ok=True)
                print(f"✅ Table created or already exists: {self.table_ref}")
                return True
            except Exception as e:
                print(f"❌ Table creation error: {e}")
                return False

        except Exception as e:
            print(f"❌ Error setting up BigQuery: {e}")
            return False


# Test the module when run directly
if __name__ == "__main__":
    print("Testing BigQuery Logger...\n")

    # Initialize logger
    logger = BigQueryLogger()

    if logger.client:
        print("Testing dataset/table creation...")
        success = logger.create_dataset_and_table()

        if success:
            # Test logging
            test_analysis = {
                'total_workers': 5,
                'workers_compliant': 3,
                'workers_non_compliant': 2,
                'overall_compliance_score': 75,
                'risk_assessment': 'MEDIUM',
                'critical_violations': [],
                'warnings': [{
                    'violation': 'Test warning',
                    'bis_code': 'TEST_001'
                }],
                'compliant_items': ['Test compliant item'],
                'potential_fine_if_inspected': '₹50,000',
                'estimated_compliance_cost': '₹10,000'
            }

            test_site = {
                'site_id': 'TEST-001',
                'location': 'Test Location',
                'contractor': 'Test Contractor',
                'project_type': 'Test'
            }

            analysis_id = logger.log_analysis(test_analysis, test_site)
            if analysis_id:
                print(f"\n✅ Test analysis logged: {analysis_id}")

            # Test analytics
            print("\nTesting analytics...")
            analytics = logger.get_analytics(days=30)
            if analytics:
                print(f"Analytics: {analytics}")
    else:
        print("⚠️ BigQuery client not available. Set GCP_PROJECT_ID to test.")
