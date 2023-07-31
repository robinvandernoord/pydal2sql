"""
This file has methods to guess which variables are unknown and to potentially (monkey-patch) fix this.
"""

import ast
import builtins
import importlib
import textwrap
import typing

BUILTINS = set(builtins.__dict__.keys())


def traverse_ast(node: ast.AST, variable_collector: typing.Callable[[ast.AST], None]) -> None:
    """
    Calls variable_collector on each node recursively.
    """
    variable_collector(node)
    for child in ast.iter_child_nodes(node):
        traverse_ast(child, variable_collector)


def find_defined_variables(code_str: str) -> set[str]:
    tree: ast.Module = ast.parse(code_str)

    variables: set[str] = set()

    def collect_definitions(node: ast.AST) -> None:
        if isinstance(node, ast.Assign):
            node_targets = typing.cast(list[ast.Name], node.targets)

            variables.update(target.id for target in node_targets)

    traverse_ast(tree, collect_definitions)
    return variables


def remove_specific_variables(code: str, to_remove: typing.Iterable[str] = ("db", "database")) -> str:
    # Parse the code into an Abstract Syntax Tree (AST) - by ChatGPT
    tree = ast.parse(code)

    # Function to check if a variable name is 'db' or 'database'
    def should_remove(var_name: str) -> bool:
        return var_name in to_remove

    # Function to recursively traverse the AST and remove definitions of 'db' or 'database'
    def remove_db_and_database_defs_rec(node: ast.AST) -> typing.Optional[ast.AST]:
        if isinstance(node, ast.Assign):
            # Check if the assignment targets contain 'db' or 'database'
            new_targets = [
                target for target in node.targets if not (isinstance(target, ast.Name) and should_remove(target.id))
            ]
            node.targets = new_targets

        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)) and should_remove(node.name):
            # Check if function or class name is 'db' or 'database'
            return None

        for child_node in ast.iter_child_nodes(node):
            # Recursively process child nodes
            new_child_node = remove_db_and_database_defs_rec(child_node)
            if new_child_node is None and hasattr(node, "body"):
                # If the child node was removed, remove it from the parent's body
                node.body.remove(child_node)

        return node

    # Traverse the AST to remove 'db' and 'database' definitions
    new_tree = remove_db_and_database_defs_rec(tree)

    if not new_tree:  # pragma: no cover
        return ""

    # Generate the modified code from the new AST
    return ast.unparse(new_tree)


def find_local_imports(code: str) -> bool:
    class FindLocalImports(ast.NodeVisitor):
        def visit_ImportFrom(self, node: ast.ImportFrom) -> bool:
            if node.level > 0:  # This means it's a relative import
                return True
            return False

    tree = ast.parse(code)
    visitor = FindLocalImports()
    return any(visitor.visit(node) for node in ast.walk(tree))


def remove_import(code: str, module_name: typing.Optional[str]) -> str:
    tree = ast.parse(code)
    new_body = [
        node
        for node in tree.body
        if not isinstance(node, (ast.Import, ast.ImportFrom))
        or (not isinstance(node, ast.Import) or all(alias.name != module_name for alias in node.names))
        and (not isinstance(node, ast.ImportFrom) or node.module != module_name)
    ]
    tree.body = new_body
    return ast.unparse(tree)


def remove_local_imports(code: str) -> str:
    class RemoveLocalImports(ast.NodeTransformer):
        def visit_ImportFrom(self, node: ast.ImportFrom) -> typing.Optional[ast.ImportFrom]:
            if node.level > 0:  # This means it's a relative import
                return None  # Remove the node
            return node  # Keep the node

    tree = ast.parse(code)
    tree = RemoveLocalImports().visit(tree)
    return ast.unparse(tree)


def find_variables(code_str: str) -> tuple[set[str], set[str]]:
    """
    Look through the source code in code_str and try to detect using ast parsing which variables are undefined.
    """
    # Partly made by ChatGPT
    code_str = textwrap.dedent(code_str)

    # could raise SyntaxError
    tree: ast.Module = ast.parse(code_str)

    used_variables: set[str] = set()
    defined_variables: set[str] = set()
    imported_modules: set[str] = set()
    imported_names: set[str] = set()
    loop_variables: set[str] = set()

    def collect_variables(node: ast.AST) -> None:
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                used_variables.add(node.id)
            elif isinstance(node.ctx, ast.Store):
                defined_variables.add(node.id)
            elif isinstance(node.ctx, ast.Del):
                defined_variables.discard(node.id)

    def collect_definitions(node: ast.AST) -> None:
        if isinstance(node, ast.Assign):
            node_targets = typing.cast(list[ast.Name], node.targets)

            defined_variables.update(target.id for target in node_targets)

    def collect_imports(node: ast.AST) -> None:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            module_name = node.module
            imported_module = importlib.import_module(module_name)
            if node.names[0].name == "*":
                imported_names.update(name for name in dir(imported_module) if not name.startswith("_"))
            else:
                imported_names.update(alias.asname or alias.name for alias in node.names)

    def collect_imported_names(node: ast.AST) -> None:
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)

    def collect_loop_variables(node: ast.AST) -> None:
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            loop_variables.add(node.target.id)

    def collect_everything(node: ast.AST) -> None:
        collect_variables(node)
        collect_definitions(node)
        collect_imported_names(node)
        collect_imports(node)
        collect_loop_variables(node)

    # manually rewritten (2.19s for 10k):
    traverse_ast(tree, collect_everything)

    all_variables = defined_variables | imported_modules | loop_variables | imported_names | BUILTINS

    return used_variables, all_variables


def find_missing_variables(code: str) -> set[str]:
    used_variables, defined_variables = find_variables(code)
    return {var for var in used_variables if var not in defined_variables}


def generate_magic_code(missing_vars: set[str]) -> str:
    """
    After finding missing vars, fill them in with an object that does nothing except return itself or an empty string.

    This way, it's least likely to crash (when used as default or validator in pydal, don't use this for running code!).
    """
    extra_code = """
        class Empty:
            # class that does absolutely nothing
            # but can be accessed like an object (obj.something.whatever)
            # or a dict[with][some][keys]
            def __getattribute__(self, _):
                return self

            def __getitem__(self, _):
                return self

            def __get__(self):
                return self

            def __call__(self, *_):
                return self

            def __str__(self):
                return ''

            def __repr__(self):
                return ''

        # todo: overload more methods
        empty = Empty()
            \n
        """
    for variable in missing_vars:
        extra_code += f"{variable} = empty; "

    return textwrap.dedent(extra_code)
