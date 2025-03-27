class FormacaoPreco:
    def __init__(self, custo_producao, percentual_margem=30.0, percentual_comissao=3.0, 
                 percentual_impostos=10.0, valor_desconto=0.0):
        self.custo_producao = custo_producao
        self.percentual_margem = percentual_margem
        self.percentual_comissao = percentual_comissao
        self.percentual_impostos = percentual_impostos
        self.valor_desconto = valor_desconto
        self.preco_sem_impostos_solicitado = None

    @property
    def valor_margem(self):
        return self.custo_producao * (self.percentual_margem / 100)

    @property
    def preco_com_margem(self):
        return self.custo_producao + self.valor_margem

    @property
    def base_calculo_comissao(self):
        """Base para cálculo da comissão: preço com margem menos desconto"""
        if self.preco_sem_impostos_solicitado:
            # Se tiver preço solicitado, a base de cálculo deve ser recalculada
            # para manter a comissão proporcional ao valor final
            return self.preco_sem_impostos_solicitado / (1 + self.percentual_comissao / 100)
        return self.preco_com_margem - self.valor_desconto

    @property
    def valor_comissao(self):
        return self.base_calculo_comissao * (self.percentual_comissao / 100)

    @property
    def preco_sem_impostos(self):
        """Preço sem impostos: base de cálculo + comissão"""
        if self.preco_sem_impostos_solicitado:
            return self.preco_sem_impostos_solicitado
        return self.base_calculo_comissao + self.valor_comissao

    @property
    def valor_impostos(self):
        return self.preco_sem_impostos * (self.percentual_impostos / 100)

    @property
    def preco_com_impostos(self):
        return self.preco_sem_impostos + self.valor_impostos

    @property
    def percentual_desconto_real(self):
        """Calcula o percentual real de desconto"""
        if self.preco_sem_impostos_solicitado:
            # Qual seria o preço sem impostos sem desconto
            preco_sem_desconto = self.custo_producao + self.valor_margem + self.valor_comissao
            
            # Calculamos o desconto real
            desconto_real = preco_sem_desconto - self.preco_sem_impostos_solicitado
            
            # Retorna como percentual
            if preco_sem_desconto == 0:
                return 0.0
            return (desconto_real / preco_sem_desconto) * 100
        else:
            # Se não houver preço solicitado, usamos o desconto original
            preco_sem_desconto = self.custo_producao + self.valor_margem
            if preco_sem_desconto == 0:
                return 0.0
            return (self.valor_desconto / preco_sem_desconto) * 100

    def definir_preco_sem_impostos(self, preco):
        """Define um novo preço sem impostos solicitado"""
        self.preco_sem_impostos_solicitado = preco

    def definir_desconto(self, valor_desconto):
        """Define um valor de desconto"""
        self.valor_desconto = valor_desconto
        # Limpa o preço solicitado, pois vamos calcular com base no desconto
        self.preco_sem_impostos_solicitado = None

    def get_display_model(self):
        """Retorna um dicionário com os valores formatados para exibição"""
        return {
            'custo_producao': self.custo_producao,
            'percentual_margem': self.percentual_margem,
            'valor_margem': self.valor_margem,
            'percentual_desconto': self.percentual_desconto_real,
            'valor_desconto': self.valor_desconto if not self.preco_sem_impostos_solicitado else 
                               (self.custo_producao + self.valor_margem + self.valor_comissao - self.preco_sem_impostos_solicitado),
            'base_calculo_comissao': self.base_calculo_comissao,
            'percentual_comissao': self.percentual_comissao,
            'valor_comissao': self.valor_comissao,
            'preco_sem_impostos': self.preco_sem_impostos,
            'percentual_impostos': self.percentual_impostos,
            'valor_impostos': self.valor_impostos,
            'preco_com_impostos': self.preco_com_impostos
        }

    def get_formatted_output(self):
        """Retorna um texto formatado para exibição dos valores de formação de preço"""
        model = self.get_display_model()
        
        # Formatação de números em estilo brasileiro (com vírgula)
        def fmt_valor(valor):
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Formatação para percentuais (1 casa decimal)
        def fmt_perc(percentual):
            return f"{percentual:.1f}%"
        
        linhas = [
            f"*Custo de produção*                                                {fmt_valor(model['custo_producao'])}",
            f"Margem ({fmt_perc(model['percentual_margem'])})                                                     {fmt_valor(model['valor_margem'])}",
            f"Desconto ({fmt_perc(model['percentual_desconto'])})                                                   -{fmt_valor(model['valor_desconto'])}",
            f"Base Cálculo Comissão                                             {fmt_valor(model['base_calculo_comissao'])}",
            f"Comissão ({fmt_perc(model['percentual_comissao'])})                                                        {fmt_valor(model['valor_comissao'])}",
            f"**Preço sem impostos**                                               **{fmt_valor(model['preco_sem_impostos'])}**",
            f"Impostos ({fmt_perc(model['percentual_impostos'])})                                                      {fmt_valor(model['valor_impostos'])}",
            f"**Preço com impostos**                                      **{fmt_valor(model['preco_com_impostos'])}**"
        ]
        
        return "\n".join(linhas)