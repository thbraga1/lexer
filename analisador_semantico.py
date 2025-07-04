class ErroSemantico(Exception):
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(mensagem)

class Simbolo:
    def __init__(self, nome, tipo, categoria, escopo=None, parametros=None):
        self.nome = nome
        self.tipo = tipo  # 'int', 'float'
        self.categoria = categoria  # 'variavel', 'funcao', 'parametro'
        self.escopo = escopo
        self.parametros = parametros or []  # Para funções
        self.usado = False
        self.declarado = True

class TabelaSimbolos:
    def __init__(self):
        self.pilha_escopos = [{}]  # Pilha de escopos (global primeiro)
        self.escopo_atual = 0
        self.contador_escopo = 0
    
    def entrar_escopo(self):
        """Entra em um novo escopo"""
        self.pilha_escopos.append({})
        self.contador_escopo += 1
        self.escopo_atual = self.contador_escopo
    
    def sair_escopo(self):
        """Sai do escopo atual"""
        if len(self.pilha_escopos) > 1:
            self.pilha_escopos.pop()
            self.escopo_atual -= 1
    
    def declarar_simbolo(self, nome, tipo, categoria, parametros=None):
        """Declara um novo símbolo no escopo atual"""
        if nome in self.pilha_escopos[-1]:
            raise ErroSemantico(f"Símbolo '{nome}' já declarado no escopo atual")
        
        simbolo = Simbolo(nome, tipo, categoria, self.escopo_atual, parametros)
        self.pilha_escopos[-1][nome] = simbolo
        return simbolo
    
    def buscar_simbolo(self, nome):
        """Busca um símbolo em todos os escopos (do mais interno ao mais externo)"""
        for escopo in reversed(self.pilha_escopos):
            if nome in escopo:
                escopo[nome].usado = True
                return escopo[nome]
        return None
    
    def obter_simbolos_escopo_atual(self):
        """Retorna todos os símbolos do escopo atual"""
        return self.pilha_escopos[-1]

