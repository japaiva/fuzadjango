import math
from simulador.utils.utils import formatar_demanda_placas
from simulador.utils.formacao_preco  import FormacaoPreco

def get_all_custos():
    """
    Retorna todos os custos do banco de dados
    """
    from ..models import Custo
    return Custo.objects.all()

# dimensoes
# componentes

# largura painel
# chapas cabine

def calcular_dimensionamento_completo(respostas: dict):
    # Extrair dados das respostas
    altura = float(respostas.get("Altura da Cabine", 0))
    largura_poco = float(respostas.get("Largura do Poço", 0))
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))
    modelo_porta = respostas.get("Modelo Porta", "")
    folhas_porta = respostas.get("Folhas Porta", "")
    contrapeso = respostas.get("Contrapeso", "")
    modelo = respostas.get("Modelo do Elevador", "")
    capacidade_original = float(respostas.get("Capacidade", 0))
    saida = respostas.get("Saída", "")
    
    # Calcular largura
    sub_largura = 0.42 if largura_poco <= 1.5 else 0.48
    largura = largura_poco - sub_largura
    if contrapeso == "Lateral":
        largura -= 0.23
    
    # Calcular comprimento
    comprimento = comprimento_poco - 0.10
    ajuste_porta = 0.0
    if modelo_porta == "Automática":
        if folhas_porta == "Central":
            ajuste_porta = 0.138
        elif folhas_porta == "2":
            ajuste_porta = 0.21
        elif folhas_porta == "3":
            ajuste_porta = 0.31
    elif modelo_porta == "Pantográfica":
        ajuste_porta = 0.13
    elif modelo_porta == "Pivotante":
        ajuste_porta = 0.04
    
    # Multiplicar ajuste da porta por 2 se a saída for oposta
    if saida == "Oposta":
        ajuste_porta *= 2
    
    comprimento -= ajuste_porta
    if contrapeso == "Traseiro":
        comprimento -= 0.23
    
    # Arredondar dimensões
    largura = round(largura, 2)
    comprimento = round(comprimento, 2)
    
    # Calcular capacidade e tracao
    if "Passageiro" in modelo:
        capacidade_cabine = capacidade_original * 80
    else:
        capacidade_cabine = capacidade_original
    tracao_cabine = capacidade_cabine / 2 + 500
    
    # Calcular chapas
    chapas_info = calcular_chapas_cabine(altura, largura, comprimento)
    
    # Função para formatação segura
    def formato_seguro(valor, decimais=2):
        """Formata um número com segurança, tratando possíveis erros"""
        try:
            numero = float(valor)
            return round(numero, decimais)
        except (ValueError, TypeError):
            return 0
    
    # Função para formatar texto com negrito de forma compatível
    def formato_negrito(texto):
        """Formata texto com negrito de maneira compatível com PDF e HTML"""
        return f"<strong>{texto}</strong>"
    
    # Gerar explicações detalhadas de modo compatível tanto com HTML quanto PDF
    explicacoes = []
    
    # Dimensões da cabine
    explicacoes.append(f"{formato_negrito('Dimensões Cabine:')}")
    explicacoes.append(f"Largura: Poço = {formato_seguro(largura_poco)}m - ({formato_seguro(sub_largura)}m)"
                      f"{' -Contrapeso lateral (0,23m),' if contrapeso == 'Lateral' else ''} = {formato_seguro(largura)}m")
    
    explicacoes.append(f"Comprimento: Poço = {formato_seguro(comprimento_poco)}m - (0,10m) - "
                      f"Ajuste de porta {modelo_porta} {f'({folhas_porta} folhas)' if folhas_porta else ''} "
                      f"{'(x2 pois saída é oposta)' if saida == 'Oposta' else ''} ({formato_seguro(ajuste_porta)}m)"
                      f"{' - Contrapeso traseiro (0,23m)' if contrapeso == 'Traseiro' else ''} = {formato_seguro(comprimento)}m")
    
    explicacoes.append(f"Altura: Informada pelo usuário = {formato_seguro(altura)}m")
    
    # Capacidade e tração
    explicacoes.append(f"{formato_negrito('Capacidade e Tração Cabine:')}")
    explicacoes.append(f"{'pessoas' if 'Passageiro' in modelo else 'kg'} {formato_seguro(capacidade_original)} "
                      f"{'* 80 kg' if 'Passageiro' in modelo else ''} = {formato_seguro(capacidade_cabine)} kg")
    explicacoes.append(f"(Capacidade Cabine / 2) + 500 = {formato_seguro(tracao_cabine)} kg")
    
    # Informações sobre painéis e chapas
    if isinstance(chapas_info, dict):
        explicacoes.append(f"{formato_negrito('Painéis Corpo Cabine:')}")
        explicacoes.append(f"Laterais: {chapas_info['num_paineis_lateral']} de "
                          f"{formato_seguro(chapas_info['largura_painel_lateral']*100)}cm "
                          f"(com dobras {formato_seguro((chapas_info['largura_painel_lateral']+0.085)*100)}cm), "
                          f"{formato_seguro(chapas_info['altura_painel_lateral'])}m altura")
        
        explicacoes.append(f"Fundo: {chapas_info['num_paineis_fundo']} de "
                          f"{formato_seguro(chapas_info['largura_painel_fundo']*100)}cm "
                          f"(com dobras {formato_seguro((chapas_info['largura_painel_fundo']+0.085)*100)}cm), "
                          f"{formato_seguro(chapas_info['altura_painel_fundo'])}m altura")
        
        explicacoes.append(f"Teto: {chapas_info['num_paineis_teto']} de "
                          f"{formato_seguro(chapas_info['largura_painel_teto']*100)}cm "
                          f"(com dobras {formato_seguro((chapas_info['largura_painel_teto']+0.085)*100)}cm), "
                          f"{formato_seguro(chapas_info['altura_painel_teto'])}m altura")
        
        explicacoes.append(f"{formato_negrito('Chapas Corpo Cabine:')}")
        explicacoes.append(f"Laterais e Teto: {chapas_info['num_chapalt']} chapas, "
                          f"sobra/chapa = {formato_seguro(chapas_info['sobra_chapalt']*100)} cm")
        explicacoes.append(f"Fundo: {chapas_info['num_chapaf']} chapas, "
                          f"sobra/chapa = {formato_seguro(chapas_info['sobra_chapaf']*100)} cm")
        explicacoes.append(f"Reserva: 2 chapas. Total: {chapas_info['num_chapatot']} chapas")
        
        explicacoes.append(f"{formato_negrito('Chapas Piso Cabine:')}")
        explicacoes.append(f"{chapas_info['num_chapa_piso']} chapa(s)")
    else:
        explicacoes.append(f"Erro no cálculo de chapas: {chapas_info}")
    
    # Junta tudo em uma string (com quebras de linha)
    explicacao_texto = "\n".join(explicacoes)
    
    # Montar o resultado
    dimensionamento = {
        "cab": {
            "altura": altura,
            "largura": largura,
            "compr": comprimento,
            "capacidade": capacidade_cabine,
            "tracao": tracao_cabine,
            "chp": {
                "corpo": chapas_info.get("num_chapatot", 0) if isinstance(chapas_info, dict) else 0,
                "piso": chapas_info.get("num_chapa_piso", 0) if isinstance(chapas_info, dict) else 0
            },
            "pnl": {
                "lateral": chapas_info.get("num_paineis_lateral", 0) if isinstance(chapas_info, dict) else 0,
                "fundo": chapas_info.get("num_paineis_fundo", 0) if isinstance(chapas_info, dict) else 0,
                "teto": chapas_info.get("num_paineis_teto", 0) if isinstance(chapas_info, dict) else 0
            }
        }
    }
    
    return dimensionamento, explicacao_texto

