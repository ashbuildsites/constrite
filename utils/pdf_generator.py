"""
Professional PDF Report Generator for Construction Safety Analysis
Generates comprehensive, print-ready safety reports with charts and formatting
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.pdfgen import canvas


class SafetyReportPDF:
    """Generate professional PDF reports for construction safety analyses"""

    def __init__(self):
        """Initialize PDF generator with custom styles"""
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#1f77b4'),
            borderPadding=5,
            backColor=colors.HexColor('#e3f2fd')
        ))

        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))

        # Critical text
        self.styles.add(ParagraphStyle(
            name='Critical',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#f44336'),
            fontName='Helvetica-Bold'
        ))

        # Warning text
        self.styles.add(ParagraphStyle(
            name='Warning',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#ff9800'),
            fontName='Helvetica-Bold'
        ))

        # Success text
        self.styles.add(ParagraphStyle(
            name='Success',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4caf50'),
            fontName='Helvetica-Bold'
        ))

    def _create_header_footer(self, canvas_obj, doc):
        """Create header and footer for each page"""
        canvas_obj.saveState()

        # Header
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(colors.HexColor('#1f77b4'))
        canvas_obj.drawString(50, self.height - 30, "ConStrite - Construction Safety Report")

        # Footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        canvas_obj.drawRightString(self.width - 50, 30, f"Page {doc.page}")

        # Footer line
        canvas_obj.setStrokeColor(colors.HexColor('#1f77b4'))
        canvas_obj.setLineWidth(1)
        canvas_obj.line(50, 50, self.width - 50, 50)

        canvas_obj.restoreState()

    def _create_cover_page(self, site_info: Dict, analysis_data: Dict, risk_data: Dict) -> List:
        """Create an impressive cover page"""
        elements = []

        # Logo/Title
        title = Paragraph(
            "ConStrite<br/><font size='16'>Construction Safety Analysis Report</font>",
            self.styles['CustomTitle']
        )
        elements.append(Spacer(1, 1.2*inch))
        elements.append(title)
        elements.append(Spacer(1, 1*inch))

        # Risk badge
        risk_level = risk_data.get('risk_level', 'UNKNOWN')
        risk_colors = {
            'CRITICAL': '#B71C1C',
            'HIGH': '#E53935',
            'MEDIUM': '#FB8C00',
            'LOW': '#43A047'
        }
        risk_color = risk_colors.get(risk_level, '#757575')

        risk_text = Paragraph(
            f'<para align="center" fontSize="20" textColor="{risk_color}" fontName="Helvetica-Bold" spaceAfter="20">'
            f'Risk Level: {risk_level}<br/><br/>'
            f'Score: {risk_data.get("risk_score", 0)}/100'
            f'</para>',
            self.styles['Normal']
        )
        elements.append(risk_text)
        elements.append(Spacer(1, 0.8*inch))

        # Site information table
        site_data = [
            ['Site ID:', site_info.get('site_id', 'N/A')],
            ['Location:', site_info.get('location', 'N/A')],
            ['Contractor:', site_info.get('contractor', 'N/A')],
            ['Project Type:', site_info.get('project_type', 'N/A')],
            ['Analysis Date:', datetime.now().strftime('%B %d, %Y')],
            ['Analysis Time:', datetime.now().strftime('%I:%M %p')]
        ]

        site_table = Table(site_data, colWidths=[2*inch, 3.5*inch])
        site_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f77b4')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(site_table)
        elements.append(Spacer(1, 0.5*inch))

        # Compliance score
        score = analysis_data.get('overall_compliance_score', 0)
        score_color = '#4caf50' if score >= 80 else '#ff9800' if score >= 50 else '#f44336'

        # Score with proper spacing
        score_para = Paragraph(
            f'<para align="center" fontSize="36" textColor="{score_color}" fontName="Helvetica-Bold">'
            f'{score}%'
            f'</para>',
            self.styles['Normal']
        )
        elements.append(score_para)
        elements.append(Spacer(1, 0.3*inch))

        label_para = Paragraph(
            '<para align="center" fontSize="14" textColor="grey">'
            'Overall Compliance Score'
            '</para>',
            self.styles['Normal']
        )
        elements.append(label_para)
        elements.append(Spacer(1, 0.5*inch))

        # Disclaimer
        disclaimer = Paragraph(
            '<i>This report is generated using AI-powered analysis and should be used in conjunction '
            'with professional safety inspections. ConStrite is powered by Gemini 2.5 Pro.</i>',
            self.styles['CustomBody']
        )
        elements.append(disclaimer)

        elements.append(PageBreak())
        return elements

    def _create_executive_summary(self, analysis_data: Dict, risk_data: Dict, financial_data: Dict) -> List:
        """Create executive summary section"""
        elements = []

        # Section header
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.3*inch))

        # Key metrics
        summary_data = [
            ['Metric', 'Value'],
            ['Total Workers', str(analysis_data.get('total_workers', 0))],
            ['Compliant Workers', str(analysis_data.get('workers_compliant', 0))],
            ['Non-Compliant Workers', str(analysis_data.get('workers_non_compliant', 0))],
            ['Compliance Score', f"{analysis_data.get('overall_compliance_score', 0)}%"],
            ['Risk Level', risk_data.get('risk_level', 'UNKNOWN')],
            ['Critical Violations', str(len(analysis_data.get('critical_violations', [])))],
            ['Warnings', str(len(analysis_data.get('warnings', [])))],
            ['Potential Fine', f"Rs. {financial_data.get('potential_fine', 0):,.0f}"],
            ['Compliance Cost', f"Rs. {financial_data.get('compliance_cost', 0):,.0f}"],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f5f5f5')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))

        # Recommendation box
        recommendation = Paragraph(
            f'<b>Recommended Action:</b> {risk_data.get("recommendation", "N/A")}',
            self.styles['CustomBody']
        )
        elements.append(recommendation)

        urgency = Paragraph(
            f'<b>Action Urgency:</b> {risk_data.get("action_urgency", "N/A").replace("_", " ")}',
            self.styles['CustomBody']
        )
        elements.append(urgency)

        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_violations_section(self, analysis_data: Dict) -> List:
        """Create critical violations section"""
        elements = []

        # Critical violations
        elements.append(Paragraph("Critical Violations", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        critical_violations = analysis_data.get('critical_violations', [])

        if critical_violations:
            for i, violation in enumerate(critical_violations, 1):
                confidence = violation.get('confidence', 85)
                violation_data = [
                    ['#', str(i)],
                    ['Violation', violation.get('violation', 'Unknown')],
                    ['Location', violation.get('location', 'Unknown')],
                    ['BIS Code', violation.get('bis_code', 'N/A')],
                    ['Confidence', f"{confidence}%"],
                    ['Recommendation', violation.get('recommendation', 'Fix immediately')]
                ]

                # Wrap text in Paragraphs for better layout
                violation_data_wrapped = [
                    [Paragraph('<b>#</b>', self.styles['Normal']),
                     Paragraph(f'<b>{i}</b>', self.styles['Normal'])],
                    [Paragraph('<b>Violation</b>', self.styles['Normal']),
                     Paragraph(violation.get('violation', 'Unknown'), self.styles['Normal'])],
                    [Paragraph('<b>Location</b>', self.styles['Normal']),
                     Paragraph(violation.get('location', 'Unknown'), self.styles['Normal'])],
                    [Paragraph('<b>BIS Code</b>', self.styles['Normal']),
                     Paragraph(violation.get('bis_code', 'N/A'), self.styles['Normal'])],
                    [Paragraph('<b>Confidence</b>', self.styles['Normal']),
                     Paragraph(f"{confidence}%", self.styles['Normal'])],
                    [Paragraph('<b>Recommendation</b>', self.styles['Normal']),
                     Paragraph(violation.get('recommendation', 'Fix immediately'), self.styles['Normal'])]
                ]

                violation_table = Table(violation_data_wrapped, colWidths=[1.2*inch, 4.5*inch])
                violation_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ffebee')),
                    ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f44336')),
                    ('TEXTCOLOR', (1, 0), (1, 0), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))

                elements.append(violation_table)
                elements.append(Spacer(1, 0.4*inch))
        else:
            elements.append(Paragraph(
                '✅ No critical violations detected!',
                self.styles['Success']
            ))
            elements.append(Spacer(1, 0.2*inch))

        # Warnings
        elements.append(Paragraph("Warnings", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        warnings = analysis_data.get('warnings', [])

        if warnings:
            for i, warning in enumerate(warnings, 1):
                confidence = warning.get('confidence', 85)
                warning_data = [
                    ['#', str(i)],
                    ['Warning', warning.get('violation', 'Unknown')],
                    ['Location', warning.get('location', 'Unknown')],
                    ['BIS Code', warning.get('bis_code', 'N/A')],
                    ['Risk Level', warning.get('risk_level', 'MEDIUM')],
                    ['Confidence', f"{confidence}%"],
                    ['Recommendation', warning.get('recommendation', 'Address soon')]
                ]

                # Wrap text in Paragraphs for better layout
                warning_data_wrapped = [
                    [Paragraph('<b>#</b>', self.styles['Normal']),
                     Paragraph(f'<b>{i}</b>', self.styles['Normal'])],
                    [Paragraph('<b>Warning</b>', self.styles['Normal']),
                     Paragraph(warning.get('violation', 'Unknown'), self.styles['Normal'])],
                    [Paragraph('<b>Location</b>', self.styles['Normal']),
                     Paragraph(warning.get('location', 'Unknown'), self.styles['Normal'])],
                    [Paragraph('<b>BIS Code</b>', self.styles['Normal']),
                     Paragraph(warning.get('bis_code', 'N/A'), self.styles['Normal'])],
                    [Paragraph('<b>Risk Level</b>', self.styles['Normal']),
                     Paragraph(warning.get('risk_level', 'MEDIUM'), self.styles['Normal'])],
                    [Paragraph('<b>Confidence</b>', self.styles['Normal']),
                     Paragraph(f"{confidence}%", self.styles['Normal'])],
                    [Paragraph('<b>Recommendation</b>', self.styles['Normal']),
                     Paragraph(warning.get('recommendation', 'Address soon'), self.styles['Normal'])]
                ]

                warning_table = Table(warning_data_wrapped, colWidths=[1.2*inch, 4.5*inch])
                warning_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
                    ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#ff9800')),
                    ('TEXTCOLOR', (1, 0), (1, 0), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))

                elements.append(warning_table)
                elements.append(Spacer(1, 0.4*inch))
        else:
            elements.append(Paragraph(
                '✅ No warnings!',
                self.styles['Success']
            ))
            elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_compliant_items_section(self, analysis_data: Dict) -> List:
        """Create compliant items section"""
        elements = []

        elements.append(Paragraph("Compliant Items", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        compliant_items = analysis_data.get('compliant_items', [])

        if compliant_items:
            compliant_data = [['✓', item] for item in compliant_items]

            compliant_table = Table(compliant_data, colWidths=[0.5*inch, 5*inch])
            compliant_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f5e9')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4caf50')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4caf50')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))

            elements.append(compliant_table)
        else:
            elements.append(Paragraph(
                'No compliant items detected.',
                self.styles['CustomBody']
            ))

        elements.append(Spacer(1, 0.3*inch))
        return elements

    def _create_action_plan_section(self, actions: List[Dict]) -> List:
        """Create action plan section"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("Immediate Action Plan", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        if not actions:
            elements.append(Paragraph('No actions required.', self.styles['CustomBody']))
            return elements

        # Show top 10 actions
        for action in actions[:10]:
            action_data = [
                ['Priority', f"#{action['priority']} - {action['urgency']}"],
                ['Action', action['action']],
                ['Violation', action['violation']],
                ['Location', action['location']],
                ['BIS Code', action['bis_code']],
                ['Time Required', action['estimated_time']],
                ['Estimated Cost', action['estimated_cost']]
            ]

            urgency_colors = {
                'IMMEDIATE': '#f44336',
                'HIGH': '#ff9800',
                'MEDIUM': '#2196f3'
            }
            bg_color = urgency_colors.get(action['urgency'], '#757575')

            # Wrap text in Paragraphs for better layout
            action_data_wrapped = [
                [Paragraph(f'<b>Priority {action["priority"]}</b>', self.styles['Normal']),
                 Paragraph(f'<b>[{action["urgency"]}]</b>', self.styles['Normal'])],
                [Paragraph('<b>Action</b>', self.styles['Normal']),
                 Paragraph(action['action'], self.styles['Normal'])],
                [Paragraph('<b>Violation</b>', self.styles['Normal']),
                 Paragraph(action['violation'], self.styles['Normal'])],
                [Paragraph('<b>Location</b>', self.styles['Normal']),
                 Paragraph(action['location'], self.styles['Normal'])],
                [Paragraph('<b>BIS Code</b>', self.styles['Normal']),
                 Paragraph(action['bis_code'], self.styles['Normal'])],
                [Paragraph('<b>Time Required</b>', self.styles['Normal']),
                 Paragraph(action['estimated_time'], self.styles['Normal'])],
                [Paragraph('<b>Estimated Cost</b>', self.styles['Normal']),
                 Paragraph(action['estimated_cost'], self.styles['Normal'])]
            ]

            action_table = Table(action_data_wrapped, colWidths=[1.5*inch, 4*inch])
            action_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(bg_color)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f5f5f5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            elements.append(action_table)
            elements.append(Spacer(1, 0.5*inch))

        return elements

    def generate_report(
        self,
        analysis_data: Dict,
        site_info: Dict,
        risk_data: Dict,
        financial_data: Dict,
        actions: List[Dict],
        output_path: Optional[str] = None
    ) -> BytesIO:
        """
        Generate complete PDF report

        Args:
            analysis_data: Analysis results from Gemini
            site_info: Site information dictionary
            risk_data: Risk assessment data
            financial_data: Financial impact data
            actions: Prioritized action items
            output_path: Optional file path to save PDF

        Returns:
            BytesIO buffer containing the PDF
        """
        # Create buffer
        buffer = BytesIO()

        # Create document
        if output_path:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=60,
                bottomMargin=60
            )
        else:
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=60,
                bottomMargin=60
            )

        # Build content
        story = []

        # Cover page
        story.extend(self._create_cover_page(site_info, analysis_data, risk_data))

        # Executive summary
        story.extend(self._create_executive_summary(analysis_data, risk_data, financial_data))

        # Violations
        story.append(PageBreak())
        story.extend(self._create_violations_section(analysis_data))

        # Compliant items
        story.extend(self._create_compliant_items_section(analysis_data))

        # Action plan
        story.extend(self._create_action_plan_section(actions))

        # Build PDF
        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

        # Reset buffer position
        if not output_path:
            buffer.seek(0)

        return buffer


