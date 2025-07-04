class GeradorCodigo:
    def __init__(self):
        self.codigo = []
        self.contador_label = 0
        self.pilha_registradores = []
        self.variaveis_locais = {}
        self.offset_atual = 0
        self.funcao_atual = None
        
    def gerar_label(self, prefixo="label"):
        """Gera um label único"""
        self.contador_label += 1
        return f"{prefixo}_{self.contador_label}"
    
    def emit(self, instrucao):
        """Adiciona uma instrução ao código"""
        self.codigo.append(instrucao)
    
    def gerar(self, arvore):
        """Ponto de entrada para geração de código"""
        self.emit("section .text")
        self.emit("global _start")
        self.emit("")
        
        # Gera código para todas as funções
        self.gerar_programa(arvore)
        
        # Adiciona ponto de entrada
        self.emit("_start:")
        self.emit("    call main")
        self.emit("    mov rdi, rax")  # Código de saída = retorno de main
        self.emit("    mov rax, 60")   # sys_exit
        self.emit("    syscall")
        
        return '\n'.join(self.codigo)
    
    def gerar_programa(self, no):
        """Gera código para o programa"""
        for funcao in no.funcoes:
            self.gerar_funcao(funcao)
    
    def gerar_funcao(self, no):
        """Gera código para uma função"""
        self.funcao_atual = no
        self.variaveis_locais = {}
        self.offset_atual = 0
        
        # Label da função
        self.emit(f"{no.nome}:")
        self.emit("    push rbp")
        self.emit("    mov rbp, rsp")
        
        # Reserva espaço para variáveis locais (será ajustado depois)
        espaco_placeholder = len(self.codigo)
        self.emit("    ; espaço para variáveis locais")
        
        # Mapeia parâmetros
        registradores_params = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        for i, param in enumerate(no.parametros):
            if i < len(registradores_params):
                self.offset_atual += 8
                self.variaveis_locais[param.nome] = -self.offset_atual
                # Move parâmetro para pilha
                self.emit(f"    mov [rbp-{self.offset_atual}], {registradores_params[i]}")
        
        # Gera código do corpo da função
        self.gerar_bloco(no.corpo)
        
        # Ajusta espaço para variáveis locais
        if self.offset_atual > 0:
            self.codigo[espaco_placeholder] = f"    sub rsp, {self.offset_atual}"
        
        # Retorno padrão (caso não haja return explícito)
        self.emit("    mov rax, 0")
        self.emit("    mov rsp, rbp")
        self.emit("    pop rbp")
        self.emit("    ret")
        self.emit("")
    
    def gerar_bloco(self, no):
        """Gera código para um bloco"""
        for comando in no.comandos:
            self.gerar_comando(comando)
    
    def gerar_comando(self, no):
        """Gera código para um comando"""
        from analisador_sintatico import (NoDeclaracao, NoAtribuicao, NoRetorno, 
                                        NoSe, NoEnquanto, NoPara, NoBloco, NoExpressao)
        
        if isinstance(no, NoDeclaracao):
            self.gerar_declaracao(no)
        elif isinstance(no, NoAtribuicao):
            self.gerar_atribuicao(no)
        elif isinstance(no, NoRetorno):
            self.gerar_retorno(no)
        elif isinstance(no, NoSe):
            self.gerar_se(no)
        elif isinstance(no, NoEnquanto):
            self.gerar_enquanto(no)
        elif isinstance(no, NoPara):
            self.gerar_para(no)
        elif isinstance(no, NoBloco):
            self.gerar_bloco(no)
        elif isinstance(no, NoExpressao):
            self.gerar_expressao(no)
            # Remove resultado da pilha se não for usado
            self.emit("    pop rax")
    
    def gerar_declaracao(self, no):
        """Gera código para declaração de variável"""
        # Reserva espaço na pilha
        self.offset_atual += 8
        self.variaveis_locais[no.nome] = -self.offset_atual
        
        # Se há inicialização
        if no.valor:
            self.gerar_expressao(no.valor)
            self.emit("    pop rax")
            self.emit(f"    mov [rbp{self.variaveis_locais[no.nome]}], rax")
        else:
            # Inicializa com zero
            self.emit(f"    mov qword [rbp{self.variaveis_locais[no.nome]}], 0")
    
    def gerar_atribuicao(self, no):
        """Gera código para atribuição"""
        self.gerar_expressao(no.valor)
        self.emit("    pop rax")
        self.emit(f"    mov [rbp{self.variaveis_locais[no.nome]}], rax")
    
    def gerar_retorno(self, no):
        """Gera código para return"""
        self.gerar_expressao(no.valor)
        self.emit("    pop rax")
        self.emit("    mov rsp, rbp")
        self.emit("    pop rbp")
        self.emit("    ret")
    
    def gerar_se(self, no):
        """Gera código para if/else"""
        label_else = self.gerar_label("else")
        label_fim = self.gerar_label("endif")
        
        # Gera condição
        self.gerar_expressao(no.condicao)
        self.emit("    pop rax")
        self.emit("    cmp rax, 0")
        self.emit(f"    je {label_else}")
        
        # Bloco if
        self.gerar_bloco(no.bloco_se)
        self.emit(f"    jmp {label_fim}")
        
        # Bloco else
        self.emit(f"{label_else}:")
        if no.bloco_senao:
            self.gerar_bloco(no.bloco_senao)
        
        self.emit(f"{label_fim}:")
    
    def gerar_enquanto(self, no):
        """Gera código para while"""
        label_inicio = self.gerar_label("while_start")
        label_fim = self.gerar_label("while_end")
        
        self.emit(f"{label_inicio}:")
        
        # Gera condição
        self.gerar_expressao(no.condicao)
        self.emit("    pop rax")
        self.emit("    cmp rax, 0")
        self.emit(f"    je {label_fim}")
        
        # Corpo do loop
        self.gerar_bloco(no.bloco)
        self.emit(f"    jmp {label_inicio}")
        
        self.emit(f"{label_fim}:")
    
    def gerar_para(self, no):
        """Gera código para for"""
        label_inicio = self.gerar_label("for_start")
        label_fim = self.gerar_label("for_end")
        
        # Inicialização
        self.gerar_comando(no.inicializacao)
        
        self.emit(f"{label_inicio}:")
        
        # Condição
        self.gerar_expressao(no.condicao)
        self.emit("    pop rax")
        self.emit("    cmp rax, 0")
        self.emit(f"    je {label_fim}")
        
        # Corpo
        self.gerar_bloco(no.bloco)
        
        # Incremento
        self.gerar_expressao(no.incremento)
        self.emit("    pop rax")  # Remove resultado do incremento
        
        self.emit(f"    jmp {label_inicio}")
        self.emit(f"{label_fim}:")
    
    def gerar_expressao(self, no):
        """Gera código para expressão (resultado na pilha)"""
        from analisador_sintatico import (NoExpressao, NoNumero, NoIdentificador, NoChamadaFuncao)
        
        if isinstance(no, NoNumero):
            # Carrega número na pilha
            self.emit(f"    push {no.valor}")
        
        elif isinstance(no, NoIdentificador):
            # Carrega variável na pilha
            if no.nome in self.variaveis_locais:
                self.emit(f"    push qword [rbp{self.variaveis_locais[no.nome]}]")
            else:
                raise Exception(f"Variável {no.nome} não encontrada")
        
        elif isinstance(no, NoChamadaFuncao):
            self.gerar_chamada_funcao(no)
        
        elif isinstance(no, NoExpressao):
            if no.direita:  # Operação binária
                self.gerar_expressao(no.esquerda)
                self.gerar_expressao(no.direita)
                
                # Operandos estão na pilha
                self.emit("    pop rbx")  # direita
                self.emit("    pop rax")  # esquerda
                
                if no.operador == '+':
                    self.emit("    add rax, rbx")
                elif no.operador == '-':
                    self.emit("    sub rax, rbx")
                elif no.operador == '*':
                    self.emit("    imul rax, rbx")
                elif no.operador == '/':
                    self.emit("    cqo")  # estende rax para rdx:rax
                    self.emit("    idiv rbx")
                else:
                    raise Exception(f"Operador {no.operador} não implementado")
                
                self.emit("    push rax")
            
            else:  # Operação unária
                self.gerar_expressao(no.esquerda)
                self.emit("    pop rax")
                
                if no.operador == '-':
                    self.emit("    neg rax")
                elif no.operador == '+':
                    pass  # Nada a fazer
                else:
                    raise Exception(f"Operador unário {no.operador} não implementado")
                
                self.emit("    push rax")
    
    def gerar_chamada_funcao(self, no):
        """Gera código para chamada de função"""
        registradores_params = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        
        # Salva registradores que podem ser alterados
        self.emit("    push rdi")
        self.emit("    push rsi")
        self.emit("    push rdx")
        self.emit("    push rcx")
        self.emit("    push r8")
        self.emit("    push r9")
        
        # Prepara argumentos
        for i, arg in enumerate(no.argumentos):
            if i < len(registradores_params):
                self.gerar_expressao(arg)
                self.emit(f"    pop {registradores_params[i]}")
            else:
                # Mais de 6 argumentos vão para pilha
                self.gerar_expressao(arg)
        
        # Chama função
        self.emit(f"    call {no.nome}")
        
        # Restaura registradores
        self.emit("    pop r9")
        self.emit("    pop r8")
        self.emit("    pop rcx")
        self.emit("    pop rdx")
        self.emit("    pop rsi")
        self.emit("    pop rdi")
        
        # Resultado em rax, coloca na pilha
        self.emit("    push rax")
    
    def otimizar_codigo(self):
        """Otimizações básicas do código gerado"""
        # Remove push/pop consecutivos desnecessários
        codigo_otimizado = []
        i = 0
        while i < len(self.codigo):
            if (i + 1 < len(self.codigo) and 
                self.codigo[i].strip().startswith('push') and 
                self.codigo[i + 1].strip().startswith('pop')):
                # Verifica se é push/pop do mesmo registrador
                push_reg = self.codigo[i].strip().split()[-1]
                pop_reg = self.codigo[i + 1].strip().split()[-1]
                if push_reg != pop_reg:
                    # Substitui push reg1; pop reg2 por mov reg2, reg1
                    codigo_otimizado.append(f"    mov {pop_reg}, {push_reg}")
                    i += 2
                else:
                    # Remove push/pop do mesmo registrador
                    i += 2
            else:
                codigo_otimizado.append(self.codigo[i])
                i += 1
        
        self.codigo = codigo_otimizado