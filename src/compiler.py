# compiler.py - Liga parser, codegen e interpreter
from parser import parser
from tokens import lexer
from codegen import CodeGenerator
from interpreter import Interpreter
import sys
from io import StringIO

class LispCompiler:
    def __init__(self):
        self.parser = parser
        self.codegen = CodeGenerator()
        self.interpreter = Interpreter()
        self.current_ast = None
        self.current_code = None
    
    def parse(self, lisp_code):
        """Analisa código Lisp e retorna AST."""
        lexer.input(lisp_code)
        self.current_ast = self.parser.parse(lisp_code, lexer=lexer)
        return self.current_ast
    
    def generate_code(self, ast=None):
        """Gera código intermediário a partir da AST."""
        if ast is None:
            ast = self.current_ast
        self.current_code = self.codegen.generate(ast)
        return self.current_code
    
    def execute(self, code=None):
        """Executa código intermediário e retorna resultado."""
        if code is None:
            code = self.current_code
        result = self.interpreter.execute(code)
        return result
    
    def compile_and_execute(self, lisp_code):
        """Compila e executa código Lisp completo."""
        print(f"\n{'='*60}")
        print(f"Compilando: {lisp_code}")
        print('='*60)
        
        try:
            # 1. Análise léxica e sintática
            print("\n1. Análise léxica/sintática...")
            ast = self.parse(lisp_code)
            
            if ast is None:
                print("ERRO: Falha na análise sintática")
                return None
            
            print(f"AST gerada com {len(ast)} elemento(s)")
            
            # 2. Geração de código intermediário
            print("\n2. Gerando código intermediário...")
            intermediate_code = self.generate_code(ast)
            
            print("\nCódigo Intermediário Gerado:")
            print("-" * 40)
            for i, instr in enumerate(intermediate_code):
                print(f"{i:3d}: {instr}")
            
            # 3. Execução
            print("\n3. Executando...")
            print("-" * 40)
            result = self.execute(intermediate_code)
            
            print(f"\n✓ Execução concluída")
            return result
            
        except Exception as e:
            print(f"\n✗ Erro durante compilação/execução: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def compile_and_execute_file(self, filename):
        """Compila e executa código de um arquivo."""
        try:
            with open(filename, 'r') as f:
                lisp_code = f.read()
            
            print(f"\n📁 Lendo arquivo: {filename}")
            print(f"\n📝 Código Lisp:\n{lisp_code}")
            
            # Processar cada expressão separadamente
            lines = lisp_code.strip().split('\n')
            results = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith(';'):  # Ignorar linhas vazias e comentários
                    continue
                    
                # Reiniciar geradores para cada expressão
                self.codegen = CodeGenerator()
                self.interpreter = Interpreter()
                
                result = self.compile_and_execute(line)
                if result is not None:
                    results.append(result)
            
            return results
            
        except FileNotFoundError:
            print(f"ERRO: Arquivo '{filename}' não encontrado")
            return None
    
    def interactive_mode(self):
        """Modo REPL interativo."""
        print("\n" + "="*60)
        print("🎮 INTERPRETADOR LISP INTERATIVO")
        print("="*60)
        print("Comandos disponíveis:")
        print("  <expressão Lisp>  - Avaliar expressão")
        print("  :ast              - Mostrar AST da última expressão")
        print("  :code             - Mostrar código intermediário")
        print("  :mem              - Mostrar estado da memória")
        print("  :reset            - Reiniciar interpretador")
        print("  :quit, :q         - Sair")
        print("="*60)
        
        while True:
            try:
                user_input = input("\nlisp> ").strip()
                
                # Comandos especiais
                if user_input.startswith(':'):
                    cmd = user_input[1:].lower()
                    
                    if cmd in ['quit', 'q', 'exit']:
                        print("👋 Saindo...")
                        break
                    
                    elif cmd == 'ast':
                        if self.current_ast:
                            print("\nAST atual:")
                            from ast_formatter import print_organized_ast
                            print_organized_ast(self.current_ast)
                        else:
                            print("Nenhuma AST disponível")
                    
                    elif cmd == 'code':
                        if self.current_code:
                            print("\nCódigo intermediário atual:")
                            for i, instr in enumerate(self.current_code):
                                print(f"{i:3d}: {instr}")
                        else:
                            print("Nenhum código intermediário disponível")
                    
                    elif cmd == 'mem':
                        print("\nEstado da memória:")
                        print(f"  Último resultado: {self.interpreter.last_result}")
                        print(f"  Variáveis: {self.interpreter.memory}")
                        print(f"  Funções: {list(self.interpreter.functions.keys())}")
                    
                    elif cmd == 'reset':
                        self.codegen = CodeGenerator()
                        self.interpreter = Interpreter()
                        self.current_ast = None
                        self.current_code = None
                        print("✅ Interpretador reiniciado")
                    
                    elif cmd == 'help':
                        print("\nComandos disponíveis:")
                        print("  :ast     - Mostrar AST da última expressão")
                        print("  :code    - Mostrar código intermediário")
                        print("  :mem     - Mostrar estado da memória")
                        print("  :reset   - Reiniciar interpretador")
                        print("  :quit    - Sair")
                    
                    else:
                        print(f"Comando desconhecido: '{cmd}'")
                        print("Use :help para ver comandos disponíveis")
                    
                    continue
                
                # Ignorar entrada vazia
                if not user_input:
                    continue
                
                # Compilar e executar expressão Lisp
                print(f"\n➡️  Avaliando: {user_input}")
                
                # Reiniciar para nova expressão
                self.codegen = CodeGenerator()
                self.interpreter = Interpreter()
                
                result = self.compile_and_execute(user_input)
                
                if result is not None:
                    # Armazenar para possível uso futuro
                    self.interpreter.last_result = result
                    print(f"\n✅ Resultado: {self.interpreter.format_result(result)}")
                
            except KeyboardInterrupt:
                print("\n⚠️  Use ':quit' para sair")
            except EOFError:
                print("\n👋 Saindo...")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}")
    
    def test_suite(self):
        """Executa uma suíte de testes."""
        print("\n🧪 EXECUTANDO SUÍTE DE TESTES")
        print("="*60)
        
        tests = [
            # (descrição, código, resultado esperado)
            ("Soma simples", "(+ 5 3)", 8),
            ("Subtração", "(- 10 4)", 6),
            ("Multiplicação", "(* 3 4)", 12),
            ("Divisão", "(/ 20 5)", 4),
            ("Comparação >", "(> 5 3)", True),
            ("Comparação <", "(< 2 5)", True),
            ("IF verdadeiro", "(if (> 5 3) 10 20)", 10),
            ("IF falso", "(if (< 5 3) 10 20)", 20),
            ("CONS básico", "(cons 1 nil)", [1]),
            ("CAR de lista", "(car (cons 1 (cons 2 nil)))", 1),
            ("CDR de lista", "(cdr (cons 1 (cons 2 nil)))", [2]),
        ]
        
        passed = 0
        failed = 0
        
        for desc, code, expected in tests:
            print(f"\nTeste: {desc}")
            print(f"Código: {code}")
            
            try:
                # Reiniciar para cada teste
                self.codegen = CodeGenerator()
                self.interpreter = Interpreter()
                
                result = self.compile_and_execute(code)
                
                if result == expected:
                    print(f"✅ PASSOU: esperado {expected}, obtido {result}")
                    passed += 1
                else:
                    print(f"❌ FALHOU: esperado {expected}, obtido {result}")
                    failed += 1
                    
            except Exception as e:
                print(f"❌ ERRO: {e}")
                failed += 1
        
        print("\n" + "="*60)
        print(f"RESUMO DOS TESTES: {passed} passaram, {failed} falharam")
        print("="*60)
        
        return passed, failed

