class CodeGenerator:
    def __init__(self):
        self.code = []		# Array para guardar o código inntermediário (CI)
        self.temp_count = 0	# Contador de variáveis temporárias
        self.label_count = 0	# Contador de labels

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

    # ==============================
    #         Entrada principal
    # ==============================
    
    def generate(self, ast):
        # Validação da AST
        if ast is None:
            raise TypeError("O parser retornou None. Verifique se o código LISP está sintaticamente correto.")
        
        if not isinstance(ast, list):
            raise TypeError(f"AST inválida. Esperado: lista, Recebido: {type(ast)}")
        
        try:
            # Iteração pela AST
            for node in ast:
                # Tratamento para função
                if node[0] == 'defun':
                    self.gen_function(node)
                # Tratamento para expressão solta
                else:
                    result = self.gen_expression(node)
                    self.insert("RESULT", result, None, None)
            
            # Retorna o código gerado do programa
            return self.code
        except (IndexError, KeyError, AttributeError) as e:
            raise NotImplementedError(f"Código LISP mal formatado ou operação não suportada: {e}")
        except Exception as e:
            raise NotImplementedError(f"Erro ao processar código LISP: {e}")

    # ==============================
    #            Funções
    # ==============================
    
    def gen_function(self, func_node):
	# Separação dos campos da declaração de função
        _, name, params, body = func_node

	# Insere no array do CI o começo da função
        self.insert("FUNC_BEGIN", name, None, None)

        # Reconhecimento dos parâmetros
        for p in params:
            self.insert("PARAM_DEF", p, None, None)

	# Geração para o corpo da função
        result = self.gen_expression(body)

        # Tratamento para guardar o resultado em temporário para RETURN
        if not (isinstance(result, str) and result.startswith("t")):
            tmp = self.new_temp()
            self.insert("ASSIGN", result, None, tmp)
            result = tmp

        self.insert("RETURN", result, None, None)
        self.insert("FUNC_END", name, None, None)

    # ==============================
    #         Expressões
    # ==============================
    
    def gen_expression(self, expr):
        # -------- Literais e IDs --------
        if isinstance(expr, (int, str)):
            return expr

        # Operador da expressão (cdr, if, +, ...)
        op = expr[0]

        # -------- Aritmética --------
        if op in ['+', '-', '*', '/', 'floor', 'mod', 'expt']:
            left = self.gen_expression(expr[1])		# Primeiro operando
            right = self.gen_expression(expr[2])	# Segundo operando
            tmp = self.new_temp()			# Variável temporária para o resultado
            self.insert(op, left, right, tmp)		# Inserção no array do CI
            return tmp

        # -------- Comparações --------
        if op in ['eq', 'eql', 'equal', 'equalp', 'num_eq', 'num_neq', '>', '>=', '<', '<=']:
            left = self.gen_expression(expr[1])		
            right = self.gen_expression(expr[2])	
            tmp = self.new_temp()
            self.insert("CMP_" + op, left, right, tmp)
            return tmp

	# -------- CONS, CAR, CDR --------
        if op == 'cons':
            a = self.gen_expression(expr[1])
            b = self.gen_expression(expr[2])
            tmp = self.new_temp()
            self.insert("CONS", a, b, tmp)
            return tmp
        
        if op == 'list':
            # (list 1 2 3) -> cria lista [1, 2, 3]
            args = expr[1]  # Lista de argumentos
            if not args:  # (list) -> lista vazia
                return 'nil'
            
            # Constrói lista recursivamente: (list a b c) -> (cons a (cons b (cons c nil)))
            result = 'nil'
            for arg in reversed(args):  # Processa de trás para frente
                arg_val = self.gen_expression(arg)
                tmp = self.new_temp()
                self.insert("CONS", arg_val, result, tmp)
                result = tmp
            return result

        if op == 'car':
            val = self.gen_expression(expr[1])
            tmp = self.new_temp()
            self.insert("CAR", val, None, tmp)
            return tmp

        if op == 'cdr':
            val = self.gen_expression(expr[1])
            tmp = self.new_temp()
            self.insert("CDR", val, None, tmp)
            return tmp

        # -------- IF --------
        if op == 'if':
            cond_expr = expr[1]	# Condição
            then_expr = expr[2]	# Caso seja verdadeira 
            else_expr = expr[3]	# Caso seja falsa

            cond_tmp = self.gen_expression(cond_expr)	# t1 Guarda a variavel temporaria do teste de condição (t?)

            label_then = self.new_label() # Label para true
            label_else = self.new_label() # Label para false
            label_end  = self.new_label() # Label para o fim do bloco IF

            result_temp = self.new_temp() # t2 Temporário para guardar o retorno do bloco IF

	    # if t? -> l?
            self.insert("IF_TRUE_GOTO", cond_tmp, None, label_then)

            # else
            else_val = self.gen_expression(else_expr)
	    # Caso ELSE seja literal ou ID
            if not (isinstance(else_val, str) and else_val.startswith("t")):
                tmp = self.new_temp() #t3
                self.insert("ASSIGN", else_val, None, tmp)
		# Atribui a variavel aleatoria para o ELSE
                else_val = tmp
	    # Codigo de atribuiçao de ELSE para a variavel de retorno do bloco
            self.insert("ASSIGN", else_val, None, result_temp)
	    # Desvio para o label do fim do  bloco
            self.insert("GOTO", None, None, label_end)

            # then
            self.insert("LABEL", None, None, label_then)
            then_val = self.gen_expression(then_expr)
            if not (isinstance(then_val, str) and then_val.startswith("t")):
                tmp = self.new_temp()
                self.insert("ASSIGN", then_val, None, tmp)
                then_val = tmp
            self.insert("ASSIGN", then_val, None, result_temp)

            # end
            self.insert("LABEL", None, None, label_end)
            return result_temp

        # -------- COND --------
        if op == 'cond':
            clauses = expr[1]		   # Lista de clausulas
            end_label = self.new_label()   # Label para o fim
            result_temp = self.new_temp()  # Temporario para o bloco

	    # Iteraçao pelas clausulas
            for cond_expr, body_expr in clauses:
                label_clause = self.new_label()
                label_next   = self.new_label()

                cond_tmp = self.gen_expression(cond_expr)
                self.insert("IF_TRUE_GOTO", cond_tmp, None, label_clause)
                self.insert("GOTO", None, None, label_next)

                
                self.insert("LABEL", None, None, label_clause)
                body_tmp = self.gen_expression(body_expr)
                if not (isinstance(body_tmp, str) and body_tmp.startswith("t")):
                    tmp = self.new_temp()
                    self.insert("ASSIGN", body_tmp, None, tmp)
                    body_tmp = tmp

                self.insert("ASSIGN", body_tmp, None, result_temp)
                self.insert("GOTO", None, None, end_label)

                # next clause
                self.insert("LABEL", None, None, label_next)

            self.insert("LABEL", None, None, end_label)
            return result_temp


        # -------- Chamada de função --------
        # Verifica se é uma tupla com 2 elementos onde o segundo é uma lista
        if len(expr) == 2 and isinstance(op, str) and isinstance(expr[1], list):
            func_name = op
            args = expr[1]

            for a in args:
                val = self.gen_expression(a)
                self.insert("PARAM", val, None, None)

            tmp = self.new_temp()
            self.insert("CALL", func_name, len(args), tmp)
            return tmp


        # ERRO
        raise NotImplementedError(f"Operação não reconhecida na geração de código intermediário: {expr}")