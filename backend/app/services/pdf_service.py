import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from typing import Dict, Any

class NumberedCanvas(canvas.Canvas):
    """Canvas wrapper to compute total page counts and print headers/footers dynamically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A365D")) # Navy
        
        # Header (Only on page 2 and later)
        if self._pageNumber > 1:
            self.drawString(54, 750, "CLINICAL DECISION SUPPORT SYSTEM (CDSS) - GENERAL ASSESSMENT")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)
            
        # Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        # Left footer (Disclaimer snippet)
        self.drawString(54, 40, "Confidential - Medical Decision Support Tool - Not a final diagnosis.")
        # Right footer (Page numbers)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 40, page_str)
        
        # Bottom decorative bar
        self.setStrokeColor(colors.HexColor("#1A365D"))
        self.setLineWidth(1)
        self.line(54, 52, letter[0] - 54, 52)
        
        self.restoreState()


class PDFReportGenerator:
    @staticmethod
    def generate_assessment_pdf(assessment: Any) -> io.BytesIO:
        """
        Generates a professionally styled clinical PDF report for the given assessment.
        Returns:
            BytesIO stream containing the PDF binary.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=64
        )
        
        styles = getSampleStyleSheet()
        
        # Define premium color scheme styles
        primary_color = colors.HexColor("#1A365D")   # Deep Slate Blue
        secondary_color = colors.HexColor("#0D9488") # Emerald Teal
        text_dark = colors.HexColor("#0F172A")       # Charcoal Body Text
        alert_bg = colors.HexColor("#FEF2F2")        # Light Red alert background
        alert_border = colors.HexColor("#FCA5A5")    # Red alert border
        
        # Custom Typography Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=primary_color,
            spaceAfter=15,
            leading=26
        )
        
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=primary_color,
            spaceBefore=14,
            spaceAfter=6,
            leading=18
        )
        
        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            textColor=text_dark,
            spaceAfter=6,
            leading=14
        )
        
        bold_body_style = ParagraphStyle(
            'BoldBodyDark',
            parent=body_style,
            fontName='Helvetica-Bold'
        )

        disclaimer_style = ParagraphStyle(
            'DisclaimerText',
            parent=body_style,
            fontName='Helvetica-Oblique',
            fontSize=8,
            textColor=colors.HexColor("#475569"),
            leading=11
        )

        story = []
        
        # 1. Header Banner
        banner_data = [
            [Paragraph("CLINICAL ASSESSMENT SUPPORT REPORT", ParagraphStyle('BannerTitle', fontName='Helvetica-Bold', fontSize=14, textColor=colors.white)),
             Paragraph(f"Timestamp: {assessment.created_at.strftime('%Y-%m-%d %H:%M:%S')}", ParagraphStyle('BannerTime', fontName='Helvetica', fontSize=9, textColor=colors.white, alignment=2))]
        ]
        banner_table = Table(banner_data, colWidths=[350, 154])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), primary_color),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 15))

        # 2. Patient Demographics & Vitals Table
        story.append(Paragraph("1. Patient Profile & Vital Signs", section_heading))
        patient = assessment.patient
        
        # Calculate BMI
        height_m = patient.height / 100.0
        bmi = patient.weight / (height_m ** 2) if height_m > 0 else 0
        
        demographics_data = [
            [Paragraph("<b>Patient Name:</b>", body_style), Paragraph(patient.name, body_style),
             Paragraph("<b>Blood Pressure:</b>", body_style), Paragraph(f"{assessment.blood_pressure_systolic}/{assessment.blood_pressure_diastolic} mmHg", body_style)],
            [Paragraph("<b>Age / Gender:</b>", body_style), Paragraph(f"{patient.age} yrs / {patient.gender}", body_style),
             Paragraph("<b>Heart Rate:</b>", body_style), Paragraph(f"{assessment.heart_rate} bpm", body_style)],
            [Paragraph("<b>Height / Weight:</b>", body_style), Paragraph(f"{patient.height} cm / {patient.weight} kg", body_style),
             Paragraph("<b>Temperature:</b>", body_style), Paragraph(f"{assessment.temperature} °C", body_style)],
            [Paragraph("<b>Calculated BMI:</b>", body_style), Paragraph(f"{bmi:.1f} kg/m²", body_style),
             Paragraph("<b>Respiration Rate:</b>", body_style), Paragraph(f"{assessment.respiratory_rate} /min", body_style)],
            [Paragraph("<b>Urgency Priority:</b>", body_style), Paragraph(f"<b>{assessment.priority}</b>", ParagraphStyle('Pri', parent=body_style, textColor=secondary_color if assessment.priority != 'EMERGENCY' else colors.HexColor("#B91C1C"))),
             Paragraph("<b>Oxygen Saturation:</b>", body_style), Paragraph(f"{assessment.oxygen_saturation}%", body_style)]
        ]
        
        demo_table = Table(demographics_data, colWidths=[100, 150, 110, 144])
        demo_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8FAFC")),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#F8FAFC")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(demo_table)
        story.append(Spacer(1, 12))

        # 3. Symptoms & History
        story.append(Paragraph("2. Symptoms & Medical Background", section_heading))
        symptoms_text = ", ".join([s.replace("_", " ").title() for s in assessment.symptoms]) if assessment.symptoms else "None logged"
        
        # Medical History format
        med_hx_list = []
        for cond, has in assessment.medical_history.items():
            if has is True or str(has).lower() == "true":
                med_hx_list.append(cond.replace("_", " ").title())
        med_hx_str = ", ".join(med_hx_list) if med_hx_list else "No active conditions reported"
        
        lifestyle_list = []
        for key, val in assessment.lifestyle.items():
            lifestyle_list.append(f"{key.title()}: {val}")
        lifestyle_str = ", ".join(lifestyle_list) if lifestyle_list else "No lifestyle records logged"

        symptom_data = [
            [Paragraph("<b>Logged Symptoms:</b>", bold_body_style), Paragraph(symptoms_text, body_style)],
            [Paragraph("<b>Medical History:</b>", bold_body_style), Paragraph(med_hx_str, body_style)],
            [Paragraph("<b>Lifestyle Factors:</b>", bold_body_style), Paragraph(lifestyle_str, body_style)]
        ]
        
        sym_table = Table(symptom_data, colWidths=[120, 384])
        sym_table.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(sym_table)
        story.append(Spacer(1, 15))

        # 4. Machine Learning Classification & SHAP
        story.append(Paragraph("3. Machine Learning Classification & Explanations", section_heading))
        ml_headers = [Paragraph("<b>Target Classification Model</b>", bold_body_style), 
                      Paragraph("<b>Calculated Probability</b>", bold_body_style), 
                      Paragraph("<b>Assigned Risk</b>", bold_body_style)]
        
        ml_rows = [ml_headers]
        shap_explanations = []
        
        for pred in assessment.predictions:
            prob_pct = f"{pred.probability * 100:.1f}%"
            # Color code risk column
            risk_color = colors.HexColor("#10B981") # Green
            if pred.risk_level == "HIGH":
                risk_color = colors.HexColor("#EF4444") # Red
            elif pred.risk_level == "MEDIUM":
                risk_color = colors.HexColor("#F59E0B") # Orange
                
            risk_para = Paragraph(f"<b>{pred.risk_level}</b>", ParagraphStyle('RCol', parent=body_style, textColor=risk_color))
            
            ml_rows.append([
                Paragraph(pred.disease, body_style),
                Paragraph(prob_pct, body_style),
                risk_para
            ])
            
            # Extract SHAP sentences
            if pred.shap_data and "natural_language_explanation" in pred.shap_data:
                shap_explanations.append(f"<b>{pred.disease} Analysis:</b> {pred.shap_data['natural_language_explanation']}")
        
        ml_table = Table(ml_rows, colWidths=[200, 150, 154])
        ml_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(ml_table)
        story.append(Spacer(1, 10))
        
        # Append SHAP Text box
        shap_box_data = [[Paragraph("<font color='#1E293B'><b>Explainable AI (SHAP) Insights:</b></font>", bold_body_style)]]
        for sentence in shap_explanations:
            shap_box_data.append([Paragraph(sentence, ParagraphStyle('ShapPara', parent=body_style, fontSize=9, leading=12))])
            
        shap_table = Table(shap_box_data, colWidths=[504])
        shap_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(shap_table)
        story.append(Spacer(1, 15))

        # Page Break before clinical RAG reports
        story.append(PageBreak())

        # 5. Clinical Synthesis (RAG / Local LLM)
        story.append(Paragraph("4. Clinical Synthesis & Differential Diagnoses", section_heading))
        
        report_record = assessment.reports[0] if assessment.reports else None
        if report_record:
            # Replace markdown hash tags or bullets with bold reportlab paragraphs
            report_text = report_record.llm_diagnosis
            # Simple conversion of markdown lines to paragraphs
            lines = report_text.split('\n')
            for line in lines:
                if not line.strip():
                    continue
                # Handle Headings
                if line.startswith('#'):
                    heading_text = line.replace('#', '').strip()
                    story.append(Paragraph(heading_text, ParagraphStyle('RepHead', parent=section_heading, fontSize=11, spaceBefore=6, spaceAfter=2)))
                # Handle bullet points
                elif line.startswith('*') or line.startswith('-'):
                    bullet_text = line[1:].strip()
                    story.append(Paragraph(f"• {bullet_text}", ParagraphStyle('RepBullet', parent=body_style, leftIndent=12, spaceAfter=3)))
                else:
                    story.append(Paragraph(line, ParagraphStyle('RepBody', parent=body_style, spaceAfter=4)))
        else:
            story.append(Paragraph("Clinical synthesis report unavailable.", body_style))
            
        story.append(Spacer(1, 15))

        # 6. Medical Disclaimer Alert Box
        disclaimer_box = Table(
            [[Paragraph("<b>WARNING & MEDICAL DISCLAIMER</b><br/>"
                       "This document is an automated clinical support output generated by a local Clinical Decision Support System (CDSS). "
                       "This is NOT a confirmed medical diagnosis. The information, predictions, and recommendations contained herein are "
                       "intended solely as analytical reference insights for licensed healthcare professionals. "
                       "Patient outcomes must be verified with blood laboratories, clinical exams, and diagnostic monitoring. "
                       "In case of critical clinical red flags, seek emergency medical services immediately.", disclaimer_style)]],
            colWidths=[504]
        )
        disclaimer_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), alert_bg),
            ('BOX', (0,0), (-1,-1), 1.0, alert_border),
            ('PADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        # Keep disclaimer, signing lines together
        signing_data = [
            [Spacer(1, 15)],
            [Table([
                [Paragraph("<b>Clinician Review Signature:</b> ___________________________", body_style),
                 Paragraph(f"<b>Review Date:</b> ________________________", body_style)]
            ], colWidths=[280, 224])]
        ]
        
        story.append(KeepTogether([disclaimer_box] + signing_data))

        # Build PDF
        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer
