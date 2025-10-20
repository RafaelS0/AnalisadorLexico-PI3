from parser import parser

code = """
(defun soma (lista)
    (if (eq lista nil) 0
        (+ (car lista) (soma (cdr lista)))))
		
(defun ordenar (lista)
    (if (eq lista nil) nil
        (cons (menor (car lista) (cdr lista))
              (retirar (menor (car lista) (cdr lista)) lista))))
(defun menor (atual lista)
    (if (eq lista nil) atual
        (if (< (car lista) atual)
            (menor (car lista) (cdr lista))
            (menor atual (cdr lista)))))
"""

ast = parser.parse(code)
print(ast)