def calcular_componentes(dimensionamento, respostas):
    componentes = {}
    custos = {}
    custo_total = 0
    
    todos_custos = {custo.codigo: custo for custo in get_all_custos()}

    def adicionar_componente(codigo, quantidade, grupo, subgrupo, explicacao, nome_outro=None, valor_outro=None, comprimento=None):
        codigo_original = codigo
        contador = 1
        while codigo in componentes:
            if codigo == "INF":
                codigo = f"INF_{contador}"
            else:
                codigo = f"{codigo_original}_{contador}"
            contador += 1

        if codigo.startswith("INF"):
            if nome_outro and valor_outro:
                descricao = nome_outro
                custo_unitario = float(valor_outro)
                unidade = "un"
            else:
                return
        elif codigo_original in todos_custos:
            descricao = todos_custos[codigo_original].descricao
            custo_unitario = todos_custos[codigo_original].valor
            unidade = todos_custos[codigo_original].unidade
        else:
            return

        if comprimento is not None and unidade == "m":
            custo_total_item = quantidade * comprimento * custo_unitario
            quantidade_efetiva = quantidade * comprimento
        else:
            custo_total_item = quantidade * custo_unitario
            quantidade_efetiva = quantidade

        custos[codigo] = custo_total_item
        nonlocal custo_total
        custo_total += custo_total_item
        
        componentes[codigo] = {
            "codigo": codigo,
            "descricao": descricao,
            "quantidade": quantidade_efetiva,
            "unidade": unidade,
            "custo_unitario": custo_unitario,
            "custo_total": custo_total_item,
            "explicacao": explicacao,
            "grupo": grupo,
            "subgrupo": subgrupo
        }
 
    # Variáveis obtidas do dimensionamento e respostas
    #elevador
    comprimento_poco = float(respostas.get("Comprimento do Poço", 0))
    largura_poco = float(respostas.get("Largura do Poço", 0))
    altura_poco = float(respostas.get("Altura do Poço", 0))
    pavimentos = int(respostas.get("Pavimentos", 0))
    acionamento = respostas.get("Acionamento", "")
    tracao = respostas.get("Tração", "")
    contrapeso_posicao = respostas.get("Contrapeso", "")
    modelo_elevador = respostas.get("Modelo do Elevador", "")
    capacidade = dimensionamento['cab']['capacidade']
    tracao_cabine = dimensionamento['cab']['tracao']
    
    #cabine
    material = respostas.get("Material", "")
    espessura = respostas.get("Espessura", "")  
    piso_conta = respostas.get("Piso", "")
    tipo_piso = respostas.get("Material Piso Cabine", "")
    largura_cabine = dimensionamento['cab']['largura']
    altura_cabine = dimensionamento['cab']['altura']
    comprimento_cabine = dimensionamento['cab']['compr']

    #chapas e perfis
    qtd_chp_corpo = dimensionamento['cab']['chp']['corpo']
    qtd_chp_piso = dimensionamento['cab']['chp']['piso']

    # Grupo CABINE
    # Chapa Corpo Cabine
    if "Inox 304" in material:
        codigo_chapa = "CH03" if espessura == "1,2" else "CH04"
    elif "Inox 430" in material:
        codigo_chapa = "CH01" if espessura == "1,2" else "CH02"
    elif "Chapa Pintada" in material:
        codigo_chapa = "CH05" if espessura == "1,2" else "CH06"
    elif "Alumínio" in material:
        codigo_chapa = "CH07" if espessura == "1,2" else "CH08"
    elif material == "Outro":
        codigo_chapa = "INF"
    else:
        codigo_chapa = None

    if codigo_chapa:
        quantidade = qtd_chp_corpo
        explicacao = "Dim. chapas corpo cabine"
        if codigo_chapa == "INF":
            nome_outro = respostas.get("Material Outro Nome")
            valor_outro = respostas.get("Material Outro Valor")
            adicionar_componente(codigo_chapa, quantidade, "CABINE", "Chapas", explicacao, 
                                 nome_outro=nome_outro, valor_outro=valor_outro)
        else:
            adicionar_componente(codigo_chapa, quantidade, "CABINE", "Chapas", explicacao)

        if "Inox" in material or "Alumínio" in material:
            codigo_chapa_adicional = "CH50" if "Inox" in material else "CH51"
            quantidade = qtd_chp_corpo
            explicacao = f"Código adicional para cada chapa de {material}"
            adicionar_componente(codigo_chapa_adicional, quantidade, "CABINE", "Chapas", explicacao)

    # Parafusos
    explicacao = "13 * painéis laterais) + (2 * painéis de fundo) + (2 * painéis de teto)"
    qtd_parafusos = (13 * dimensionamento['cab']['pnl']['lateral'] + 
                     2 * dimensionamento['cab']['pnl']['fundo'] + 
                     2 * dimensionamento['cab']['pnl']['teto'])
    explicacao += f" = (13 * {dimensionamento['cab']['pnl']['lateral']}) + (2 * {dimensionamento['cab']['pnl']['fundo']}) + (2 * {dimensionamento['cab']['pnl']['teto']}) = {qtd_parafusos}"
    adicionar_componente("FE01", qtd_parafusos, "CABINE", "Chapas", explicacao)

    # Chapa Piso Cabine
    if piso_conta == "Por conta da empresa":
        if "Antiderrapante" in tipo_piso:
            codigo_chapa_piso = "CH09"
        elif tipo_piso == "Outro":
            codigo_chapa_piso = "INF"
        else:
            codigo_chapa = None
    else:
        codigo_chapa_piso = "CH10"

    if codigo_chapa_piso:
        quantidade = qtd_chp_piso
        explicacao = "Dim. chapas piso cabine"
        if codigo_chapa_piso == "INF":
            nome_outro = respostas.get("Material Piso Outro Nome")
            valor_outro = respostas.get("Material Piso Outro Valor")
            adicionar_componente(codigo_chapa_piso, quantidade, "CABINE", "Chapas Piso", explicacao, 
                                 nome_outro=nome_outro, valor_outro=valor_outro)
        else:
            adicionar_componente(codigo_chapa_piso, quantidade, "CABINE", "Chapas Piso", explicacao)

        # Parafusos para o piso
        explicacao = "13 por chapa de piso."
        qtd_parafusos = 13 * quantidade
        explicacao += f" = 13 * {quantidade} = {qtd_parafusos}"
        adicionar_componente("FE04", qtd_parafusos, "CABINE", "Chapas Piso", explicacao)

    # Grupo CARRINHO
    # Chassi
    # Travessa
    if capacidade <= 1000:
        codigo_travessa = "PE01"
    elif capacidade <= 1800:
        codigo_travessa = "PE02"
    else:
        codigo_travessa = "PE03"

    qtd_travessa = 4
    if capacidade > 2000:
        qtd_travessa += 4

    if codigo_travessa:
        quantidade = qtd_travessa
        comp_travessa = largura_cabine + 0.17 
        explicacao = (
            f"Quantidade base de 4 unidades, +4 se capacidade > 2000kg. Comprimento = largura da cabine + 0,17m. "
            f"Tipo selecionado com base na capacidade do elevador."
        )
        adicionar_componente(codigo_travessa, quantidade, "CARRINHO", "Chassi", explicacao, comprimento=comp_travessa)

    # Longarina
    if capacidade <= 1500:
        codigo_longarina = "PE04"
    elif capacidade <= 2000:
        codigo_longarina = "PE05"
    else:
        codigo_longarina = "PE06"

    qtd_longarina = 2
    if codigo_longarina:
        quantidade = qtd_longarina
        explicacao = (
            f"2 unidades fixas. Comprimento = altura da cabine + 0,70m. "
            f"Tipo selecionado com base na capacidade do elevador."
        )
        comp_longarina = altura_cabine + 0.70 
        adicionar_componente(codigo_longarina, quantidade, "CARRINHO", "Chassi", explicacao, comprimento=comp_longarina)
    
    # Parafusos para chassi
    qtd_parafusos = 65
    explicacao = "Quantidade fixa de 65 unidades para montagem do chassi"
    adicionar_componente("FE02", qtd_parafusos, "CARRINHO", "Chassi", explicacao)

    # Plataforma
    # Perfis externos
    if capacidade <= 1000:
        codigo_perfil_externo = "PE07"
    elif capacidade <= 1800:
        codigo_perfil_externo = "PE08"
    else:
        codigo_perfil_externo = "PE09"

    qtd_perfil_externo = 2

    if codigo_perfil_externo:
        quantidade = qtd_perfil_externo
        comp_perfil_externo = largura_cabine
        explicacao = (
            f"2 unidades com comprimento igual à largura da cabine."
            f"Tipo selecionado com base na capacidade do elevador"
        )
        adicionar_componente(codigo_perfil_externo, quantidade, "CARRINHO", "Plataforma", explicacao, comprimento=comp_perfil_externo)

    if codigo_perfil_externo:
        quantidade = qtd_perfil_externo
        comp_perfil_externo = comprimento_cabine
        explicacao = (
            f"2 unidades com comprimento igual ao comprimento da cabine."
            f"Tipo selecionado com base na capacidade do elevador"
        )
        adicionar_componente(codigo_perfil_externo, quantidade, "CARRINHO", "Plataforma", explicacao, comprimento=comp_perfil_externo)

    # Perfis internos
    if capacidade <= 1000:
        codigo_perfil_interno = "PE10"
    elif capacidade <= 1800:
        codigo_perfil_interno = "PE11"
    else:
        codigo_perfil_interno = "PE12"

    qtd_perfil_interno = round(largura_cabine / 0.35)  # 35 cm = 0.35 m
    if codigo_perfil_interno:
        quantidade = qtd_perfil_interno
        comp_perfil_interno = comprimento_cabine
        explicacao = "Quantidade = largura da cabine / 0,35m (arredondado)."
        qtd_perfil_interno = round(largura_cabine / 0.35)
        explicacao += f" = round({largura_cabine} / 0,35) = {qtd_perfil_interno}"
        adicionar_componente(codigo_perfil_interno, qtd_perfil_interno, "CARRINHO", "Plataforma", explicacao, comprimento=comp_perfil_interno)

    # Parafusos para plataforma
    explicacao = "24 unidades base + (4 * número de perfis internos)."
    qtd_parafusos_plataforma = 24 + (4 * qtd_perfil_interno)
    explicacao += f" = 24 + (4 * {qtd_perfil_interno}) = {qtd_parafusos_plataforma}"
    adicionar_componente("FE02", qtd_parafusos_plataforma, "CARRINHO", "Plataforma", explicacao)
    
    
    # Barra Roscada
    comprimento_barra = (comprimento_cabine / 2) / 0.60
    qtd_barras_necessarias = 4
    comprimento_total = comprimento_barra * qtd_barras_necessarias
    qtd_barras_compradas = math.ceil(comprimento_total / 3)  # Arredonda para cima

    explicacao = (f"Comprimento da barra = (comprimento_cabine / 2) / 0.60 = {comprimento_barra:.2f}m. "
                  f"4 barras necessárias, comprimento total = {comprimento_total:.2f}m. "
                  f"Barras compradas (3m cada): {qtd_barras_compradas}")
    adicionar_componente("PE25", qtd_barras_compradas, "CARRINHO", "Barra Roscada", explicacao)

    # Parafusos para barra roscada
    explicacao = "4 parafusos por barra, 16 no total"
    adicionar_componente("FE01", 16, "CARRINHO", "Barra Roscada", explicacao)
    adicionar_componente("FE02", 16, "CARRINHO", "Barra Roscada", explicacao)

    # Suportes para barra roscada
    explicacao = "1 suporte por barra, 4 no total"
    adicionar_componente("PE26", 4, "CARRINHO", "Barra Roscada", explicacao)
    adicionar_componente("PE27", 4, "CARRINHO", "Barra Roscada", explicacao)
    
    # Grupo TRACAO
    # Acionamento
    if acionamento.lower() == "hidráulico":
        quantidade = 1
        explicacao = "1 unidade se o acionamento for hidráulico"
        adicionar_componente("MO01", quantidade, "TRACAO", "Acionamento", explicacao)

    # Tracionamento
    if acionamento.lower() == "motor":

        # Polia (PE13)
        qtd_polias = 0
        if tracao == "2x1":
            qtd_polias = 1
            if largura_cabine > 2:
                qtd_polias = 2

        if qtd_polias > 0:
            quantidade = qtd_polias
            explicacao = "1 unidade se tração 2x1, 2 unidades se tração 2x1 e largura da cabine > 2m"
            adicionar_componente("PE13", quantidade, "TRACAO", "Tracionamento", explicacao)

        # Cabo de aço (PE14)
        explicacao = "Comprimento do poço (2x se tração 2x1) + 5m adicionais. "
        comp_cabo = comprimento_poco
        if tracao == "2x1":
            comp_cabo = 2 * comprimento_poco
            explicacao += "2 * comprimento_poco + 5"
        else:
            explicacao += "comprimento_poco + 5"
        comp_cabo += 5
        explicacao += f" = {'2 * ' if tracao == '2x1' else ''}{comprimento_poco} + 5 = {comp_cabo}"
        adicionar_componente("PE14", comp_cabo, "TRACAO", "Tracionamento", explicacao)

        # Travessa da polia (PE15)
        if qtd_polias > 1:
            quantidade = 1
            comp_travessa = largura_cabine / 2
            explicacao = "1 unidade se houver 2 polias. Comprimento = largura da cabine / 2"
            adicionar_componente("PE15", quantidade, "TRACAO", "Tracionamento", explicacao, comprimento=comp_travessa)

        # Contrapeso
        contrapeso_tipo = None
        if contrapeso_posicao == "Lateral":
            if comprimento_poco < 1.90:
                contrapeso_tipo = "PE16" if tracao_cabine <= 1000 else "PE17"
            else:
                contrapeso_tipo = "PE18"
        elif contrapeso_posicao == "Traseiro":
            if largura_poco < 1.90:
                contrapeso_tipo = "PE16" if tracao_cabine <= 1000 else "PE17"
            else:
                contrapeso_tipo = "PE18"

        if contrapeso_tipo:
            quantidade = 1
            explicacao = "Tipo selecionado com base na posição do contrapeso, dimensões do poço e tração da cabine"
            adicionar_componente(contrapeso_tipo, quantidade, "TRACAO", "Contrapeso", explicacao)
        
        # Pedra
        if contrapeso_tipo in ["PE16", "PE17"]:
            pedra_tipo = "PE19"
            explicacao = "Quantidade = tração da cabine / 45 (para PE16/PE17). "
            qtd_pedras = int(tracao_cabine / 45)
            explicacao += f" = int({tracao_cabine} / 45) = {qtd_pedras}"
        else:
            pedra_tipo = "PE20"
            explicacao = "Quantidade = tração da cabine / 75 (para PE18). "
            qtd_pedras = int(tracao_cabine / 75)
            explicacao += f" = int({tracao_cabine} / 75) = {qtd_pedras}"

        if pedra_tipo:
            adicionar_componente(pedra_tipo, qtd_pedras, "TRACAO", "Contrapeso", explicacao)
        
        # Guias
        explicacao = "Quantidade = (altura do poço / 5) * 2, arredondado. "
        qtd_guia_elevador = round(altura_poco / 5 * 2)
        explicacao += f" = round(({altura_poco} / 5) * 2) = {qtd_guia_elevador}"
        adicionar_componente("PE21", qtd_guia_elevador, "TRACAO", "Guia", explicacao)

        explicacao = "Quantidade = (altura do poço / 5) * 2, arredondado. "
        qtd_suporte_guia = round(altura_poco / 5 * 2)
        explicacao += f" = round(({altura_poco} / 5) * 2) = {qtd_suporte_guia}"
        adicionar_componente("PE22", qtd_suporte_guia, "TRACAO", "Guia", explicacao)

        if contrapeso_tipo:
            explicacao = "Quantidade = (altura do poço / 5) * 2, arredondado. "
            qtd_guia_contrapeso = round(altura_poco / 5 * 2)
            explicacao += f" = round(({altura_poco} / 5) * 2) = {qtd_guia_contrapeso}"
            adicionar_componente("PE23", qtd_guia_contrapeso, "TRACAO", "Guia", explicacao)

            explicacao = "Quantidade = 4 + (número de pavimentos * 2). "
            qtd_suporte_guia_contrapeso = 4 + pavimentos * 2
            explicacao += f" = 4 + ({pavimentos} * 2) = {qtd_suporte_guia_contrapeso}"
            adicionar_componente("PE24", qtd_suporte_guia_contrapeso, "TRACAO", "Guia", explicacao)
    
    # Grupo SISTEMAS COMPLEMENTARES
    # Iluminação
    explicacao = "2 lâmpadas LED se comprimento da cabine <= 1,80m, senão 4 lâmpadas. "
    qtd_lampadas = 2 if comprimento_cabine <= 1.80 else 4
    explicacao += f" = {qtd_lampadas} (comprimento_cabine = {comprimento_cabine})"
    adicionar_componente("CC01", qtd_lampadas, "SIST. COMPLEMENTARES", "Iluminação", explicacao)

    # Ventilação
    qtd_ventiladores = 1 if "Passageiro" in modelo_elevador else 0
    if qtd_ventiladores > 0:
        explicacao = "1 ventilador se o elevador for do tipo passageiro, senão 0"
        adicionar_componente("CC02", qtd_ventiladores, "SIST. COMPLEMENTARES", "Ventilação", explicacao)

    return componentes, custos, custo_total, todos_custos

