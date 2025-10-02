from ply.yacc import yacc
from tokens import tokens,lexer

# --- Parser

# lista de argumentos (múltiplos ou um só)
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
    p[0] = (p[2],p[3],p[5],p[7])
    
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
    '''expression : NUM
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

def p_condition(p):
    '''
    operation : IF comparation expression expression
    '''
    p[0] = (p[1],p[2],p[3],p[4])
    
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
    p[0] = (p[1],p[2],p[3])

def p_elements_call(p):
    '''
    operation : ID arglist
    '''
    p[0] = (p[1], p[2])
    
def p_especial_in2(p):
    '''
    operation : CAR expression
			  | CDR expression
    '''
    p[0] = (p[1], p[2])
    
def p_especial_in3(p):
    '''
    operation : CONS expression expression
    '''
    p[0] = (p[1],p[2],p[3])
    
def p_especial_cond(p):
    '''
    operation : COND LPAREN expression RPAREN
    '''
    p[0] = (p[1],p[2],p[3],p[4])
    
def p_operation_compp(p):
    '''
    operation : comparation
    '''
    p[0] = p[1]
    
def p_comparation(p):
    '''
    comparation : LPAREN EQ expression expression RPAREN
                | LPAREN EQL expression expression RPAREN
                | LPAREN EQUAL expression expression RPAREN
                | LPAREN EQUALP expression expression RPAREN
                | LPAREN NUM_EQ expression expression RPAREN
                | LPAREN NUM_NEQ expression expression RPAREN
                | LPAREN GT expression expression RPAREN
                | LPAREN GTE expression expression RPAREN
                | LPAREN LT expression expression RPAREN
                | LPAREN LTE expression expression RPAREN
    '''
    # p[2] é o valor do token (ex.: 'eq', 'eql', '>')
    p[0] = (p[2], [p[3], p[4]])


def p_arglist_empty(p):
    '''arglist : '''
    p[0] = []

def p_arglist_list(p):
    '''arglist : expression arglist'''
    p[0] = [p[1]] + p[2]

def p_error(p):
    print("Erro de sintaxe!", p)

parser = yacc()
