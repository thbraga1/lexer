class Simbolo:
    def __init__(self, nome, tipo, categoria, linha, coluna, valor=None):
        self.nome = nome
        self.tipo = tipo  # 'int', 'float'
        self.categoria = categoria  # 'variavel', 'funcao'
        self.linha = linha
        self.coluna = coluna
        self.valor = valor
        self.usado = False
    
    def __str__(self):
        return f"Simbolo({self.nome}, {self.tipo}, {self.categoria})"

class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]  # Lista de dicionários (pilha de escopos)
        self.escopo_atual = 0
    
    def entrar_escopo(self):
        """Entra em um novo escopo"""
        self.escopos.append({})
        self.escopo_atual += 1
    
    def sair_escopo(self):
        """Sai do escopo atual"""
        if self.escopo_atual > 0:
            self.escopos.pop()
            self.escopo_atual -= 1
    
    def inserir(self, simbolo):
        """Insere um símbolo no escopo atual"""
        if simbolo.nome in self.escopos[self.escopo_atual]:
            return False  # Símbolo já existe no escopo atual
        self.escopos[self.escopo_atual][simbolo.nome] = simbolo
        return True
    
    def buscar(self, nome):
        """Busca um símbolo em todos os escopos (do atual para o global)"""
        for i in range(self.escopo_atual, -1, -1):
            if nome in self.escopos[i]:
                return self.escopos[i][nome]
        return None
    
    def marcar_usado(self, nome):
        """Marca um símbolo como usado"""
        simbolo = self.buscar(nome)
        if simbolo:
            simbolo.usado = True
    
    def obter_nao_usados(self):
        """Retorna símbolos não utilizados"""
        nao_usados = []
        for escopo in self.escopos:
            for simbolo in escopo.values():
                if not simbolo.usado and simbolo.categoria == 'variavel':
                    nao_usados.append(simbolo)
        return nao_usados

class ErroSemantico:
    def __init__(self, tipo, mensagem, linha, coluna):
        self.tipo = tipo
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
    
    def __str__(self):
        return f"Erro Semântico (linha {self.linha}, coluna {self.coluna}): {self.mensagem}"

