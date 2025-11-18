"""
Update BigQuery table schema to include all required fields
"""
from google.cloud import bigquery
import os

def update_schema():
    """Update the BigQuery table schema"""

    project_id = os.getenv('GCP_PROJECT_ID')
    dataset = os.getenv('BIGQUERY_DATASET', 'construction_safety')
    table = os.getenv('BIGQUERY_TABLE', 'violations')

    if not project_id:
        print("❌ GCP_PROJECT_ID not set")
        return False

    try:
        client = bigquery.Client(project=project_id)
        table_ref = f"{project_id}.{dataset}.{table}"

        print(f"Updating schema for: {table_ref}")

        # Get existing table
        table_obj = client.get_table(table_ref)

        # Define complete schema with all fields
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

        # Update table schema
        table_obj.schema = schema
        table_obj = client.update_table(table_obj, ["schema"])

        print("✅ Schema updated successfully!")
        print("\nNew schema fields:")
        for field in table_obj.schema:
            print(f"  - {field.name} ({field.field_type})")

        return True

    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BigQuery Schema Update Tool")
    print("=" * 60)
    print()

    success = update_schema()

    if success:
        print("\n✅ Schema update complete!")
        print("\nYou can now run the app without BigQuery schema errors.")
    else:
        print("\n❌ Schema update failed.")
        print("\nAlternative: Delete and recreate the table:")
        print("  1. Visit: https://console.cloud.google.com/bigquery")
        print("  2. Delete the violations table")
        print("  3. Run: python setup_gcp.py")
