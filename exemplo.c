
int fatorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * fatorial(n - 1);
    }
}

int main() {
    int num = 5;
    int resultado = fatorial(num);
    
    /* Esse e um comentario para testar
       o analisador lexico */
    
    return 0;
}