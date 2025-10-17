from ply.yacc import yacc
from tokens import tokens, lexer

# --- Parser ---

def p_program(p):
    '''
    program : function_list
    '''
    p[0] = p[1]

def p_function_list_multi(p):
    '''
    function_list : function function_list
    '''
    p[0] = [p[1]] + p[2]

def p_function_list_single(p):
    '''
    function_list : function
    '''
    p[0] = [p[1]]

def p_function(p):
    '''
    function : LPAREN DEFUN ID LPAREN parameters RPAREN expression RPAREN
    '''
    p[0] = (p[2], p[3], p[5], p[7])

def p_param_multi(p):
    '''
    parameters : ID parameters
    '''
    p[0] = [p[1]] + p[2]

def p_param_single(p):
    '''
    parameters : ID
    '''
    p[0] = [p[1]]

def p_expression_term(p):
    '''
    expression : term
    '''
    p[0] = p[1]

def p_term(p):
    '''
    term : NUM
         | ID
         | NIL
         | T
    '''
    p[0] = p[1]

def p_expression_op(p):
    '''
    expression : LPAREN operation RPAREN
    '''
    p[0] = p[2]

# --- OPERAÇÕES ---

def p_if(p):
    '''
    operation : IF expression expression expression
    '''
    p[0] = (p[1], p[2], p[3], p[4])

def p_arith(p):
    '''
    operation : PLUS expression expression
              | MINUS expression expression
              | TIMES expression expression
              | DIVIDE expression expression
              | FLOOR expression expression
              | MOD expression expression
              | EXPT expression expression
    '''
    p[0] = (p[1], p[2], p[3])

# --- Argumentos ---

def p_call(p):
    '''
    operation : ID arglist
    '''
    p[0] = (p[1], p[2])

def p_arglist_empty(p):
    '''arglist : '''
    p[0] = []

def p_arglist_list(p):
    '''arglist : expression arglist'''
    p[0] = [p[1]] + p[2]

def p_especial_in2(p):
    '''
    operation : CAR expression
              | CDR expression
              | COND cond_clauses
    '''
    p[0] = (p[1], p[2])

def p_especial_in3(p):
    '''
    operation : CONS expression expression
    '''
    p[0] = (p[1], p[2], p[3])

# --- COND ---

def p_cond_clause(p):
    '''
    cond_clause : LPAREN expression expression RPAREN
    '''
    p[0] = (p[2], p[3])

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

# --- Comparações ---

def p_comparation(p):
    '''
    operation : EQ expression expression
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

# --- Erros ---

def p_error(p):
    if p:
        print("Erro de sintaxe! Token:", p.type, "Valor:", p.value)
    else:
        print("Erro de sintaxe: EOF inesperado")

parser = yacc()
