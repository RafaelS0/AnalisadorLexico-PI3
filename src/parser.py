from ply.yacc import yacc
from tokens import tokens, lexer

# ===========================================
#                 PROGRAMA
# ===========================================

# O programa é uma sequência de código
def p_program(p):
    '''
    program : sequence
    '''
    p[0] = p[1]
    
    
# ===========================================
#            SEQUÊNCIA E BLOCO DE CÓDIGO
# ===========================================

# Uma sequência de código é uma sequência de código seguida de um bloco de código
def p_sequence_list(p):
    '''
    sequence : sequence block
    '''
    p[0] = p[1] + [p[2]]

# Uma sequência de código é um bloco de código
def p_sequence_single(p):
    '''
    sequence : block
    '''
    p[0] = [p[1]]

# Um bloco de código pode ser uma função ou uma expressão
def p_element(p):
    '''
    block : function
          | expression
    '''
    p[0] = p[1]

# ===========================================
#                 FUNÇÕES
# ===========================================

# Definição de função
def p_function(p):
    '''
    function : LPAREN DEFUN ID LPAREN param_list RPAREN expression RPAREN
    '''
    p[0] = ('defun', p[3], p[5], p[7])

# Lista de parâmetros
def p_param_list_multi(p):
    '''
    param_list : ID param_list
    '''
    p[0] = [p[1]] + p[2]

def p_param_list_single(p):
    '''
    param_list : ID
    '''
    p[0] = [p[1]]

def p_param_list_empty(p):
    '''
    param_list :
    '''
    p[0] = []

# ===========================================
#                EXPRESSÕES
# ===========================================

# Expressão -> Termo 
def p_expression_term(p):
    '''
    expression : term
    '''
    p[0] = p[1]

# Expressão -> Operação 
def p_expression_operation(p):
    '''
    expression : LPAREN operation RPAREN
    '''
    p[0] = p[2]

# ===========================================
#                TERMOS
# ===========================================

def p_term(p):
    '''
    term : NUM
         | ID
         | NIL
         | T
         | LPAREN RPAREN
    '''
    if len(p) == 3:  # () -> nil se a lista estiver vazia retorna NIL
        p[0] = 'nil'
    else:
        p[0] = p[1]

# ===========================================
#                OPERAÇÕES
# ===========================================

def p_operation(p):
    '''
    operation : if
              | arith
              | comparation
              | call
              | especial_1
              | especial_2
    '''
    p[0] = p[1]

# If
def p_if(p):
    '''
    if : IF expression expression expression
    '''
    p[0] = ('if', p[2], p[3], p[4])

# Aritméticas
def p_arith(p):
    '''
    arith : PLUS expression expression
          | MINUS expression expression
          | TIMES expression expression
          | DIVIDE expression expression
          | FLOOR expression expression
          | MOD expression expression
          | EXPT expression expression
    '''
    p[0] = (p[1], p[2], p[3])

# Comparações
def p_comparation(p):
    '''
    comparation : EQ expression expression
                | EQL expression expression
                | EQUAL expression expression
                | EQUALP expression expression
                | NUM_EQ expression expression
                | NUM_NEQ expression expression
                | GT expression expression
                | GTE expression expression
                | LT expression expression
                | LTE expression expression
    '''
    p[0] = (p[1], p[2], p[3])

# Chamada de funções
def p_call(p):
    '''
    call : ID arglist
    '''
    p[0] = (p[1], p[2])

def p_arglist_list(p):
    '''
    arglist : expression arglist
    '''
    p[0] = [p[1]] + p[2]

def p_arglist_empty(p):
    '''
    arglist :
    '''
    p[0] = []

# Especiais 1: car, cdr e cond
def p_especial_1(p):
    '''
    especial_1 : CAR expression
               | CDR expression
               | COND cond_clauses
    '''
    op = p[1]
    if op in ['car', 'cdr']:
        p[0] = (op, p[2])
    else:
        p[0] = ('cond', p[2])

# -------------------------------------------
# Cláusulas COND
# -------------------------------------------
def p_cond_clauses_empty(p):
    '''
    cond_clauses :
    '''
    p[0] = []

def p_cond_clauses_nonempty(p):
    '''
    cond_clauses : cond_clause cond_clauses
    '''
    p[0] = [p[1]] + p[2]

def p_cond_clause(p):
    '''
    cond_clause : LPAREN expression expression RPAREN
    '''
    p[0] = (p[2], p[3])

# Especiais 2: cons
def p_especial_2(p):
    '''
    especial_2 : CONS expression expression
    '''
    p[0] = ('cons', p[2], p[3])

# ===========================================
#                ERROS
# ===========================================

def p_error(p):
    if p:
        print("Erro de sintaxe! Token:", p.type, "Valor:", p.value)
    else:
        print("Erro de sintaxe: EOF inesperado")

parser = yacc()
