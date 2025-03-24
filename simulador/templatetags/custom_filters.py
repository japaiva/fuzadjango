from django import template

register = template.Library()

@register.filter
def format_br(value):
    try:
        # Formata o número com duas casas decimais e separadores
        return "{:,.2f}".format(float(value)).replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return value