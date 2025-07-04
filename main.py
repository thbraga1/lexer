import sys
from analisador_lexico import AnalisadorLexico
from analisador_sintatico import AnalisadorSintatico, imprimir_arvore

def formatar_tokens(tokens):
    """Formata e exibe os tokens de forma organizada"""
    print(f"{'TIPO':<15} | {'VALOR':<15} | {'LINHA':<5} | {'COLUNA':<6}")
    print(f"{'-' * 15} | {'-' * 15} | {'-' * 5} | {'-' * 6}")
    
    for token in tokens:
        if token.tipo != 'EOF':  
            print(f"{token.tipo:<15} | {token.valor:<15} | {token.linha:<5} | {token.coluna:<6}")
    
    print(f"\nTotal de tokens: {len(tokens) - 1}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python main_sintatico.py <arquivo_codigo>")
        print("Ou: python main_sintatico.py --entrada")
        print("Ou: python main_sintatico.py <arquivo_codigo> --tokens (para mostrar apenas tokens)")
        return

    # Determina se deve mostrar apenas tokens
    apenas_tokens = '--tokens' in sys.argv

    # Cria os analisadores
    analisador_lexico = AnalisadorLexico()
    codigo_fonte = ""
    
    # Lê o código fonte
    if sys.argv[1] == "--entrada":
        print("Digite seu código (termine com Ctrl+D no Linux/Mac ou Ctrl+Z no Windows):")
        codigo_fonte = sys.stdin.read()
    else:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as arquivo:
                codigo_fonte = arquivo.read()
        except FileNotFoundError:
            print(f"Erro: Arquivo '{sys.argv[1]}' não encontrado.")
            return
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return

    # Análise léxica
    print("=== INICIANDO ANÁLISE LÉXICA ===")
    try:
        tokens = analisador_lexico.tokenizar(codigo_fonte)
        print("✅ Análise léxica concluída com sucesso!")
        
        print("\n=== TOKENS GERADOS ===")
        formatar_tokens(tokens)
        
        # Se foi solicitado apenas tokens, para aqui
        if apenas_tokens:
            return
            
    except Exception as e:
        print(f"❌ Erro na análise léxica: {e}")
        return

    # Análise sintática
    print("\n" + "="*50)
    print("=== INICIANDO ANÁLISE SINTÁTICA ===")
    
    try:
        analisador_sintatico = AnalisadorSintatico(tokens)
        arvore = analisador_sintatico.analisar()
        
        if arvore:
            print("✅ Análise sintática concluída com sucesso!")
            print("\n=== ÁRVORE SINTÁTICA ABSTRATA ===")
            imprimir_arvore(arvore)
            
            # Estatísticas da análise
            print(f"\n=== ESTATÍSTICAS ===")
            print(f"📄 Código analisado: {len(codigo_fonte.splitlines())} linhas")
            print(f"🔤 Tokens processados: {len(tokens) - 1}")
            print(f"🌳 Análise sintática: Sucesso")
            
        else:
            print("❌ Falha na análise sintática.")
            
    except Exception as e:
        print(f"❌ Erro na análise sintática: {e}")
        return

def teste_exemplos():
    """Função para testar o analisador com vários exemplos"""
    exemplos = [
        # Exemplo 1: Função simples
        """
        int soma(int a, int b) {
            return a + b;
        }
        """,
        
        # Exemplo 2: Função com if-else
        """
        int maximo(int a, int b) {
            if (a + b) {
                return a;
            } else {
                return b;
            }
        }
        """,
        
        # Exemplo 3: Função com while
        """
        int fatorial(int n) {
            int resultado = 1;
            while (n) {
                resultado = resultado * n;
                n = n - 1;
            }
            return resultado;
        }
        """,
        
        # Exemplo 4: Função com for
        """
        int potencia(int base, int exp) {
            int resultado = 1;
            for (int i = 0; i; i = i + 1) {
                resultado = resultado * base;
            }
            return resultado;
        }
        """
    ]
    
    analisador_lexico = AnalisadorLexico()
    
    for i, codigo in enumerate(exemplos, 1):
        print(f"\n{'='*60}")
        print(f"=== EXEMPLO {i} ===")
        print(f"{'='*60}")
        print("CÓDIGO:")
        print(codigo.strip())
        
        print(f"\n--- ANÁLISE LÉXICA ---")
        try:
            tokens = analisador_lexico.tokenizar(codigo)
            print(f"✅ {len(tokens) - 1} tokens gerados")
            
            print(f"\n--- ANÁLISE SINTÁTICA ---")
            analisador_sintatico = AnalisadorSintatico(tokens)
            arvore = analisador_sintatico.analisar()
            
            if arvore:
                print("✅ Análise sintática bem-sucedida!")
                print("\nÁRVORE:")
                imprimir_arvore(arvore)
            else:
                print("❌ Falha na análise sintática")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--teste":
        teste_exemplos()
    else:
        main()