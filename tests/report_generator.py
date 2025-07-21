from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Drawing, String, Rect
from reportlab.graphics.charts.piecharts import Pie
from datetime import datetime
import os

class TestReportGenerator:
    def __init__(self, test_results):
        self.test_results = test_results
        self.styles = getSampleStyleSheet()

    def create_cover(self):
        elements = []

        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            img = Image(logo_path, width=3*inch, height=1.5*inch)
            img.hAlign = 'CENTER'
            elements.append(Spacer(1, 0.5*inch))
            elements.append(img)
            elements.append(Spacer(1, 0.7*inch))
        else:
            elements.append(Spacer(1, 2.2*inch))

        academic_style = ParagraphStyle(
            'AcademicInfo',
            parent=self.styles['Normal'],
            alignment=1,
            fontName='Helvetica',
            fontSize=14,
            leading=22,
            spaceAfter=12
        )

        academic_information = f"""
        <b><font size=18>Universidad Nacional de Colombia</font></b><br/><br/>
        <b>Facultad de Ingeniería</b><br/>
        <b>Ingeniería de Sistemas y Computación</b><br/><br/>
        <b>Asignatura:</b> Ingeniería de Software II<br/>
        <b>Equipo:</b> Cobras<br/><br/>
        <b>Fecha de generación:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        ac_info = Paragraph(academic_information, academic_style)
        elements.append(ac_info)

        elements.append(Spacer(1, 1.5*inch))

        return elements

    def create_summary_table(self):
        data = [
            ['Resumen de pruebas', ''],
            ['Total', len(self.test_results)],
            ['Exitosas', sum(1 for result in self.test_results if result['outcome'] == 'passed')],
            ['Fallidas', sum(1 for result in self.test_results if result['outcome'] == 'failed')],
            ["Porcentaje de éxito", f"{(sum(1 for result in self.test_results if result['outcome'] == 'passed') / len(self.test_results)) * 100:.2f}%"],
            ['Duración total (s)', f"{sum(result.get('duration', 0) for result in self.test_results):.2f}"],
            ["Duración promedio (s)", f"{(sum(result.get('duration', 0) for result in self.test_results) / len(self.test_results)):.2f}"]
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.8)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.2, 0.4, 0.8)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table

    def create_pie_chart(self, test_results):
        drawing = Drawing(450, 250)

        pie = Pie()
        pie.x = 165
        pie.y = 70
        pie.width = 140
        pie.height = 140

        successful = sum(1 for result in test_results if result.get('outcome') == 'passed')
        failed = sum(1 for result in test_results if result.get('outcome') == 'failed')
        total = successful + failed

        azul = colors.HexColor('#345D9D')
        rojo = colors.HexColor('#E74C3C')

        if total == 0:
            pie.data = [1]
            pie.labels = ['Sin datos']
            pie.slices[0].fillColor = colors.grey
        elif failed > 0:
            pie.data = [successful, failed]
            pie.labels = [f'{(successful / total) * 100:.0f}%', f'{(failed / total) * 100:.0f}%']
            pie.slices[0].fillColor = azul
            pie.slices[1].fillColor = rojo
        else:
            pie.data = [successful]
            pie.labels = ['100%']
            pie.slices[0].fillColor = azul

        pie.slices.strokeWidth = 2
        pie.slices.strokeColor = colors.white
        pie.slices.labelRadius = 0.7
        pie.slices.fontSize = 14
        pie.slices.fontName = 'Helvetica-Bold'
        pie.slices.fontColor = colors.white
        pie.slices.popout = 0

        title = String(225, 225, 'Resultados de las pruebas', fontSize=14,
                    fontName='Helvetica-Bold', textAnchor='middle')
        drawing.add(title)

        legend_y = 180
        if total == 0:
            drawing.add(Rect(50, legend_y, 15, 15, fillColor=colors.grey, strokeColor=colors.black))
            drawing.add(String(75, legend_y + 4, f'Sin resultados', fontSize=10, fontName='Helvetica'))
        elif failed > 0:
            drawing.add(Rect(50, legend_y, 15, 15, fillColor=azul, strokeColor=colors.black))
            drawing.add(String(75, legend_y + 4, f'Exitosas ({successful})', fontSize=10, fontName='Helvetica'))

            drawing.add(Rect(50, legend_y - 20, 15, 15, fillColor=rojo, strokeColor=colors.black))
            drawing.add(String(75, legend_y - 16, f'Fallidas ({failed})', fontSize=10, fontName='Helvetica'))
        else:
            drawing.add(Rect(50, legend_y, 15, 15, fillColor=azul, strokeColor=colors.black))
            drawing.add(String(75, legend_y + 4, f'Exitosas ({successful})', fontSize=10, fontName='Helvetica-Bold'))

        drawing.add(pie)
        return drawing


    def create_detailed_results(self):
        """Create a detailed table of test results"""
        data = [['Nombre de la prueba', 'Resultado', 'Duración (s)']]
        for result in self.test_results:
            status = 'Exitosa' if result['outcome'] == 'passed' else 'Fallida'
            data.append([
                result['name'],
                status,
                f"{result.get('duration', 0):.2f}"
            ])
        
        table = Table(data, colWidths=[4*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.8)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.2, 0.4, 0.8)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            *[('BACKGROUND', (0, i), (-1, i), colors.Color(0.95, 0.95, 0.95)) for i in range(2, len(data), 2)]
        ]))
        
        return table

    def generate_report(self, output_path='test_report.pdf'):
        """Generate the complete PDF report"""
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        story.extend(self.create_cover())
        story.append(PageBreak())

        report_title = Paragraph("Reporte de pruebas BE - Servicio de autenticación", self.styles['Heading1'])
        report_title.alignment = TA_CENTER
        story.append(report_title)
        story.append(Spacer(1, 12))
        
        story.append(self.create_summary_table())
        story.append(Spacer(1, 20))
        
        story.append(self.create_pie_chart(self.test_results))
        
        story.append(Paragraph("Resultados Detallados", self.styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(self.create_detailed_results())
        
        doc.build(story)
