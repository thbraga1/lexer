class No:
    """Classe base para nós da árvore sintática"""
    pass

class NoPrograma(No):
    def __init__(self, funcoes):
        self.funcoes = funcoes
    
    def __str__(self):
        return f"Programa({len(self.funcoes)} funções)"

class NoFuncao(No):
    def __init__(self, tipo_retorno, nome, parametros, corpo):
        self.tipo_retorno = tipo_retorno
        self.nome = nome
        self.parametros = parametros
        self.corpo = corpo
    
    def __str__(self):
        return f"Função({self.tipo_retorno} {self.nome})"

class NoParametro(No):
    def __init__(self, tipo, nome):
        self.tipo = tipo
        self.nome = nome
    
    def __str__(self):
        return f"Parâmetro({self.tipo} {self.nome})"

class NoBloco(No):
    def __init__(self, comandos):
        self.comandos = comandos
    
    def __str__(self):
        return f"Bloco({len(self.comandos)} comandos)"

class NoDeclaracao(No):
    def __init__(self, tipo, nome, valor=None):
        self.tipo = tipo
        self.nome = nome
        self.valor = valor
    
    def __str__(self):
        return f"Declaração({self.tipo} {self.nome})"

class NoAtribuicao(No):
    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor
    
    def __str__(self):
        return f"Atribuição({self.nome} = ...)"

class NoRetorno(No):
    def __init__(self, valor):
        self.valor = valor
    
    def __str__(self):
        return "Retorno(...)"

class NoSe(No):
    def __init__(self, condicao, bloco_se, bloco_senao=None):
        self.condicao = condicao
        self.bloco_se = bloco_se
        self.bloco_senao = bloco_senao
    
    def __str__(self):
        return "Se(...)"

class NoEnquanto(No):
    def __init__(self, condicao, bloco):
        self.condicao = condicao
        self.bloco = bloco
    
    def __str__(self):
        return "Enquanto(...)"

class NoPara(No):
    def __init__(self, inicializacao, condicao, incremento, bloco):
        self.inicializacao = inicializacao
        self.condicao = condicao
        self.incremento = incremento
        self.bloco = bloco
    
    def __str__(self):
        return "Para(...)"

class NoExpressao(No):
    def __init__(self, operador, esquerda, direita=None):
        self.operador = operador
        self.esquerda = esquerda
        self.direita = direita
    
    def __str__(self):
        if self.direita:
            return f"Expressão({self.esquerda} {self.operador} {self.direita})"
        return f"Expressão({self.operador} {self.esquerda})"

class NoNumero(No):
    def __init__(self, valor):
        self.valor = valor
    
    def __str__(self):
        return f"Número({self.valor})"

class NoIdentificador(No):
    def __init__(self, nome):
        self.nome = nome
    
    def __str__(self):
        return f"ID({self.nome})"

class NoChamadaFuncao(No):
    def __init__(self, nome, argumentos):
        self.nome = nome
        self.argumentos = argumentos
    
    def __str__(self):
        return f"Chamada({self.nome})"

class ErroSintatico(Exception):
    def __init__(self, mensagem, token=None):
        self.mensagem = mensagem
        self.token = token
        super().__init__(mensagem)

