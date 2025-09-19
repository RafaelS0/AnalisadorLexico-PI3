import ply.lex as lex

# Palavras reservadas (keywords)
reserved = {
    # strings
    'string='       : 'STRING_EQ',
    'string-equal'  : 'STRING_EQUAL',

    # comandos e funções lisp
    'list'          : 'LIST',       # cria uma lista com os argumentos passados
    'cons'          : 'CONS',       # coloca o primeiro argumento no início da lista
    'nil'           : 'NIL',        # lista vazia
    'car'           : 'CAR',        # recebe uma lista e devolve o primeiro elemento
    'cdr'           : 'CDR',        # tira o primeiro elemento de uma lista
    'defun'         : 'DEFUN',      # constrói uma função
    'cond'          : 'COND',       # teste condicional
    'if'            : 'IF'
}

# Categorias de funções
ARITH_FUNCS = {"floor", "mod", "expt"}
COMP_FUNCS  = {"eq", "eql", "equal", "equalp"}
LOGIC_FUNCS = {"and", "or", "not"}

# Lista de tokens
tokens = [
	'NUM',          # números inteiros
    'ID',           # identificadores
    'COMP_OP',      # operadores de comparação
    'ARITH_OP',     # operadores aritméticos
    'LOGIC_OP',    	# operadores lógicos
    'DELIM'         # delimitadores: (), [], {}
] + list(reserved.values())

# Regras de tokens simples

t_ARITH_OP = r'[\+\-\*/]'   	# + - * /
t_DELIM    = r'[\(\)\[\]\{\}]'  # parênteses, colchetes, chaves

# Regras de tokens mais complexos

def t_NUM(t): # tokens numéricos
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t): # tokens de string
    r'[a-zA-Z_][a-zA-Z_0-9-]*'
    if t.value in ARITH_FUNCS:    # reconhece operadores aritméticos
        t.type = "ARITH_OP"
    elif t.value in COMP_FUNCS:   # reconhece operadores de comparação
        t.type = "COMP_OP"
    elif t.value in LOGIC_FUNCS:  # reconhece operadores lógicos
        t.type = "LOGIC_OP"
    else:
        t.type = reserved.get(t.value, 'ID') # reconhece como identificador
    return t

def t_COMP_OP(t): # tokens de operadores de comparação
    r'<=|>=|/=|<|>|='
    return t

def t_coment(t): # reconhece comentários
    r'--.*'
    pass         # ignora comentários

# Regras auxiliares

t_ignore = ' \t'  # ignora espaços e tabs

def t_newline(t): # localiza quebra de linha
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):   # reconhece caracteres ilegais
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Construção do lexer
lexer = lex.lex()

# dados para o teste
cmp_data = '''
-- Test

(defun soma (lista)
    (if (eq lista nil) 0
        (+ (car lista) (soma (cdr lista)))))

(defun concat (lista1 lista2)
    (if (eq lista1 nil) lista2
        (cons (car lista1)
            (concat (cdr lista1) lista2))))

(defun inverter (lista)
    (if (eq lista nil) nil
        (concat (inverter (cdr lista))
            (cons (car lista) nil))))

(defun ordenar (lista)
    (if (eq lista nil) nil
        (cons (menor (car lista) (cdr lista)) (retirar (menor (car lista) (cdr lista)) lista))))
(defun menor (atual lista)
    (if (eq lista nil) atual
        (if (lt (car lista) atual
            (menor (car lista) (cdr lista)) (menor atual (cdr lista))))
(defun retirar (elem lista)
    (cond
        ((eq lista nil) nil)
        ((eq elem (car lista)) (cdr lista))
        (T (cons (car lista) (retirar elem (cdr lista)))))
'''

# fornece os dados de teste
lexer.input(cmp_data)

print("Data (instructions):\n", cmp_data)
print("Token list:\n")

# imprime os tokens
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
