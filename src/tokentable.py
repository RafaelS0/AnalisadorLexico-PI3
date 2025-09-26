from ply.lex import lex

reserved = {
 'floor'  : 'DIV',
 'mod'    : 'MOD',
 'expt'   : 'EXPT',
 'nil'    : 'NIL'
}

# --- Tokenizer
tokens = [
    'PLUS','MINUS','TIMES','DIVIDE',
    'LPAREN','RPAREN','NUMBER','ID'
] + list(reserved.values())

t_ignore = ' \t'

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_SYMBOL(t):
    r'[a-zA-Z_][a-zA-Z0-9_-]*'#Lisp permite hifen
    t.type = reserved.get(t.value, 'ID')#valor encontrado é palavra reservada?
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)

lexer = lex()