class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0
        self.token_atual = self.tokens[0] if tokens else None
    
    def erro(self, mensagem):
        if self.token_atual:
            raise ErroSintatico(
                f"Erro sintático na linha {self.token_atual.linha}, coluna {self.token_atual.coluna}: {mensagem}. "
                f"Token encontrado: {self.token_atual.tipo} '{self.token_atual.valor}'",
                self.token_atual
            )
        else:
            raise ErroSintatico(f"Erro sintático: {mensagem}")
    
    def avancar(self):
        """Avança para o próximo token"""
        if self.posicao < len(self.tokens) - 1:
            self.posicao += 1
            self.token_atual = self.tokens[self.posicao]
        return self.token_atual
    
    def consumir(self, tipo_esperado):
        """Consome um token do tipo esperado"""
        if self.token_atual.tipo != tipo_esperado:
            self.erro(f"Esperado '{tipo_esperado}', encontrado '{self.token_atual.tipo}'")
        
        token = self.token_atual
        self.avancar()
        return token
    
    def verificar(self, tipo):
        """Verifica se o token atual é do tipo especificado"""
        return self.token_atual.tipo == tipo
    
    def analisar(self):
        """Ponto de entrada da análise sintática"""
        try:
            programa = self.programa()
            if not self.verificar('EOF'):
                self.erro("Código após o fim do programa")
            return programa
        except ErroSintatico as e:
            print(f"ERRO SINTÁTICO: {e.mensagem}")
            return None
    
    def programa(self):
        """programa -> funcao+"""
        funcoes = []
        
        while not self.verificar('EOF'):
            funcao = self.funcao()
            funcoes.append(funcao)
        
        return NoPrograma(funcoes)
    
    def funcao(self):
        """funcao -> tipo ID '(' parametros? ')' bloco"""
        tipo_retorno = self.tipo()
        nome = self.consumir('ID')
        
        self.consumir('DELIM_AP')  # '('
        
        parametros = []
        if not self.verificar('DELIM_FP'):  # se não é ')'
            parametros = self.parametros()
        
        self.consumir('DELIM_FP')  # ')'
        corpo = self.bloco()
        
        return NoFuncao(tipo_retorno.valor, nome.valor, parametros, corpo)
    
    def parametros(self):
        """parametros -> parametro (',' parametro)*"""
        params = []
        params.append(self.parametro())
        
        while self.verificar('VIRGULA'):
            self.consumir('VIRGULA')
            params.append(self.parametro())
        
        return params
    
    def parametro(self):
        """parametro -> tipo ID"""
        tipo = self.tipo()
        nome = self.consumir('ID')
        return NoParametro(tipo.valor, nome.valor)
    
    def tipo(self):
        """tipo -> 'int' | 'float'"""
        if self.verificar('TIPO_INT'):
            return self.consumir('TIPO_INT')
        elif self.verificar('TIPO_FLOAT'):
            return self.consumir('TIPO_FLOAT')
        else:
            self.erro("Esperado tipo (int ou float)")
    
    def bloco(self):
        """bloco -> '{' comando* '}'"""
        self.consumir('DELIM_AC')  # '{'
        
        comandos = []
        while not self.verificar('DELIM_FC'):  # enquanto não é '}'
            comando = self.comando()
            comandos.append(comando)
        
        self.consumir('DELIM_FC')  # '}'
        return NoBloco(comandos)
    
    def comando(self):
        """
        comando -> declaracao ';' 
                | atribuicao ';'
                | retorno ';'
                | se
                | enquanto
                | para
                | expressao ';'
        """
        if self.verificar('TIPO_INT') or self.verificar('TIPO_FLOAT'):
            cmd = self.declaracao()
            self.consumir('PONTO_VIRGULA')
            return cmd
        elif self.verificar('RETORNO'):
            cmd = self.retorno()
            self.consumir('PONTO_VIRGULA')
            return cmd
        elif self.verificar('SE'):
            return self.se()
        elif self.verificar('ENQUANTO'):
            return self.enquanto()
        elif self.verificar('PARA'):
            return self.para()
        elif self.verificar('ID'):
            # Pode ser atribuição ou expressão
            # Salvamos a posição para backtrack se necessário
            pos_atual = self.posicao
            try:
                # Tenta analisar como atribuição
                nome = self.consumir('ID')
                if self.verificar('OPERADOR_ATRIB'):
                    self.consumir('OPERADOR_ATRIB')
                    valor = self.expressao()
                    self.consumir('PONTO_VIRGULA')
                    return NoAtribuicao(nome.valor, valor)
                else:
                    # Volta e trata como expressão
                    self.posicao = pos_atual
                    self.token_atual = self.tokens[self.posicao]
                    expr = self.expressao()
                    self.consumir('PONTO_VIRGULA')
                    return expr
            except:
                # Se der erro, volta e tenta como expressão
                self.posicao = pos_atual
                self.token_atual = self.tokens[self.posicao]
                expr = self.expressao()
                self.consumir('PONTO_VIRGULA')
                return expr
        else:
            # Tenta como expressão
            expr = self.expressao()
            self.consumir('PONTO_VIRGULA')
            return expr
    
    def declaracao(self):
        """declaracao -> tipo ID ('=' expressao)?"""
        tipo = self.tipo()
        nome = self.consumir('ID')
        
        valor = None
        if self.verificar('OPERADOR_ATRIB'):
            self.consumir('OPERADOR_ATRIB')
            valor = self.expressao()
        
        return NoDeclaracao(tipo.valor, nome.valor, valor)
    
    def retorno(self):
        """retorno -> 'return' expressao"""
        self.consumir('RETORNO')
        valor = self.expressao()
        return NoRetorno(valor)
    
    def se(self):
        """se -> 'if' '(' expressao ')' bloco ('else' bloco)?"""
        self.consumir('SE')
        self.consumir('DELIM_AP')
        condicao = self.expressao()
        self.consumir('DELIM_FP')
        bloco_se = self.bloco()
        
        bloco_senao = None
        if self.verificar('SENAO'):
            self.consumir('SENAO')
            bloco_senao = self.bloco()
        
        return NoSe(condicao, bloco_se, bloco_senao)
    
    def enquanto(self):
        """enquanto -> 'while' '(' expressao ')' bloco"""
        self.consumir('ENQUANTO')
        self.consumir('DELIM_AP')
        condicao = self.expressao()
        self.consumir('DELIM_FP')
        bloco = self.bloco()
        
        return NoEnquanto(condicao, bloco)
    
    def para(self):
        """para -> 'for' '(' comando expressao ';' expressao ')' bloco"""
        self.consumir('PARA')
        self.consumir('DELIM_AP')
        
        # Inicialização (pode ser declaração ou atribuição)
        if self.verificar('TIPO_INT') or self.verificar('TIPO_FLOAT'):
            inicializacao = self.declaracao()
        else:
            nome = self.consumir('ID')
            self.consumir('OPERADOR_ATRIB')
            valor = self.expressao()
            inicializacao = NoAtribuicao(nome.valor, valor)
        
        self.consumir('PONTO_VIRGULA')
        condicao = self.expressao()
        self.consumir('PONTO_VIRGULA')
        incremento = self.expressao()
        self.consumir('DELIM_FP')
        bloco = self.bloco()
        
        return NoPara(inicializacao, condicao, incremento, bloco)
    
    def expressao(self):
        """expressao -> termo (('+' | '-') termo)*"""
        no = self.termo()
        
        while self.verificar('OPERADOR_SOMA') or self.verificar('OPERADOR_SUB'):
            operador = self.token_atual.valor
            self.avancar()
            direita = self.termo()
            no = NoExpressao(operador, no, direita)
        
        return no
    
    def termo(self):
        """termo -> fator ('*' fator)*"""
        no = self.fator()
        
        while self.verificar('OPERADOR_MUL'):
            operador = self.token_atual.valor
            self.avancar()
            direita = self.fator()
            no = NoExpressao(operador, no, direita)
        
        return no
    
    def fator(self):
        """fator -> NUMERO | chamada_funcao | ID | '(' expressao ')'"""
        if self.verificar('NUMERO'):
            token = self.consumir('NUMERO')
            return NoNumero(token.valor)
        elif self.verificar('ID'):
            # Verifica se é uma chamada de função (ID seguido de '(')
            if self.posicao + 1 < len(self.tokens) and self.tokens[self.posicao + 1].tipo == 'DELIM_AP':
                return self.chamada_funcao()
            else:
                token = self.consumir('ID')
                return NoIdentificador(token.valor)
        elif self.verificar('DELIM_AP'):
            self.consumir('DELIM_AP')
            no = self.expressao()
            self.consumir('DELIM_FP')
            return no
        else:
            self.erro("Esperado número, identificador ou '('")
    
    def chamada_funcao(self):
        """chamada_funcao -> ID '(' argumentos? ')'"""
        nome = self.consumir('ID')
        self.consumir('DELIM_AP')
        
        argumentos = []
        if not self.verificar('DELIM_FP'):  # se não é ')'
            argumentos = self.argumentos()
        
        self.consumir('DELIM_FP')
        return NoChamadaFuncao(nome.valor, argumentos)
    
    def argumentos(self):
        """argumentos -> expressao (',' expressao)*"""
        args = []
        args.append(self.expressao())
        
        while self.verificar('VIRGULA'):
            self.consumir('VIRGULA')
            args.append(self.expressao())
        
        return args

