"""
PDF Generation Service for Repayment Plans - FinanceBrews Themed
app/services/pdf_service.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from typing import Dict, Any

class NumberedCanvas(canvas.Canvas):
    """Custom canvas for page numbers with FinanceBrews branding"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Footer with FinanceBrews branding
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#78350F'))
        # Center text manually
        text = "Keep Brewing Your Financial Success"
        text_width = self.stringWidth(text, "Helvetica", 8)
        self.drawString((8.5*inch - text_width) / 2, 0.4*inch, text)
        
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor('#92400E'))
        self.drawRightString(7.5*inch, 0.4*inch, f"Page {self._pageNumber} of {page_count}")
        
        # Decorative line
        self.setStrokeColor(colors.HexColor('#D97706'))
        self.setLineWidth(1.5)
        self.line(0.75*inch, 0.55*inch, 7.75*inch, 0.55*inch)

class PDFService:
    
    @staticmethod
    def create_repayment_plan_pdf(plan_data: Dict[str, Any]) -> BytesIO:
        """Generate FinanceBrews themed PDF for repayment plan"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.8*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # FinanceBrews Brand Colors
        BROWN_DARK = colors.HexColor('#92400E')
        BROWN_MEDIUM = colors.HexColor('#B45309')
        ORANGE = colors.HexColor('#D97706')
        CREAM = colors.HexColor('#FEF3C7')
        LIGHT_CREAM = colors.HexColor('#FFFBEB')
        
        # Custom Styles with proper spacing
        logo_style = ParagraphStyle(
            'Logo',
            parent=styles['Normal'],
            fontSize=28,
            textColor=BROWN_DARK,
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=34
        )
        
        tagline_style = ParagraphStyle(
            'Tagline',
            parent=styles['Normal'],
            fontSize=11,
            textColor=BROWN_MEDIUM,
            spaceAfter=25,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique',
            leading=14
        )
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=BROWN_DARK,
            spaceAfter=15,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=24
        )
        
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=BROWN_DARK,
            spaceAfter=15,
            spaceBefore=25,
            fontName='Helvetica-Bold',
            leading=18,
            leftIndent=0
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=14,
            spaceAfter=10
        )
        
        # Header - FinanceBrews Logo with Coffee Cup
        elements.append(Spacer(1, 15))
        coffee_header = """
        <para align=center>
        <font size=32 color="#92400E">☕</font>
        </para>
        """
        elements.append(Paragraph(coffee_header, body_style))
        elements.append(Spacer(1, 5))
        
        elements.append(Paragraph("FINANCEBREWS", logo_style))
        elements.append(Paragraph("Brewing Your Way to Financial Freedom", tagline_style))
        
        # Decorative line
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2.5, ORANGE),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, BROWN_MEDIUM),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 20))
        
        # Document Title with coffee theme
        elements.append(Paragraph("YOUR PERSONALIZED DEBT REPAYMENT PLAN", title_style))
        
        # Document info in coffee-themed box
        doc_info_data = [[
            Paragraph(f"""
            <para align=center>
            <font size=9 color="#78350F">
            <b>Plan Brewed On:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
            <b>Document Type:</b> Official Repayment Schedule<br/>
            <b>Confidential Financial Document</b>
            </font>
            </para>
            """, body_style)
        ]]
        doc_info_table = Table(doc_info_data, colWidths=[6.5*inch])
        doc_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CREAM),
            ('BOX', (0, 0), (-1, -1), 1, ORANGE),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(doc_info_table)
        elements.append(Spacer(1, 30))
        
        # Plan Summary Section
        elements.append(Paragraph("☕ PLAN OVERVIEW", section_style))
        elements.append(Spacer(1, 5))
        
        summary_data = [
            [Paragraph('<b>Plan Details</b>', body_style), ''],
            ['Plan Name:', plan_data.get('plan_name', 'N/A')],
            ['Strategy:', plan_data.get('strategy', 'N/A')],
            ['', ''],
            [Paragraph('<b>Financial Summary</b>', body_style), ''],
            ['Total Debt Amount:', f"₹ {plan_data.get('original_total_debt', 0):,.2f}"],
            ['Monthly Budget:', f"₹ {plan_data.get('monthly_budget', 0):,.2f}"],
            ['Total Interest to Pay:', f"₹ {plan_data.get('total_interest_paid', 0):,.2f}"],
            ['', ''],
            [Paragraph('<b>Timeline</b>', body_style), ''],
            ['Repayment Duration:', f"{plan_data.get('months_to_debt_free', 0)} months ({(plan_data.get('months_to_debt_free', 0) / 12):.1f} years)"],
            ['Estimated Debt-Free Date:', (datetime.now().replace(day=1) + 
                                          __import__('dateutil.relativedelta').relativedelta.relativedelta(
                                              months=plan_data.get('months_to_debt_free', 0))).strftime('%B %Y')],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            # Headers
            ('SPAN', (0, 0), (1, 0)),
            ('SPAN', (0, 4), (1, 4)),
            ('SPAN', (0, 9), (1, 9)),
            ('BACKGROUND', (0, 0), (1, 0), CREAM),
            ('BACKGROUND', (0, 4), (1, 4), CREAM),
            ('BACKGROUND', (0, 9), (1, 9), CREAM),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, ORANGE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_CREAM]),
            ('LINEABOVE', (0, 0), (-1, 0), 2, ORANGE),
            ('LINEABOVE', (0, 4), (-1, 4), 2, ORANGE),
            ('LINEABOVE', (0, 9), (-1, 9), 2, ORANGE),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 25))
        
        # Important Notice
        notice_data = [[
            Paragraph("""
            <para align=justify>
            <b>📋 IMPORTANT NOTE:</b> This repayment plan is a projection based on your current financial 
            information and assumes consistent monthly payments. Actual results may vary based on interest 
            rate changes, payment timing, or additional charges. This document is for planning purposes 
            and does not constitute professional financial advice.
            </para>
            """, ParagraphStyle('Notice', parent=body_style, fontSize=9, textColor=colors.HexColor('#78350F')))
        ]]
        notice_table = Table(notice_data, colWidths=[6.5*inch])
        notice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FEF9C3')),
            ('BOX', (0, 0), (-1, -1), 1, ORANGE),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(notice_table)
        
        # Page Break
        elements.append(PageBreak())
        
        # Payment Schedule
        elements.append(Paragraph("☕ COMPLETE PAYMENT SCHEDULE", section_style))
        elements.append(Spacer(1, 10))
        
        # Build schedule data
        schedule_data = [[
            Paragraph('<b>Month</b>', body_style),
            Paragraph('<b>Account/Creditor</b>', body_style),
            Paragraph('<b>Payment</b>', body_style),
            Paragraph('<b>Interest</b>', body_style),
            Paragraph('<b>Principal</b>', body_style),
            Paragraph('<b>Total</b>', body_style)
        ]]
        
        monthly_payments = plan_data.get('monthly_payments', [])
        
        for payment in monthly_payments:
            month_num = payment.get('month_index', 0) + 1
            allocations = payment.get('allocations', [])
            
            for idx, alloc in enumerate(allocations):
                row = [
                    str(month_num) if idx == 0 else '',
                    alloc.get('name', 'N/A'),
                    f"₹ {alloc.get('payment', 0):,.0f}",
                    f"₹ {alloc.get('interest_accrued', 0):,.0f}",
                    f"₹ {alloc.get('principal_reduction', 0):,.0f}",
                    f"₹ {payment.get('total_paid', 0):,.0f}" if idx == 0 else ''
                ]
                schedule_data.append(row)
        
        # Create table with lighter header
        schedule_table = Table(schedule_data, colWidths=[0.5*inch, 2.3*inch, 1*inch, 1*inch, 1*inch, 1*inch], repeatRows=1)
        schedule_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FED7AA')),  # Light orange/cream header
            ('TEXTCOLOR', (0, 0), (-1, 0), BROWN_DARK),  # Dark brown text
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, ORANGE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_CREAM]),
        ]))
        
        elements.append(schedule_table)
        elements.append(Spacer(1, 20))
        
        # Summary footer
        footer_box = [[
            Paragraph(f"""
            <para align=center>
            <font size=9 color="#92400E">
            <b>Complete Schedule:</b> Showing all {len(monthly_payments)} months | 
            <b>Total to be Paid:</b> ₹{(plan_data.get('original_total_debt', 0) + plan_data.get('total_interest_paid', 0)):,.2f}
            </font>
            </para>
            """, body_style)
        ]]
        footer_table = Table(footer_box, colWidths=[6.5*inch])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CREAM),
            ('BOX', (0, 0), (-1, -1), 1, ORANGE),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(footer_table)
        
        # Page Break for Terms
        elements.append(PageBreak())
        
        # Terms Section
        elements.append(Paragraph("☕ TERMS & CONDITIONS", section_style))
        elements.append(Spacer(1, 10))
        
        terms = ParagraphStyle('Terms', parent=body_style, fontSize=9, leading=13, spaceAfter=12)
        
        elements.append(Paragraph(
            "<b>1. Payment Commitment:</b> This plan requires consistent monthly payments as outlined. "
            "Additional payments will reduce total interest and accelerate your debt-free date.",
            terms
        ))
        
        elements.append(Paragraph(
            "<b>2. Interest Calculations:</b> Interest amounts are based on current APR rates provided. "
            "These may change if your creditors adjust rates or if payments are delayed.",
            terms
        ))
        
        elements.append(Paragraph(
            "<b>3. On-Time Payments:</b> Late or missed payments may result in additional fees, "
            "increased interest, and extension of your debt-free timeline.",
            terms
        ))
        
        elements.append(Paragraph(
            "<b>4. Plan Flexibility:</b> You can modify this plan if your financial situation changes. "
            "Contact FinanceBrews to recalculate your schedule.",
            terms
        ))
        
        elements.append(Paragraph(
            "<b>5. Not Financial Advice:</b> This is a planning tool only. For personalized guidance, "
            "consult qualified financial professionals.",
            terms
        ))
        
        elements.append(Spacer(1, 30))
        
        # Document signature
        sig_data = [
            ['Generated By:', 'FinanceBrews Automated Planning System'],
            ['Date Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Document ID:', f"FBP-{datetime.now().strftime('%Y%m%d')}-{plan_data.get('plan_name', 'PLAN')[:8].replace(' ', '').upper()}"],
        ]
        sig_table = Table(sig_data, colWidths=[2*inch, 4.5*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), BROWN_DARK),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ]))
        elements.append(sig_table)
        elements.append(Spacer(1, 25))
        
        # Confidentiality notice
        conf_box = [[
            Paragraph("""
            <para align=center>
            <font size=8 color="#78350F">
            <b>CONFIDENTIAL DOCUMENT</b><br/>
            This document contains sensitive financial information. Keep secure.<br/>
            © 2025 FinanceBrews. All Rights Reserved.
            </font>
            </para>
            """, body_style)
        ]]
        conf_table = Table(conf_box, colWidths=[6.5*inch])
        conf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_CREAM),
            ('BOX', (0, 0), (-1, -1), 1, ORANGE),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(conf_table)
        
        # Build PDF
        doc.build(elements, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def create_payment_receipt_pdf(payment_data: Dict[str, Any]) -> BytesIO:
        """Generate FinanceBrews themed payment receipt"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.8*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Colors
        GREEN = colors.HexColor('#059669')
        GREEN_LIGHT = colors.HexColor('#ECFDF5')
        BROWN_DARK = colors.HexColor('#92400E')
        ORANGE = colors.HexColor('#D97706')
        CREAM = colors.HexColor('#FEF3C7')
        
        # Styles
        logo_style = ParagraphStyle(
            'Logo',
            parent=styles['Normal'],
            fontSize=24,
            textColor=BROWN_DARK,
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            leading=14
        )
        
        # Header
        elements.append(Spacer(1, 15))
        coffee_icon = "<para align=center><font size=28>☕</font></para>"
        elements.append(Paragraph(coffee_icon, body_style))
        elements.append(Spacer(1, 5))
        
        elements.append(Paragraph("FINANCEBREWS", logo_style))
        elements.append(Paragraph("Brewing Your Way to Financial Freedom", 
                                 ParagraphStyle('Tag', parent=styles['Normal'], fontSize=10,
                                              textColor=colors.HexColor('#78350F'), alignment=TA_CENTER,
                                              fontName='Helvetica-Oblique', spaceAfter=20)))
        
        # Line
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, GREEN),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 25))
        
        # Receipt title
        elements.append(Paragraph("PAYMENT CONFIRMATION RECEIPT", 
                                 ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18,
                                              textColor=GREEN, alignment=TA_CENTER, fontName='Helvetica-Bold',
                                              spaceAfter=20)))
        
        # Receipt number
        receipt_num = f"FBR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        receipt_box = [[
            Paragraph(f"""
            <para align=center>
            <font size=11 color="#059669"><b>Receipt No: {receipt_num}</b></font><br/>
            <font size=9 color="#666666">Issued: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</font>
            </para>
            """, body_style)
        ]]
        receipt_table = Table(receipt_box, colWidths=[6.5*inch])
        receipt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), GREEN_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1.5, GREEN),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(receipt_table)
        elements.append(Spacer(1, 30))
        
        # Payment details
        principal_paid = payment_data.get('total_paid', 0) - payment_data.get('total_interest', 0)
        details_data = [
            [Paragraph('<b>Payment Information</b>', body_style), ''],
            ['Repayment Plan:', payment_data.get('plan_name', 'N/A')],
            ['Payment Period:', f"Month {payment_data.get('month_index', 0) + 1}"],
            ['Payment Date:', payment_data.get('payment_date', datetime.now().strftime('%B %d, %Y'))],
            ['', ''],
            [Paragraph('<b>Financial Breakdown</b>', body_style), ''],
            ['Total Payment:', f"₹ {payment_data.get('total_paid', 0):,.2f}"],
            ['Interest Portion:', f"₹ {payment_data.get('total_interest', 0):,.2f}"],
            ['Principal Portion:', f"₹ {principal_paid:,.2f}"],
            ['', ''],
            [Paragraph('<b>Progress Update</b>', body_style), ''],
            ['Completed Payments:', f"{payment_data.get('completed_months', 0)} of {payment_data.get('total_months', 0)} months"],
            ['Overall Progress:', f"{payment_data.get('progress_percentage', 0):.1f}% Complete"],
        ]
        
        details_table = Table(details_data, colWidths=[2.5*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),
            ('SPAN', (0, 5), (1, 5)),
            ('SPAN', (0, 10), (1, 10)),
            ('BACKGROUND', (0, 0), (1, 0), GREEN_LIGHT),
            ('BACKGROUND', (0, 5), (1, 5), GREEN_LIGHT),
            ('BACKGROUND', (0, 10), (1, 10), GREEN_LIGHT),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, GREEN),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GREEN_LIGHT]),
            ('LINEABOVE', (0, 0), (-1, 0), 2, GREEN),
            ('LINEABOVE', (0, 5), (-1, 5), 2, GREEN),
            ('LINEABOVE', (0, 10), (-1, 10), 2, GREEN),
        ]))
        
        elements.append(details_table)
        elements.append(Spacer(1, 30))
        
        # Allocation section
        elements.append(Paragraph("Payment Allocation by Account", 
                                 ParagraphStyle('Section', parent=styles['Heading2'], fontSize=12,
                                              textColor=GREEN, fontName='Helvetica-Bold', spaceAfter=12)))
        
        alloc_data = [['Account Name', 'Payment', 'Interest', 'Principal']]
        for alloc in payment_data.get('allocations', []):
            alloc_data.append([
                alloc.get('name', 'N/A'),
                f"₹ {alloc.get('payment', 0):,.2f}",
                f"₹ {alloc.get('interest_accrued', 0):,.2f}",
                f"₹ {alloc.get('principal_reduction', 0):,.2f}"
            ])
        
        alloc_table = Table(alloc_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        alloc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A7F3D0')),  # Light green header
            ('TEXTCOLOR', (0, 0), (-1, 0), GREEN),  # Green text
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, GREEN),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GREEN_LIGHT]),
        ]))
        
        elements.append(alloc_table)
        elements.append(Spacer(1, 40))
        
        # Success message
        success_box = [[
            Paragraph(f"""
            <para align=center>
            <font size=16 color="#059669">🎉</font><br/>
            <font size=11 color="#059669"><b>Congratulations!</b></font><br/>
            <font size=10 color="#065F46">
            You're {payment_data.get('progress_percentage', 0):.1f}% of the way to being debt-free!<br/>
            Keep brewing your financial success!
            </font>
            </para>
            """, body_style)
        ]]
        success_table = Table(success_box, colWidths=[6.5*inch])
        success_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), CREAM),
            ('BOX', (0, 0), (-1, -1), 2, ORANGE),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(success_table)
        elements.append(Spacer(1, 25))
        
        # Footer
        footer = [[
            Paragraph("""
            <para align=center>
            <font size=9 color="#78350F">
            <b>Official Payment Receipt</b><br/>
            Keep this receipt for your financial records<br/><br/>
            <font size=8 color="#999999">
            This is a system-generated document | For support: support@financebrews.com<br/>
            © 2025 FinanceBrews. All Rights Reserved | Confidential Document
            </font>
            </font>
            </para>
            """, body_style)
        ]]
        footer_table = Table(footer, colWidths=[6.5*inch])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFBEB')),
            ('BOX', (0, 0), (-1, -1), 1, ORANGE),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(footer_table)
        
        doc.build(elements, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer