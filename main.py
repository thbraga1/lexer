import sys
from analisador_lexico import AnalisadorLexico

def formatar_tokens(tokens):
    print(f"{'TIPO':<15} | {'VALOR':<15} | {'LINHA':<5} | {'COLUNA':<6}")
    print(f"{'-' * 15} | {'-' * 15} | {'-' * 5} | {'-' * 6}")
    
    for token in tokens:
        if token.tipo != 'EOF':  
            print(f"{token.tipo:<15} | {token.valor:<15} | {token.linha:<5} | {token.coluna:<6}")
    
    print(f"\nTotal de tokens: {len(tokens) - 1}")  

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_codigo>")
        print("Ou: python main.py --entrada")
        return

    analisador = AnalisadorLexico()

    codigo_fonte = ""
    
    if sys.argv[1] == "--entrada":
        print("Digite seu codigo (termine com Ctrl+D no Linux/Mac ou Ctrl+Z no Windows):")
        codigo_fonte = sys.stdin.read()
    else:
        try:
            with open(sys.argv[1], 'r') as arquivo:
                codigo_fonte = arquivo.read()
        except FileNotFoundError:
            print(f"Erro: Arquivo '{sys.argv[1]}' não encontrado.")
            return
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return

    tokens = analisador.tokenizar(codigo_fonte)

    print("\nRESULTADO DA ANALISE LEXICA:")
    formatar_tokens(tokens)

if __name__ == "__main__":
    main()