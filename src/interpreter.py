from parser import parser
from tokens import lexer
from codegen import CodeGenerator
            

# interpreter.py
class Interpreter:
    def __init__(self):
        self.memory = {}           # Memória para variáveis temporárias e parâmetros: Dicionário {string: int/array/boolean/etc.}
        self.functions = {}        # Dicionário de funções definidas: Dicionário {string: int}
        self.call_stack = []       # Pilha de argumentos para chamadas de função: Array [int/array/boolean/etc.]
        self.label_positions = {}  # Cache de posições de labels: Dicionário {string: int}
        self.return_stack = []     # Pilha de retorno (PC, memória): Aray [dicionário]
        self.pc = 0                # Contador de programa: Int
        self.code = None           # Código atual sendo executado: List ou None
        self.last_result = None    # Último resultado calculado: int/array/boolean/etc.

    # ==============================
    #     Método Principal
    # ==============================
    
    def execute(self, code):
        """Executa o código intermediário."""
        # Preserva funções já definidas e código anterior
        preserved_functions = self.functions.copy()
        preserved_code = self.code if self.code else []
        
        # Mescla código anterior com novo código
        self.code = preserved_code + code
        self.memory = {}
        self.call_stack = []
        self.return_stack = []
        self.label_positions = {}
        self.pc = len(preserved_code)  # Começa após código copiado
        self.last_result = None
        
        # Restaura funções copiadas
        self.functions = preserved_functions
        
        # PRIMEIRA PASSAGEM: Mapear labels
        self.map_labels(code)
        
        # PRIMEIRA PASSAGEM: Registrar funções
        self.register_functions(code)
        
        # SEGUNDA PASSAGEM: Executar
        while self.pc < len(self.code):
            instr = self.code[self.pc]
            op = instr[0]
            
            # Pular definições de função durante execução principal
            if op == 'FUNC_BEGIN':
                self.jump_to_function_end(instr[1])
                continue
            
            # Executar instrução
            try:
                should_continue = self.execute_instruction(instr)
                if should_continue:
                    self.pc += 1
            except Exception as e:
                print(f"Erro na instrução {self.pc}: {instr}")
                print(f"Erro: {e}")
                break
        
        return self.last_result

    # ==============================
    #     Mapeamento e Registro
    # ==============================
    
    def map_labels(self, code):
        """Mapeia todas as labels para suas posições no código."""
        self.label_positions = {}
        for i, instr in enumerate(self.code):
            if instr[0] == 'LABEL':
                label = instr[3]
                self.label_positions[label] = i
    
    def register_functions(self, code):
        """Registra todas as funções definidas no código."""
        current_func = None
        for i, instr in enumerate(self.code):
            op = instr[0]
            
            if op == 'FUNC_BEGIN':
                current_func = {
                    'name': instr[1],
                    'start': i,
                    'params': [],
                    'end': -1
                }
            elif op == 'PARAM_DEF' and current_func:
                current_func['params'].append(instr[1])
            elif op == 'FUNC_END' and current_func and instr[1] == current_func['name']:
                current_func['end'] = i
                self.functions[current_func['name']] = current_func
                # Armazena descritor na memória para persistência
                self.memory[current_func['name']] = {
                    '__type__': 'function',
                    'name': current_func['name'],
                    'start': current_func['start'],
                    'end': current_func['end'],
                    'params': list(current_func['params'])
                }
                current_func = None
    
    # ==============================
    #     Execução de Instruções
    # ==============================
    
    def execute_instruction(self, instr):
        """Executa uma única instrução. Retorna True se deve continuar."""
        op = instr[0]
        
        if op == 'RESULT':
            result = self.get_value(instr[1])
            self.last_result = result
            print(f"=> {self.format_result(result)}")
            return True
            
        elif op == 'ASSIGN':
            self.memory[instr[3]] = self.get_value(instr[1])
            return True
            
        elif op in ['+', '-', '*', '/', 'floor', 'mod', 'expt']:
            self.execute_arithmetic(instr)
            return True
            
        elif op.startswith('CMP_'):
            self.execute_comparison(instr)
            return True
            
        elif op == 'CONS':
            self.execute_cons(instr)
            return True
            
        elif op == 'CAR':
            self.execute_car(instr)
            return True
            
        elif op == 'CDR':
            self.execute_cdr(instr)
            return True
            
        elif op == 'IF_TRUE_GOTO':
            return self.execute_if_true_goto(instr)
            
        elif op == 'GOTO':
            return self.execute_goto(instr)
            
        elif op == 'LABEL':
            # Labels não fazem nada na execução
            return True
            
        elif op == 'PARAM':
            self.execute_param(instr)
            return True
            
        elif op == 'CALL':
            self.execute_call(instr)
            return True
            
        elif op == 'LOAD':
            self.execute_load(instr)
            return True
            
        elif op == 'RETURN':
            self.execute_return(instr)
            return False  # Não incrementa PC após RETURN
            
        elif op == 'FUNC_BEGIN':
            # Não deve acontecer aqui - tratado no execute principal
            return True
            
        elif op == 'FUNC_END':
            # Não deve acontecer aqui - tratado no execute principal
            return True
            
        elif op == 'PARAM_DEF':
            # Não deve acontecer aqui - tratado no register_functions
            return True
            
        else:
            print(f"AVISO: Instrução não reconhecida: {op}")
            return True

    # ==============================
    #     Execução Específica
    # ==============================
    
    def execute_arithmetic(self, instr):
        """Executa operação aritmética."""
        op = instr[0]
        left = self.get_value(instr[1])
        right = self.get_value(instr[2])
        result_var = instr[3]
        
        # Garantir que são números
        if not isinstance(left, (int, float)):
            left = 0
        if not isinstance(right, (int, float)):
            right = 0
        
        if op == '+':
            result = left + right
        elif op == '-':
            result = left - right
        elif op == '*':
            result = left * right
        elif op == '/':
            result = left // right if right != 0 else 0
        elif op == 'floor':
            result = left // right if right != 0 else 0
        elif op == 'mod':
            result = left % right if right != 0 else 0
        elif op == 'expt':
            result = left ** right
        else:
            result = 0
        
        self.memory[result_var] = result
    
    def execute_comparison(self, instr):
        """Executa operação de comparação."""
        op = instr[0]
        left = self.get_value(instr[1])
        right = self.get_value(instr[2])
        result_var = instr[3]
        
        cmp_op = op[4:]  # Remove 'CMP_'
        
        if cmp_op == '=' or cmp_op == 'eq' or cmp_op == 'num_eq':
            result = left == right
        elif cmp_op == '/=' or cmp_op == 'num_neq':
            result = left != right
        elif cmp_op == '>':
            result = left > right
        elif cmp_op == '>=':
            result = left >= right
        elif cmp_op == '<':
            result = left < right
        elif cmp_op == '<=':
            result = left <= right
        elif cmp_op == 'eql':
            result = left == right
        elif cmp_op == 'equal':
            result = left == right
        elif cmp_op == 'equalp':
            result = str(left).lower() == str(right).lower()
        else:
            result = False
        
        self.memory[result_var] = result
    
    def execute_cons(self, instr):
        """Executa CONS (construção de lista)."""
        a = self.get_value(instr[1])
        b = self.get_value(instr[2])
        result_var = instr[3]
        
        # Se b é uma lista, adiciona a no início
        if isinstance(b, list):
            result = [a] + b
        # Se b é nil, cria lista com um elemento
        elif b == [] or b == 'nil':
            result = [a]
        # Caso contrário, cria par (cons cell)
        else:
            result = [a, b]
        
        self.memory[result_var] = result
    
    def execute_car(self, instr):
        """Executa CAR (primeiro elemento da lista)."""
        val = self.get_value(instr[1])
        result_var = instr[3]
        
        if isinstance(val, list) and len(val) > 0:
            result = val[0]
        else:
            result = []
        
        self.memory[result_var] = result
    
    def execute_cdr(self, instr):
        """Executa CDR (resto da lista)."""
        val = self.get_value(instr[1])
        result_var = instr[3]
        
        if isinstance(val, list) and len(val) > 0:
            result = val[1:] if len(val) > 1 else []
        else:
            result = []
        
        self.memory[result_var] = result
    
    def execute_if_true_goto(self, instr):
        """Executa IF_TRUE_GOTO (salto condicional)."""
        cond = self.get_value(instr[1])
        label = instr[3]
        
        if cond:
            self.jump_to_label(label)
            return False  # Não incrementa PC
        return True  # Incrementa PC normalmente
    
    def execute_goto(self, instr):
        """Executa GOTO (salto incondicional)."""
        label = instr[3]
        self.jump_to_label(label)
        return False  # Não incrementa PC
    
    def execute_param(self, instr):
        """Empilha parâmetro para chamada de função."""
        val = self.get_value(instr[1])
        self.call_stack.append(val)
    
    def execute_call(self, instr):
        """Executa CALL (chamada de função)."""
        func_name = instr[1]
        num_args = instr[2]
        result_var = instr[3]
        
        # Verifica se função existe
        if func_name not in self.functions:
            print(f"ERRO: Função '{func_name}' não definida")
            self.memory[result_var] = []
            return True
        
        # Desempilha argumentos (em ordem reversa pois foi empilhado)
        args = []
        for _ in range(num_args):
            if self.call_stack:
                args.insert(0, self.call_stack.pop())
            else:
                args.insert(0, [])
        
        # Salva estado atual
        saved_pc = self.pc
        saved_memory = self.memory.copy()
        saved_call_stack = self.call_stack.copy()
        
        # Adiciona à pilha de retorno
        self.return_stack.append({
            'pc': saved_pc,
            'memory': saved_memory,
            'call_stack': saved_call_stack,
            'result_var': result_var
        })
        
        # Configura novo ambiente (preserva funções)
        func_descriptors = {k: v for k, v in self.memory.items() 
                           if isinstance(v, dict) and v.get('__type__') == 'function'}
        self.memory = func_descriptors
        self.call_stack = []
        
        # Mapeia parâmetros para variáveis locais
        func = self.functions[func_name]
        for param, arg in zip(func['params'], args):
            self.memory[param] = arg
        
        # Pula para início da função (próxima instrução após FUNC_BEGIN)
        self.pc = func['start'] + 1
        return False  # Não incrementa PC
    
    def execute_return(self, instr):
        """Executa RETURN (retorno de função)."""
        return_value = self.get_value(instr[1])
        
        if not self.return_stack:
            # RETURN no nível principal
            self.last_result = return_value
            self.pc = len(self.code)  # Termina execução
            return
        
        # Restaura estado anterior
        saved_state = self.return_stack.pop()
        
        # Restaura memória e pilha
        self.memory = saved_state['memory']
        self.call_stack = saved_state['call_stack']
        
        # Armazena valor de retorno
        self.memory[saved_state['result_var']] = return_value
        
        # Retorna para ponto de chamada
        self.pc = saved_state['pc'] + 1
    
    # ==============================
    #     Utilitários
    # ==============================
    
    def jump_to_label(self, label):
        """Salta para uma label."""
        if label in self.label_positions:
            self.pc = self.label_positions[label]
        else:
            print(f"ERRO: Label '{label}' não encontrada")
            self.pc = len(self.code)  # Termina execução
    
    def jump_to_function_end(self, func_name):
        """Pula para o final de uma função."""
        if func_name in self.functions:
            func = self.functions[func_name]
            self.pc = func['end'] + 1
        else:
            # Procura FUNC_END correspondente
            while self.pc < len(self.code):
                instr = self.code[self.pc]
                if instr[0] == 'FUNC_END' and instr[1] == func_name:
                    self.pc += 1
                    break
                self.pc += 1
    
    def get_value(self, val):
        """Resolve o valor real de uma variável ou literal."""
        # Se for None, retorna None
        if val is None:
            return None
        
        # Se for número ou booleano Python
        if isinstance(val, (int, float, bool)):
            return val
        
        # Se for string
        if isinstance(val, str):
            # nil ou NIL -> lista vazia
            if val.lower() == 'nil':
                return []
            # T -> True
            if val.upper() == 'T':
                return True
            # Variável temporária ou parâmetro
            if val in self.memory:
                # Resolve recursivamente
                resolved = self.memory[val]
                if resolved == val:  # Evitar loop infinito
                    return resolved
                return self.get_value(resolved)
            # Outra string literal
            return val
        
        # Se for lista
        if isinstance(val, list):
            return [self.get_value(item) for item in val]
        
        # Tipo não reconhecido
        return val
    
    def format_result(self, result):
        """Formata resultado para impressão no estilo Lisp."""
        if result is None:
            return "NIL"
        elif result == []:
            return "NIL"
        elif result is True:
            return "T"
        elif isinstance(result, list):
            return self.format_list(result)
        else:
            return str(result)
    
    def format_list(self, lst):
        """Formata lista no estilo Lisp."""
        if not lst:
            return "NIL"
        
        # Verifica se é uma lista própria ou cons cell
        if len(lst) == 2 and not isinstance(lst[1], list):
            return f"({lst[0]} . {self.format_result(lst[1])})"
        
        items = [self.format_result(item) for item in lst]
        return f"({' '.join(items)})"
    
    # ==============================
    #     Interface Pública
    # ==============================
    
    def call_function(self, func_name, args):
        """Chama uma função diretamente (para testes)."""
        if func_name not in self.functions:
            print(f"ERRO: Função '{func_name}' não definida")
            return []
        
        # Simula CALL
        temp_result = "t_result"
        fake_instr = ('CALL', func_name, len(args), temp_result)
        
        # Empilha argumentos em ordem reversa
        for arg in reversed(args):
            self.call_stack.append(arg)
        
        # Executa a chamada
        self.execute_call(fake_instr)
        
        # Continua execução até RETURN
        while self.pc < len(self.code):
            instr = self.code[self.pc]
            if instr[0] == 'RETURN':
                self.execute_return(instr)
                break
            self.execute_instruction(instr)
            self.pc += 1
        
        # Obtém resultado
        result = self.get_value(temp_result)
        
        # Limpa para próxima execução
        self.memory = {}
        self.call_stack = []
        self.return_stack = []
        
        return result
    
    def reset(self):
        """Reseta o interpretador para estado inicial."""
        self.__init__()
    
    def print_state(self):
        """Imprime estado atual do interpretador (para debug)."""
        print(f"\n=== Estado do Interpretador ===")
        print(f"PC: {self.pc}")
        print(f"Memória: {self.memory}")
        print(f"Pilha de Chamada: {self.call_stack}")
        print(f"Pilha de Retorno: {len(self.return_stack)} frames")
        print(f"Funções: {list(self.functions.keys())}")
    
    def execute_load(self, instr):
        """Executa LOAD (carregamento de arquivo)."""
        filename = self.get_value(instr[1])
        result_var = instr[3]
        
        try:
            # Adicionar extensão .lisp se não tiver
            if not (filename.endswith('.lisp') or filename.endswith('.txt')):
                filename += '.lisp'
            
            # Verificar se arquivo existe
            import os
            if not os.path.exists(filename):
                print(f"ERRO: Arquivo '{filename}' não encontrado")
                self.memory[result_var] = []
                return
            
            # Ler arquivo
            with open(filename, 'r', encoding='utf-8') as f:
                lisp_code = f.read()
            
            print(f"Carregando arquivo: {filename}")
            
            # Compilar código do arquivo
           
            lexer.input(lisp_code)
            ast = parser.parse(lisp_code, lexer=lexer)
            
            if ast is None:
                print(f"ERRO: Falha ao analisar arquivo '{filename}'")
                self.memory[result_var] = []
                return
            
            # Gerar código intermediário
            codegen = CodeGenerator()
            new_code = codegen.generate(ast)
            
            # Mesclar com código atual
            old_pc = self.pc
            self.code.extend(new_code)
            
            # Mapear labels e registrar funções do novo código
            self.map_labels(new_code)
            self.register_functions(new_code)
            
            # Executar novo código
            saved_pc = self.pc
            self.pc = len(self.code) - len(new_code)  # Início do novo código
            
            while self.pc < len(self.code):
                instr = self.code[self.pc]
                op = instr[0]
                
                if op == 'FUNC_BEGIN':
                    self.jump_to_function_end(instr[1])
                    continue
                
                should_continue = self.execute_instruction(instr)
                if should_continue:
                    self.pc += 1
                else:
                    break
            
            # Restaurar PC
            self.pc = saved_pc
            
            print(f"Arquivo '{filename}' carregado com sucesso")
            self.memory[result_var] = True  # Sucesso
            
        except Exception as e:
            print(f"ERRO ao carregar arquivo '{filename}': {e}")
            self.memory[result_var] = []
