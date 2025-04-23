// Exemplo de código para teste do analisador léxico
int fatorial(int n) {
    // Função para calcular o fatorial de um número
    if (n <= 1) {
        return 1;
    } else {
        return n * fatorial(n - 1);
    }
}

int main() {
    int num = 5;
    int resultado = fatorial(num);
    
    /* Este é um comentário de 
       múltiplas linhas para testar
       o analisador léxico */
    
    return 0;
}