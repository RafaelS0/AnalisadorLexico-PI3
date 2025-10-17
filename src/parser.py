from ply.yacc import yacc
from tokens import tokens, lexer

# **** PARSER ****

# ---- Programa ----

def p_program(p):
    '''
    program : function_list
    '''
    p[0] = p[1]

# ---- Funções ----

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

# ---- Parametros ----

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

# ---- Expressões----

# ---- Expressão: Termo ----

def p_expression_term(p):
    '''expression : term'''
    p[0] = p[1]

# ---- Expressão: Operaçaõ ----

def p_expression_operation(p):
    '''expression : LPAREN operation RPAREN'''
    p[0] = p[2]

# ---- Termos ----

def p_term(p):
    '''
    term : NUM
         | ID
         | NIL
         | T
    '''
    p[0] = p[1]

# ---- Operações ----

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

# ---- If ----

def p_if(p):
    '''
    if : IF expression expression expression
    '''
    p[0] = (p[1], p[2], p[3], p[4])

# ---- Aritméticas ----

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

# ---- Comparações ----

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

# ---- Chamada ----

def p_call(p):
    '''
    call : ID arglist
    '''
    p[0] = (p[1], p[2])

def p_arglist_list(p):
    '''arglist : expression arglist'''
    p[0] = [p[1]] + p[2]

def p_arglist_empty(p):
    '''arglist : '''
    p[0] = []

# ---- Especiais 1 ----

def p_especial_1(p):
    '''
    especial_1 : CAR expression
               | CDR expression
               | COND cond_clauses
    '''
    p[0] = (p[1], p[2])

# ---- Especiais 1: Clausulas COND ----

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

# ---- Especiais 2 ----

def p_especial_2(p):
    '''
    especial_2 : CONS expression expression
    '''
    p[0] = (p[1], p[2], p[3])

# --- Erros ---

def p_error(p):
    if p:
        print("Erro de sintaxe! Token:", p.type, "Valor:", p.value)
    else:
        print("Erro de sintaxe: EOF inesperado")

parser = yacc()
