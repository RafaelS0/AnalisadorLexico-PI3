# codegen.py
class CodeGenerator:
    def __init__(self):
        self.code = []        # Array para guardar o código intermediário (CI)
        self.temp_count = 0   # Contador de variáveis temporárias
        self.label_count = 0  # Contador de labels
        self.current_func = None  # Função sendo processada atualmente

    # ==============================
    #     Ferramentas internas
    # ==============================
    
    # Gerador de variáveis temporárias
    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"
    
    # Gerador de labels
    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    # Inserção no array de código intermediário
    def insert(self, op, a1=None, a2=None, res=None):
        self.code.append((op, a1, a2, res))
        return res

    # ==============================
    #         Entrada principal
    # ==============================
    
    def generate(self, ast):
        """Gera código intermediário a partir da AST."""
        # Resetar gerador para nova geração
        self.code = []
        self.temp_count = 0
        self.label_count = 0
        
        # Iteração pela AST
        for node in ast:
            # Tratamento para função
            if isinstance(node, tuple) and node[0] == 'defun':
                self.gen_function(node)
            # Tratamento para expressão solta
            else:
                result = self.gen_expression(node)
                if result is not None:
                    self.insert("RESULT", result, None, None)
        
        # Retorna o código gerado do programa
        return self.code

    # ==============================
    #            Funções
    # ==============================
    
    def gen_function(self, func_node):
        """Gera código para definição de função."""
        _, name, params, body = func_node
        old_func = self.current_func
        self.current_func = name
        
        # Insere no array do CI o começo da função
        self.insert("FUNC_BEGIN", name, None, None)

        # Registro dos parâmetros
        for p in params:
            self.insert("PARAM_DEF", p, None, None)

        # Geração para o corpo da função
        result = self.gen_expression(body)

        # Tratamento para guardar o resultado em temporário para RETURN
        if result is not None:
            if not (isinstance(result, str) and result.startswith("t")):
                tmp = self.new_temp()
                self.insert("ASSIGN", result, None, tmp)
                result = tmp
            self.insert("RETURN", result, None, None)
        
        self.insert("FUNC_END", name, None, None)
        self.current_func = old_func

    # ==============================
    #         Expressões
    # ==============================
    
    def gen_expression(self, expr):
        """Gera código para uma expressão e retorna o temporário resultante."""
        # -------- Literais e IDs --------
        if isinstance(expr, (int, float, str)):
            return expr
        
        # Se não for tupla, retorna como está
        if not isinstance(expr, tuple):
            return expr

        # Operador da expressão (cdr, if, +, ...)
        op = expr[0]

        # -------- Aritmética --------
        if op in ['+', '-', '*', '/', 'floor', 'mod', 'expt']:
            left = self.gen_expression(expr[1])     # Primeiro operando
            right = self.gen_expression(expr[2])    # Segundo operando
            tmp = self.new_temp()                   # Variável temporária para o resultado
            
            # Se os operandos não são temporários, atribui a temporários
            if not (isinstance(left, str) and left.startswith("t")):
                left_tmp = self.new_temp()
                self.insert("ASSIGN", left, None, left_tmp)
                left = left_tmp
                
            if not (isinstance(right, str) and right.startswith("t")):
                right_tmp = self.new_temp()
                self.insert("ASSIGN", right, None, right_tmp)
                right = right_tmp
                
            self.insert(op, left, right, tmp)       # Inserção no array do CI
            return tmp

        # -------- Comparações --------
        if op in ['eq', 'eql', 'equal', 'equalp', 'num_eq', 'num_neq', '>', '>=', '<', '<=']:
            left = self.gen_expression(expr[1])
            right = self.gen_expression(expr[2])
            
            # Se os operandos não são temporários, atribui a temporários
            if not (isinstance(left, str) and left.startswith("t")):
                left_tmp = self.new_temp()
                self.insert("ASSIGN", left, None, left_tmp)
                left = left_tmp
                
            if not (isinstance(right, str) and right.startswith("t")):
                right_tmp = self.new_temp()
                self.insert("ASSIGN", right, None, right_tmp)
                right = right_tmp
                
            tmp = self.new_temp()
            
            # Mapeia operadores Lisp para operadores CI
            cmp_op = op
            if op == 'num_eq': cmp_op = '='
            elif op == 'num_neq': cmp_op = '/='
            
            self.insert("CMP_" + cmp_op, left, right, tmp)
            return tmp

        # -------- CONS, CAR, CDR --------
        if op == 'cons':
            a = self.gen_expression(expr[1])
            b = self.gen_expression(expr[2])
            
            # Se os operandos não são temporários, atribui a temporários
            if not (isinstance(a, str) and a.startswith("t")):
                a_tmp = self.new_temp()
                self.insert("ASSIGN", a, None, a_tmp)
                a = a_tmp
                
            if not (isinstance(b, str) and b.startswith("t")):
                b_tmp = self.new_temp()
                self.insert("ASSIGN", b, None, b_tmp)
                b = b_tmp
                
            tmp = self.new_temp()
            self.insert("CONS", a, b, tmp)
            return tmp

        if op == 'car':
            val = self.gen_expression(expr[1])
            
            if not (isinstance(val, str) and val.startswith("t")):
                val_tmp = self.new_temp()
                self.insert("ASSIGN", val, None, val_tmp)
                val = val_tmp
                
            tmp = self.new_temp()
            self.insert("CAR", val, None, tmp)
            return tmp

        if op == 'cdr':
            val = self.gen_expression(expr[1])
            
            if not (isinstance(val, str) and val.startswith("t")):
                val_tmp = self.new_temp()
                self.insert("ASSIGN", val, None, val_tmp)
                val = val_tmp
                
            tmp = self.new_temp()
            self.insert("CDR", val, None, tmp)
            return tmp

        # -------- IF --------
        if op == 'if':
            cond_expr = expr[1]    # Condição
            then_expr = expr[2]    # Caso seja verdadeira 
            else_expr = expr[3]    # Caso seja falsa

            cond_tmp = self.gen_expression(cond_expr)  # Variável temporária do teste

            label_then = self.new_label()  # Label para true
            label_else = self.new_label()  # Label para false
            label_end  = self.new_label()  # Label para o fim do bloco IF

            result_temp = self.new_temp()  # Temporário para guardar o retorno

            # Testa condição e pula para THEN se verdadeiro
            self.insert("IF_TRUE_GOTO", cond_tmp, None, label_then)
            
            # ELSE: executa bloco else
            self.insert("GOTO", None, None, label_else)
            
            # THEN: bloco verdadeiro
            self.insert("LABEL", None, None, label_then)
            then_val = self.gen_expression(then_expr)
            if not (isinstance(then_val, str) and then_val.startswith("t")):
                tmp = self.new_temp()
                self.insert("ASSIGN", then_val, None, tmp)
                then_val = tmp
            self.insert("ASSIGN", then_val, None, result_temp)
            self.insert("GOTO", None, None, label_end)
            
            # ELSE: bloco falso
            self.insert("LABEL", None, None, label_else)
            else_val = self.gen_expression(else_expr)
            if not (isinstance(else_val, str) and else_val.startswith("t")):
                tmp = self.new_temp()
                self.insert("ASSIGN", else_val, None, tmp)
                else_val = tmp
            self.insert("ASSIGN", else_val, None, result_temp)
            
            # END: fim do if
            self.insert("LABEL", None, None, label_end)
            return result_temp

        # -------- COND --------
        if op == 'cond':
            clauses = expr[1]           # Lista de cláusulas
            end_label = self.new_label()   # Label para o fim
            result_temp = self.new_temp()  # Temporário para o bloco
            has_default = False

            # Itera pelas cláusulas
            for i, (cond_expr, body_expr) in enumerate(clauses):
                label_clause = self.new_label()
                label_next = self.new_label()

                # Última cláusula com T (default)?
                is_default = (isinstance(cond_expr, str) and cond_expr.upper() == 'T')
                
                if is_default:
                    has_default = True
                    # Cláusula default: executa diretamente
                    self.insert("LABEL", None, None, label_clause)
                    body_tmp = self.gen_expression(body_expr)
                    if not (isinstance(body_tmp, str) and body_tmp.startswith("t")):
                        tmp = self.new_temp()
                        self.insert("ASSIGN", body_tmp, None, tmp)
                        body_tmp = tmp
                    self.insert("ASSIGN", body_tmp, None, result_temp)
                    self.insert("GOTO", None, None, end_label)
                else:
                    # Cláusula normal: testa condição
                    cond_tmp = self.gen_expression(cond_expr)
                    self.insert("IF_TRUE_GOTO", cond_tmp, None, label_clause)
                    self.insert("GOTO", None, None, label_next)

                    # Corpo da cláusula
                    self.insert("LABEL", None, None, label_clause)
                    body_tmp = self.gen_expression(body_expr)
                    if not (isinstance(body_tmp, str) and body_tmp.startswith("t")):
                        tmp = self.new_temp()
                        self.insert("ASSIGN", body_tmp, None, tmp)
                        body_tmp = tmp
                    self.insert("ASSIGN", body_tmp, None, result_temp)
                    self.insert("GOTO", None, None, end_label)

                    # Próxima cláusula
                    self.insert("LABEL", None, None, label_next)

            # Se não há cláusula default e nenhuma foi verdadeira
            if not has_default:
                # Nenhuma condição verdadeira: retorna nil
                self.insert("ASSIGN", 'nil', None, result_temp)

            self.insert("LABEL", None, None, end_label)
            return result_temp

        # -------- Chamada de função --------
        if isinstance(op, str) and len(expr) == 2 and isinstance(expr[1], list):
            func_name = op
            args = expr[1]

            # Gera código para cada argumento e empilha
            for a in args:
                val = self.gen_expression(a)
                self.insert("PARAM", val, None, None)

            tmp = self.new_temp()
            self.insert("CALL", func_name, len(args), tmp)
            return tmp
        
        # -------- Chamada direta (ID com args) --------
        if op == 'call' or (isinstance(op, str) and op.isalpha()):
            # Verifica se é uma chamada de função do parser
            if len(expr) == 2:
                func_name = expr[0]
                args_list = expr[1]
                
                # Gera código para cada argumento
                for arg in args_list:
                    val = self.gen_expression(arg)
                    self.insert("PARAM", val, None, None)
                
                tmp = self.new_temp()
                self.insert("CALL", func_name, len(args_list), tmp)
                return tmp

        # -------- Operação unária --------
        if len(expr) == 2 and op in ['-', 'car', 'cdr']:
            val = self.gen_expression(expr[1])
            tmp = self.new_temp()
            
            if not (isinstance(val, str) and val.startswith("t")):
                val_tmp = self.new_temp()
                self.insert("ASSIGN", val, None, val_tmp)
                val = val_tmp
            
            if op == '-':  # Negativo unário
                zero_tmp = self.new_temp()
                self.insert("ASSIGN", 0, None, zero_tmp)
                self.insert("-", zero_tmp, val, tmp)
            else:
                self.insert(op.upper(), val, None, tmp)
            return tmp

        # ERRO - Operação não reconhecida
        print(f"AVISO: Operação não reconhecida no codegen: {expr}")
        return None

    # ==============================
    #     Utilitários de Debug
    # ==============================
    
    def print_code(self):
        """Imprime o código intermediário gerado."""
        print("\n=== Código Intermediário Gerado ===")
        for i, instr in enumerate(self.code):
            print(f"{i:3d}: {instr}")
    
    def save_code(self, filename="codigo_intermediario.txt"):
        """Salva o código intermediário em arquivo."""
        with open(filename, "w") as f:
            f.write("[\n")
            for i, instr in enumerate(self.code):
                f.write(f"   {repr(instr)}")
                if i < len(self.code) - 1:
                    f.write(",")
                f.write("\n")
            f.write("]\n")
        print(f"Código intermediário salvo em '{filename}'")
