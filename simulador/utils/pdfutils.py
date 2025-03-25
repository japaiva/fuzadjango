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

def gerar_pdf_demonstrativo(dimensionamento, explicacao, componentes, custo_total, respostas, respostas_agrupadas, grupos, username="Admin"):
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
    user_info = f"Usuário: {username} | Data: {format_date(now)} | Hora: {now.strftime('%H:%M:%S')}"
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
                explicacao_item = item.get('explicacao', 'Cálculo padrão')
                item_text = f"""
                {item['descricao']} ({item['codigo']}) - {item['quantidade']} {item['unidade']}
                Custo Unitário: {format_currency(item.get('custo_unitario', 0))}
                Custo Total: {format_currency(item['custo_total'])}
                Cálculo: {explicacao_item}
                """
                item_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_text)
                elements.append(Paragraph(item_text, normal_style))
            elements.append(Spacer(1, 0.1 * inch))
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- RESULTADO FINAL ----
    elements.append(Paragraph("Resultado Final", subtitle_style))
    elements.append(Paragraph(f"Custo Total: {format_currency(custo_total)}", bold_style))

    # ---- TABELA COMPONENTES (Simplificada) ----
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Componentes Utilizados", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Em vez de buscar do banco de dados, use os componentes passados como parâmetro
    table_data = [["Código", "Descrição", "Unidade", "Quantidade", "Custo Total"]]
    
    # Criar uma lista plana de todos os componentes
    todos_componentes = []
    for codigo, info in componentes.items():
        todos_componentes.append(info)
    
    # Ordenar por código para melhor visualização
    todos_componentes.sort(key=lambda x: x['codigo'])
    
    for comp in todos_componentes:
        desc_tratada = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', comp['descricao'])
        table_data.append([
            comp['codigo'],
            Paragraph(desc_tratada, normal_style),
            comp['unidade'],
            f"{comp['quantidade']:.2f}",
            format_currency(comp['custo_total'])
        ])
    
    table = Table(table_data, colWidths=[0.8*inch, 3*inch, 0.8*inch, 0.9*inch, 1.5*inch])
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
    elements.append(Indenter(left=20))
    elements.append(table)
    elements.append(Indenter(left=-20))

    # ---- FINALIZA O PDF ----
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def gerar_pdf_proposta_comercial(dimensionamento, componentes, custo_total, respostas_agrupadas, nome_cliente, empresa, username="Admin"):
    """
    Gera um PDF com a proposta comercial.
    """
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
    title_paragraph = Paragraph("Proposta Comercial - Elevadores Fuza", title_style)
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
    date_info = f"Data: {format_date(now)}"
    elements.append(Paragraph(date_info, normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # ---- INFORMAÇÕES DO CLIENTE ----
    elements.append(Paragraph("1. Informações do Cliente", subtitle_style))
    elements.append(Paragraph(f"Cliente: {nome_cliente}", normal_style))
    elements.append(Paragraph(f"Empresa: {empresa}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # ---- CONFIGURAÇÃO DO ELEVADOR ----
    elements.append(Paragraph("2. Configuração do Elevador", subtitle_style))
    
    # Dimensões
    elements.append(Paragraph("Dimensões do Elevador:", bold_style))
    dim_cabine = f"""
    Largura: {dimensionamento['cab']['largura']:.2f}m
    Comprimento: {dimensionamento['cab']['compr']:.2f}m
    Altura: {dimensionamento['cab']['altura']:.2f}m
    Capacidade: {format_currency(dimensionamento['cab']['capacidade'])} kg
    """
    elements.append(Paragraph(dim_cabine, normal_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    # Resumo das configurações
    for categoria, dados in respostas_agrupadas.items():
        elements.append(Paragraph(f"{categoria}:", bold_style))
        config_data = []
        for chave, valor in dados.items():
            config_data.append([chave, str(valor)])
        
        if config_data:
            table = Table(config_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(table)
        elements.append(Spacer(1, 0.1 * inch))

    elements.append(Spacer(1, 0.2 * inch))

    # ---- PROPOSTA COMERCIAL ----
    elements.append(Paragraph("3. Proposta Comercial", subtitle_style))
    
    # Valor total com destaque
    elements.append(Paragraph("Valor Total do Elevador:", bold_style))
    
    valor_style = ParagraphStyle(
        'valor_style',
        parent=bold_style,
        fontSize=14,
        textColor=colors.blue
    )
    
    elements.append(Paragraph(f"{format_currency(custo_total)}", valor_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Condições comerciais
    elements.append(Paragraph("Condições Comerciais:", bold_style))
    condicoes = [
        "• Prazo de entrega: 45 dias úteis após aprovação da proposta",
        "• Forma de pagamento: 50% de entrada e 50% na entrega",
        "• Garantia: 12 meses contra defeitos de fabricação",
        "• Assistência técnica: Suporte técnico 24 horas",
        "• Validade da proposta: 15 dias"
    ]
    
    for cond in condicoes:
        elements.append(Paragraph(cond, normal_style))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Instalação e entrega
    elements.append(Paragraph("Instalação e Entrega:", bold_style))
    instalacao = [
        "• Inclui instalação por técnicos especializados",
        "• Treinamento de uso para o cliente",
        "• Manual de operação e manutenção",
        "• Primeira manutenção gratuita após 3 meses"
    ]
    
    for inst in instalacao:
        elements.append(Paragraph(inst, normal_style))
    
    elements.append(Spacer(1, 0.3 * inch))
    
    # Assinaturas
    date_now = format_date(datetime.now())
    signature = f"""
    ________________, {date_now}
    
    
    
    ______________________                       ______________________
    Elevadores Fuza                              Cliente
    {username}
    """
    elements.append(Paragraph(signature, normal_style))

    # ---- FINALIZA O PDF ----
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf