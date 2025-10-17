from parser import parser
from tokens import lexer

with open("src/lisp_code.txt", "r") as file:
    code = file.read()
    ast = parser.parse(code, lexer=lexer)
    print(ast)
