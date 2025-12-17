import pprint
import os
from tokens import lexer
from parser import parser
from codegen import CodeGenerator

def save_outputs(tokens_list, ast, intermediate_code):
    os.makedirs("saidas_codigo", exist_ok=True)
    
    with open("saidas_codigo/tokens.txt", "w") as f:
        for tok in tokens_list:
            f.write(f"{tok}\n")
    
    with open("saidas_codigo/ast.txt", "w") as f:
        pp = pprint.PrettyPrinter(indent=4, width=80, stream=f)
        pp.pprint(ast)
    
    with open("saidas_codigo/codigo_intermediario.txt", "w") as f:
        for instr in intermediate_code:
            f.write(f"{instr}\n")
    
    print("\n✓ Saídas salvas na pasta 'saidas_codigo/'")


def main():
    filename = "src/lisp_code.txt"

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
    
    lexer.input(data)
    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(tok)
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
        print(f"\nTipo da AST: {type(result)}")
    else:
        print("O Parser retornou vazio. Verifique se há erros de sintaxe acima.")



    # ---------------------------------------------------------
    # 4. Geração do Código Intermediário 
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print(">>> INICIANDO GERAÇÃO DE CÓDIGO INTERMEDIÁRIO <<<")
    print("="*50)

    try:
        codegen = CodeGenerator()
        intermediate_code = codegen.generate(result)
        print("Código Intermediário gerado:\n")
        for instr in intermediate_code:
            print(instr)
        
        # Salvar saídas em arquivos
        if result and intermediate_code:
            save_outputs(tokens_list, result, intermediate_code)
    except (TypeError, NotImplementedError) as e:
        print(f"ERRO: {e}")
    except Exception as e:
        print(f"ERRO inesperado: {e}")





if __name__ == "__main__":
    main()