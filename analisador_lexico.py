import re  
class Token:
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna
    
    def __str__(self):
        return f"Token({self.tipo}, '{self.valor}', linha={self.linha}, coluna={self.coluna})"

class AnalisadorLexico:
    def __init__(self):
        #expressoes regulares
        self.padroes = [
            ('NUMERO', r'\d+(\.\d+)?'),
            ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OPERADOR_SOMA', r'\+'),
            ('OPERADOR_SUB', r'-'),
            ('OPERADOR_MUL', r'\*'),
            ('OPERADOR_DIV', r'/'),  # Adicionado operador de divisão
            ('OPERADOR_ATRIB', r'='),
            ('DELIM_AP', r'\('),
            ('DELIM_FP', r'\)'),
            ('DELIM_AC', r'\{'),
            ('DELIM_FC', r'\}'),
            ('VIRGULA', r','),  # Adicionado vírgula
            ('PONTO_VIRGULA', r';'),
            ('ESPACO', r'\s+'),  
            ('COMENTARIO', r'//.*|/\*[\s\S]*?\*/'),
        ]
        self.regex = '|'.join('(?P<%s>%s)' % (nome, padrao) for nome, padrao in self.padroes)
        self.padrao_compilado = re.compile(self.regex)

        self.palavras_reservadas = {
            'if': 'SE',
            'else': 'SENAO',
            'while': 'ENQUANTO',
            'for': 'PARA',
            'int': 'TIPO_INT',
            'float': 'TIPO_FLOAT',
            'return': 'RETORNO',
        }
    
    def tokenizar(self, codigo_fonte):
        tokens = []
        linha = 1
        coluna_inicio = 0

        for match in self.padrao_compilado.finditer(codigo_fonte):
            tipo = match.lastgroup
            valor = match.group()
            coluna = match.start() - coluna_inicio

            if tipo == 'ESPACO':
                novas_linhas = valor.count('\n')
                if novas_linhas > 0:
                    linha += novas_linhas
                    coluna_inicio = match.start() + valor.rfind('\n') + 1
                continue
            
            if tipo == 'COMENTARIO':
                novas_linhas = valor.count('\n')
                if novas_linhas > 0:
                    linha += novas_linhas
                    coluna_inicio = match.start() + valor.rfind('\n') + 1
                continue
            
            if tipo == 'ID' and valor in self.palavras_reservadas:
                tipo = self.palavras_reservadas[valor]
   
            token = Token(tipo, valor, linha, coluna)
            tokens.append(token)
 
        tokens.append(Token('EOF', '', linha, 0))
        
        return tokens

if __name__ == '__main__':
    codigo = """
    int soma(int a, int b) {
        // Funcao para somar dois numeros
        return a + b;
    }
    """

    analisador = AnalisadorLexico()
    tokens = analisador.tokenizar(codigo)

    for token in tokens:
        if token.tipo != 'EOF':
            print(token)