def imprimir_arvore(no, nivel=0):
    """Função auxiliar para imprimir a árvore sintática"""
    indentacao = "  " * nivel
    
    if isinstance(no, NoPrograma):
        print(f"{indentacao}PROGRAMA")
        for funcao in no.funcoes:
            imprimir_arvore(funcao, nivel + 1)
    
    elif isinstance(no, NoFuncao):
        print(f"{indentacao}FUNÇÃO: {no.tipo_retorno} {no.nome}")
        if no.parametros:
            print(f"{indentacao}  PARÂMETROS:")
            for param in no.parametros:
                imprimir_arvore(param, nivel + 2)
        print(f"{indentacao}  CORPO:")
        imprimir_arvore(no.corpo, nivel + 2)
    
    elif isinstance(no, NoParametro):
        print(f"{indentacao}PARÂMETRO: {no.tipo} {no.nome}")
    
    elif isinstance(no, NoBloco):
        print(f"{indentacao}BLOCO")
        for comando in no.comandos:
            imprimir_arvore(comando, nivel + 1)
    
    elif isinstance(no, NoDeclaracao):
        if no.valor:
            print(f"{indentacao}DECLARAÇÃO: {no.tipo} {no.nome} =")
            imprimir_arvore(no.valor, nivel + 1)
        else:
            print(f"{indentacao}DECLARAÇÃO: {no.tipo} {no.nome}")
    
    elif isinstance(no, NoAtribuicao):
        print(f"{indentacao}ATRIBUIÇÃO: {no.nome} =")
        imprimir_arvore(no.valor, nivel + 1)
    
    elif isinstance(no, NoRetorno):
        print(f"{indentacao}RETORNO")
        imprimir_arvore(no.valor, nivel + 1)
    
    elif isinstance(no, NoSe):
        print(f"{indentacao}SE")
        print(f"{indentacao}  CONDIÇÃO:")
        imprimir_arvore(no.condicao, nivel + 2)
        print(f"{indentacao}  ENTÃO:")
        imprimir_arvore(no.bloco_se, nivel + 2)
        if no.bloco_senao:
            print(f"{indentacao}  SENÃO:")
            imprimir_arvore(no.bloco_senao, nivel + 2)
    
    elif isinstance(no, NoEnquanto):
        print(f"{indentacao}ENQUANTO")
        print(f"{indentacao}  CONDIÇÃO:")
        imprimir_arvore(no.condicao, nivel + 2)
        print(f"{indentacao}  CORPO:")
        imprimir_arvore(no.bloco, nivel + 2)
    
    elif isinstance(no, NoPara):
        print(f"{indentacao}PARA")
        print(f"{indentacao}  INICIALIZAÇÃO:")
        imprimir_arvore(no.inicializacao, nivel + 2)
        print(f"{indentacao}  CONDIÇÃO:")
        imprimir_arvore(no.condicao, nivel + 2)
        print(f"{indentacao}  INCREMENTO:")
        imprimir_arvore(no.incremento, nivel + 2)
        print(f"{indentacao}  CORPO:")
        imprimir_arvore(no.bloco, nivel + 2)
    
    elif isinstance(no, NoExpressao):
        if no.direita:
            print(f"{indentacao}EXPRESSÃO: {no.operador}")
            imprimir_arvore(no.esquerda, nivel + 1)
            imprimir_arvore(no.direita, nivel + 1)
        else:
            print(f"{indentacao}EXPRESSÃO: {no.operador}")
            imprimir_arvore(no.esquerda, nivel + 1)
    
    elif isinstance(no, NoNumero):
        print(f"{indentacao}NÚMERO: {no.valor}")
    
    elif isinstance(no, NoIdentificador):
        print(f"{indentacao}ID: {no.nome}")
    
    elif isinstance(no, NoChamadaFuncao):
        print(f"{indentacao}CHAMADA: {no.nome}")
        if no.argumentos:
            print(f"{indentacao}  ARGUMENTOS:")
            for arg in no.argumentos:
                imprimir_arvore(arg, nivel + 2)
    
    else:
        print(f"{indentacao}{str(no)}")

if __name__ == '__main__':
    from analisador_lexico import AnalisadorLexico
    
    codigo = """
    int soma(int a, int b) {
        return a + b;
    }
    
    int main() {
        int x = 10;
        int y = 5;
        int resultado = soma(x, y);
        return resultado;
    }
    """
    
    # Análise léxica
    analisador_lexico = AnalisadorLexico()
    tokens = analisador_lexico.tokenizar(codigo)
    
    print("=== TOKENS ===")
    for token in tokens:
        if token.tipo != 'EOF':
            print(token)
    
    print("\n=== ANÁLISE SINTÁTICA ===")
    
    # Análise sintática
    analisador_sintatico = AnalisadorSintatico(tokens)
    arvore = analisador_sintatico.analisar()
    
    if arvore:
        print("Análise sintática concluída com sucesso!")
        print("\n=== ÁRVORE SINTÁTICA ===")
        imprimir_arvore(arvore)
    else:
        print("Falha na análise sintática.")