# SUBROTINAS

def calcular_largura_painel(dimensao):
    """Calcula a largura ideal do painel, entre 25 e 33 cm, não excedendo 40 cm com as dobras."""
    for divisoes in range(10, 1, -1):  # Começamos com 10 divisões e vamos até 2
        largura_base = dimensao / divisoes
        if .25 <= largura_base <= .33 and largura_base + .085 <= .40:
            return largura_base, divisoes
    return None, None  # Retorna None se nenhuma divisão for adequada

def calcular_chapas_cabine(altura, largura, comprimento):
    """Calcula o número de chapas e painéis necessários para a cabine do elevador."""
    # Dimensões da Chapa de Aço Bruta
    chapa_largura = 1.20
    chapa_comprimento = 3.00

    # Cálculo para as paredes laterais
    largura_painel_lateral, num_paineis_lateral = calcular_largura_painel(comprimento)
    if largura_painel_lateral is None:
        return "Erro: Não foi possível calcular uma largura de painel adequada para as laterais."
    
    # Cálculo para a parede do fundo
    largura_painel_fundo, num_paineis_fundo = calcular_largura_painel(largura)
    if largura_painel_fundo is None:
        return "Erro: Não foi possível calcular uma largura de painel adequada para o fundo."

    # Ajustes para o número total de painéis
    num_paineis_lateral *= 2  # Duas laterais
    num_paineis_teto = num_paineis_lateral // 2

    # Cálculo do número de Chapas de Aço Brutas (CAB) necessárias
    paineis_por_chapa_lt = math.floor(chapa_largura / (largura_painel_lateral + 0.085))
    paineis_por_chapa_f = math.floor(chapa_largura / (largura_painel_fundo + 0.085))

    num_chapalt = math.ceil((num_paineis_lateral + num_paineis_teto) / paineis_por_chapa_lt)
    num_chapaf = math.ceil(num_paineis_fundo / paineis_por_chapa_f)

    # Cálculo das chapas do piso
    area_piso = largura * comprimento
    area_chapa = chapa_largura * chapa_comprimento
    num_chapapiso = math.ceil(area_piso / area_chapa)

    # Cálculo da sobra da chapa do piso
    area_utilizada_piso = area_piso
    sobra_chapapiso = (num_chapapiso * area_chapa) - area_utilizada_piso

    num_chapamargem = 2
    num_chapatot = num_chapalt + num_chapaf + num_chapamargem

    # Cálculo das sobras
    sobra_chapalt = (0.40 - (largura_painel_lateral + 0.085)) * num_chapalt
    sobra_chapaf = (0.40 - (largura_painel_fundo + 0.085)) * num_chapaf

    return {
        "num_paineis_lateral": num_paineis_lateral,
        "largura_painel_lateral": largura_painel_lateral,
        "altura_painel_lateral": altura,
        "num_paineis_fundo": num_paineis_fundo,
        "largura_painel_fundo": largura_painel_fundo,
        "altura_painel_fundo": altura,
        "num_paineis_teto": num_paineis_teto,
        "largura_painel_teto": largura_painel_lateral,
        "altura_painel_teto": largura,
        "num_chapalt": num_chapalt,
        "sobra_chapalt": sobra_chapalt,
        "num_chapaf": num_chapaf,
        "sobra_chapaf": sobra_chapaf,
        "num_chapa_piso": num_chapapiso,
        "sobra_chapapiso": sobra_chapapiso,
        "num_chapatot": num_chapatot
    }

