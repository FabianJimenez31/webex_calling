"""
Report Generation Service
Generates PDF and CSV reports for security analysis and chat responses
"""
import csv
import io
import logging
from datetime import datetime
from typing import List, Dict, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate PDF and CSV reports"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom styles for Davivienda branding"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#E30519'),  # Davivienda red
            spaceAfter=30,
            alignment=TA_CENTER
        )

        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#E30519'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Normal text
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#010101')
        )

    def generate_security_report_pdf(self, analysis: Dict, cdrs_count: int) -> bytes:
        """
        Generate PDF security analysis report

        Args:
            analysis: Security analysis results
            cdrs_count: Number of CDRs analyzed

        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Title
        title = Paragraph("Webex Calling - Reporte de Seguridad", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Metadata
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        metadata = f"""
        <b>Fecha del Reporte:</b> {now}<br/>
        <b>CDRs Analizados:</b> {cdrs_count}<br/>
        <b>Nivel de Riesgo:</b> <font color="{self._get_risk_color(analysis.get('risk_level', 'UNKNOWN'))}">{analysis.get('risk_level', 'UNKNOWN')}</font>
        """
        story.append(Paragraph(metadata, self.normal_style))
        story.append(Spacer(1, 0.3 * inch))

        # Overall Assessment
        story.append(Paragraph("Evaluación General", self.heading_style))
        assessment = analysis.get('overall_assessment', 'No assessment available')
        story.append(Paragraph(assessment, self.normal_style))
        story.append(Spacer(1, 0.2 * inch))

        # Anomalies
        anomalies = analysis.get('anomalies', [])
        if anomalies:
            story.append(Paragraph(f"Anomalías Detectadas ({len(anomalies)})", self.heading_style))

            for i, anomaly in enumerate(anomalies, 1):
                anomaly_text = f"""
                <b>{i}. {anomaly.get('type', 'Unknown')} - Severidad: {anomaly.get('severity', 'UNKNOWN')}</b><br/>
                {anomaly.get('description', 'No description')}<br/>
                <b>Recomendación:</b> {anomaly.get('recommendation', 'No recommendation')}
                """
                story.append(Paragraph(anomaly_text, self.normal_style))
                story.append(Spacer(1, 0.15 * inch))
        else:
            story.append(Paragraph("No se detectaron anomalías", self.normal_style))
            story.append(Spacer(1, 0.2 * inch))

        # Insights
        insights = analysis.get('insights', [])
        if insights:
            story.append(Paragraph("Observaciones Clave", self.heading_style))
            for insight in insights:
                story.append(Paragraph(f"• {insight}", self.normal_style))
            story.append(Spacer(1, 0.2 * inch))

        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            story.append(Paragraph("Recomendaciones", self.heading_style))
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", self.normal_style))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_chat_report_pdf(self, chat_response: Dict) -> bytes:
        """
        Generate PDF report from chat response

        Args:
            chat_response: Chat assistant response

        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Title
        title = Paragraph("Webex Calling - Reporte de Análisis", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))

        # Question
        story.append(Paragraph("Pregunta", self.heading_style))
        story.append(Paragraph(chat_response.get('question', ''), self.normal_style))
        story.append(Spacer(1, 0.2 * inch))

        # Answer
        story.append(Paragraph("Respuesta", self.heading_style))
        story.append(Paragraph(chat_response.get('answer', ''), self.normal_style))
        story.append(Spacer(1, 0.2 * inch))

        # Details
        details = chat_response.get('details', {})

        # Key Metrics
        if 'key_metrics' in details:
            story.append(Paragraph("Métricas Clave", self.heading_style))
            metrics = details['key_metrics']
            for key, value in metrics.items():
                story.append(Paragraph(f"<b>{key}:</b> {value}", self.normal_style))
            story.append(Spacer(1, 0.2 * inch))

        # Insights
        if 'insights' in details:
            story.append(Paragraph("Observaciones", self.heading_style))
            for insight in details['insights']:
                story.append(Paragraph(f"• {insight}", self.normal_style))
            story.append(Spacer(1, 0.2 * inch))

        # Recommendations
        if 'recommendations' in details:
            story.append(Paragraph("Recomendaciones", self.heading_style))
            for rec in details['recommendations']:
                story.append(Paragraph(f"• {rec}", self.normal_style))

        # Timestamp
        timestamp = chat_response.get('timestamp', datetime.utcnow().isoformat())
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(f"<i>Generado: {timestamp}</i>", self.normal_style))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_cdrs_csv(self, cdrs: List[Dict]) -> str:
        """
        Generate CSV export of CDRs

        Args:
            cdrs: List of CDR records

        Returns:
            CSV content as string
        """
        if not cdrs:
            return "No data available"

        output = io.StringIO()

        # Get all unique keys from all CDRs
        fieldnames = set()
        for cdr in cdrs:
            fieldnames.update(cdr.keys())

        fieldnames = sorted(list(fieldnames))

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for cdr in cdrs:
            writer.writerow(cdr)

        return output.getvalue()

    def generate_analysis_csv(self, analysis: Dict) -> str:
        """
        Generate CSV export of security analysis

        Args:
            analysis: Security analysis results

        Returns:
            CSV content as string
        """
        output = io.StringIO()

        # Analysis summary
        writer = csv.writer(output)
        writer.writerow(['Webex Calling Security Analysis'])
        writer.writerow([''])
        writer.writerow(['Risk Level', analysis.get('risk_level', 'UNKNOWN')])
        writer.writerow(['Overall Assessment', analysis.get('overall_assessment', '')])
        writer.writerow([''])

        # Anomalies
        anomalies = analysis.get('anomalies', [])
        if anomalies:
            writer.writerow(['Anomalies'])
            writer.writerow(['Type', 'Severity', 'Description', 'Recommendation'])
            for anomaly in anomalies:
                writer.writerow([
                    anomaly.get('type', ''),
                    anomaly.get('severity', ''),
                    anomaly.get('description', ''),
                    anomaly.get('recommendation', '')
                ])
            writer.writerow([''])

        # Insights
        insights = analysis.get('insights', [])
        if insights:
            writer.writerow(['Insights'])
            for insight in insights:
                writer.writerow([insight])
            writer.writerow([''])

        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            writer.writerow(['Recommendations'])
            for rec in recommendations:
                writer.writerow([rec])

        return output.getvalue()

    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level"""
        colors_map = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred',
            'UNKNOWN': 'gray'
        }
        return colors_map.get(risk_level, 'gray')


# Global instance
report_generator = ReportGenerator()
