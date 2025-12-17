# compiler.py - Liga parser, codegen e interpreter
from parser import parser
from tokens import lexer
from codegen import CodeGenerator
from interpreter import Interpreter
import os
import sys

class LispCompiler:
    def __init__(self):
        self.parser = parser
        self.codegen = CodeGenerator()
        self.interpreter = Interpreter()
        self.current_ast = None
        self.current_code = None
        self.current_filename = None
    
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
        print(f"Compilando: {lisp_code[:50]}{'...' if len(lisp_code) > 50 else ''}")
        print('='*60)
        
        try:
            # 1. Análise léxica e sintática
            print("\n1. Análise léxica/sintática...")
            ast = self.parse(lisp_code)
            
            if ast is None:
                print("ERRO: Falha na análise sintática")
                return None
            
            print(f"✓ AST gerada com {len(ast)} elemento(s)")
            
            # 2. Geração de código intermediário
            print("\n2. Gerando código intermediário...")
            intermediate_code = self.generate_code(ast)
            
            print(f"✓ Gerado {len(intermediate_code)} instruções")
            
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
            if not os.path.exists(filename):
                print(f"ERRO: Arquivo '{filename}' não encontrado")
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                lisp_code = f.read()
            
            self.current_filename = filename
            
            print(f"\n📁 Arquivo: {filename}")
            print(f"📏 Tamanho: {len(lisp_code)} caracteres")
            print(f"📄 Conteúdo:\n{'-'*40}")
            print(lisp_code)
            print(f"{'-'*40}")
            
            # Processar todo o arquivo como uma única unidade
            result = self.compile_and_execute(lisp_code)
            
            # Salvar outputs
            self.save_outputs()
            
            return result
            
        except Exception as e:
            print(f"ERRO ao processar arquivo: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_outputs(self, base_name=None):
        """Salva tokens, AST e código intermediário em arquivos."""
        if base_name is None:
            if self.current_filename:
                base_name = os.path.splitext(self.current_filename)[0]
            else:
                base_name = "output"
        
        try:
            # 1. Salvar tokens
            if hasattr(self, 'current_ast') and self.current_ast is not None:
                tokens_file = f"{base_name}_tokens.txt"
                self.save_tokens(tokens_file)
                print(f"✓ Tokens salvos em: {tokens_file}")
            
            # 2. Salvar AST
            if self.current_ast is not None:
                ast_file = f"{base_name}_ast.txt"
                from ast_formatter import save_ast_to_file
                save_ast_to_file(self.current_ast, ast_file)
                print(f"✓ AST salva em: {ast_file}")
            
            # 3. Salvar código intermediário
            if self.current_code is not None:
                code_file = f"{base_name}_code.txt"
                self.save_intermediate_code(code_file)
                print(f"✓ Código intermediário salvo em: {code_file}")
            
            # 4. Salvar resultado da execução
            if self.interpreter.last_result is not None:
                result_file = f"{base_name}_result.txt"
                with open(result_file, 'w', encoding='utf-8') as f:
                    f.write(f"Resultado: {self.interpreter.last_result}\n")
                print(f"✓ Resultado salvo em: {result_file}")
                
        except Exception as e:
            print(f"⚠️  Aviso ao salvar outputs: {e}")
    
    def save_tokens(self, filename):
        """Salva tokens em arquivo."""
        if self.current_ast is None:
            return
        
        try:
            # Recria tokens a partir do código atual
            from tokens import lexer
            with open(self.current_filename, 'r', encoding='utf-8') as f:
                code = f.read()
            
            lexer.input(code)
            tokens = []
            while True:
                tok = lexer.token()
                if not tok:
                    break
                tokens.append(tok)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== TOKENS ===\n")
                for tok in tokens:
                    f.write(f"{tok}\n")
                f.write(f"\nTotal: {len(tokens)} tokens\n")
                
        except Exception as e:
            print(f"Erro ao salvar tokens: {e}")
    
    def save_intermediate_code(self, filename):
        """Salva código intermediário em arquivo."""
        if self.current_code is None:
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== CÓDIGO INTERMEDIÁRIO ===\n")
            f.write(f"Instruções: {len(self.current_code)}\n\n")
            for i, instr in enumerate(self.current_code):
                f.write(f"{i:4d}: {instr}\n")
    
    def interactive_mode(self):
        """Modo REPL interativo."""
        self.show_main_menu()
    
    def show_main_menu(self):
        """Mostra menu principal com opções."""
        while True:
            print("\n" + "="*60)
            print("🏆 COMPILADOR/INTERPRETADOR LISP")
            print("="*60)
            print("1. 📁 Carregar arquivo Lisp")
            print("2. ✏️  Modo interativo (REPL)")
            print("3. 🧪 Executar suíte de testes")
            print("4. 📊 Mostrar informações do sistema")
            print("5. 🚪 Sair")
            print("="*60)
            
            choice = input("\nEscolha uma opção (1-5): ").strip()
            
            if choice == '1':
                self.file_menu()
            elif choice == '2':
                self.repl_menu()
            elif choice == '3':
                self.test_suite()
            elif choice == '4':
                self.show_system_info()
            elif choice == '5':
                print("\n👋 Saindo do programa...")
                break
            else:
                print("❌ Opção inválida! Tente novamente.")
    
    def file_menu(self):
        """Menu para seleção e processamento de arquivos."""
        while True:
            print("\n" + "="*60)
            print("📁 MENU DE ARQUIVOS")
            print("="*60)
            print("1. 📂 Listar arquivos .lisp/.txt no diretório atual")
            print("2. ⌨️  Digitar caminho do arquivo")
            print("3. ↩️  Voltar ao menu principal")
            print("="*60)
            
            choice = input("\nEscolha uma opção (1-3): ").strip()
            
            if choice == '1':
                self.list_and_select_file()
            elif choice == '2':
                self.enter_file_path()
            elif choice == '3':
                break
            else:
                print("❌ Opção inválida!")
    
    def list_and_select_file(self):
        """Lista arquivos e permite selecionar um."""
        # Listar arquivos Lisp e TXT
        lisp_files = []
        txt_files = []
        
        for file in os.listdir('.'):
            if file.endswith('.lisp'):
                lisp_files.append(file)
            elif file.endswith('.txt'):
                txt_files.append(file)
        
        all_files = sorted(lisp_files) + sorted(txt_files)
        
        if not all_files:
            print("\n📭 Nenhum arquivo .lisp ou .txt encontrado no diretório atual.")
            return
        
        print("\n📋 Arquivos disponíveis:")
        print("-" * 40)
        
        for i, filename in enumerate(all_files, 1):
            size = os.path.getsize(filename)
            print(f"{i:2d}. {filename} ({size} bytes)")
        
        print("-" * 40)
        print(f"{len(all_files) + 1:2d}. Voltar")
        
        try:
            choice = int(input(f"\nSelecione um arquivo (1-{len(all_files) + 1}): "))
            
            if 1 <= choice <= len(all_files):
                filename = all_files[choice - 1]
                self.process_selected_file(filename)
            elif choice == len(all_files) + 1:
                return
            else:
                print("❌ Seleção inválida!")
        except ValueError:
            print("❌ Por favor, digite um número.")
    
    def enter_file_path(self):
        """Permite digitar o caminho do arquivo."""
        filepath = input("\nDigite o caminho do arquivo: ").strip()
        
        if not filepath:
            print("❌ Caminho vazio!")
            return
        
        # Adicionar extensão .lisp se não tiver
        if not (filepath.endswith('.lisp') or filepath.endswith('.txt')):
            filepath += '.lisp'
        
        self.process_selected_file(filepath)
    
    def process_selected_file(self, filename):
        """Processa o arquivo selecionado."""
        print(f"\n📄 Processando arquivo: {filename}")
        print("-" * 40)
        
        try:
            # Reiniciar compilador para novo arquivo
            self.codegen = CodeGenerator()
            self.interpreter = Interpreter()
            self.current_ast = None
            self.current_code = None
            
            # Compilar e executar
            result = self.compile_and_execute_file(filename)
            
            if result is not None:
                print(f"\n🎯 Resultado final: {result}")
            
            input("\nPressione Enter para continuar...")
            
        except Exception as e:
            print(f"❌ Erro ao processar arquivo: {e}")
            input("\nPressione Enter para continuar...")
    
    def repl_menu(self):
        """Menu do modo REPL interativo."""
        print("\n" + "="*60)
        print("✏️  MODO INTERATIVO LISP (REPL)")
        print("="*60)
        print("Digite expressões Lisp para avaliar")
        print("Comandos especiais:")
        print("  :ast     - Mostrar AST da última expressão")
        print("  :code    - Mostrar código intermediário")
        print("  :mem     - Mostrar estado da memória")
        print("  :reset   - Reiniciar interpretador")
        print("  :save    - Salvar outputs em arquivo")
        print("  :back    - Voltar ao menu principal")
        print("  :quit    - Sair do programa")
        print("="*60)
        
        while True:
            try:
                user_input = input("\nlisp> ").strip()
                
                # Comandos especiais
                if user_input.startswith(':'):
                    cmd = user_input[1:].lower()
                    
                    if cmd in ['back', 'b']:
                        break
                    elif cmd in ['quit', 'q', 'exit']:
                        print("👋 Saindo do programa...")
                        sys.exit(0)
                    elif cmd == 'ast':
                        self.show_current_ast()
                    elif cmd == 'code':
                        self.show_current_code()
                    elif cmd == 'mem':
                        self.show_memory_state()
                    elif cmd == 'reset':
                        self.reset_compiler()
                    elif cmd == 'save':
                        self.save_repl_outputs()
                    elif cmd == 'help':
                        self.show_repl_help()
                    else:
                        print(f"❌ Comando desconhecido: '{cmd}'")
                    
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
                    print(f"\n✅ Resultado: {self.interpreter.format_result(result)}")
                
            except KeyboardInterrupt:
                print("\n⚠️  Use ':back' para voltar ou ':quit' para sair")
            except EOFError:
                print("\n👋 Saindo...")
                break
            except Exception as e:
                print(f"\n❌ Erro: {e}")
    
    def show_current_ast(self):
        """Mostra AST atual."""
        if self.current_ast:
            from ast_formatter import print_organized_ast
            print_organized_ast(self.current_ast)
        else:
            print("Nenhuma AST disponível")
    
    def show_current_code(self):
        """Mostra código intermediário atual."""
        if self.current_code:
            print("\n💻 Código Intermediário:")
            print("-" * 40)
            for i, instr in enumerate(self.current_code):
                print(f"{i:4d}: {instr}")
        else:
            print("Nenhum código intermediário disponível")
    
    def show_memory_state(self):
        """Mostra estado da memória."""
        print("\n💾 Estado da Memória:")
        print(f"  Último resultado: {self.interpreter.last_result}")
        print(f"  Variáveis temporárias: {len([k for k in self.interpreter.memory if k.startswith('t')])}")
        print(f"  Funções definidas: {list(self.interpreter.functions.keys())}")
        
        if self.interpreter.memory:
            print("\n  Conteúdo da memória:")
            for key, value in sorted(self.interpreter.memory.items()):
                print(f"    {key}: {value}")
    
    def reset_compiler(self):
        """Reinicia o compilador."""
        self.codegen = CodeGenerator()
        self.interpreter = Interpreter()
        self.current_ast = None
        self.current_code = None
        print("✅ Compilador reiniciado")
    
    def save_repl_outputs(self):
        """Salva outputs do REPL."""
        base_name = input("Digite o nome base para os arquivos (ou Enter para 'repl'): ").strip()
        if not base_name:
            base_name = "repl"
        
        self.save_outputs(base_name)
        print(f"✅ Outputs salvos com prefixo '{base_name}_'")
    
    def show_repl_help(self):
        """Mostra ajuda do REPL."""
        print("\n📚 AJUDA DO REPL")
        print("-" * 40)
        print("Comandos disponíveis:")
        print("  :ast     - Mostrar AST da última expressão")
        print("  :code    - Mostrar código intermediário")
        print("  :mem     - Mostrar estado da memória")
        print("  :reset   - Reiniciar interpretador")
        print("  :save    - Salvar outputs em arquivo")
        print("  :back    - Voltar ao menu principal")
        print("  :quit    - Sair do programa")
        print("  :help    - Mostrar esta ajuda")
    
    def test_suite(self):
        """Executa uma suíte de testes."""
        print("\n🧪 EXECUTANDO SUÍTE DE TESTES")
        print("="*60)
        
        tests = [
            ("Soma simples", "(+ 5 3)", 8),
            ("Subtração", "(- 10 4)", 6),
            ("Multiplicação", "(* 3 4)", 12),
            ("Divisão inteira", "(/ 20 5)", 4),
            ("Maior que", "(> 5 3)", True),
            ("Menor que", "(< 2 5)", True),
            ("IF verdadeiro", "(if (> 5 3) 10 20)", 10),
            ("IF falso", "(if (< 5 3) 10 20)", 20),
            ("CONS básico", "(cons 1 nil)", [1]),
            ("CAR de lista", "(car (cons 1 (cons 2 nil)))", 1),
            ("Definição e chamada de função", "(defun quadrado (x) (* x x)) (quadrado 4)", 16),
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
        print(f"📊 RESUMO: {passed} passaram, {failed} falharam")
        print("="*60)
        
        input("\nPressione Enter para continuar...")
        return passed, failed
    
    def show_system_info(self):
        """Mostra informações do sistema."""
        print("\n🖥️  INFORMAÇÕES DO SISTEMA")
        print("="*60)
        print(f"Python: {sys.version}")
        print(f"Plataforma: {sys.platform}")
        print(f"Diretório atual: {os.getcwd()}")
        print(f"Arquivo atual: {self.current_filename or 'Nenhum'}")
        
        # Informações do compilador
        print(f"\nCompilador Lisp:")
        print(f"  Variáveis temporárias usadas: {self.codegen.temp_count}")
        print(f"  Labels gerados: {self.codegen.label_count}")
        print(f"  Funções registradas: {len(self.interpreter.functions)}")
        
        input("\nPressione Enter para continuar...")

def main():
    """Função principal."""
    print("\n" + "="*60)
    print("🚀 INICIANDO COMPILADOR/INTERPRETADOR LISP")
    print("="*60)
    
    # Verificar dependências
    try:
        import ply
        print(f"✅ PLY versão: {ply.__version__}")
    except ImportError:
        print("❌ ERRO: PLY não está instalado!")
        print("Instale com: pip install ply")
        return
    
    # Criar e executar compilador
    compiler = LispCompiler()
    compiler.show_main_menu()
    
    print("\n👋 Programa finalizado.")

if __name__ == "__main__":
    main()