class AnalisadorSemantico:
    def __init__(self):
        self.tabela_simbolos = TabelaSimbolos()
        self.funcao_atual = None
        self.erros = []
    
    def erro(self, mensagem):
        """Registra um erro semântico"""
        self.erros.append(mensagem)
        raise ErroSemantico(mensagem)
    
    def analisar(self, arvore):
        """Ponto de entrada da análise semântica"""
        try:
            self.analisar_programa(arvore)
            
            # Verifica se há função main
            main_func = self.tabela_simbolos.buscar_simbolo('main')
            if not main_func:
                self.erro("Função 'main' não encontrada")
            elif main_func.tipo != 'int':
                self.erro("Função 'main' deve retornar 'int'")
            
            print("✅ Análise semântica concluída com sucesso!")
            return True
            
        except ErroSemantico as e:
            print(f"❌ Erro semântico: {e.mensagem}")
            return False
    
    def analisar_programa(self, no):
        """Analisa o programa (lista de funções)"""
        # Primeira passada: declara todas as funções
        for funcao in no.funcoes:
            tipos_parametros = []
            if funcao.parametros:
                tipos_parametros = [param.tipo for param in funcao.parametros]
            
            self.tabela_simbolos.declarar_simbolo(
                funcao.nome, 
                funcao.tipo_retorno, 
                'funcao', 
                tipos_parametros
            )
        
        # Segunda passada: analisa o corpo das funções
        for funcao in no.funcoes:
            self.analisar_funcao(funcao)
    
    def analisar_funcao(self, no):
        """Analisa uma função"""
        self.funcao_atual = no
        self.tabela_simbolos.entrar_escopo()
        
        # Declara os parâmetros no escopo da função
        for param in no.parametros:
            self.tabela_simbolos.declarar_simbolo(
                param.nome, 
                param.tipo, 
                'parametro'
            )
        
        # Analisa o corpo da função
        self.analisar_bloco(no.corpo)
        
        # Verifica se a função tem return (exceto se for void - não implementado ainda)
        if not self.tem_return(no.corpo):
            self.erro(f"Função '{no.nome}' deve ter pelo menos um comando return")
        
        self.tabela_simbolos.sair_escopo()
        self.funcao_atual = None
    
    def tem_return(self, bloco):
        """Verifica se um bloco tem pelo menos um comando return"""
        from analisador_sintatico import NoRetorno, NoSe, NoEnquanto, NoPara, NoBloco
        
        for comando in bloco.comandos:
            if isinstance(comando, NoRetorno):
                return True
            elif isinstance(comando, NoSe):
                # Se tem else, verifica se ambos os blocos têm return
                if comando.bloco_senao and self.tem_return(comando.bloco_se) and self.tem_return(comando.bloco_senao):
                    return True
            elif isinstance(comando, NoBloco):
                if self.tem_return(comando):
                    return True
        return False
    
    def analisar_bloco(self, no):
        """Analisa um bloco de comandos"""
        for comando in no.comandos:
            self.analisar_comando(comando)
    
    def analisar_comando(self, no):
        """Analisa um comando"""
        from analisador_sintatico import (NoDeclaracao, NoAtribuicao, NoRetorno, 
                                        NoSe, NoEnquanto, NoPara, NoBloco, NoExpressao)
        
        if isinstance(no, NoDeclaracao):
            self.analisar_declaracao(no)
        elif isinstance(no, NoAtribuicao):
            self.analisar_atribuicao(no)
        elif isinstance(no, NoRetorno):
            self.analisar_retorno(no)
        elif isinstance(no, NoSe):
            self.analisar_se(no)
        elif isinstance(no, NoEnquanto):
            self.analisar_enquanto(no)
        elif isinstance(no, NoPara):
            self.analisar_para(no)
        elif isinstance(no, NoBloco):
            self.tabela_simbolos.entrar_escopo()
            self.analisar_bloco(no)
            self.tabela_simbolos.sair_escopo()
        elif isinstance(no, NoExpressao):
            self.analisar_expressao(no)
    
    def analisar_declaracao(self, no):
        """Analisa uma declaração de variável"""
        # Verifica se o tipo é válido
        if no.tipo not in ['int', 'float']:
            self.erro(f"Tipo inválido: {no.tipo}")
        
        # Declara a variável
        self.tabela_simbolos.declarar_simbolo(no.nome, no.tipo, 'variavel')
        
        # Se há inicialização, analisa a expressão
        if no.valor:
            tipo_valor = self.analisar_expressao(no.valor)
            
            # Verifica compatibilidade de tipos
            if not self.tipos_compativeis(no.tipo, tipo_valor):
                self.erro(f"Tipo incompatível na inicialização da variável '{no.nome}': "
                         f"esperado '{no.tipo}', encontrado '{tipo_valor}'")
    
    def analisar_atribuicao(self, no):
        """Analisa uma atribuição"""
        # Verifica se a variável foi declarada
        simbolo = self.tabela_simbolos.buscar_simbolo(no.nome)
        if not simbolo:
            self.erro(f"Variável '{no.nome}' não declarada")
        
        if simbolo.categoria != 'variavel' and simbolo.categoria != 'parametro':
            self.erro(f"'{no.nome}' não é uma variável")
        
        # Analisa a expressão do valor
        tipo_valor = self.analisar_expressao(no.valor)
        
        # Verifica compatibilidade de tipos
        if not self.tipos_compativeis(simbolo.tipo, tipo_valor):
            self.erro(f"Tipo incompatível na atribuição: "
                     f"esperado '{simbolo.tipo}', encontrado '{tipo_valor}'")
    
    def analisar_retorno(self, no):
        """Analisa um comando return"""
        if not self.funcao_atual:
            self.erro("Comando 'return' fora de função")
        
        tipo_retorno = self.analisar_expressao(no.valor)
        
        # Verifica se o tipo de retorno é compatível
        if not self.tipos_compativeis(self.funcao_atual.tipo_retorno, tipo_retorno):
            self.erro(f"Tipo de retorno incompatível: "
                     f"esperado '{self.funcao_atual.tipo_retorno}', encontrado '{tipo_retorno}'")
    
    def analisar_se(self, no):
        """Analisa um comando if"""
        tipo_condicao = self.analisar_expressao(no.condicao)
        
        # A condição deve ser de um tipo que pode ser avaliado como booleano
        if tipo_condicao not in ['int', 'float']:
            self.erro(f"Condição deve ser do tipo 'int' ou 'float', encontrado '{tipo_condicao}'")
        
        # Analisa os blocos
        self.tabela_simbolos.entrar_escopo()
        self.analisar_bloco(no.bloco_se)
        self.tabela_simbolos.sair_escopo()
        
        if no.bloco_senao:
            self.tabela_simbolos.entrar_escopo()
            self.analisar_bloco(no.bloco_senao)
            self.tabela_simbolos.sair_escopo()
    
    def analisar_enquanto(self, no):
        """Analisa um comando while"""
        tipo_condicao = self.analisar_expressao(no.condicao)
        
        if tipo_condicao not in ['int', 'float']:
            self.erro(f"Condição deve ser do tipo 'int' ou 'float', encontrado '{tipo_condicao}'")
        
        self.tabela_simbolos.entrar_escopo()
        self.analisar_bloco(no.bloco)
        self.tabela_simbolos.sair_escopo()
    
    def analisar_para(self, no):
        """Analisa um comando for"""
        self.tabela_simbolos.entrar_escopo()
        
        # Analisa inicialização
        self.analisar_comando(no.inicializacao)
        
        # Analisa condição
        tipo_condicao = self.analisar_expressao(no.condicao)
        if tipo_condicao not in ['int', 'float']:
            self.erro(f"Condição deve ser do tipo 'int' ou 'float', encontrado '{tipo_condicao}'")
        
        # Analisa incremento
        self.analisar_expressao(no.incremento)
        
        # Analisa corpo
        self.analisar_bloco(no.bloco)
        
        self.tabela_simbolos.sair_escopo()
    
    def analisar_expressao(self, no):
        """Analisa uma expressão e retorna seu tipo"""
        from analisador_sintatico import (NoExpressao, NoNumero, NoIdentificador, NoChamadaFuncao)
        
        if isinstance(no, NoNumero):
            # Determina o tipo do número
            if '.' in str(no.valor):
                return 'float'
            else:
                return 'int'
        
        elif isinstance(no, NoIdentificador):
            simbolo = self.tabela_simbolos.buscar_simbolo(no.nome)
            if not simbolo:
                self.erro(f"Variável '{no.nome}' não declarada")
            
            if simbolo.categoria == 'funcao':
                self.erro(f"'{no.nome}' é uma função, não uma variável")
            
            return simbolo.tipo
        
        elif isinstance(no, NoChamadaFuncao):
            return self.analisar_chamada_funcao(no)
        
        elif isinstance(no, NoExpressao):
            if no.direita:  # Operação binária
                tipo_esq = self.analisar_expressao(no.esquerda)
                tipo_dir = self.analisar_expressao(no.direita)
                
                # Verifica se os tipos são compatíveis para a operação
                if no.operador in ['+', '-', '*', '/']:
                    if tipo_esq not in ['int', 'float'] or tipo_dir not in ['int', 'float']:
                        self.erro(f"Operação aritmética inválida entre '{tipo_esq}' e '{tipo_dir}'")
                    
                    # Retorna o tipo mais "forte" (float > int)
                    if tipo_esq == 'float' or tipo_dir == 'float':
                        return 'float'
                    else:
                        return 'int'
                
                else:
                    self.erro(f"Operador desconhecido: {no.operador}")
            
            else:  # Operação unária
                tipo_expr = self.analisar_expressao(no.esquerda)
                
                if no.operador in ['+', '-']:
                    if tipo_expr not in ['int', 'float']:
                        self.erro(f"Operação unária inválida com tipo '{tipo_expr}'")
                    return tipo_expr
                else:
                    self.erro(f"Operador unário desconhecido: {no.operador}")
        
        else:
            self.erro(f"Tipo de expressão desconhecido: {type(no)}")
    
    def analisar_chamada_funcao(self, no):
        """Analisa uma chamada de função"""
        simbolo = self.tabela_simbolos.buscar_simbolo(no.nome)
        if not simbolo:
            self.erro(f"Função '{no.nome}' não declarada")
        
        if simbolo.categoria != 'funcao':
            self.erro(f"'{no.nome}' não é uma função")
        
        # Verifica número de argumentos
        if len(no.argumentos) != len(simbolo.parametros):
            self.erro(f"Função '{no.nome}' espera {len(simbolo.parametros)} argumentos, "
                     f"mas {len(no.argumentos)} foram fornecidos")
        
        # Verifica tipos dos argumentos
        for i, (arg, tipo_esperado) in enumerate(zip(no.argumentos, simbolo.parametros)):
            tipo_arg = self.analisar_expressao(arg)
            if not self.tipos_compativeis(tipo_esperado, tipo_arg):
                self.erro(f"Argumento {i+1} da função '{no.nome}': "
                         f"esperado '{tipo_esperado}', encontrado '{tipo_arg}'")
        
        return simbolo.tipo
    
    def tipos_compativeis(self, tipo1, tipo2):
        """Verifica se dois tipos são compatíveis"""
        # Por enquanto, apenas tipos exatamente iguais são compatíveis
        # Pode ser expandido para permitir conversões implícitas
        return tipo1 == tipo2
    
    def imprimir_tabela_simbolos(self):
        """Imprime a tabela de símbolos para debug"""
        print("\n=== TABELA DE SÍMBOLOS ===")
        for i, escopo in enumerate(self.tabela_simbolos.pilha_escopos):
            print(f"Escopo {i}:")
            for nome, simbolo in escopo.items():
                print(f"  {nome}: {simbolo.tipo} ({simbolo.categoria})")
                if simbolo.parametros:
                    print(f"    Parâmetros: {simbolo.parametros}")