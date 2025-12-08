
"O interpretador executa instruções em formato de tuplas (op, arg1, arg2, result)"

class Interpreter:
    def __init__(self):
       
        self.memory = {}        # Memória para variáveis temporárias e parâmetros
        self.functions = {}     # Dicionário de funções definidas {nome: {name, start, params}}
        self.call_stack = []    # Pilha de argumentos para chamadas de função
        
    def execute(self, code):
        """Executa o código intermediário.
        
        Primeira passagem: registra todas as funções definidas no código.
        Segunda passagem: executa expressões soltas.
        
        Args:
            code (list): Lista de tuplas representando instruções do CI
                        Formato: (operação, arg1, arg2, resultado)
        """
        # PRIMEIRA PASSAGEM: Registrar todas as funções
        current_func = None
        for pc, instr in enumerate(code):
            if instr[0] == 'FUNC_BEGIN':
                current_func = {'name': instr[1], 'start': pc, 'params': []}
            elif instr[0] == 'PARAM_DEF':
                current_func['params'].append(instr[1])
            elif instr[0] == 'FUNC_END':
                self.functions[instr[1]] = current_func
        
        # SEGUNDA PASSAGEM: Executar expressões soltas
        pc = 0
        while pc < len(code):
            instr = code[pc]
            op = instr[0]
            
            # Pula definições de funções
            if op == 'FUNC_BEGIN':
                # Encontra o FUNC_END correspondente
                func_name = instr[1]
                while pc < len(code) and not (code[pc][0] == 'FUNC_END' and code[pc][1] == func_name):
                    pc += 1
                pc += 1
                continue
            
            # Executa expressões soltas
            if op == 'RESULT':
                result = self.get_value(instr[1])
                print(f"=> {result if result != [] else 'NIL'}")
            elif op in ['+', '-', '*', '/', 'floor', 'mod', 'expt']:
                left = self.get_value(instr[1])
                right = self.get_value(instr[2])
                if op == '+': result = left + right
                elif op == '-': result = left - right
                elif op == '*': result = left * right
                elif op == '/': result = left // right
                elif op == 'floor': result = left // right
                elif op == 'mod': result = left % right
                elif op == 'expt': result = left ** right
                self.memory[instr[3]] = result
            
            pc += 1
                
    def get_value(self, val):
        """Resolve o valor real de uma variável ou literal.
        
        Resolve recursivamente variáveis temporárias até chegar no valor final.
        Exemplo: se t1=5 e t2=t1, get_value('t2') retorna 5
        
        Args:
            val: Pode ser int, list, string (variável ou literal)
            
        Returns:
            O valor real resolvido
        """
        # Literais numéricos e listas já são valores finais
        if isinstance(val, (int, list)):
            return val
        # nil em Lisp é representado como lista vazia (case-insensitive)
        if isinstance(val, str) and val.lower() == 'nil':
            return []
        # T em Lisp é o valor booleano verdadeiro (case-insensitive)
        if isinstance(val, str) and val.upper() == 'T':
            return True
        # Se é uma variável temporária (t1, t2, ...), resolve recursivamente
        if isinstance(val, str) and val in self.memory:
            return self.get_value(self.memory[val])
        # Caso contrário, retorna o valor como está (ex: nome de parâmetro)
        return val
        
    def find_label(self, code, label):
        """Encontra a posição de um label no código.
        
        Labels são usados para controle de fluxo (if, goto).
        Exemplo: ('LABEL', None, None, 'L1') marca a posição do label L1
        
        Args:
            code (list): Lista de instruções
            label (str): Nome do label a procurar (ex: 'L1', 'L2')
            
        Returns:
            int: Índice da instrução do label, ou -1 se não encontrado
        """
        for i, instr in enumerate(code):
            if instr[0] == 'LABEL' and instr[3] == label:
                return i
        return -1
        
    def call_function(self, code, func_name, args):
        
        func = self.functions[func_name]
        old_memory = self.memory.copy()  # Salva memória atual (escopo anterior)
        
        # DEFINIR PARÂMETROS: Mapeia argumentos para parâmetros da função
        # Exemplo: se função é soma(lista) e args=[[1,2,3]], então memory['lista']=[1,2,3]
        for param, arg in zip(func['params'], args):
            self.memory[param] = arg
            
        # EXECUTAR: Processa cada instrução da função
        pc = func['start'] + 1  # Começa após FUNC_BEGIN
        while pc < len(code):
            instr = code[pc]  # Instrução atual: (op, arg1, arg2, result)
            op = instr[0]     # Operação (primeiro elemento da tupla)
            
            # Fim da função: para a execução
            if op == 'FUNC_END' and instr[1] == func_name:
                break
            
            # Pula instruções de definição (já processadas)
            if op in ['FUNC_BEGIN', 'PARAM_DEF']:
                pc += 1
                continue
                
            # OPERAÇÕES ARITMÉTICAS
            # Formato: (op, operando1, operando2, resultado)
            if op in ['+', '-', '*', '/', 'floor', 'mod', 'expt']:
                left = self.get_value(instr[1])   # Resolve primeiro operando
                right = self.get_value(instr[2])  # Resolve segundo operando
                if op == '+': result = left + right
                elif op == '-': result = left - right
                elif op == '*': result = left * right
                elif op == '/': result = left // right      # Divisão inteira
                elif op == 'floor': result = left // right  # Floor division
                elif op == 'mod': result = left % right     # Módulo
                elif op == 'expt': result = left ** right   # Exponenciação
                self.memory[instr[3]] = result  # Guarda resultado na variável temporária
                
            # OPERAÇÕES DE COMPARAÇÃO
            # Formato: ('CMP_op', valor1, valor2, resultado)
            elif op.startswith('CMP_'):
                left = self.get_value(instr[1])
                right = self.get_value(instr[2])
                cmp_op = op[4:]  # Remove prefixo 'CMP_' para pegar operador
                
                # Comparações de igualdade 
                if cmp_op in ['eq', 'eql', 'equal', 'equalp']:
                    result = left == right
                # Comparações numéricas
                elif cmp_op == 'num_neq':
                    result = left != right
                elif cmp_op == '>':
                    result = left > right
                elif cmp_op == '>=':
                    result = left >= right
                elif cmp_op == '<':
                    result = left < right
                elif cmp_op == '<=':
                    result = left <= right
                else:
                    result = left == right
                self.memory[instr[3]] = result  # Guarda True ou False
                
            # ATRIBUIÇÃO
            # Formato: ('ASSIGN', origem, None, destino)
            # Exemplo: ('ASSIGN', 5, None, 't1') -> t1 = 5
            elif op == 'ASSIGN':
                self.memory[instr[3]] = self.get_value(instr[1])
                
            # CONTROLE DE FLUXO
            # IF_TRUE_GOTO: Salta para label se condição for verdadeira
            # Formato: ('IF_TRUE_GOTO', condição, None, label)
            elif op == 'IF_TRUE_GOTO':
                if self.get_value(instr[1]):  # Se condição é True
                    pc = self.find_label(code, instr[3])  # Pula para o label
                    continue  # Não incrementa pc no final
            
            # GOTO: Salta incondicionalmente para um label
            # Formato: ('GOTO', None, None, label)
            elif op == 'GOTO':
                pc = self.find_label(code, instr[3])
                continue
            
            # LABEL: Marca uma posição no código (não faz nada na execução)
            # Formato: ('LABEL', None, None, nome_label)
            elif op == 'LABEL':
                pass  # Labels são apenas marcadores
                
            # OPERAÇÕES DE LISTA (Lisp)
            # CONS: Constrói uma lista adicionando elemento no início
            # Formato: ('CONS', elemento, lista, resultado)
            # Exemplo: ('CONS', 1, [2,3], 't1') -> t1 = [1,2,3]
            elif op == 'CONS':
                a = self.get_value(instr[1])  # Elemento a adicionar
                b = self.get_value(instr[2])  # Lista existente
                if isinstance(b, list):
                    self.memory[instr[3]] = [a] + b  # Adiciona a no início de b
                elif b == []:
                    self.memory[instr[3]] = [a]      # Lista com um elemento
                else:
                    self.memory[instr[3]] = [a, b]   # Par (a . b)
            
            # CAR: Retorna o primeiro elemento da lista
            # Formato: ('CAR', lista, None, resultado)
            # Exemplo: ('CAR', [1,2,3], None, 't1') -> t1 = 1
            elif op == 'CAR':
                val = self.get_value(instr[1])
                self.memory[instr[3]] = val[0] if val else []
            
            # CDR: Retorna a lista sem o primeiro elemento
            # Formato: ('CDR', lista, None, resultado)
            # Exemplo: ('CDR', [1,2,3], None, 't1') -> t1 = [2,3]
            elif op == 'CDR':
                val = self.get_value(instr[1])
                self.memory[instr[3]] = val[1:] if len(val) > 1 else []
                
            # CHAMADAS DE FUNÇÃO
            # PARAM: Empilha um argumento para a próxima chamada
            # Formato: ('PARAM', valor, None, None)
            elif op == 'PARAM':
                self.call_stack.append(self.get_value(instr[1]))
            
            # CALL: Chama uma função com os argumentos empilhados
            # Formato: ('CALL', nome_função, num_args, resultado)
            # Exemplo: ('CALL', 'soma', 1, 't5') -> t5 = soma(arg_da_pilha)
            elif op == 'CALL':
                fname = instr[1]   # Nome da função
                nargs = instr[2]   # Número de argumentos
                # Desempilha argumentos (inverte ordem pois pilha é LIFO)
                fargs = [self.call_stack.pop() for _ in range(nargs)][::-1]
                # Chama função recursivamente e guarda resultado
                self.memory[instr[3]] = self.call_function(code, fname, fargs)
            
            # RETURN: Retorna valor e restaura memória anterior
            # Formato: ('RETURN', valor, None, None)
            elif op == 'RETURN':
                result = self.get_value(instr[1])  # Resolve valor de retorno
                self.memory = old_memory           # Restaura escopo anterior
                return result
            
            # RESULT: Já tratado no execute principal
            elif op == 'RESULT':
                pass
                
            pc += 1  # Avança para próxima instrução
        
        # Se chegou aqui sem RETURN, restaura memória e retorna lista vazia
        self.memory = old_memory
        return []
