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
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"

# Função personalizada para formatação de data
def format_date(date):
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return str(date)
    if isinstance(date, datetime):
        return date.strftime("%d/%m/%Y")
    return str(date)

def gerar_pdf_demonstrativo(dimensionamento, explicacao, componentes, custo_total, respostas, respostas_agrupadas, grupos, username="Admin"):
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter, 
            rightMargin=72, 
            leftMargin=72, 
            topMargin=72, 
            bottomMargin=18
        )
    except Exception as e:
        print(f"Erro ao criar o documento PDF: {str(e)}")
        return None
        
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
    
    try:
        for categoria, dados in respostas_agrupadas.items():
            elements.append(Paragraph(f"{categoria}:", bold_style))
            for chave, valor in dados.items():
                elements.append(Paragraph(f"{chave}: {valor}", normal_style))
            elements.append(Spacer(1, 0.1 * inch))
    except Exception as e:
        error_msg = f"Erro ao processar configurações: {str(e)}"
        elements.append(Paragraph(error_msg, normal_style))
        print(error_msg)

    elements.append(Spacer(1, 0.2 * inch))

    # ---- 2. FICHA TÉCNICA ----
    elements.append(Paragraph("2. Ficha Técnica", subtitle_style))
    
    try:
        # Verifique a estrutura do dimensionamento antes de acessar os campos
        if isinstance(dimensionamento, dict) and 'cab' in dimensionamento:
            cab = dimensionamento['cab']
            
            # Verificar se cada campo existe antes de acessá-lo
            largura = cab.get('largura', 0)
            compr = cab.get('compr', 0)  
            altura = cab.get('altura', 0)
            capacidade = cab.get('capacidade', 0)
            tracao = cab.get('tracao', 0)
            
            # Criar strings seguras para cada valor
            largura_str = f"{float(largura):.2f}" if isinstance(largura, (int, float)) else "N/A"
            compr_str = f"{float(compr):.2f}" if isinstance(compr, (int, float)) else "N/A"
            altura_str = f"{float(altura):.2f}" if isinstance(altura, (int, float)) else "N/A"
            
            # Montar o texto da ficha técnica
            dim_text = f"Dimensões Cabine: {largura_str}m L x {compr_str}m C x {altura_str}m A"
            cap_tracao = f"Capacidade e Tração Cabine: {format_currency(capacidade)} kg, {format_currency(tracao)} kg"
            
            elements.append(Paragraph(dim_text, normal_style))
            elements.append(Paragraph(cap_tracao, normal_style))
        else:
            elements.append(Paragraph("Dados de dimensionamento incompletos ou em formato inválido.", normal_style))
    except Exception as e:
        # Tratar erros de acesso ao dimensionamento
        error_msg = f"Erro ao acessar informações de dimensionamento: {str(e)}"
        elements.append(Paragraph(error_msg, normal_style))
        print(error_msg)
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- 3. CÁLCULO DIMENSIONAMENTO ----
    elements.append(Paragraph("3. Cálculo Dimensionamento", subtitle_style))
    
    try:
        if explicacao and isinstance(explicacao, str):
            # Processar o texto de explicação linha por linha
            # Isso garante que cada linha seja tratada como um parágrafo separado
            linhas = explicacao.strip().split('\n')
            
            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue
                
                # Substituir tags HTML <strong> por tags Reportlab <b>
                linha = linha.replace('<strong>', '<b>').replace('</strong>', '</b>')
                
                # Processar possíveis valores numéricos para formatação BR
                linha = re.sub(r'(\d+\.\d+)', lambda m: f"{float(m.group(1)):.2f}".replace('.', ','), linha)
                
                try:
                    elements.append(Paragraph(linha, normal_style))
                except:
                    # Se falhar ao renderizar, tente remover formatações
                    linha_limpa = re.sub(r'<[^>]+>', '', linha)
                    elements.append(Paragraph(linha_limpa, normal_style))
        else:
            elements.append(Paragraph("Explicação de dimensionamento não disponível.", normal_style))
    except Exception as e:
        error_msg = f"Erro ao processar explicação: {str(e)}"
        elements.append(Paragraph(error_msg, normal_style))
        print(error_msg)
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- 4. CÁLCULO COMPONENTES ----
    elements.append(Paragraph("4. Cálculo Componentes", subtitle_style))
    try:
        if grupos and isinstance(grupos, dict):
            for grupo, subgrupos in grupos.items():
                elements.append(Paragraph(grupo, bold_style))
                if isinstance(subgrupos, dict):
                    for subgrupo, itens in subgrupos.items():
                        elements.append(Paragraph(subgrupo, bold_style))
                        if isinstance(itens, list):
                            for item in itens:
                                if isinstance(item, dict):
                                    # Extrair informações do item com segurança
                                    descricao = item.get('descricao', 'Sem descrição')
                                    codigo = item.get('codigo', 'N/A')
                                    quantidade = item.get('quantidade', 0)
                                    unidade = item.get('unidade', 'un')
                                    custo_unitario = item.get('custo_unitario', 0)
                                    custo_total_item = item.get('custo_total', 0)
                                    explicacao_item = item.get('explicacao', 'Cálculo padrão')
                                    
                                    # Sanitizar texto
                                    descricao = str(descricao).replace('<', '&lt;').replace('>', '&gt;')
                                    explicacao_item = str(explicacao_item).replace('<', '&lt;').replace('>', '&gt;')
                                    
                                    # Criar texto seguro
                                    item_text = (
                                        f"{descricao} ({codigo}) - {quantidade} {unidade}\n"
                                        f"Custo Unitário: {format_currency(custo_unitario)}\n"
                                        f"Custo Total: {format_currency(custo_total_item)}\n"
                                        f"Cálculo: {explicacao_item}"
                                    )
                                    elements.append(Paragraph(item_text, normal_style))
                        elements.append(Spacer(1, 0.1 * inch))
        else:
            elements.append(Paragraph("Dados de componentes não disponíveis ou em formato inválido.", normal_style))
    except Exception as e:
        error_msg = f"Erro ao processar componentes: {str(e)}"
        elements.append(Paragraph(error_msg, normal_style))
        print(error_msg)
    
    elements.append(Spacer(1, 0.2 * inch))

    # ---- RESULTADO FINAL ----
    elements.append(Paragraph("Resultado Final", subtitle_style))
    elements.append(Paragraph(f"Custo Total: {format_currency(custo_total)}", bold_style))

    # ---- TABELA COMPONENTES (Simplificada) ----
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Componentes Utilizados", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))

    try:
        if componentes and isinstance(componentes, dict):
            # Em vez de buscar do banco de dados, use os componentes passados como parâmetro
            table_data = [["Código", "Descrição", "Unidade", "Quantidade", "Custo Total"]]
            
            # Criar uma lista plana de todos os componentes
            todos_componentes = []
            for codigo, info in componentes.items():
                if isinstance(info, dict):
                    todos_componentes.append(info)
            
            # Ordenar por código para melhor visualização
            if todos_componentes:
                try:
                    todos_componentes.sort(key=lambda x: x.get('codigo', ''))
                except Exception as e:
                    print(f"Erro ao ordenar componentes: {str(e)}")
            
            for comp in todos_componentes:
                try:
                    # Sanitizar descrição
                    desc = str(comp.get('descricao', 'Sem descrição'))
                    desc_tratada = re.sub(r'\*\*(.*?)\*\*', r'\1', desc)
                    
                    # Valores seguros
                    codigo = comp.get('codigo', 'N/A')
                    unidade = comp.get('unidade', 'un')
                    quantidade = comp.get('quantidade', 0)
                    custo_total_item = comp.get('custo_total', 0)
                    
                    # Formatar quantidade
                    quantidade_str = f"{float(quantidade):.2f}" if isinstance(quantidade, (int, float)) else "0.00"
                    
                    # Adicionar linha na tabela
                    table_data.append([
                        codigo,
                        Paragraph(desc_tratada, normal_style),
                        unidade,
                        quantidade_str,
                        format_currency(custo_total_item)
                    ])
                except Exception as e:
                    print(f"Erro ao processar componente específico: {str(e)}")
            
            # Só criar tabela se houver dados
            if len(table_data) > 1:
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
            else:
                elements.append(Paragraph("Não há componentes para exibir na tabela.", normal_style))
        else:
            elements.append(Paragraph("Dados de componentes não disponíveis ou em formato inválido.", normal_style))
    except Exception as e:
        error_msg = f"Erro ao gerar tabela de componentes: {str(e)}"
        elements.append(Paragraph(error_msg, normal_style))
        print(error_msg)

