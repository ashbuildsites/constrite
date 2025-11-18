"""
BIS Standards Database Module
Manages Indian Bureau of Standards construction safety codes
"""

import json
import os
from dataclasses import dataclass
from typing import List, Optional, Dict
from pathlib import Path


@dataclass
class BISStandard:
    """Represents a single BIS safety standard"""
    code: str
    title: str
    requirement: str
    penalty: str
    severity: str
    category: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'code': self.code,
            'title': self.title,
            'requirement': self.requirement,
            'penalty': self.penalty,
            'severity': self.severity,
            'category': self.category
        }


class BISDatabase:
    """Singleton class for managing BIS standards database"""

    _instance = None
    _standards: List[BISStandard] = []
    _standards_dict: Dict[str, BISStandard] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BISDatabase, cls).__new__(cls)
            cls._instance._load_standards()
        return cls._instance

    def _load_standards(self):
        """Load BIS standards from JSON file"""
        try:
            # Get the path to the config file
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / 'config' / 'bis_codes.json'

            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._standards = []
            self._standards_dict = {}

            for item in data:
                standard = BISStandard(
                    code=item['code'],
                    title=item['title'],
                    requirement=item['requirement'],
                    penalty=item['penalty'],
                    severity=item['severity'],
                    category=item['category']
                )
                self._standards.append(standard)
                self._standards_dict[item['code']] = standard

            print(f"✅ Loaded {len(self._standards)} BIS standards")

        except FileNotFoundError:
            print("⚠️ Warning: BIS codes file not found. Using empty database.")
            self._standards = []
            self._standards_dict = {}
        except json.JSONDecodeError as e:
            print(f"⚠️ Warning: Error parsing BIS codes JSON: {e}")
            self._standards = []
            self._standards_dict = {}

    def get_standard(self, code: str) -> Optional[BISStandard]:
        """
        Retrieve a standard by its code

        Args:
            code: BIS standard code (e.g., 'IS_2925_1984')

        Returns:
            BISStandard object or None if not found
        """
        return self._standards_dict.get(code)

    def get_penalty(self, code: str) -> Optional[str]:
        """
        Get penalty amount for a specific standard

        Args:
            code: BIS standard code

        Returns:
            Penalty string or None if not found
        """
        standard = self.get_standard(code)
        return standard.penalty if standard else None

    def search_standards(self, category: Optional[str] = None,
                        severity: Optional[str] = None) -> List[BISStandard]:
        """
        Search standards by category and/or severity

        Args:
            category: Filter by category (PPE, STRUCTURAL, ELECTRICAL, FIRE, etc.)
            severity: Filter by severity (CRITICAL, HIGH, MEDIUM)

        Returns:
            List of matching BISStandard objects
        """
        results = self._standards

        if category:
            results = [s for s in results if s.category == category.upper()]

        if severity:
            results = [s for s in results if s.severity == severity.upper()]

        return results

    def get_all_standards(self) -> List[BISStandard]:
        """Get all standards"""
        return self._standards.copy()

    def get_categories(self) -> List[str]:
        """Get list of all unique categories"""
        return list(set(s.category for s in self._standards))

    def get_critical_standards(self) -> List[BISStandard]:
        """Get all critical severity standards"""
        return self.search_standards(severity='CRITICAL')

    def format_for_prompt(self) -> str:
        """
        Format all standards as text for AI prompt

        Returns:
            Formatted string with all BIS standards
        """
        output = "INDIAN BIS CONSTRUCTION SAFETY STANDARDS:\n\n"

        for standard in self._standards:
            output += f"📋 {standard.code}\n"
            output += f"Title: {standard.title}\n"
            output += f"Requirement: {standard.requirement}\n"
            output += f"Penalty: {standard.penalty}\n"
            output += f"Severity: {standard.severity}\n"
            output += f"Category: {standard.category}\n"
            output += "-" * 80 + "\n\n"

        return output

    def get_standards_summary(self) -> Dict:
        """Get statistical summary of standards"""
        categories = {}
        severities = {}

        for standard in self._standards:
            categories[standard.category] = categories.get(standard.category, 0) + 1
            severities[standard.severity] = severities.get(standard.severity, 0) + 1

        return {
            'total': len(self._standards),
            'by_category': categories,
            'by_severity': severities
        }


# Convenience functions for easy access
def get_bis_database() -> BISDatabase:
    """Get the singleton BIS database instance"""
    return BISDatabase()


def get_standard(code: str) -> Optional[BISStandard]:
    """Get a specific standard by code"""
    db = BISDatabase()
    return db.get_standard(code)


def get_all_standards() -> List[BISStandard]:
    """Get all BIS standards"""
    db = BISDatabase()
    return db.get_all_standards()


# Test the module when run directly
if __name__ == "__main__":
    print("Testing BIS Standards Database...\n")

    db = BISDatabase()

    print(f"Total standards loaded: {len(db.get_all_standards())}")
    print(f"\nCategories: {db.get_categories()}")

    print(f"\nStatistics: {db.get_standards_summary()}")

    # Test retrieving a specific standard
    helmet = db.get_standard("IS_2925_1984")
    if helmet:
        print(f"\n📋 Test Standard:")
        print(f"Code: {helmet.code}")
        print(f"Title: {helmet.title}")
        print(f"Penalty: {helmet.penalty}")
        print(f"Severity: {helmet.severity}")

    # Test searching by category
    ppe_standards = db.search_standards(category="PPE")
    print(f"\n👷 PPE Standards: {len(ppe_standards)}")

    # Test critical standards
    critical = db.get_critical_standards()
    print(f"\n⚠️ Critical Standards: {len(critical)}")
