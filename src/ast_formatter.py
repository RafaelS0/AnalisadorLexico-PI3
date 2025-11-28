def format_ast_organized(ast_node, indent=0):
    
    spaces = "  " * indent
    
    if isinstance(ast_node, (int, str)):
        return f"'{ast_node}'"
    
    if isinstance(ast_node, list):
        if len(ast_node) == 1:
            return format_ast_organized(ast_node[0], indent)
        
        result = "["
        for i, item in enumerate(ast_node):
            if i > 0:
                result += ","
            result += format_ast_organized(item, indent)
        result += "]"
        return result
    
    if isinstance(ast_node, tuple):
        if len(ast_node) == 1:
            return f"('{ast_node[0]}')"
        
        result = f"('{ast_node[0]}'"
        for child in ast_node[1:]:
            result += ","
            if isinstance(child, (tuple, list)) and len(str(child)) > 50:
                result += "\n" + spaces + "  "
                result += format_ast_organized(child, indent + 1)
            else:
                result += format_ast_organized(child, indent)
        result += ")"
        return result
    
    return str(ast_node)

def print_organized_ast(ast):
    """Imprime AST em formato organizado"""
    print("('PROGRAM',")
    print("  [", end="")
    
    for i, node in enumerate(ast):
        if i > 0:
            print(",")
        print(f"\n    {format_ast_organized(node, 2)}", end="")
    
    print("\n  ]")
    print(")")