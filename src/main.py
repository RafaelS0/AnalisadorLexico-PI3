from parser import parser
from tokens import lexer
from codegen import CodeGenerator
from ast_formatter import print_organized_ast
from interpreter import Interpreter


# ==============================
#     Gerar e imprimir a análise léxica
# ==============================

# Abre o arquivo com o código e o lê
with open("lisp_code.txt") as f:
    code = f.read()

# Alimenta o lexer
lexer.input(code)

# Imprime a análise léxica
print("\n")
for tok in lexer:
    print(tok)

# ==============================
#     Gerar e imprimir a AST
# ==============================

# Abre o arquivo com o código e o lê
with open("lisp_code.txt", "r") as file:
    code = file.read()

# Alimenta o parser
ast = parser.parse(code, lexer=lexer)


# Imprime AST em formato de árvore
print("\n=== AST ===")
print_organized_ast(ast)


# ==============================
#     Gerar e imprimir o código intermediário
# ==============================

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

print("\n Código intermediário salvo em 'codigo_intermediario.txt'")

# ==============================
#     Executar código intermediário
# ==============================

print("\n=== Executando Código Intermediário ===")
interpreter = Interpreter()
interpreter.execute(intermediate)


# Teste 1: soma de lista [1, 2, 3]
print("\nTeste: (soma '(1 2 3))")
result = interpreter.call_function(intermediate, 'soma', [[1, 2, 3]])
print(f"Resultado: {result}")

# Teste 2: menor elemento
print("\nTeste: (menor 5 '(3 7 2))")
result = interpreter.call_function(intermediate, 'menor', [5, [3, 7, 2]])
print(f"Resultado: {result}")

# Teste 3: retirar elemento
print("\nTeste: (retirar 2 '(1 2 3 2 4))")
result = interpreter.call_function(intermediate, 'retirar', [2, [1, 2, 3, 2, 4]])
print(f"Resultado: {result}")
