from ply.lex import lex
from ply.yacc import yacc

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

# --- Parser

# lista de argumentos (múltiplos ou um só)
def p_expression_list_multiple(p):
    '''
    expression_list : expression expression_list
    '''
    p[0] = (p[1],p[2])

def p_expression_list_single(p):
    '''
    expression_list : expression
    '''
    p[0] = p[1]

def p_expression_call(p):
    '''
    expression : LPAREN operator expression_list RPAREN
    '''
    p[0] = (p[2],p[3])

def p_expression_one(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    p[0] = p[2]
    
def p_expression_call_no_args(p):
    '''
    expression : LPAREN operator RPAREN
    '''
    p[0] = p[2]

def p_expression_empty(p):
    '''
    expression : LPAREN RPAREN
    '''
    p[0] = ('nil')

# números
def p_expression_number(p):
    '''
    expression : NUMBER
    '''
    p[0] = ('num',p[1])
    
# identificadores
def p_expression_name(p):
    '''
    expression : ID
    '''
    p[0] = ('id',p[1])

# operador pode ser um dos tokens ou um nome qualquer
def p_operator_reserved(p):
    '''
    operator : PLUS
             | MINUS
             | TIMES
             | DIVIDE
             | DIV
             | MOD
             | EXPT
             | NIL
             | ID
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
    elif p.slice[1].type == "NIL":
        p[0] = ('nil', p[1])
    elif p.slice[1].type == "ID":
        p[0] = ('id', p[1])

def p_error(p):
    print(f'Syntax error at {p.value!r}')

parser = yacc()

# --- Testes

print(parser.parse('(T (cons (car lista) (retirar elem (cdr lista))))'))
