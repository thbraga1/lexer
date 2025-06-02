import sys
from analisador_lexico import AnalisadorLexico
from analisador_semantico import AnalisadorSemantico

def formatar_tokens(tokens):
    """Formata e exibe os tokens gerados pelo analisador léxico"""
    print(f"{'TIPO':<15} | {'VALOR':<15} | {'LINHA':<5} | {'COLUNA':<6}")
    print(f"{'-' * 15} | {'-' * 15} | {'-' * 5} | {'-' * 6}")
    
    for token in tokens:
        if token.tipo != 'EOF':  
            print(f"{token.tipo:<15} | {token.valor:<15} | {token.linha:<5} | {token.coluna:<6}")
    
    print(f"\nTotal de tokens: {len(tokens) - 1}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_codigo> [opcoes]")
        print("Ou: python main.py --entrada [opcoes]")
        print("\nOpções:")
        print("  --apenas-lexico    : Executa apenas a análise léxica")
        print("  --apenas-semantico : Executa apenas a análise semântica")
        print("  --completo         : Executa análise léxica + semântica (padrão)")
        return

    # Configurações
    apenas_lexico = '--apenas-lexico' in sys.argv
    apenas_semantico = '--apenas-semantico' in sys.argv
    completo = '--completo' in sys.argv or (not apenas_lexico and not apenas_semantico)

    analisador_lexico = AnalisadorLexico()
    codigo_fonte = ""
    
    # Leitura do código fonte
    if sys.argv[1] == "--entrada":
        print("Digite seu código (termine com Ctrl+D no Linux/Mac ou Ctrl+Z no Windows):")
        try:
            codigo_fonte = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            return
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

    # Verifica se há código para analisar
    if not codigo_fonte.strip():
        print("Aviso: Código fonte vazio.")
        return

    # Análise Léxica
    print("Executando análise léxica...")
    tokens = analisador_lexico.tokenizar(codigo_fonte)

    if apenas_lexico or completo:
        print("\n" + "="*60)
        print("RESULTADO DA ANÁLISE LÉXICA")
        print("="*60)
        formatar_tokens(tokens)

    # Análise Semântica
    if apenas_semantico or completo:
        print("\nExecutando análise semântica...")
        
        analisador_semantico = AnalisadorSemantico(tokens)
        sucesso = analisador_semantico.analisar()
        
        analisador_semantico.imprimir_resultados()
        
        # Status final
        if sucesso:
            print("\n🎉 Análise concluída com sucesso!")
        else:
            print("\n❌ Análise concluída com erros.")

if __name__ == "__main__":
    main()