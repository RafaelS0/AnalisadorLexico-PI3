def format_ast_organized(ast_node, indent=0, is_last=True):
    """Formata um nó da AST de maneira legível e indentada."""
    spaces = "  " * indent
    connector = "└── " if is_last else "├── "
    
    # Caso base: valores primitivos
    if isinstance(ast_node, (int, float)):
        return f"{spaces}{connector}NUM: {ast_node}"
    elif isinstance(ast_node, str):
        # Verifica se é operador especial
        if ast_node in ['+', '-', '*', '/', '>', '<', '>=', '<=', '=', '/=']:
            return f"{spaces}{connector}OP: {ast_node}"
        elif ast_node.upper() in ['T', 'NIL']:
            return f"{spaces}{connector}LITERAL: {ast_node.upper()}"
        else:
            return f"{spaces}{connector}ID: {ast_node}"
    
    # Caso: tupla (estrutura da AST)
    elif isinstance(ast_node, tuple):
        if not ast_node:  # Tupla vazia
            return f"{spaces}{connector}()"
        
        op = ast_node[0]
        children = ast_node[1:]
        
        # Formata o operador principal
        result = f"{spaces}{connector}{op}"
        
        # Para operadores especiais, mostra tipo
        if op in ['+', '-', '*', '/', 'floor', 'mod', 'expt']:
            result = f"{spaces}{connector}ARITH({op})"
        elif op in ['>', '<', '>=', '<=', '=', '/=', 'eq', 'eql', 'equal', 'equalp', 'num_eq', 'num_neq']:
            result = f"{spaces}{connector}CMP({op})"
        elif op in ['car', 'cdr', 'cons']:
            result = f"{spaces}{connector}LIST({op})"
        elif op == 'if':
            result = f"{spaces}{connector}IF"
        elif op == 'cond':
            result = f"{spaces}{connector}COND"
        elif op == 'defun':
            result = f"{spaces}{connector}DEFUN: {ast_node[1]}"
        
        # Formata filhos
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            new_indent = indent + 1
            
            # Para listas dentro de tuplas (ex: parâmetros de função)
            if isinstance(child, list):
                if not child:  # Lista vazia
                    child_str = f"{'  ' * new_indent}└── []"
                else:
                    child_str = f"{'  ' * new_indent}└── LIST[{len(child)} items]"
                    # Adiciona cada item da lista
                    for j, item in enumerate(child):
                        is_last_item = (j == len(child) - 1)
                        item_indent = new_indent + 1
                        item_str = format_ast_organized(item, item_indent, is_last_item)
                        child_str += f"\n{item_str}"
            else:
                child_str = format_ast_organized(child, new_indent, is_last_child)
            
            result += f"\n{child_str}"
        
        return result
    
    # Caso: lista (sequência de expressões)
    elif isinstance(ast_node, list):
        if not ast_node:  # Lista vazia
            return f"{spaces}{connector}[]"
        
        result = f"{spaces}{connector}SEQUENCE[{len(ast_node)}]"
        for i, item in enumerate(ast_node):
            is_last_item = (i == len(ast_node) - 1)
            child_str = format_ast_organized(item, indent + 1, is_last_item)
            result += f"\n{child_str}"
        return result
    
    # Caso desconhecido
    else:
        return f"{spaces}{connector}{repr(ast_node)}"

def print_organized_ast(ast):
    """Imprime a AST completa de maneira organizada."""
    print("\n" + "="*60)
    print("ABSTRACT SYNTAX TREE (AST)")
    print("="*60)
    
    if not ast:
        print("AST vazia")
        return
    
    # Se ast for uma lista (programa), formata cada elemento
    if isinstance(ast, list):
        if len(ast) == 1 and isinstance(ast[0], tuple) and ast[0][0] == 'PROGRAM':
            # Já está no formato ('PROGRAM', [...])
            program_ast = ast[0]
            if len(program_ast) >= 2:
                for i, node in enumerate(program_ast[1]):
                    is_last = (i == len(program_ast[1]) - 1)
                    print(format_ast_organized(node, 0, is_last))
        else:
            # Formato antigo: lista direta de nós
            print("ROOT")
            for i, node in enumerate(ast):
                is_last = (i == len(ast) - 1)
                print(format_ast_organized(node, 1, is_last))
    else:
        # AST é um único nó
        print(format_ast_organized(ast, 0, True))
    
    print("="*60)

def ast_to_string(ast):
    """Converte AST para string formatada."""
    import io
    import sys
    
    # Captura a saída do print
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
    print_organized_ast(ast)
    
    # Restaura stdout
    sys.stdout = old_stdout
    
    return buffer.getvalue()

def save_ast_to_file(ast, filename="ast_output.txt"):
    """Salva a AST formatada em um arquivo."""
    ast_string = ast_to_string(ast)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ast_string)
    
    print(f"AST salva em: {filename}")
    return ast_string

# Funções auxiliares para análise
def count_nodes(ast_node):
    """Conta o número de nós na AST."""
    if isinstance(ast_node, (int, float, str)):
        return 1
    elif isinstance(ast_node, tuple):
        count = 1
        for child in ast_node:
            count += count_nodes(child)
        return count
    elif isinstance(ast_node, list):
        count = 0
        for item in ast_node:
            count += count_nodes(item)
        return count
    else:
        return 1

def get_ast_stats(ast):
    """Retorna estatísticas sobre a AST."""
    stats = {
        'total_nodes': count_nodes(ast),
        'max_depth': 0,
        'operators': {},
        'types': {}
    }
    
    def analyze_node(node, depth=0):
        nonlocal stats
        stats['max_depth'] = max(stats['max_depth'], depth)
        
        if isinstance(node, tuple) and node:
            op = node[0]
            stats['operators'][op] = stats['operators'].get(op, 0) + 1
            
            for child in node[1:]:
                analyze_node(child, depth + 1)
        elif isinstance(node, list):
            for child in node:
                analyze_node(child, depth + 1)
    
    analyze_node(ast)
    return stats

# Teste da formatação
if __name__ == "__main__":
    # Exemplo de AST de teste
    test_ast = [
        ('defun', 'soma', ['x', 'y'], ('+', 'x', 'y')),
        ('call', 'soma', [5, 3]),
        ('if', ('>', 'a', 'b'), ('+', 1, 2), ('-', 1, 2)),
        ('cons', 1, ('cons', 2, 'nil'))
    ]
    
    print("Exemplo de AST formatada:")
    print_organized_ast(test_ast)
    
    print("\nEstatísticas:")
    stats = get_ast_stats(test_ast)
    for key, value in stats.items():
        print(f"  {key}: {value}")
