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
    
    # Analisa o código Lisp e retorna a AST
    def parse(self, lisp_code):
        lexer.input(lisp_code)
        self.current_ast = self.parser.parse(lisp_code, lexer=lexer)
        return self.current_ast
    
    # Gera código intermediário a partir da AST
    def generate_code(self, ast=None):
        if ast is None:
            ast = self.current_ast
        self.current_code = self.codegen.generate(ast)
        return self.current_code
    
    # Executa o código intermediário e retorna o resultado
    def execute(self, code=None):
        if code is None:
            code = self.current_code
        result = self.interpreter.execute(code)
        return result
    
    # Compila e executa o código Lisp completo
    def compile_and_execute(self, lisp_code):
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
            
            print(f" AST gerada com {len(ast)} elemento(s)")
            
            # 2. Geração de código intermediário
            print("\n2. Gerando código intermediário...")
            intermediate_code = self.generate_code(ast)
            
            print(f" Gerado {len(intermediate_code)} instruções")
            
            # 3. Execução
            print("\n3. Executando...")
            print("-" * 40)
            result = self.execute(intermediate_code)
            
            print(f"\n Execução concluída")
            return result
            
        except Exception as e:
            print(f"\n Erro durante compilação/execução: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # Compila e executa o arquivo
    def compile_and_execute_file(self, filename):
        try:
            if not os.path.exists(filename):
                print(f"ERRO: Arquivo '{filename}' não encontrado")
                return None
            
            # Lê o arquivo
            with open(filename, 'r', encoding='utf-8') as f:
                lisp_code = f.read()
                
            # Atualiza o nome do atual arquivo da classe
            self.current_filename = filename
            
            print(f"\n Arquivo: {filename}")
            print(f" Tamanho: {len(lisp_code)} caracteres")
            print(f" Conteúdo:\n{'-'*40}")
            print(lisp_code)
            print(f"{'-'*40}")
            
            # Processa todo o arquivo como uma única unidade
            result = self.compile_and_execute(lisp_code)
            
            # Salvar outputs
            self.save_outputs()
            
            return result
            
        except Exception as e:
            print(f"ERRO ao processar arquivo: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # Salva tokens, AST e código intermediário em arquivos
    def save_outputs(self, base_name=None):
        if base_name is None:
            if self.current_filename:
                base_name = os.path.splitext(self.current_filename)[0]
            else:
                base_name = "output"
        
        try:
            # Salvar tokens
            if hasattr(self, 'current_ast') and self.current_ast is not None:
                tokens_file = f"{base_name}_tokens.txt"
                self.save_tokens(tokens_file)
                print(f" Tokens salvos em: {tokens_file}")
            
            # Salvar AST
            if self.current_ast is not None:
                ast_file = f"{base_name}_ast.txt"
                self.save_ast(ast_file)
                print(f" AST salva em: {ast_file}")
            
            # Salvar código intermediário
            if self.current_code is not None:
                code_file = f"{base_name}_instr.txt"
                self.save_intermediate_code(code_file)
                print(f" Código intermediário salvo em: {code_file}")
            
            # Salvar resultado da execução
            if self.interpreter.last_result is not None:
                result_file = f"{base_name}_result.txt"
                with open(result_file, 'w', encoding='utf-8') as f:
                    f.write(f"Resultado: {self.interpreter.last_result}\n")
                print(f" Resultado salvo em: {result_file}")
                
        except Exception as e:
            print(f" Aviso ao salvar outputs: {e}")
    
    # Salva os tokens em um arquivo
    def save_tokens(self, filename):
		# Teste caso o nome do arquivo seja vazio
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
            
            # Escreve no arquivo a lista de tokens
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== TOKENS ===\n")
                for tok in tokens:
                    f.write(f"{tok}\n")
                f.write(f"\nTotal: {len(tokens)} tokens\n")
                
        except Exception as e:
            print(f"Erro ao salvar tokens: {e}")
    
    # Salva a AST em um arquivo usando pprint
    def save_ast(self, filename):
        if self.current_ast is None:
            return
        
        try:
            import pprint
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== ÁRVORE SINTÁTICA ABSTRATA (AST) ===\n\n")
                # Usa pprint para formatar a AST de forma legível
                ast_str = pprint.pformat(self.current_ast, width=80, depth=None)
                f.write(ast_str)
                f.write("\n")
        except Exception as e:
            print(f"Erro ao salvar AST: {e}")
    
    # Salva o código intermediário em um arquivo
    def save_intermediate_code(self, filename):
        # Teste caso o nome do arquivo seja vazio
        if self.current_code is None:
            return
        
        # Escreve no arquivo o código intermediário 
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== CÓDIGO INTERMEDIÁRIO ===\n")
            f.write(f"Instruções: {len(self.current_code)}\n\n")
            for i, instr in enumerate(self.current_code):
                f.write(f"{i:4d}: {instr}\n")

	# Menu principal
    def show_main_menu(self):
        while True:
            print("\n" + "="*60)
            print(" COMPILADOR/INTERPRETADOR LISP")
            print("="*60)
            print("1. Carregar arquivo Lisp")
            print("2. Modo Terminal (Interativo)")
            #print("3. Executar suíte de testes")
     #       print("4. Mostrar informações do sistema")
            print("3. Sair")
            print("="*60)
            
            # Lê a opção removendo espaços em branco do início e final
            choice = input("\nEscolha uma opção (1-4): ").strip()
            
            if choice == '1':
                self.file_menu()
            elif choice == '2':
                self.repl_menu()
        #    elif choice == '3':
          #      self.test_suite()
       #     elif choice == '4':
        #        self.show_system_info()
            elif choice == '3':
                print("\n Saindo do programa...")
                break
            else:
                print(" Opção inválida! Tente novamente.")
    
    # Menu para carregar arquivos Lisp
    def file_menu(self):
        while True:
            print("\n" + "="*60)
            print(" MENU DE ARQUIVOS")
            print("="*60)
            print("1. Listar arquivos lisp.txt no diretório atual")
            print("2. Digitar caminho do arquivo")
            print("3. Voltar ao menu principal")
            print("="*60)
            
            # Lê a opção removendo espaços em branco do início e final
            choice = input("\nEscolha uma opção (1-3): ").strip()
            
            if choice == '1':
                self.list_and_select_file()
            elif choice == '2':
                self.enter_file_path()
            elif choice == '3':
                break
            else:
                print(" Opção inválida!")
    
    # Lista arquivos Lisp e TXT no diretório atual
    def list_and_select_file(self):
        lisp_files = []  # Array para arquivos Lisp 
        txt_files = []   # Array para arquivos TXT
        
        for file in os.listdir('.'):    # Itera sobre os arquivos com extensão no diretório atual
            if file.endswith('.lisp'):  # Itera sobre os arquivos Lisp
                lisp_files.append(file) # Adiciona ao array de arquivos Lisp
            elif file.endswith('.txt'): # Itera sobre os arquivos TXT
                # Ignora arquivos gerados automaticamente
                if not (file.endswith('_ast.txt') or file.endswith('_instr.txt') or file.endswith('_tokens.txt')):
                    txt_files.append(file)  # Adiciona ao array de arquivos TXT
        
        # Guarda a lista ordenada de todos os arquivos
        all_files = sorted(lisp_files) + sorted(txt_files)
        
        # Tratamento caso a lista esteja vazia
        if not all_files:
            print("\n Nenhum arquivo .lisp ou .txt encontrado no diretório atual.")
            return
        
        # Imprime o menu com a lista de arquivos enumerados
        print("\n Arquivos disponíveis:")
        print("-" * 40)
        
        for i, filename in enumerate(all_files, 1):
            size = os.path.getsize(filename)
            print(f"{i:2d}. {filename} ({size} bytes)")
        
        print("-" * 40)
        print(f"{len(all_files) + 1:2d}. Voltar")
        
        # Teste para selecionar a opção
        try:
            choice = int(input(f"\nSelecione um arquivo (1-{len(all_files) + 1}): "))
            
            if 1 <= choice <= len(all_files):    # Caso para a escolha de um arquivo
                filename = all_files[choice - 1]
                self.process_selected_file(filename)
            elif choice == len(all_files) + 1:   # Caso para a escolha de voltar ao menu anterior
                return
            else:
                print(" Seleção inválida!")
        except ValueError:
            print(" Por favor, digite um número.")
    
    # Recebe o caminho do arquivo de entrada
    def enter_file_path(self):
        filepath = input("\nDigite o caminho do arquivo: ").strip()
        
        if not filepath:
            print(" Caminho vazio!")
            return
        
        # Adicionar extensão .lisp se não tiver
        if not (filepath.endswith('.lisp') or filepath.endswith('.txt')):
            filepath += '.lisp'
        
        # Chama o processo de compilação e execução de arquivos
        self.process_selected_file(filepath)
    
    # Processo inicial da compilação e execução
    def process_selected_file(self, filename):
        print(f"\n Processando arquivo: {filename}")
        print("-" * 40)
        
        try:
            # Reinicia o compilador para o novo arquivo
            self.codegen = CodeGenerator()
            self.interpreter = Interpreter()
            self.current_ast = None
            self.current_code = None
            
            # Compila e executa
            result = self.compile_and_execute_file(filename)
            
            if result is not None:
                print(f"\n Resultado final: {result}")
            
            input("\nPressione Enter para continuar...")
            
        except Exception as e:
            print(f" Erro ao processar arquivo: {e}")
            input("\nPressione Enter para continuar...")
    
    # Modo interativo (REPL)
    def repl_menu(self):
        print("\n" + "="*60)
        print(" MODO INTERATIVO LISP (REPL)")
        print("="*60)
        print("Digite expressões Lisp para avaliar")
        print("Comandos especiais:")
        print("  :ast     - Mostrar AST da última expressão")
        print("  :code    - Mostrar código intermediário")
    #    print("  :mem     - Mostrar estado da memória")
        print("  :reset   - Reiniciar interpretador")
        print("  :save    - Salvar outputs em arquivo")
        print("  :back    - Voltar ao menu principal")
        print("  :quit    - Sair do programa")
        print("="*60)
        
        while True:
            try:
				# Lê a opção removendo espaços em branco do início e final
                user_input = input("\nlisp> ").strip()
                
                # Comandos especiais
                if user_input.startswith(':'):
                    cmd = user_input[1:].lower()
                    
                    if cmd in ['back', 'b']:
                        break
                    elif cmd in ['quit', 'q', 'exit']:
                        print(" Saindo do programa...")
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
                        print(f" Comando desconhecido: '{cmd}'")
                    
                    continue
                
                # Ignorar entrada vazia
                if not user_input:
                    continue
                
                # Compilar e executar expressão Lisp
                print(f"\n Avaliando: {user_input}")
                
                # Reiniciar para nova expressão
                self.codegen = CodeGenerator()
                self.interpreter = Interpreter()
                
                # Compila e executa
                result = self.compile_and_execute(user_input)
                
                # Imprime o resultado se não for vazio
                if result is not None:
                    print(f"\n Resultado: {self.interpreter.format_result(result)}")
                
            except KeyboardInterrupt:
                print("\n Use ':back' para voltar ou ':quit' para sair")
            except EOFError:
                print("\n Saindo...")
                break
            except Exception as e:
                print(f"\n Erro: {e}")
                
    # Opção ':ast' : Imprime a AST
    def show_current_ast(self):
        if self.current_ast:
            import pprint
            print("\n AST Atual:")
            print("-" * 40)
            pprint.pprint(self.current_ast, width=80)
        else:
            print("Nenhuma AST disponível")
    
    # Opção ':code' : Mostra o código intermediário atual
    def show_current_code(self):
        if self.current_code:
            print("\n Código Intermediário:")
            print("-" * 40)
            for i, instr in enumerate(self.current_code):
                print(f"{i:4d}: {instr}")
        else:
            print("Nenhum código intermediário disponível")
    
    # Opção ':mem' : Mostra o estado atual da memória do compilador
    def show_memory_state(self):
        print("\n Estado da Memória:")
        print(f"  Último resultado: {self.interpreter.last_result}")
        print(f"  Variáveis temporárias: {len([k for k in self.interpreter.memory if k.startswith('t')])}")
        print(f"  Funções definidas: {list(self.interpreter.functions.keys())}")
        
        if self.interpreter.memory:
            print("\n  Conteúdo da memória:")
            for key, value in sorted(self.interpreter.memory.items()):
                print(f"    {key}: {value}")
    
    # Opção ':reset' : Reseta  compilador
    def reset_compiler(self):
        self.codegen = CodeGenerator()
        self.interpreter = Interpreter()
        self.current_ast = None
        self.current_code = None
        print(" Compilador reiniciado")
    
    # Opção ':save' : Salva os outputs
    def save_repl_outputs(self):
        base_name = input("Digite o nome base para os arquivos (ou Enter para 'repl'): ").strip()
        if not base_name:
            base_name = "repl"
        
        self.save_outputs(base_name)
        print(f" Outputs salvos com prefixo '{base_name}_'")
    
    # Opção ':help' : Mostra os comandos disponíveis
    def show_repl_help(self):
        print("\n AJUDA DO REPL")
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
    
    # suíte de testes
    def test_suite(self):
        print("\n EXECUTANDO SUÍTE DE TESTES")
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
        
        passed = 0 # Contador de programas executados com suceso
        failed = 0 # Contador de programas executados com erro
        
        for desc, code, expected in tests:
            print(f"\nTeste: {desc}") # Imprime o nome do teste
            print(f"Código: {code}")  # Imprime o código
            
            try:
                # Reiniciar para cada teste
                self.codegen = CodeGenerator()
                self.interpreter = Interpreter()
                
                # Compila e executa
                result = self.compile_and_execute(code)
                
                if result == expected:
                    print(f" Execução com sucesso!")
                    passed += 1 # Incrementa o número de programas executados com sucesso
                else:
                    print(f" Execução com erro!")
                    failed += 1 # Incrementa o número de programas executados com erro
                    
            except Exception as e:
                print(f" ERRO: {e}")
                failed += 1
        
        # Imprime o resumo da suíte de testes
        print("\n" + "="*60)
        print(f" RESUMO: {passed} passaram, {failed} falharam")
        print("="*60)
        
        input("\nPressione Enter para continuar...")
        return passed, failed
    
    # Mostra informações do sistema
    def show_system_info(self):
        print("\n INFORMAÇÕES DO SISTEMA")
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
    print("\n" + "="*60)
    print(" INICIANDO COMPILADOR/INTERPRETADOR LISP")
    print("="*60)
    
    # Verifica dependências
    try:
        import ply
        print(f" PLY versão: {ply.__version__}")
    except ImportError:
        print(" ERRO: PLY não está instalado!")
        print("Instale com: pip install ply")
        return
    
    compiler = LispCompiler() # Cria o compilador
    compiler.show_main_menu() # Chama o menu principal
    
    print("\n Programa finalizado.")

if __name__ == "__main__":
    main()
