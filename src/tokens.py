import ply.lex as lex

# palavras reservadas (keywords) em um único dicionário
reserved = {
    # funções de string
    'string='       : 'STRING_EQ',
    'string-equal'  : 'STRING_EQUAL',

    # funções Lisp
    'list'          : 'LIST',
    'cons'          : 'CONS',
    'nil'           : 'NIL',
    'car'           : 'CAR',
    'cdr'           : 'CDR',
    'defun'         : 'DEFUN',
    'cond'          : 'COND',
    'if'            : 'IF',

    # funções aritméticas
    'floor'         : 'FLOOR',
    'mod'           : 'MOD',
    'expt'          : 'EXPT',

    # funções de comparação
    'eq'            : 'EQ',
    'eql'           : 'EQL',
    'equal'         : 'EQUAL',
    'equalp'        : 'EQUALP',

    # funções lógicas
    'and'           : 'AND',
    'or'            : 'OR',
    'not'           : 'NOT'
}

# lista de tokens
tokens = [
             # tipos de dados
             'NUM',
             'STRING',
             'ID',  # só para identificadores que não são palavras-chave

             # operadores
             'PLUS',      # +
             'MINUS',     # -
             'TIMES',     # *
             'DIVIDE',    # /
             'NUM_EQ',    # =
             'NUM_NEQ',   # /=
             'GT',        # >
             'GTE',       # >=
             'LT',        # <
             'LTE',       # <=

             # delimitadores
             'LPAREN',
             'RPAREN',
             'LBRACKET',  # [
             'RBRACKET',  # ]
             'LBRACE',    # {
             'RBRACE',    # }
             'T'          # true
         ] + list(reserved.values()) # adiciona as palavras-chave do dicionário

# regras de tokens simples para símbolos
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_NUM_EQ    = r'='
t_NUM_NEQ   = r'/='
t_GT        = r'>'
t_GTE       = r'>='
t_LT        = r'<'
t_LTE       = r'<='
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'


# regras de tokens mais complexos

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"[^\"]*\"'
    t.value = t.value[1:-1]
    return t

def t_SYMBOL(t):
    r'[a-zA-Z_][a-zA-Z_0-9-]*'
    lower_val = t.value.lower() # converte para minúsculas para comparação
    if lower_val == 't':
        t.type = 'T'
        t.value = 'T'
    elif lower_val == 'nil':
        t.type = 'NIL'
        t.value = 'nil'
    else:
        t.type = reserved.get(t.value, 'ID') # a verificação é no dicionário de palavras reservadas
    return t

def t_coment(t):
    r';.*'
    pass

# Regras auxiliares
t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Construção do lexer
lexer = lex.lex()

with open("lisp_code.txt", "r") as file:
    cmp_data = file.read()

lexer.input(cmp_data)

print("Data (instructions):\n", cmp_data)
print("Token list:\n")

# imprime os tokens
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
