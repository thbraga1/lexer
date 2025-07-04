// Exemplo de programa para testar o compilador
// Arquivo: exemplo.c

int soma(int a, int b) {
    return a + b;
}

int fatorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * fatorial(n - 1);
}

int main() {
    int x = 5;
    int y = 3;
    int resultado_soma = soma(x, y);
    
    int num = 5;
    int resultado_fatorial = fatorial(num);
    
    // Teste de loop
    int i = 0;
    int contador = 0;
    for (i = 0; i < 10; i = i + 1) {
        contador = contador + 1;
    }
    
    // Teste de condição
    if (resultado_soma > 5) {
        return resultado_fatorial;
    } else {
        return contador;
    }
}