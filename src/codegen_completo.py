class CodeGenerator:
    def __init__(self):
        # lista de instruções: cada item é (op, arg1, arg2, result)
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        # gera t1, t2, ...
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        # gera L1, L2, ...
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, op, arg1=None, arg2=None, result=None):
        # adiciona uma instrução à lista
        self.code.append((op, arg1, arg2, result))

    def generate(self, ast):
        # ponto de entrada: recebe a AST (lista de funções)
        for func in ast:
            self.gen_function(func)
        return self.code

    def gen_function(self, func):
        # func é uma tupla (DEFUN, nome, params, corpo)
        _, name, params, body = func
        self.emit("FUNC_BEGIN", name, None, None)
        # opcional: emitir instruções que definam parâmetros/formato de pilha
        result = self.gen_expression(body)
        # garante que o retorno esteja em um temporário (se for literal, coloca em temp)
        if not isinstance(result, str) or not result.startswith("t"):
            tmp = self.new_temp()
            self.emit("ASSIGN", result, None, tmp)
            result = tmp
        self.emit("RETURN", result, None, None)
        self.emit("FUNC_END", name, None, None)

    def gen_expression(self, expr):
        # Caso expr seja inteiro literal (NUM) ou identificador (ID ou NIL/T),
        # no parser atual termos são passados como int ou string diretamente.
        if isinstance(expr, (int, float)):
            return expr
        if isinstance(expr, str):
            # pode ser ID, 'nil' ou 't'
            return expr

        # expr é uma tupla representando uma operação: (op, ...args)
        op = expr[0]

        # — Operações aritméticas binárias
        if op in ['+', '-', '*', '/', 'FLOOR', 'MOD', 'EXPT']:
            left = self.gen_expression(expr[1])
            right = self.gen_expression(expr[2])
            # se left/right forem literais não-temporários, OK: podemos usá-los direto
            temp = self.new_temp()
            self.emit(op, left, right, temp)
            return temp

        # — Comparações
        if op in ['=', 'EQL', 'EQUAL', 'EQUALP', 'NUM_EQ', 'NUM_NEQ', '>', '>=', '<', '<=']:
            left = self.gen_expression(expr[1])
            right = self.gen_expression(expr[2])
            temp = self.new_temp()
            self.emit("CMP_"+op, left, right, temp)  # ex: ("CMP_>", a, b, t3)
            return temp

        # — If (IF cond then else)
        if op == 'IF' or op == 'if' or op == 'IF':
            cond = self.gen_expression(expr[1])
            # result temporário que guardará o valor do if
            result_temp = self.new_temp()
            label_then = self.new_label()
            label_else = self.new_label()
            label_end = self.new_label()

            # se cond for um temporário/valor booleano, verificamos e saltamos
            self.emit("IF_TRUE_GOTO", cond, None, label_then)
            # else branch
            val_else = self.gen_expression(expr[3])
            # garantir que val_else esteja em temporário
            if not (isinstance(val_else, str) and val_else.startswith("t")):
                te = self.new_temp()
                self.emit("ASSIGN", val_else, None, te)
                val_else = te
            self.emit("ASSIGN", val_else, None, result_temp)
            self.emit("GOTO", None, None, label_end)

            # then branch
            self.emit("LABEL", None, None, label_then)
            val_then = self.gen_expression(expr[2])
            if not (isinstance(val_then, str) and val_then.startswith("t")):
                tt = self.new_temp()
                self.emit("ASSIGN", val_then, None, tt)
                val_then = tt
            self.emit("ASSIGN", val_then, None, result_temp)

            # end
            self.emit("LABEL", None, None, label_end)
            return result_temp

        # — Chamadas de função: (funcName arg1 arg2 ...)
        if isinstance(op, str):
            func_name = op
            args_list = expr[1] if len(expr) > 1 else []
            # avaliar argumentos (cada um vira um temporário ou literal)
            evaluated_args = []
            for a in args_list:
                ev = self.gen_expression(a)
                # force to temp if literal
                if not (isinstance(ev, str) and ev.startswith("t")) and not isinstance(ev, (int, float, str)):
                    pass
                evaluated_args.append(ev)

            # empilhar parâmetros (ou emitir PARAM por argumento)
            for arg in evaluated_args:
                self.emit("PARAM", arg, None, None)

            # gerar chamada
            ret_temp = self.new_temp()
            self.emit("CALL", func_name, len(evaluated_args), ret_temp)
            return ret_temp

        # — Outros casos (CONS, CAR, CDR, COND, etc) devem ser implementados explicitamente
        # Exemplo simples para CAR:
        if op == 'CAR':
            val = self.gen_expression(expr[1])
            tmp = self.new_temp()
            self.emit("CAR", val, None, tmp)
            return tmp

        if op == 'CDR':
            val = self.gen_expression(expr[1])
            tmp = self.new_temp()
            self.emit("CDR", val, None, tmp)
            return tmp

        if op == 'CONS':
            a = self.gen_expression(expr[1])
            b = self.gen_expression(expr[2])
            tmp = self.new_temp()
            self.emit("CONS", a, b, tmp)
            return tmp

        # fallback
        raise NotImplementedError(f"Operação não implementada no codegen: {op}")