# Funções de utilidade
def print_tokens(lisp_code):
    """Imprime tokens gerados pelo lexer."""
    print("\n🔤 TOKENS:")
    print("-" * 40)
    
    lexer.input(lisp_code)
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok)
        print(tok)
    
    print(f"\nTotal de tokens: {len(tokens)}")
    return tokens

def print_ast_tree(ast):
    """Imprime AST em formato de árvore."""
    print("\n🌳 AST:")
    print("-" * 40)
    
    try:
        from ast_formatter import print_organized_ast
        print_organized_ast(ast)
    except ImportError:
        # Fallback simples
        import pprint
        pprint.pprint(ast, indent=2)

def save_outputs(compiler, filename="output.txt"):
    """Salva todas as saídas em um arquivo."""
    import sys
    from io import StringIO
    
    # Capturar stdout
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    
    try:
        # Executar e capturar saída
        if compiler.current_code:
            compiler.interpreter.execute(compiler.current_code)
        
        # Restaurar stdout
        sys.stdout = old_stdout
        
        # Salvar em arquivo
        with open(filename, 'w') as f:
            f.write(captured.getvalue())
        
        print(f"✅ Saída salva em '{filename}'")
        
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ Erro ao salvar saída: {e}")

# Ponto de entrada principal
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compilador/Interpretador Lisp')
    parser.add_argument('--file', '-f', help='Arquivo Lisp para executar')
    parser.add_argument('--expr', '-e', help='Expressão Lisp para executar')
    parser.add_argument('--interactive', '-i', action='store_true', help='Modo interativo')
    parser.add_argument('--test', '-t', action='store_true', help='Executar suíte de testes')
    parser.add_argument('--tokens', action='store_true', help='Mostrar tokens')
    parser.add_argument('--ast', action='store_true', help='Mostrar AST')
    parser.add_argument('--code', action='store_true', help='Mostrar código intermediário')
    
    args = parser.parse_args()
    
    compiler = LispCompiler()
    
    # Modo teste
    if args.test:
        compiler.test_suite()
        return
    
    # Modo arquivo
    if args.file:
        results = compiler.compile_and_execute_file(args.file)
        if results:
            print(f"\n📊 Resultados: {results}")
        return
    
    # Modo expressão única
    if args.expr:
        result = compiler.compile_and_execute(args.expr)
        
        # Opções adicionais
        if args.tokens:
            print_tokens(args.expr)
        
        if args.ast and compiler.current_ast:
            print_ast_tree(compiler.current_ast)
        
        if args.code and compiler.current_code:
            print("\n💻 Código Intermediário:")
            for i, instr in enumerate(compiler.current_code):
                print(f"{i:3d}: {instr}")
        
        if result is not None:
            print(f"\n🎯 Resultado final: {result}")
        return
    
    # Modo interativo (padrão)
    if args.interactive or (not args.file and not args.expr and not args.test):
        compiler.interactive_mode()
        return
    
    # Se nenhum argumento, mostrar ajuda
    parser.print_help()

if __name__ == "__main__":
    main()
