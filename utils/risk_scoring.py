"""
Risk Scoring Module
Calculates risk scores and provides recommendations
"""

from typing import Dict, List


def calculate_risk_score(analysis_result: Dict) -> Dict:
    """
    Calculate comprehensive risk score based on violations

    Args:
        analysis_result: Dictionary from Gemini vision analysis

    Returns:
        Dictionary with risk score, level, and recommendations
    """

    # Initialize score
    risk_score = 0

    # Get violation data
    critical_violations = analysis_result.get('critical_violations', [])
    warnings = analysis_result.get('warnings', [])
    compliance_score = analysis_result.get('overall_compliance_score', 100)

    # Calculate base risk from violations
    # Critical violations: +20 points each
    risk_score += len(critical_violations) * 20

    # High warnings: +10 points each
    # Medium warnings: +5 points each
    for warning in warnings:
        risk_level = warning.get('risk_level', 'MEDIUM')
        if risk_level == 'HIGH':
            risk_score += 10
        elif risk_level == 'MEDIUM':
            risk_score += 5

    # Apply compliance score multiplier
    # Lower compliance = higher risk multiplier
    compliance_multiplier = (100 - compliance_score) / 100
    risk_score = risk_score * (1 + compliance_multiplier)

    # Worker ratio penalty
    total_workers = analysis_result.get('total_workers', 0)
    non_compliant_workers = analysis_result.get('workers_non_compliant', 0)

    if total_workers > 0:
        non_compliance_ratio = non_compliant_workers / total_workers
        risk_score += non_compliance_ratio * 15

    # Cap at 100
    risk_score = min(int(risk_score), 100)

    # Determine risk level
    if risk_score >= 75:
        risk_level = 'CRITICAL'
        risk_color = '#B71C1C'  # Dark red
        action_urgency = 'IMMEDIATE'
        recommendation = (
            "🚨 CRITICAL RISK: Site operations must be halted immediately. "
            "Multiple life-threatening violations detected. "
            "Emergency safety review required before resuming work."
        )
    elif risk_score >= 50:
        risk_level = 'HIGH'
        risk_color = '#E53935'  # Red
        action_urgency = '24_HOURS'
        recommendation = (
            "⚠️ HIGH RISK: Serious safety violations present. "
            "Immediate corrective action required within 24 hours. "
            "Site supervisor must address all critical issues before next shift."
        )
    elif risk_score >= 25:
        risk_level = 'MEDIUM'
        risk_color = '#FB8C00'  # Orange
        action_urgency = '48_HOURS'
        recommendation = (
            "⚡ MEDIUM RISK: Several safety improvements needed. "
            "Address violations within 48 hours. "
            "Schedule safety training and equipment upgrades."
        )
    else:
        risk_level = 'LOW'
        risk_color = '#43A047'  # Green
        action_urgency = 'WEEKLY'
        recommendation = (
            "✅ LOW RISK: Site shows good safety compliance. "
            "Continue monitoring and maintain current safety standards. "
            "Address minor warnings during routine inspections."
        )

    return {
        'risk_score': risk_score,
        'risk_level': risk_level,
        'risk_color': risk_color,
        'recommendation': recommendation,
        'action_urgency': action_urgency,
        'critical_count': len(critical_violations),
        'warning_count': len(warnings),
        'compliance_percentage': compliance_score
    }


def prioritize_actions(analysis_result: Dict) -> List[Dict]:
    """
    Prioritize corrective actions based on risk

    Args:
        analysis_result: Analysis result from Gemini

    Returns:
        List of prioritized actions with details
    """

    actions = []
    priority = 1

    # Critical violations first
    for violation in analysis_result.get('critical_violations', []):
        actions.append({
            'priority': priority,
            'urgency': 'IMMEDIATE',
            'action': violation.get('recommendation', 'Address violation'),
            'violation': violation.get('violation', 'Unknown'),
            'location': violation.get('location', 'Unknown'),
            'bis_code': violation.get('bis_code', 'N/A'),
            'estimated_time': '30 minutes',
            'estimated_cost': 'Varies'
        })
        priority += 1

    # High priority warnings
    high_warnings = [w for w in analysis_result.get('warnings', [])
                     if w.get('risk_level') == 'HIGH']

    for warning in high_warnings:
        actions.append({
            'priority': priority,
            'urgency': 'HIGH',
            'action': warning.get('recommendation', 'Address warning'),
            'violation': warning.get('violation', 'Unknown'),
            'location': warning.get('location', 'Unknown'),
            'bis_code': warning.get('bis_code', 'N/A'),
            'estimated_time': '1-2 hours',
            'estimated_cost': 'Moderate'
        })
        priority += 1

    # Medium priority warnings
    medium_warnings = [w for w in analysis_result.get('warnings', [])
                       if w.get('risk_level') == 'MEDIUM']

    for warning in medium_warnings:
        actions.append({
            'priority': priority,
            'urgency': 'MEDIUM',
            'action': warning.get('recommendation', 'Address warning'),
            'violation': warning.get('violation', 'Unknown'),
            'location': warning.get('location', 'Unknown'),
            'bis_code': warning.get('bis_code', 'N/A'),
            'estimated_time': '2-4 hours',
            'estimated_cost': 'Low-Moderate'
        })
        priority += 1

    return actions


