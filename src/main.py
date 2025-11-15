from parser import parser
from tokens import lexer
from codegen import CodeGenerator

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

# Imprime a AST
print("\n")
print(ast)

# ==============================
#     Gerar e imprimir o código intermediário
# ==============================

# Cria uma intância do gerador de código intermediário
generator = CodeGenerator()

# Alimenta e o gerador e gear o código intermediário
intermediate = generator.generate(ast)

# Imprime o código intermediário
print("\n")
for instr in intermediate:
    print(instr)
