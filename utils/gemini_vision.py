"""
Gemini Vision Integration Module
Uses Google's Gemini 1.5 Flash for construction safety analysis
"""

import json
import os
from typing import Dict, List, Optional
import google.generativeai as genai
from PIL import Image
from utils.bis_standards import BISDatabase


class ConstructionSafetyAnalyzer:
    """AI-powered construction safety analyzer using Gemini Vision"""

    def __init__(self, api_key: str):
        """
        Initialize the analyzer with Gemini API

        Args:
            api_key: Google Gemini API key
        """
        if not api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash for fast, efficient image analysis
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.bis_db = BISDatabase()
        print("✅ Gemini Vision initialized")

    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze construction site image for safety violations

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load image
            image = Image.open(image_path)
            print(f"📸 Analyzing image: {image_path}")

            # Create analysis prompt
            prompt = self._create_analysis_prompt()

            # Generate content with image
            response = self.model.generate_content([prompt, image])

            # Parse response
            result = self._parse_response(response.text)

            print("✅ Analysis complete")
            return result

        except Exception as e:
            print(f"❌ Error analyzing image: {e}")
            return self._get_error_response(str(e))

    def _create_analysis_prompt(self) -> str:
        """Create detailed prompt for Gemini Vision"""

        bis_context = self.bis_db.format_for_prompt()

        prompt = f"""You are an expert construction safety inspector trained in Indian BIS (Bureau of Indian Standards) codes.

Analyze this construction site image for ALL safety violations and compliances.

{bis_context}

DETECTION REQUIREMENTS:
1. Count all visible workers in the image
2. Check Personal Protective Equipment (PPE) compliance:
   - Safety helmets (IS 2925:1984)
   - Safety harness if working at height above 2m (IS 3696:1966)
   - Safety footwear (IS 5216:1982)
   - High-visibility vests (IS 15750:2008)
3. Check structural safety:
   - Scaffolding guardrails and toe boards (IS 4014:1967)
   - Ladder safety (IS 14489:1998)
   - Safety nets if height > 3m (IS 4081:1996)
   - Excavation barriers (IS 1646:1997)
4. Check electrical safety:
   - Exposed wires (IS 694:1990)
   - Proper earthing (IS 3043:1987)
5. Check fire safety:
   - Fire extinguisher visibility (IS 2190:2010)
6. Identify CRITICAL life-threatening violations
7. Note compliant safety measures

OUTPUT FORMAT (respond with valid JSON only):
{{
  "total_workers": <number of visible workers>,
  "workers_compliant": <number wearing all required PPE>,
  "workers_non_compliant": <number missing any PPE>,
  "critical_violations": [
    {{
      "violation": "<specific violation description>",
      "location": "<where in image: left/right/center/background/foreground>",
      "bis_code": "<relevant BIS code like IS_2925_1984>",
      "risk_level": "CRITICAL",
      "recommendation": "<specific action to fix>"
    }}
  ],
  "warnings": [
    {{
      "violation": "<warning description>",
      "location": "<location in image>",
      "bis_code": "<relevant BIS code>",
      "risk_level": "HIGH or MEDIUM",
      "recommendation": "<specific action>"
    }}
  ],
  "compliant_items": [
    "<list of safety measures that are properly implemented>"
  ],
  "overall_compliance_score": <integer 0-100>,
  "risk_assessment": "<CRITICAL/HIGH/MEDIUM/LOW>",
  "immediate_actions": [
    "<prioritized list of actions needed immediately>"
  ],
  "estimated_compliance_cost": "₹<amount in rupees>",
  "potential_fine_if_inspected": "₹<total potential fines>"
}}

IMPORTANT GUIDELINES:
- Be specific about locations (e.g., "worker on left scaffolding", "center area near excavation")
- If something is not visible in the image, mark as "Not visible/Cannot verify" in compliant_items
- Use actual BIS codes from the provided standards
- Provide realistic cost estimates in Indian Rupees
- Compliance score calculation: (compliant items / total checkable items) × 100
- Critical violations: immediate life threat (fall risk, electrical hazard, structural collapse)
- High warnings: serious safety gaps (missing PPE, inadequate barriers)
- Medium warnings: best practice improvements (better signage, better organization)

Respond ONLY with valid JSON. No additional text before or after."""

        return prompt

    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse Gemini response into structured format

        Args:
            response_text: Raw response from Gemini

        Returns:
            Parsed dictionary
        """
        try:
            # Remove markdown code blocks if present
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]

            cleaned_text = cleaned_text.strip()

            # Parse JSON
            result = json.loads(cleaned_text)

            # Validate required fields
            required_fields = [
                'total_workers', 'workers_compliant', 'workers_non_compliant',
                'critical_violations', 'warnings', 'compliant_items',
                'overall_compliance_score', 'risk_assessment', 'immediate_actions'
            ]

            for field in required_fields:
                if field not in result:
                    result[field] = self._get_default_value(field)

            return result

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}")
            return self._get_default_response()

    def _get_default_value(self, field: str):
        """Get default value for missing field"""
        defaults = {
            'total_workers': 0,
            'workers_compliant': 0,
            'workers_non_compliant': 0,
            'critical_violations': [],
            'warnings': [],
            'compliant_items': [],
            'overall_compliance_score': 50,
            'risk_assessment': 'MEDIUM',
            'immediate_actions': ['Unable to analyze - please retry'],
            'estimated_compliance_cost': '₹0',
            'potential_fine_if_inspected': '₹0'
        }
        return defaults.get(field, None)

    def _get_default_response(self) -> Dict:
        """Get default response structure for errors"""
        return {
            'total_workers': 0,
            'workers_compliant': 0,
            'workers_non_compliant': 0,
            'critical_violations': [],
            'warnings': [{
                'violation': 'Unable to analyze image completely',
                'location': 'General',
                'bis_code': 'N/A',
                'risk_level': 'MEDIUM',
                'recommendation': 'Please try again with a clearer image'
            }],
            'compliant_items': [],
            'overall_compliance_score': 50,
            'risk_assessment': 'MEDIUM',
            'immediate_actions': ['Retry analysis with better image quality'],
            'estimated_compliance_cost': '₹0',
            'potential_fine_if_inspected': '₹0'
        }

    def _get_error_response(self, error_message: str) -> Dict:
        """Get error response structure"""
        return {
            'total_workers': 0,
            'workers_compliant': 0,
            'workers_non_compliant': 0,
            'critical_violations': [],
            'warnings': [{
                'violation': f'Analysis error: {error_message}',
                'location': 'System',
                'bis_code': 'ERROR',
                'risk_level': 'HIGH',
                'recommendation': 'Please check API key and try again'
            }],
            'compliant_items': [],
            'overall_compliance_score': 0,
            'risk_assessment': 'UNKNOWN',
            'immediate_actions': ['Fix analysis error and retry'],
            'estimated_compliance_cost': '₹0',
            'potential_fine_if_inspected': '₹0'
        }


# Test the module when run directly
if __name__ == "__main__":
    import sys

    print("Testing Gemini Vision Analyzer...\n")

    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        sys.exit(1)

    # Create analyzer
    analyzer = ConstructionSafetyAnalyzer(api_key)

    # Test with a sample image (if provided)
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        result = analyzer.analyze_image(image_path)

        print("\n📊 Analysis Results:")
        print(f"Total Workers: {result['total_workers']}")
        print(f"Compliance Score: {result['overall_compliance_score']}/100")
        print(f"Risk Level: {result['risk_assessment']}")
        print(f"\nCritical Violations: {len(result['critical_violations'])}")
        print(f"Warnings: {len(result['warnings'])}")
        print(f"Compliant Items: {len(result['compliant_items'])}")
    else:
        print("ℹ️ Usage: python gemini_vision.py <image_path>")