def calcular_formacao_preco(custo_total, tipo_faturamento="Elevadores"):
    """
    Calcula a formação de preço com base no custo total e parâmetros do banco de dados
    
    Args:
        custo_total (float): O custo total de produção
        tipo_faturamento (str): O tipo de faturamento (Elevadores, Fuza, Manutenção)
        
    Returns:
        dict: Um dicionário contendo todos os componentes da formação de preço
    """
    from ..models import Parametro
    
    # Buscar parâmetros do banco de dados
    parametros = {param.parametro: param.valor for param in Parametro.objects.all()}
    
    # Mapeamento para chaves no banco de dados
    mapeamento_chaves = {
        'Elevadores': 'fat.Elevadores',
        'Fuza': 'fat.Fuza',
        'Manutenção': 'fat.Manutenção',
    }
    
    # Percentuais dos parâmetros
    percentual_comissao = parametros.get('comissao', 0)  
    percentual_margem = parametros.get('margem', 0)      
    
    # Busca a chave exata no mapeamento ou usa o valor padrão
    chave_imposto = mapeamento_chaves.get(tipo_faturamento, 'fat.Elevadores')
    
    percentual_impostos = parametros.get(chave_imposto, 0)
    
    # Alçada de desconto
    alcada_desconto = parametros.get('desc.alcada1', 0)  
    
    # Criar a instância de FormacaoPreco com os parâmetros obtidos
    formacao = FormacaoPreco(
        custo_producao=custo_total,
        percentual_margem=percentual_margem,
        percentual_comissao=percentual_comissao,
        percentual_impostos=percentual_impostos
    )
    
    # Retornar o modelo formatado para exibição
    resultado = formacao.get_display_model()
    
    # Adicionar a alçada de desconto
    resultado['alcada_desconto'] = alcada_desconto
    
    return resultado


def recalcular_com_desconto(formacao_preco, preco_final_sem_impostos):
    """
    Recalcula a formação de preço baseado em um preço final ajustado (sem impostos)
    
    Args:
        formacao_preco (dict): Formação de preço original
        preco_final_sem_impostos (float): Novo preço final sem impostos
        
    Returns:
        dict: Formação de preço atualizada
    """
    # Criar uma nova instância de FormacaoPreco com os valores atuais
    formacao = FormacaoPreco(
        custo_producao=formacao_preco['custo_producao'],
        percentual_margem=formacao_preco['percentual_margem'],
        percentual_comissao=formacao_preco['percentual_comissao'],
        percentual_impostos=formacao_preco['percentual_impostos']
    )
    
    # Definir o novo preço sem impostos
    formacao.definir_preco_sem_impostos(preco_final_sem_impostos)
    
    # Obter o modelo atualizado
    nova_formacao = formacao.get_display_model()
    
    # Incluir a alçada de desconto se existir no original
    if 'alcada_desconto' in formacao_preco:
        nova_formacao['alcada_desconto'] = formacao_preco['alcada_desconto']
    
    return nova_formacao