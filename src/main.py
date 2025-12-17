import sys
import pprint # Biblioteca para imprimir a árvore de forma bonita
from tokens import lexer
from parser import parser # Certifique-se que o arquivo do parser se chama parser_lisp.py

def main():
    filename = "lisp_code.txt"

    # 1. Leitura do Arquivo
    try:
        with open(filename, 'r') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{filename}' não foi encontrado.")
        return

    print("="*50)
    print(f"LENDO ARQUIVO: {filename}")
    print("="*50)
    print(data)
    print("\n" + "="*50)

    # ---------------------------------------------------------
    # 2. Execução do LEXER (Visualizar Tokens)
    # ---------------------------------------------------------
    print(">>> INICIANDO ANÁLISE LÉXICA (TOKENS) <<<")
    print("-" * 50)
    
    # Alimentamos o lexer com os dados
    lexer.input(data)

    # Loop para imprimir cada token encontrado
    while True:
        tok = lexer.token()
        if not tok:
            break      # Sem mais dados
        print(tok)

    print("-" * 50)
    print("Análise Léxica concluída.\n")

    # ---------------------------------------------------------
    # 3. Execução do PARSER (Visualizar Árvore Sintática)
    # ---------------------------------------------------------
    print("="*50)
    print(">>> INICIANDO ANÁLISE SINTÁTICA (AST) <<<")
    print("="*50)

    # O parser vai chamar o lexer internamente novamente do zero.
    # Passamos o lexer explicitamente para garantir que ele use as regras corretas.
    result = parser.parse(data, lexer=lexer)

    if result:
        print("Árvore gerada com sucesso:\n")
        # PrettyPrinter ajuda a identar as tuplas e listas para facilitar a leitura
        pp = pprint.PrettyPrinter(indent=4, width=80)
        pp.pprint(result)
    else:
        print("O Parser retornou vazio. Verifique se há erros de sintaxe acima.")

if __name__ == "__main__":
    main()