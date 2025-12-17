# main.py simplificado

from compiler import LispCompiler

def main():
    # 1. Ler arquivo de teste
    with open("lisp_code.txt", "r") as f:
        lisp_code = f.read()
    
    print("\n=== Código Lisp Original ===")
    print(lisp_code)
    
    # 2. Criar compilador
    compiler = LispCompiler()
    
    # 3. Compilar e executar
    print("\n=== Compilando e Executando ===")
    result = compiler.compile_and_execute(lisp_code)
    
    print(f"\nResultado final: {result}")
    
    # 4. Modo interativo
    print("\n=== Modo Interativo ===")
    compiler.interactive_mode()

if __name__ == "__main__":
    main()
