from ply.lex import lex
from ply.yacc import yacc

# --- Tokenizer
tokens = (
    'PLUS','MINUS','TIMES','DIVIDE','DIV','MOD','EXPT',
    'LPAREN','RPAREN',
    'NAME','NUMBER'
)

t_ignore = ' \t'

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_DIV    = r'floor'
t_MOD    = r'mod'
t_EXPT   = r'expt'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_NAME   = r'[a-zA-Z_][a-zA-Z0-9_-]*'

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

# --- Parser

# lista de argumentos (múltiplos ou um só)
def p_expression_list_multiple(p):
    '''
    expression_list : expression expression_list
    '''
    p[0] = [p[1]] + p[2]

def p_expression_list_single(p):
    '''
    expression_list : expression
    '''
    p[0] = [p[1]]

# chamadas: (op arg1 arg2 ...)
def p_expression_call(p):
    '''
    expression : LPAREN operator expression_list RPAREN
    '''
    args = " ".join(p[3])
    p[0] = f"({p[2]} {args})"

# números
def p_expression_number(p):
    '''
    expression : NUMBER
    '''
    p[0] = str(p[1])

# identificadores
def p_expression_name(p):
    '''
    expression : NAME
    '''
    p[0] = p[1]

# operador pode ser um dos tokens ou um nome qualquer
def p_operator(p):
    '''
    operator : PLUS
             | MINUS
             | TIMES
             | DIVIDE
             | DIV
             | MOD
             | EXPT
             | NAME
    '''
    if p.slice[1].type == "PLUS":
        p[0] = ('plus', p[1])
    elif p.slice[1].type == "MINUS":
        p[0] = ('minus', p[1])
    elif p.slice[1].type == "TIMES":
        p[0] = ('times', p[1])
    elif p.slice[1].type == "DIVIDE":
        p[0] = ('divide', p[1])
    elif p.slice[1].type == "DIV":
        p[0] = ('div', p[1])
    elif p.slice[1].type == "MOD":
        p[0] = ('mod', p[1])
    elif p.slice[1].type == "EXPT":
        p[0] = ('expt', p[1])
    else:
        p[0] = ('identificador', p[1])

def p_error(p):
    print(f'Syntax error at {p.value!r}')

parser = yacc()

# --- Testes
print(parser.parse('(+ 1 2)'))
print(parser.parse('(+ 1 (mod 10 3))'))
print(parser.parse('(expt 2 8)'))
print(parser.parse('(+ 1 2 3 4 5)'))