def calculate_financial_impact(analysis_result: Dict) -> Dict:
    """
    Calculate financial impact of violations vs compliance

    Args:
        analysis_result: Analysis result from Gemini

    Returns:
        Dictionary with financial breakdown
    """

    # Extract cost estimates from analysis
    potential_fine = analysis_result.get('potential_fine_if_inspected', '₹0')
    compliance_cost = analysis_result.get('estimated_compliance_cost', '₹0')

    # Parse rupee amounts (remove ₹ and commas)
    def parse_rupee(amount_str):
        try:
            cleaned = amount_str.replace('₹', '').replace(',', '').strip()
            # Handle "lakh" notation
            if 'lakh' in cleaned.lower():
                cleaned = cleaned.lower().replace('lakh', '').strip()
                return float(cleaned) * 100000
            return float(cleaned)
        except:
            return 0

    fine_amount = parse_rupee(potential_fine)
    cost_amount = parse_rupee(compliance_cost)

    # Calculate savings and ROI
    savings = fine_amount - cost_amount
    if cost_amount > 0:
        roi_percentage = (savings / cost_amount) * 100
    else:
        roi_percentage = 0

    return {
        'potential_fine': fine_amount,
        'compliance_cost': cost_amount,
        'potential_savings': savings,
        'roi_percentage': roi_percentage,
        'financial_risk_level': 'HIGH' if fine_amount > 100000 else 'MEDIUM' if fine_amount > 50000 else 'LOW'
    }


def generate_safety_report(analysis_result: Dict) -> Dict:
    """
    Generate comprehensive safety report

    Args:
        analysis_result: Analysis result from Gemini

    Returns:
        Complete safety report with all metrics
    """

    risk_data = calculate_risk_score(analysis_result)
    prioritized_actions = prioritize_actions(analysis_result)
    financial_impact = calculate_financial_impact(analysis_result)

    return {
        'analysis': analysis_result,
        'risk_assessment': risk_data,
        'prioritized_actions': prioritized_actions,
        'financial_impact': financial_impact,
        'summary': {
            'total_workers': analysis_result.get('total_workers', 0),
            'compliance_rate': f"{analysis_result.get('overall_compliance_score', 0)}%",
            'risk_level': risk_data['risk_level'],
            'critical_issues': len(analysis_result.get('critical_violations', [])),
            'total_warnings': len(analysis_result.get('warnings', [])),
            'immediate_action_needed': risk_data['action_urgency'] in ['IMMEDIATE', '24_HOURS']
        }
    }


# Test the module when run directly
if __name__ == "__main__":
    print("Testing Risk Scoring Module...\n")

    # Sample analysis result
    test_analysis = {
        'total_workers': 10,
        'workers_compliant': 3,
        'workers_non_compliant': 7,
        'critical_violations': [
            {
                'violation': 'Workers on 3rd floor without safety harness',
                'location': 'Left scaffolding',
                'bis_code': 'IS_3696_1966',
                'risk_level': 'CRITICAL',
                'recommendation': 'Immediately provide and enforce safety harness usage'
            },
            {
                'violation': 'No safety net below work platform at 4m height',
                'location': 'Center area',
                'bis_code': 'IS_4081_1996',
                'risk_level': 'CRITICAL',
                'recommendation': 'Install safety net immediately'
            }
        ],
        'warnings': [
            {
                'violation': '5 workers without safety helmets',
                'location': 'General site',
                'bis_code': 'IS_2925_1984',
                'risk_level': 'HIGH',
                'recommendation': 'Provide helmets and enforce usage'
            }
        ],
        'compliant_items': ['Fire extinguisher visible', 'Good lighting'],
        'overall_compliance_score': 30,
        'risk_assessment': 'CRITICAL',
        'immediate_actions': ['Stop work', 'Install safety equipment'],
        'estimated_compliance_cost': '₹35,000',
        'potential_fine_if_inspected': '₹5,00,000'
    }

    # Test risk scoring
    risk_result = calculate_risk_score(test_analysis)
    print("📊 Risk Score Results:")
    print(f"Risk Score: {risk_result['risk_score']}/100")
    print(f"Risk Level: {risk_result['risk_level']}")
    print(f"Action Urgency: {risk_result['action_urgency']}")
    print(f"Recommendation: {risk_result['recommendation']}")

    # Test action prioritization
    print("\n📋 Prioritized Actions:")
    actions = prioritize_actions(test_analysis)
    for action in actions[:3]:  # Show top 3
        print(f"{action['priority']}. [{action['urgency']}] {action['action']}")

    # Test financial impact
    print("\n💰 Financial Impact:")
    financial = calculate_financial_impact(test_analysis)
    print(f"Potential Fine: ₹{financial['potential_fine']:,.0f}")
    print(f"Compliance Cost: ₹{financial['compliance_cost']:,.0f}")
    print(f"Potential Savings: ₹{financial['potential_savings']:,.0f}")
    print(f"ROI: {financial['roi_percentage']:.1f}%")

    # Test full report
    print("\n📄 Generating Full Safety Report...")
    report = generate_safety_report(test_analysis)
    print(f"Report Summary: {report['summary']}")
