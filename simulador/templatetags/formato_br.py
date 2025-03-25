from django import template

register = template.Library()

@register.filter
def formato_br(valor):
    """
    Formata um número para o padrão brasileiro (1.234,56)
    """
    try:
        # Verificar se é um número
        numero = float(valor)
        # Formatar com vírgula como decimal e ponto como separador de milhar
        valor_formatado = f"{numero:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return valor_formatado
    except (ValueError, TypeError):
        # Se não for um número, retorna o valor original
        return valor