# ---- FINALIZA O PDF ----
    try:
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    except Exception as e:
        print(f"Erro ao construir o PDF: {str(e)}")
        try:
            buffer.close()
        except:
            pass
        return None

def gerar_pdf_proposta_comercial(dimensionamento, componentes, custo_total, respostas_agrupadas, nome_cliente, empresa, username="Admin"):
    """
    Gera um PDF com a proposta comercial.
    """
    try:
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
        try:
            if isinstance(dimensionamento, dict) and 'cab' in dimensionamento:
                cab = dimensionamento['cab']
                
                # Verificar se cada campo existe antes de acessá-lo
                largura = cab.get('largura', 0)
                compr = cab.get('compr', 0)  
                altura = cab.get('altura', 0)
                capacidade = cab.get('capacidade', 0)
                
                # Criar strings seguras para cada valor
                largura_str = f"{float(largura):.2f}".replace('.', ',') if isinstance(largura, (int, float)) else "N/A"
                compr_str = f"{float(compr):.2f}".replace('.', ',') if isinstance(compr, (int, float)) else "N/A"
                altura_str = f"{float(altura):.2f}".replace('.', ',') if isinstance(altura, (int, float)) else "N/A"
                
                elements.append(Paragraph("Dimensões do Elevador:", bold_style))
                dim_cabine = f"""
                Largura: {largura_str}m
                Comprimento: {compr_str}m
                Altura: {altura_str}m
                Capacidade: {format_currency(capacidade)} kg
                """
                elements.append(Paragraph(dim_cabine, normal_style))
            else:
                elements.append(Paragraph("Informações de dimensões não disponíveis.", normal_style))
            elements.append(Spacer(1, 0.1 * inch))
        except Exception as e:
            error_msg = f"Erro ao acessar informações de dimensionamento: {str(e)}"
            elements.append(Paragraph(error_msg, normal_style))
            print(error_msg)
        
        # Resumo das configurações
        try:
            if respostas_agrupadas and isinstance(respostas_agrupadas, dict):
                for categoria, dados in respostas_agrupadas.items():
                    elements.append(Paragraph(f"{categoria}:", bold_style))
                    if isinstance(dados, dict) and dados:
                        config_data = []
                        for chave, valor in dados.items():
                            config_data.append([str(chave), str(valor)])
                        
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
                    else:
                        elements.append(Paragraph("Dados de configuração não disponíveis.", normal_style))
                    elements.append(Spacer(1, 0.1 * inch))
            else:
                elements.append(Paragraph("Configurações não disponíveis.", normal_style))
        except Exception as e:
            error_msg = f"Erro ao processar configurações: {str(e)}"
            elements.append(Paragraph(error_msg, normal_style))
            print(error_msg)

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
    except Exception as e:
        print(f"Erro ao gerar PDF da proposta comercial: {str(e)}")
        try:
            buffer.close()
        except:
            pass
        return None