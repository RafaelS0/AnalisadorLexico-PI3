#!/usr/bin/env python3
"""
Interpretador Common Lisp
Uso: python3 repl.py
"""

from parser import parser
from tokens import lexer
from codegen import CodeGenerator
from interpreter import Interpreter
import sys

def format_result(result):
    """Formata resultado para exibição no estilo Lisp"""
    if result == []:
        return 'NIL'
    elif result == True:
        return 'T'
    return result

def main():
    print("=== Interpretador Common Lisp ===")
    print("Digite expressões Lisp ou 'quit' para sair")
    print("Exemplos: (+ 1 2), (- 10 5), (* 3 4), (/ 20 4), (expt 2 3)")
    print()
    
    # Carrega funções do arquivo (se existir)
    interpreter = Interpreter()
    try:
        with open("lisp_code.txt", "r") as f:
            code = f.read()
            lexer.input(code)
            ast = parser.parse(code, lexer=lexer)
            if ast:
                generator = CodeGenerator()
                intermediate = generator.generate(ast)
                interpreter.execute(intermediate)
                print("Funções carregadas de lisp_code.txt")
                print("Funções disponíveis:", list(interpreter.functions.keys()))
                print()
    except FileNotFoundError:
        print("Arquivo lisp_code.txt não encontrado - apenas expressões básicas disponíveis")
        print()
    
    # Loop principal do REPL
    while True:
        try:
            # Lê entrada do usuário
            user_input = input("lisp> ").strip()
            
            # Comandos especiais
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Saindo...")
                break
            
            if user_input.lower() == 'help':
                print("Comandos disponíveis:")
                print("  quit/exit/q - Sair do interpretador")
                print("  help - Mostrar esta ajuda")
                print("  funcs - Listar funções disponíveis")
                print("Operações: +, -, *, /, expt, mod, floor")
                print("Exemplo: (+ 1 2)")
                continue
                
            if user_input.lower() == 'funcs':
                if interpreter.functions:
                    print("Funções disponíveis:", list(interpreter.functions.keys()))
                else:
                    print("Nenhuma função definida")
                continue
            
            # Ignora linhas vazias
            if not user_input:
                continue
            
            # Processa entrada Lisp
            lexer.input(user_input)
            ast = parser.parse(user_input, lexer=lexer)
            
            if ast is None:
                print("Erro: Sintaxe inválida")
                continue
            
            # Gera e executa código intermediário
            generator = CodeGenerator()
            intermediate = generator.generate(ast)
            interpreter.execute(intermediate)
            
        except KeyboardInterrupt:
            print("\nUse 'quit' para sair")
        except EOFError:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()