# Test the module
if __name__ == "__main__":
    print("Testing PDF Generator...\n")

    # Sample data
    test_analysis = {
        'total_workers': 10,
        'workers_compliant': 6,
        'workers_non_compliant': 4,
        'overall_compliance_score': 65,
        'critical_violations': [
            {
                'violation': 'Workers not wearing safety helmets',
                'location': 'Scaffolding area - Level 3',
                'bis_code': 'IS 2925:1984',
                'recommendation': 'Immediately provide and enforce helmet usage'
            }
        ],
        'warnings': [
            {
                'violation': 'Inadequate safety signage',
                'location': 'Main entrance',
                'bis_code': 'IS 3764:1992',
                'risk_level': 'MEDIUM',
                'recommendation': 'Install proper safety signs'
            }
        ],
        'compliant_items': [
            'Fire extinguishers present and maintained',
            'First aid kit available',
            'Emergency exits clearly marked'
        ]
    }

    test_site = {
        'site_id': 'BLR-SITE-001',
        'location': 'Bangalore, Karnataka',
        'contractor': 'ABC Constructions Pvt Ltd',
        'project_type': 'Commercial'
    }

    test_risk = {
        'risk_level': 'HIGH',
        'risk_score': 68,
        'recommendation': 'Address critical violations within 24 hours',
        'action_urgency': 'HIGH_PRIORITY'
    }

    test_financial = {
        'potential_fine': 250000,
        'compliance_cost': 75000,
        'potential_savings': 175000,
        'roi_percentage': 233
    }

    test_actions = [
        {
            'priority': 1,
            'urgency': 'IMMEDIATE',
            'action': 'Provide safety helmets',
            'violation': 'Workers not wearing helmets',
            'location': 'Scaffolding area',
            'bis_code': 'IS 2925:1984',
            'estimated_time': '2 hours',
            'estimated_cost': 'Rs. 15,000'
        }
    ]

    # Generate PDF
    generator = SafetyReportPDF()
    pdf_buffer = generator.generate_report(
        test_analysis,
        test_site,
        test_risk,
        test_financial,
        test_actions,
        output_path="test_safety_report.pdf"
    )

    print("✅ Test PDF generated: test_safety_report.pdf")
