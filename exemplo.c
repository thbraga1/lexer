int soma(int a, int b) {
    // Função que soma dois números
    return a + b;
}

float media(int x, int y) {
    float resultado;
    resultado = (x + y) / 2;
    return resultado;
}

int main() {
    int num1;
    int num2;
    float result;
    int nao_usado;  // Esta variável não será usada (gera aviso)
    
    num1 = 10;
    num2 = 20;
    result = num1 + num2;  // Conversão implícita int para float
    
    // Erro: variável não declarada
    // valor = 5;
    
    return 0;
}