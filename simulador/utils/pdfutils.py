import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, HRFlowable, Indenter
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
import re
from functions.database import get_all_custos

# Função personalizada para formatação de moeda
def format_currency(value):
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função personalizada para formatação de data
def format_date(date):
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    return date.strftime("%d/%m/%Y")

def gerar_pdf_demonstrativo(dimensionamento, explicacao, componentes, custo_total, respostas, respostas_agrupadas, grupos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=72, 
        leftMargin=72, 
        topMargin=72, 
        bottomMargin=18
    )
    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles['BodyText']
    subtitle_style = styles['Heading2']

    # ---- CRIANDO ESTILOS ESPECÍFICOS PARA O RELATÓRIO ----
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.black
    )
    
    bold_style = ParagraphStyle(
        'Bold', 
        parent=normal_style, 
        fontName='Helvetica-Bold'
    )

    # ---- CABEÇALHO (TÍTULO + LINHA) ----
    title_paragraph = Paragraph("Relatório de Cálculo do Elevador Fuza", title_style)
    elements.append(title_paragraph)
    
    hr = HRFlowable(
        width="100%",
        thickness=1,
        color=colors.black,
        spaceBefore=0.2 * inch,
        spaceAfter=0.3 * inch
    )
    elements.append(hr)

    # Informações do usuário, data e hora
    now = datetime.now()
    user_info = f"Usuário: {st.session_state.username} | Data: {format_date(now)} | Hora: {now.strftime('%H:%M:%S')}"
    elements.append(Paragraph(user_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # ---- 1. CONFIGURAÇÕES ----
    elements.append(Paragraph("1. Configurações", subtitle_style))
    
    for categoria, dados in respostas_agrupadas.items():
        elements.append(Paragraph(f"{categoria}:", bold_style))
        for chave, valor in dados.items():
            elements.append(Paragraph(f"{chave}: {valor}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    elements.append(Spacer(1, 0.2 * inch))

    # ---- 2. FICHA TÉCNICA ----
    elements.append(Paragraph("2. Ficha Técnica", subtitle_style))
    
    dim_cabine = f"""
    Dimensões Cabine: {dimensionamento['cab']['largura']:.2f}m L x {dimensionamento['cab']['compr']:.2f}m C x {dimensionamento['cab']['altura']:.2f}m A
    """
    elements.append(Paragraph(dim_cabine, normal_style))
    
    cap_tracao = f"""
    Capacidade e Tração Cabine: {format_currency(dimensionamento['cab']['capacidade'])} kg, {format_currency(dimensionamento['cab']['tracao'])} kg
    """
    elements.append(Paragraph(cap_tracao, normal_style))
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- 3. CÁLCULO DIMENSIONAMENTO ----
    elements.append(Paragraph("3. Cálculo Dimensionamento", subtitle_style))
    
    paragrafos = explicacao.split('\n')
    for paragrafo in paragrafos:
        paragrafo = paragrafo.strip()
        if paragrafo:
            paragrafo_com_negrito = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', paragrafo)
            elements.append(Paragraph(paragrafo_com_negrito, normal_style))
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- 4. CÁLCULO COMPONENTES ----
    elements.append(Paragraph("4. Cálculo Componentes", subtitle_style))
    for grupo, subgrupos in grupos.items():
        elements.append(Paragraph(grupo, bold_style))
        for subgrupo, itens in subgrupos.items():
            elements.append(Paragraph(subgrupo, bold_style))
            for item in itens:
                item_text = f"""
                {item['descricao']} ({item['codigo']}) - {item['quantidade']} {item['unidade']}
                Custo Unitário: {format_currency(item['custo_unitario'])}
                Custo Total: {format_currency(item['custo_total'])}
                Cálculo: {item['explicacao']}
                """
                item_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_text)
                elements.append(Paragraph(item_text, normal_style))
            elements.append(Spacer(1, 0.1 * inch))
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- RESULTADO FINAL ----
    elements.append(Paragraph("Resultado Final", subtitle_style))
    elements.append(Paragraph(f"Custo Total: {format_currency(custo_total)}", bold_style))

    # ---- TABELA COMPONENTES ----
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Tabela de Componentes", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))

    todos_custos = get_all_custos()
    table_data = [["Código", "Descrição", "Unidade", "Custo Unitário"]]
    for custo in todos_custos:
        desc_tratada = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', custo.descricao)
        table_data.append([
            custo.codigo,
            Paragraph(desc_tratada, normal_style),
            custo.unidade,
            format_currency(custo.valor)
        ])
    
    table = Table(table_data, colWidths=[1*inch, 3.5*inch, 1*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(Indenter(left=40))
    elements.append(table)
    elements.append(Indenter(left=-40))

    # ---- FINALIZA O PDF ----
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf