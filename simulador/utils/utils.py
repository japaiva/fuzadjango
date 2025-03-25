import math
import bcrypt

def get_all_custos():
    """Função temporária para evitar importação circular"""
    return []

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def valida_campos(nome_cliente: str) -> bool:
    """Valida se um campo não está vazio."""
    return bool(nome_cliente.strip())

def formatar_demanda_placas(chapas_info): 
    paineis_texto = ( 
        f"**Painéis Corpo Cabine**:\n" 
        f"Laterais: {chapas_info['num_paineis_lateral']} de " 
        f"{chapas_info['largura_painel_lateral']*100:.2f}cm (com dobras " 
        f"{(chapas_info['largura_painel_lateral']+0.085)*100:.2f}cm), " 
        f"{chapas_info['altura_painel_lateral']:.2f}m altura; " 
        f"Fundo: {chapas_info['num_paineis_fundo']} de " 
        f"{chapas_info['largura_painel_fundo']*100:.2f}cm (com dobras " 
        f"{(chapas_info['largura_painel_fundo']+0.085)*100:.2f}cm), " 
        f"{chapas_info['altura_painel_fundo']:.2f}m altura; " 
        f"Teto: {chapas_info['num_paineis_teto']} de " 
        f"{chapas_info['largura_painel_teto']*100:.2f}cm (com dobras " 
        f"{(chapas_info['largura_painel_teto']+0.085)*100:.2f}cm), " 
        f"{chapas_info['altura_painel_teto']:.2f}m altura.\n" 
    )
    
    chapas_texto = (
        f"**Chapas Corpo Cabine**:\n"
        f"Laterais e Teto: {chapas_info['num_chapalt']:.0f} chapas, "
        f"sobra/chapa={chapas_info['sobra_chapalt']*100:.2f}cm,\n"
        f"Fundo: {chapas_info['num_chapaf']:.0f} chapas, "
        f"sobra/chapa={chapas_info['sobra_chapaf']*100:.2f}cm,\n"
        f"**Total Chapas (com margem): {chapas_info['num_chapatot']:.0f}**\n\n"
        f"**Chapas Piso Cabine**:{chapas_info['num_chapa_piso']:.0f} chapa(s).\n"
    )

    chapas_texto = (
        f"**Chapas Corpo Cabine**:\n"
        f"Laterais e Teto: {chapas_info['num_chapalt']:.0f} chapas, "
        f"sobra/chapa = {chapas_info['sobra_chapalt']*100:.2f} cm,\n"
        f"Fundo: {chapas_info['num_chapaf']:.0f} chapas, "
        f"sobra/chapa = {chapas_info['sobra_chapaf']*100:.2f} cm,\n"
        f"Reserva: 2 chapas.\n"
        f"Total: {chapas_info['num_chapatot']:.0f} chapas.\n\n"
        f"**Chapas Piso Cabine**:{chapas_info['num_chapa_piso']:.0f} chapa(s).\n"
)

    return f"{paineis_texto}\n{chapas_texto}"

def agrupar_respostas_por_pagina(respostas):
    """Agrupa as respostas de acordo com cada página, para exibir no resumo."""

    def get_unidade(campo, valor, modelo):
        unidades = {
            "Capacidade": "pessoas" if "passageiro" in modelo.lower() else "kg",
            "Pavimentos": "",
            "Altura do Poço": "m",
            "Largura do Poço": "m",
            "Comprimento do Poço": "m",
            "Altura da Cabine": "m",
            "Espessura": "mm",
            "Altura Porta": "m",
            "Largura Porta": "m",
            "Altura Porta Pavimento": "m",
            "Largura Porta Pavimento": "m"
        }
        return unidades.get(campo, "")

    paginas = {
        "Cliente": ["Solicitante", "Empresa", "Telefone", "Email", "Faturado por"],  # Adicionado "Faturado por"
        "Elevador": [
            "Modelo do Elevador", "Capacidade", "Acionamento", "Tração", "Contrapeso",
            "Largura do Poço", "Comprimento do Poço", "Altura do Poço", "Pavimentos"
        ],
        "Portas": [  # Seção unificada para portas de cabine e pavimento
            "Modelo Porta", "Material Porta", "Folhas Porta", "Altura Porta", "Largura Porta",
            "Modelo Porta Pavimento", "Material Porta Pavimento", "Folhas Porta Pavimento",
            "Altura Porta Pavimento", "Largura Porta Pavimento"
        ],
        "Cabine": [
            "Material", "Tipo de Inox", "Espessura", "Saída", "Altura da Cabine",
            "Piso", "Material Piso Cabine"
        ]
    }

    modelo_elevador = respostas.get("Modelo do Elevador", "").lower()

    respostas_agrupadas = {}
    for pagina, campos in paginas.items():
        dados_pagina = {}
        for campo in campos:
            if campo in respostas:
                valor = respostas[campo]

                # Formatação de materiais personalizados (Outro)
                if campo in ["Material", "Material Porta", "Material Porta Pavimento"] and valor == "Outro":
                    outro_nome = respostas.get(f"{campo} Outro Nome", "")
                    outro_valor = respostas.get(f"{campo} Outro Valor", "")
                elif campo == "Material Piso Cabine" and valor == "Outro":
                    outro_nome = respostas.get("Material Piso Outro Nome", "")
                    outro_valor = respostas.get("Material Piso Outro Valor", "")
                else:
                    outro_nome, outro_valor = "", ""

                if valor == "Outro" and (outro_nome or outro_valor):
                    try:
                        outro_valor_float = float(outro_valor)
                        outro_valor_formatado = f"{outro_valor_float:,.2f}"
                        outro_valor_formatado = outro_valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")
                    except Exception:
                        outro_valor_formatado = outro_valor
                    valor = f"Outro ({outro_nome} - {outro_valor_formatado})"

                unidade = get_unidade(campo, valor, modelo_elevador)
                if unidade:
                    valor = f"{valor} {unidade}"

                dados_pagina[campo] = valor

        if dados_pagina:
            respostas_agrupadas[pagina] = dados_pagina

    return respostas_agrupadas