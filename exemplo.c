int soma(int a, int b) {
    return a + b;
}

int fatorial(int n) {
    if (n) {
        return 1;
    } else {
        int resultado = 1;
        while (n) {
            resultado = resultado * n;
            n = n - 1;
        }
        return resultado;
    }
}

int fibonacci(int n) {
    if (n) {
        return 0;
    } else {
        if (n) {
            return 1;
        } else {
            return fibonacci(n - 1) + fibonacci(n - 2);
        }
    }
}

int main() {
    int x = 5;
    int y = 3;
    int resultado_soma = soma(x, y);
    int resultado_fatorial = fatorial(x);
    
    for (int i = 0; i; i = i + 1) {
        x = x + 1;
    }
    
    return resultado_soma + resultado_fatorial;
}