from parser import parser
from tokens import lexer
from codegen import CodeGenerator
from ast_formatter import print_organized_ast
from interpreter import Interpreter


#########  Gerar e imprimir a análise léxica  #########


# Abre o arquivo com o código e o lê
with open("lisp_code.txt") as f:
    code = f.read()

# Alimenta o lexer
lexer.input(code)

# Imprime e salva a análise léxica
print("\n")
tokens_list = []
for tok in lexer:
    print(tok)
    tokens_list.append(str(tok))

# Salva tokens em arquivo
with open("tokens.txt", "w") as f:
    f.write("=== ANÁLISE LÉXICA (TOKENS) ===\n")
    for token in tokens_list:
        f.write(token + "\n")


################   Gerar e imprimir a AST  ##################


# Abre o arquivo com o código e o lê
with open("lisp_code.txt", "r") as file:
    code = file.read()

# Alimenta o parser
ast = parser.parse(code, lexer=lexer)


# Imprime AST em formato de árvore
print("\n=== AST ===")
print_organized_ast(ast)

# Salva AST em arquivo
with open("ast_tree.txt", "w") as f:
    import sys
    from io import StringIO
    
    # Captura a saída do print_organized_ast
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    print_organized_ast(ast)
    
    # Restaura stdout e pega o conteúdo
    sys.stdout = old_stdout
    ast_content = captured_output.getvalue()
    
    # Escreve no arquivo
    f.write("=== (AST) ===\n")
    f.write(ast_content)
    
print("\nAST salva em 'ast_tree.txt'")



#################  Gerar e imprimir o código intermediário ##################


# Cria uma intância do gerador de código intermediário
generator = CodeGenerator()

# Alimenta e o gerador e gear o código intermediário
intermediate = generator.generate(ast)

# Imprime o código intermediário no terminal
print("\n=== Código Intermediário ===")
for instr in intermediate:
    print(instr)

# Escreve o código intermediário em um arquivo no formato de lista
with open("codigo_intermediario.txt", "w") as f:
    f.write("[\n")
    for i, instr in enumerate(intermediate):
        f.write(f"   {repr(instr)}")
        if i < len(intermediate) - 1:
            f.write(",")
        f.write("\n")
    f.write("]")

interpreter = Interpreter() # Instanciando o interpretador



###################  TESTES DO  Interpretador ###########################


# TESTE: Executar código CLisp diretamente pela main.py
print("\n=== Teste de Operações Aritméticas ===")

# Teste 1: Subtração
lisp_code_sub = "(- 5 3 )"
lexer.input(lisp_code_sub)  # Resetar lexer
ast_sub = parser.parse(lisp_code_sub, lexer=lexer)
generator_sub = CodeGenerator()
intermediate_sub = generator_sub.generate(ast_sub)
print("Executando: (- 5 3)")
interpreter.execute(intermediate_sub)

# Teste 2: Divisão
lisp_code_div = "(/ 20 4)"
lexer.input(lisp_code_div)  # Resetar lexer
ast_div = parser.parse(lisp_code_div, lexer=lexer)
generator_div = CodeGenerator()
intermediate_div = generator_div.generate(ast_div)
print("Executando: (/ 20 4)")
interpreter.execute(intermediate_div)

# Teste 3: Multiplicação
lisp_code_mult = "(* 2 3)"
lexer.input(lisp_code_mult)  # Resetar lexer
ast_mult = parser.parse(lisp_code_mult, lexer=lexer)
generator_mult = CodeGenerator()
intermediate_mult = generator_mult.generate(ast_mult)
print("Executando: (* 2 3)")
interpreter.execute(intermediate_mult)

# Teste 4: Potência
lisp_code_expt = "(expt 2 3)"
lexer.input(lisp_code_expt)  # Resetar lexer
ast_expt = parser.parse(lisp_code_expt, lexer=lexer)
generator_expt = CodeGenerator()
intermediate_expt = generator_expt.generate(ast_expt)
print("Executando: (expt 2 3)")
interpreter.execute(intermediate_expt)




print("Código intermediário salvo em 'codigo_intermediario.txt'")
print("AST salva em 'ast_tree.txt'")
print("Tokens salvos em 'tokens.txt'")
interpreter.execute(intermediate)

# Teste 1: soma de lista [1, 2, 3]
print("\nTeste: (soma '(1 2 3))")
result = interpreter.call_function(intermediate, 'soma', [[1, 2]])
print(f"Resultado: {result}")

# Teste 2: menor elemento
print("\nTeste: (menor 5 '(3 7 2))")
result = interpreter.call_function(intermediate, 'menor', [5, [1, 7, 4]])
print(f"Resultado: {result}")

# Teste 3: retirar elemento
print("\nTeste: (retirar 2 '(1 2 3 2 4))")
result = interpreter.call_function(intermediate, 'retirar', [6, [1, 2, 3, 2, 4]])
print(f"Resultado: {result}")


###################     Interpretador Interativo  ###########################


print("\n" + "="*50)
resposta = input("Deseja iniciar o interpretador? (s/n): ").strip().lower()

if resposta in ['s', 'sim', 'y', 'yes']:
    print("\nIniciando ...")
    print("Digite 'q' para encerrar")
    print()
    
    # Loop do interpretador
    while True:
        try:
            user_input = input("lisp> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Saindo...")
                break
            
            if not user_input:
                continue
            
            # Processa entrada Lisp
            lexer.input(user_input)
            ast_repl = parser.parse(user_input, lexer=lexer)
            
            if ast_repl is None:
                print("Erro: Sintaxe inválida")
                continue
            
            # Gera e executa código intermediário
            generator_repl = CodeGenerator()
            intermediate_repl = generator_repl.generate(ast_repl)
            interpreter.execute(intermediate_repl)
            
        except KeyboardInterrupt:
            print("\nUse 'q' para sair")
        except EOFError:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")
else:
    print("Programa finalizado.")




