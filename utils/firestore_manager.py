"""
Firestore Manager for Real-time Data Storage and Retrieval
Stores construction safety analyses with real-time sync capabilities
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from google.cloud import firestore
from google.cloud.firestore_v1 import FieldFilter
from google.api_core import exceptions


class FirestoreManager:
    """Manage construction safety data in Firestore"""

    def __init__(self, project_id: str = None, collection: str = None):
        """
        Initialize Firestore manager

        Args:
            project_id: GCP project ID
            collection: Firestore collection name
        """
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.collection_name = collection or os.getenv('FIRESTORE_COLLECTION', 'site_analyses')

        if not self.project_id:
            print("⚠️ Warning: GCP_PROJECT_ID not set. Firestore disabled.")
            self.db = None
            return

        try:
            self.db = firestore.Client(project=self.project_id)
            self.collection = self.db.collection(self.collection_name)
            print(f"✅ Firestore initialized: {self.collection_name}")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Firestore: {e}")
            self.db = None

    def save_analysis(
        self,
        analysis_data: Dict,
        site_info: Dict,
        risk_data: Dict,
        financial_data: Dict,
        image_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Save analysis to Firestore

        Args:
            analysis_data: Analysis results from Gemini
            site_info: Site information
            risk_data: Risk assessment data
            financial_data: Financial impact data
            image_url: Optional URL to uploaded image

        Returns:
            Document ID if successful, None otherwise
        """
        if not self.db:
            print("⚠️ Firestore not initialized. Skipping save.")
            return None

        try:
            # Generate unique ID
            doc_id = str(uuid.uuid4())

            # Prepare document
            document = {
                'analysis_id': doc_id,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'created_at': datetime.utcnow().isoformat(),

                # Site information
                'site_id': site_info.get('site_id', ''),
                'location': site_info.get('location', ''),
                'contractor': site_info.get('contractor', ''),
                'project_type': site_info.get('project_type', ''),

                # Analysis results
                'total_workers': analysis_data.get('total_workers', 0),
                'workers_compliant': analysis_data.get('workers_compliant', 0),
                'workers_non_compliant': analysis_data.get('workers_non_compliant', 0),
                'compliance_score': analysis_data.get('overall_compliance_score', 0),

                # Risk assessment
                'risk_level': risk_data.get('risk_level', 'UNKNOWN'),
                'risk_score': risk_data.get('risk_score', 0),
                'recommendation': risk_data.get('recommendation', ''),
                'action_urgency': risk_data.get('action_urgency', ''),

                # Violations
                'critical_violations': analysis_data.get('critical_violations', []),
                'warnings': analysis_data.get('warnings', []),
                'compliant_items': analysis_data.get('compliant_items', []),

                # Financial data
                'potential_fine': financial_data.get('potential_fine', 0),
                'compliance_cost': financial_data.get('compliance_cost', 0),
                'potential_savings': financial_data.get('potential_savings', 0),
                'roi_percentage': financial_data.get('roi_percentage', 0),

                # Image
                'image_url': image_url or '',

                # Metadata
                'status': 'active',
                'version': '1.0'
            }

            # Save to Firestore
            self.collection.document(doc_id).set(document)
            print(f"✅ Analysis saved to Firestore: {doc_id}")

            return doc_id

        except Exception as e:
            print(f"❌ Error saving to Firestore: {e}")
            return None

    def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """
        Get analysis by ID

        Args:
            analysis_id: Analysis document ID

        Returns:
            Analysis document or None
        """
        if not self.db:
            return None

        try:
            doc = self.collection.document(analysis_id).get()

            if doc.exists:
                return doc.to_dict()
            else:
                print(f"⚠️ Analysis not found: {analysis_id}")
                return None

        except Exception as e:
            print(f"❌ Error getting analysis: {e}")
            return None

    def get_site_analyses(
        self,
        site_id: str,
        limit: int = 10,
        order_by: str = 'created_at'
    ) -> List[Dict]:
        """
        Get all analyses for a specific site

        Args:
            site_id: Site identifier
            limit: Maximum number of results
            order_by: Field to order by

        Returns:
            List of analysis documents
        """
        if not self.db:
            return []

        try:
            query = (
                self.collection
                .where(filter=FieldFilter('site_id', '==', site_id))
                .order_by(order_by, direction=firestore.Query.DESCENDING)
                .limit(limit)
            )

            docs = query.stream()
            analyses = []

            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                analyses.append(data)

            return analyses

        except Exception as e:
            print(f"❌ Error getting site analyses: {e}")
            return []

    def get_recent_analyses(
        self,
        limit: int = 20,
        risk_level: Optional[str] = None
    ) -> List[Dict]:
        """
        Get recent analyses across all sites

        Args:
            limit: Maximum number of results
            risk_level: Optional filter by risk level

        Returns:
            List of recent analyses
        """
        if not self.db:
            return []

        try:
            query = self.collection.order_by(
                'created_at',
                direction=firestore.Query.DESCENDING
            )

            if risk_level:
                query = query.where(filter=FieldFilter('risk_level', '==', risk_level))

            query = query.limit(limit)
            docs = query.stream()

            analyses = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                analyses.append(data)

            return analyses

        except Exception as e:
            print(f"❌ Error getting recent analyses: {e}")
            return []

    def get_critical_sites(self, limit: int = 10) -> List[Dict]:
        """
        Get sites with critical or high risk levels

        Args:
            limit: Maximum number of results

        Returns:
            List of critical site analyses
        """
        if not self.db:
            return []

        try:
            # Query for CRITICAL risk
            critical_query = (
                self.collection
                .where(filter=FieldFilter('risk_level', '==', 'CRITICAL'))
                .order_by('created_at', direction=firestore.Query.DESCENDING)
                .limit(limit)
            )

            critical_docs = list(critical_query.stream())

            # If not enough critical, get HIGH risk too
            if len(critical_docs) < limit:
                high_query = (
                    self.collection
                    .where(filter=FieldFilter('risk_level', '==', 'HIGH'))
                    .order_by('created_at', direction=firestore.Query.DESCENDING)
                    .limit(limit - len(critical_docs))
                )
                high_docs = list(high_query.stream())
                critical_docs.extend(high_docs)

            analyses = []
            for doc in critical_docs:
                data = doc.to_dict()
                data['id'] = doc.id
                analyses.append(data)

            return analyses

        except Exception as e:
            print(f"❌ Error getting critical sites: {e}")
            return []

    def update_analysis_status(
        self,
        analysis_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update analysis status (e.g., 'resolved', 'in_progress')

        Args:
            analysis_id: Analysis document ID
            status: New status
            notes: Optional notes

        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            return False

        try:
            update_data = {
                'status': status,
                'last_updated': firestore.SERVER_TIMESTAMP
            }

            if notes:
                update_data['notes'] = notes

            self.collection.document(analysis_id).update(update_data)
            print(f"✅ Analysis status updated: {analysis_id} -> {status}")

            return True

        except Exception as e:
            print(f"❌ Error updating analysis: {e}")
            return False

    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete analysis document

        Args:
            analysis_id: Analysis document ID

        Returns:
            True if successful, False otherwise
        """
        if not self.db:
            return False

        try:
            self.collection.document(analysis_id).delete()
            print(f"✅ Analysis deleted: {analysis_id}")
            return True

        except Exception as e:
            print(f"❌ Error deleting analysis: {e}")
            return False

    def get_statistics(self) -> Optional[Dict]:
        """
        Get overall statistics from Firestore

        Returns:
            Dictionary with statistics
        """
        if not self.db:
            return None

        try:
            # Get all documents (be careful with large datasets)
            docs = self.collection.stream()

            total_analyses = 0
            total_workers = 0
            total_compliant = 0
            risk_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            total_violations = 0
            total_warnings = 0
            compliance_scores = []

            for doc in docs:
                data = doc.to_dict()
                total_analyses += 1
                total_workers += data.get('total_workers', 0)
                total_compliant += data.get('workers_compliant', 0)

                risk_level = data.get('risk_level', 'UNKNOWN')
                if risk_level in risk_counts:
                    risk_counts[risk_level] += 1

                total_violations += len(data.get('critical_violations', []))
                total_warnings += len(data.get('warnings', []))

                score = data.get('compliance_score', 0)
                if score > 0:
                    compliance_scores.append(score)

            avg_compliance = (
                sum(compliance_scores) / len(compliance_scores)
                if compliance_scores else 0
            )

            return {
                'total_analyses': total_analyses,
                'total_workers': total_workers,
                'total_compliant': total_compliant,
                'avg_compliance_score': round(avg_compliance, 1),
                'risk_distribution': risk_counts,
                'total_violations': total_violations,
                'total_warnings': total_warnings
            }

        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return None

    def listen_to_changes(self, callback):
        """
        Listen to real-time changes in the collection

        Args:
            callback: Function to call when data changes
        """
        if not self.db:
            print("⚠️ Firestore not initialized")
            return None

        def on_snapshot(col_snapshot, changes, read_time):
            for change in changes:
                if change.type.name == 'ADDED':
                    callback('added', change.document.to_dict())
                elif change.type.name == 'MODIFIED':
                    callback('modified', change.document.to_dict())
                elif change.type.name == 'REMOVED':
                    callback('removed', change.document.to_dict())

        # Watch the collection
        return self.collection.on_snapshot(on_snapshot)


# Test the module
if __name__ == "__main__":
    print("Testing Firestore Manager...\n")

    # Initialize manager
    manager = FirestoreManager()

    if manager.db:
        # Test data
        test_analysis = {
            'total_workers': 10,
            'workers_compliant': 7,
            'workers_non_compliant': 3,
            'overall_compliance_score': 70,
            'critical_violations': [],
            'warnings': [{'violation': 'Test warning', 'bis_code': 'TEST_001'}],
            'compliant_items': ['Test compliant item']
        }

        test_site = {
            'site_id': 'TEST-SITE-001',
            'location': 'Test Location',
            'contractor': 'Test Contractor',
            'project_type': 'Commercial'
        }

        test_risk = {
            'risk_level': 'MEDIUM',
            'risk_score': 45,
            'recommendation': 'Monitor and improve',
            'action_urgency': 'MEDIUM_PRIORITY'
        }

        test_financial = {
            'potential_fine': 100000,
            'compliance_cost': 30000,
            'potential_savings': 70000,
            'roi_percentage': 233
        }

        # Save analysis
        doc_id = manager.save_analysis(
            test_analysis,
            test_site,
            test_risk,
            test_financial
        )

        if doc_id:
            print(f"\n✅ Test analysis saved: {doc_id}")

            # Get analysis back
            retrieved = manager.get_analysis(doc_id)
            if retrieved:
                print(f"✅ Successfully retrieved analysis")

            # Get statistics
            stats = manager.get_statistics()
            if stats:
                print(f"\n📊 Statistics: {stats}")
    else:
        print("⚠️ Firestore not available. Set GCP_PROJECT_ID to test.")
