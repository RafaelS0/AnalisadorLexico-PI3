import ply.lex as lex

# keywords : token
reserved = {
    # para string
    'string='      	: 'STRING_EQ',
    'string-equal' 	: 'STRING_EQUAL',

    # comandos e funções lisp
    'list'          : 'LIST',       # cria uma lista com os argumentos passados
    'cons'          : 'CONS',       # coloca o primeiro argumento no início da lista
    'nil'           : 'NIL',        # lista vazia
    'car'           : 'CAR',        # recebe uma lista e devolve o primeiro elemento
    'cdr'           : 'CDR',        # tira o primeiro elemento de uma lista
    'defun'         : 'DEFUN',      # constrói uma função
    'cond'          : 'COND'        # teste condicional
}

tokens = [
    # para números
    'OP_COMP',
    'OP_ARITH',
    'DELIM',
    'COMENT',
	
    # outros
    'NUMBER',
    'LPAREN',
    'RPAREN',
    'IDENT' # <- ID
] + list(reserved.values())#adiciona aos tokens

t_OP_ARITH = r'[\+\-\*/]'
#t_COMENT = r'\#'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)#converte o valor do lexema para inteiro
    return t

# letra_ -> [A-Za-z_]
# digito -> [0-9]
# id     -> letra_ (letra_ | digito)*

def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z_0-9-]*(-)?'#Lisp permite hifen
    if t.value in ("floor", "mod", "expt"):
        t.type = "OP_ARITH"
    elif t.value in ("eq", "eql", "equal", "equalp"):
        t.type = "OP_COMP"
    else:
        t.type = reserved.get(t.value, 'IDENT')
    return t

def t_LIMITER(t) :
	r'[\(\)\[\]\{\}]'
	t.type = "DELIM"
	return t

def t_COMPARATORY(t):
	r'[<>][=]? | [/][=]'
	t.type = "OP_COMP"
	return t
	
def t_COMENT(t):
	r'[\#] ([ \t]+ | [\#a-zA-Z_0-9-\+\-\*/\(\)\[\]\{\}<>=])+'
	t.tipe = "COMENT"
	return t

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule - (chamada quando um caractere ilegal é encontrado)
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Build the lexer
lexer = lex.lex()

# Test it out
cmp_data = '''
(/ 4 2)  #o 1 / = + ) [
(eq 4 4)
'''

# prints (Lisp)
#(format t "gt (>): 10 > 5? ~a~%" (> 10 5))
#(format t "geq (>=): 10 >= 10? ~a~%" (>= 10 10))
#(format t "lt (<): 5 < 10? ~a~%" (< 5 10))
#(format t "leq (<=): 10 <= 10? ~a~%" (<= 10 10))
#(format t "eq (=): 10 == 10? ~a~%" (= 10 10))
#(format t "neq (/=): 5 != 10? ~a~%" (/= 5 10))

# Give the lexer some input
lexer.input(cmp_data)

print("dados (instruções):", cmp_data)
print("lista de tokens:")

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