class AnalisadorSemantico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0
        self.token_atual = self.tokens[0] if tokens else None
        self.tabela_simbolos = TabelaSimbolos()
        self.erros = []
        self.avisos = []
        
    def token_atual_tipo(self):
        return self.token_atual.tipo if self.token_atual else 'EOF'
    
    def avancar(self):
        """Avança para o próximo token"""
        if self.posicao < len(self.tokens) - 1:
            self.posicao += 1
            self.token_atual = self.tokens[self.posicao]
    
    def erro(self, tipo, mensagem):
        """Adiciona um erro semântico"""
        erro = ErroSemantico(
            tipo, 
            mensagem, 
            self.token_atual.linha, 
            self.token_atual.coluna
        )
        self.erros.append(erro)
    
    def aviso(self, mensagem):
        """Adiciona um aviso"""
        aviso = f"Aviso (linha {self.token_atual.linha}): {mensagem}"
        self.avisos.append(aviso)
    
    def analisar(self):
        """Inicia a análise semântica"""
        try:
            self.programa()
            
            # Verifica variáveis não utilizadas
            nao_usados = self.tabela_simbolos.obter_nao_usados()
            for simbolo in nao_usados:
                self.avisos.append(f"Aviso (linha {simbolo.linha}): Variável '{simbolo.nome}' declarada mas não utilizada")
            
            return len(self.erros) == 0
        except Exception as e:
            self.erro("ERRO_INTERNO", f"Erro interno do analisador: {str(e)}")
            return False
    
    def programa(self):
        """programa -> declaracao*"""
        while self.token_atual_tipo() != 'EOF':
            self.declaracao()
    
    def declaracao(self):
        """declaracao -> declaracao_funcao | declaracao_variavel"""
        if self.token_atual_tipo() in ['TIPO_INT', 'TIPO_FLOAT']:
            # Verifica se é declaração de função ou variável
            tipo_token = self.token_atual
            self.avancar()
            
            if self.token_atual_tipo() == 'ID':
                nome_token = self.token_atual
                self.avancar()
                
                if self.token_atual_tipo() == 'DELIM_AP':
                    # É uma função
                    self.declaracao_funcao(tipo_token, nome_token)
                else:
                    # É uma variável
                    self.declaracao_variavel(tipo_token, nome_token)
            else:
                self.erro("ERRO_SINTATICO", "Esperado identificador após tipo")
        else:
            self.erro("ERRO_SINTATICO", f"Declaração inválida: {self.token_atual_tipo()}")
            self.avancar()  # Tenta recuperar
    
    def declaracao_variavel(self, tipo_token, nome_token):
        """declaracao_variavel -> tipo ID ('=' expressao)? ';'"""
        # Verifica se a variável já foi declarada no escopo atual
        if not self.tabela_simbolos.inserir(
            Simbolo(nome_token.valor, tipo_token.valor, 'variavel', 
                   nome_token.linha, nome_token.coluna)
        ):
            self.erro("REDECLARACAO", f"Variável '{nome_token.valor}' já foi declarada neste escopo")
        
        # Verifica atribuição inicial
        if self.token_atual_tipo() == 'OPERADOR_ATRIB':
            self.avancar()
            tipo_expr = self.expressao()
            
            # Verifica compatibilidade de tipos
            self.verificar_compatibilidade_tipos(tipo_token.valor, tipo_expr, 
                                               "atribuição", nome_token.linha, nome_token.coluna)
        
        if self.token_atual_tipo() == 'PONTO_VIRGULA':
            self.avancar()
        else:
            self.erro("ERRO_SINTATICO", "Esperado ';' após declaração de variável")
    
    def declaracao_funcao(self, tipo_token, nome_token):
        """declaracao_funcao -> tipo ID '(' parametros? ')' bloco"""
        # Verifica se a função já foi declarada
        if not self.tabela_simbolos.inserir(
            Simbolo(nome_token.valor, tipo_token.valor, 'funcao', 
                   nome_token.linha, nome_token.coluna)
        ):
            self.erro("REDECLARACAO", f"Função '{nome_token.valor}' já foi declarada")
        
        # Entra no escopo da função
        self.tabela_simbolos.entrar_escopo()
        
        # '(' já foi consumido na análise anterior
        self.avancar()  # consome '('
        
        # Parâmetros
        if self.token_atual_tipo() != 'DELIM_FP':
            self.parametros()
        
        if self.token_atual_tipo() == 'DELIM_FP':
            self.avancar()
        else:
            self.erro("ERRO_SINTATICO", "Esperado ')' após parâmetros")
        
        # Corpo da função
        self.bloco()
        
        # Sai do escopo da função
        self.tabela_simbolos.sair_escopo()
    
    def parametros(self):
        """parametros -> tipo ID (',' tipo ID)*"""
        if self.token_atual_tipo() in ['TIPO_INT', 'TIPO_FLOAT']:
            tipo_token = self.token_atual
            self.avancar()
            
            if self.token_atual_tipo() == 'ID':
                nome_token = self.token_atual
                self.avancar()
                
                # Insere parâmetro na tabela de símbolos
                if not self.tabela_simbolos.inserir(
                    Simbolo(nome_token.valor, tipo_token.valor, 'variavel', 
                           nome_token.linha, nome_token.coluna)
                ):
                    self.erro("REDECLARACAO", f"Parâmetro '{nome_token.valor}' duplicado")
                
                # Parâmetros adicionais
                while self.token_atual_tipo() == 'VIRGULA':
                    self.avancar()
                    if self.token_atual_tipo() in ['TIPO_INT', 'TIPO_FLOAT']:
                        tipo_token = self.token_atual
                        self.avancar()
                        
                        if self.token_atual_tipo() == 'ID':
                            nome_token = self.token_atual
                            self.avancar()
                            
                            if not self.tabela_simbolos.inserir(
                                Simbolo(nome_token.valor, tipo_token.valor, 'variavel', 
                                       nome_token.linha, nome_token.coluna)
                            ):
                                self.erro("REDECLARACAO", f"Parâmetro '{nome_token.valor}' duplicado")
            else:
                self.erro("ERRO_SINTATICO", "Esperado nome do parâmetro")
    
    def bloco(self):
        """bloco -> '{' declaracao* '}'"""
        if self.token_atual_tipo() == 'DELIM_AC':
            self.avancar()
            
            while self.token_atual_tipo() != 'DELIM_FC' and self.token_atual_tipo() != 'EOF':
                self.comando()
            
            if self.token_atual_tipo() == 'DELIM_FC':
                self.avancar()
            else:
                self.erro("ERRO_SINTATICO", "Esperado '}' para fechar bloco")
        else:
            self.erro("ERRO_SINTATICO", "Esperado '{' para iniciar bloco")
    
    def comando(self):
        """comando -> declaracao | atribuicao | retorno | bloco"""
        if self.token_atual_tipo() in ['TIPO_INT', 'TIPO_FLOAT']:
            self.declaracao()
        elif self.token_atual_tipo() == 'ID':
            self.atribuicao()
        elif self.token_atual_tipo() == 'RETORNO':
            self.retorno()
        elif self.token_atual_tipo() == 'DELIM_AC':
            self.tabela_simbolos.entrar_escopo()
            self.bloco()
            self.tabela_simbolos.sair_escopo()
        else:
            self.erro("ERRO_SINTATICO", f"Comando inválido: {self.token_atual_tipo()}")
            self.avancar()
    
    def atribuicao(self):
        """atribuicao -> ID '=' expressao ';'"""
        if self.token_atual_tipo() == 'ID':
            nome_token = self.token_atual
            
            # Verifica se a variável foi declarada
            simbolo = self.tabela_simbolos.buscar(nome_token.valor)
            if not simbolo:
                self.erro("NAO_DECLARADO", f"Variável '{nome_token.valor}' não foi declarada")
            else:
                self.tabela_simbolos.marcar_usado(nome_token.valor)
                
            self.avancar()
            
            if self.token_atual_tipo() == 'OPERADOR_ATRIB':
                self.avancar()
                tipo_expr = self.expressao()
                
                # Verifica compatibilidade de tipos se a variável existe
                if simbolo:
                    self.verificar_compatibilidade_tipos(simbolo.tipo, tipo_expr, 
                                                       "atribuição", nome_token.linha, nome_token.coluna)
                
                if self.token_atual_tipo() == 'PONTO_VIRGULA':
                    self.avancar()
                else:
                    self.erro("ERRO_SINTATICO", "Esperado ';' após atribuição")
            else:
                self.erro("ERRO_SINTATICO", "Esperado '=' na atribuição")
    
    def retorno(self):
        """retorno -> 'return' expressao ';'"""
        if self.token_atual_tipo() == 'RETORNO':
            self.avancar()
            self.expressao()
            
            if self.token_atual_tipo() == 'PONTO_VIRGULA':
                self.avancar()
            else:
                self.erro("ERRO_SINTATICO", "Esperado ';' após return")
    
    def expressao(self):
        """expressao -> termo (('+'|'-') termo)*"""
        tipo_esq = self.termo()
        
        while self.token_atual_tipo() in ['OPERADOR_SOMA', 'OPERADOR_SUB']:
            op = self.token_atual
            self.avancar()
            tipo_dir = self.termo()
            
            # Verifica compatibilidade para operação aritmética
            tipo_esq = self.verificar_operacao_aritmetica(tipo_esq, tipo_dir, op.valor)
        
        return tipo_esq
    
    def termo(self):
        """termo -> fator ('*' fator)*"""
        tipo_esq = self.fator()
        
        while self.token_atual_tipo() == 'OPERADOR_MUL':
            op = self.token_atual
            self.avancar()
            tipo_dir = self.fator()
            
            # Verifica compatibilidade para multiplicação
            tipo_esq = self.verificar_operacao_aritmetica(tipo_esq, tipo_dir, op.valor)
        
        return tipo_esq
    
    def fator(self):
        """fator -> NUMERO | ID | '(' expressao ')'"""
        if self.token_atual_tipo() == 'NUMERO':
            valor = self.token_atual.valor
            self.avancar()
            
            # Determina o tipo do número
            if '.' in valor:
                return 'TIPO_FLOAT'
            else:
                return 'TIPO_INT'
                
        elif self.token_atual_tipo() == 'ID':
            nome_token = self.token_atual
            simbolo = self.tabela_simbolos.buscar(nome_token.valor)
            
            if not simbolo:
                self.erro("NAO_DECLARADO", f"Variável '{nome_token.valor}' não foi declarada")
                self.avancar()
                return 'TIPO_INT'  # Tipo padrão para continuar análise
            else:
                self.tabela_simbolos.marcar_usado(nome_token.valor)
                self.avancar()
                return simbolo.tipo
                
        elif self.token_atual_tipo() == 'DELIM_AP':
            self.avancar()
            tipo = self.expressao()
            
            if self.token_atual_tipo() == 'DELIM_FP':
                self.avancar()
            else:
                self.erro("ERRO_SINTATICO", "Esperado ')' após expressão")
            
            return tipo
        else:
            self.erro("ERRO_SINTATICO", f"Fator inválido: {self.token_atual_tipo()}")
            self.avancar()
            return 'TIPO_INT'  # Tipo padrão
    
    def verificar_compatibilidade_tipos(self, tipo1, tipo2, operacao, linha, coluna):
        """Verifica se os tipos são compatíveis para a operação"""
        if tipo1 != tipo2:
            if (tipo1 == 'TIPO_FLOAT' and tipo2 == 'TIPO_INT') or \
               (tipo1 == 'TIPO_INT' and tipo2 == 'TIPO_FLOAT'):
                self.aviso(f"Conversão implícita de tipos na {operacao}")
            else:
                self.erro("INCOMPATIBILIDADE_TIPOS", 
                         f"Tipos incompatíveis na {operacao}: {tipo1} e {tipo2}")
    
    def verificar_operacao_aritmetica(self, tipo1, tipo2, operador):
        """Verifica operação aritmética e retorna o tipo resultante"""
        if tipo1 == 'TIPO_FLOAT' or tipo2 == 'TIPO_FLOAT':
            if tipo1 != tipo2:
                self.aviso(f"Conversão implícita em operação {operador}")
            return 'TIPO_FLOAT'
        else:
            return 'TIPO_INT'
    
    def imprimir_resultados(self):
        """Imprime os resultados da análise semântica"""
        print("\n" + "="*60)
        print("RESULTADO DA ANÁLISE SEMÂNTICA")
        print("="*60)
        
        # Tabela de símbolos
        print("\nTABELA DE SÍMBOLOS:")
        print(f"{'NOME':<15} | {'TIPO':<10} | {'CATEGORIA':<10} | {'LINHA':<5} | {'USADO':<5}")
        print(f"{'-'*15} | {'-'*10} | {'-'*10} | {'-'*5} | {'-'*5}")
        
        for escopo in self.tabela_simbolos.escopos:
            for simbolo in escopo.values():
                usado = "Sim" if simbolo.usado else "Não"
                print(f"{simbolo.nome:<15} | {simbolo.tipo:<10} | {simbolo.categoria:<10} | {simbolo.linha:<5} | {usado:<5}")
        
        # Erros semânticos
        if self.erros:
            print(f"\nERROS SEMÂNTICOS ({len(self.erros)}):")
            for erro in self.erros:
                print(f"  • {erro}")
        else:
            print("\n✓ Nenhum erro semântico encontrado!")
        
        # Avisos
        if self.avisos:
            print(f"\nAVISOS ({len(self.avisos)}):")
            for aviso in self.avisos:
                print(f"  • {aviso}")
        
        # Resumo
        print(f"\nRESUMO:")
        print(f"  • Símbolos declarados: {sum(len(escopo) for escopo in self.tabela_simbolos.escopos)}")
        print(f"  • Erros encontrados: {len(self.erros)}")
        print(f"  • Avisos gerados: {len(self.avisos)}")
        print(f"  • Status: {'✓ SUCESSO' if len(self.erros) == 0 else '✗ FALHA'}")