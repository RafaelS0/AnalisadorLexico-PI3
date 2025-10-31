class CodeGenerator:
    def __init__(self):
        self.code = []			# guarda todas as instruções geradas
        self.temp_count = 0		# contador de variáveis temporárias (t)
        self.label_count = 0	# contador de rótulos para saltos (L)
        
    def new_temp(self):
        # gera t1, t2, ...
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        # gera L1, L2, ...
        self.label_count += 1
        return f"L{self.label_count}"
       
    def add_inst(self, op, arg1=None, arg2=None, result=None):
        # adiciona uma instrução à lista
        self.code.append((op, arg1, arg2, result))
        
    def generate(self, ast):
        for func in ast:	# itera por todas as funções da árvore
            self.gen_function(func)
        return self.code	# retorna a lista de instruções geradas
        
    def gen_function(self, func):
        # separa os elementos de uma função (DEFUN, nome, params, corpo)
        _, name, params, body = func
        # adiciona à lista de instruções o marcador de declaração de função e o nome dela
        self.add_inst("FUNC_DECLARE", name, None, None)
        
        result = self.gen_expression(body)
        
        self.add_inst("RETURN", result, None, None)
        self.add_inst("FUNC_END", name, None, None)
