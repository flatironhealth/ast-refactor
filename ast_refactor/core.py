import horast
import astsearch
import astcheck
import typed_ast.ast3 as ast
import astmonkey.transformers
from itertools import accumulate
import abc
from typing import Sequence, Dict, Union, NewType


NotMatchedType = NewType("NotMatchedType", object)
NotMatched = NotMatchedType(object())


class CantParseException(Exception):
    pass


def monkeypatch():
    """Monkeypatch our dependencies so that they use typed_ast instead of ast"""
    setattr(astcheck, "ast", ast)
    setattr(astsearch, "ast", ast)
    setattr(astmonkey.transformers, "ast", ast)


monkeypatch()


def find_parent_statement(node):
    """Traverse upwards through the ast until we hit a statement node"""
    while not isinstance(node, (ast.stmt, ast.Module)):
        node = node.parent
    return node


def find_next_sibling(node):
    """Finds the next sibling node of an ast element.

    This is used to determine the next statement for an interesting ast node"""
    found = False
    if node.parent is None:
        return None
    for nn in node.parent.children:
        if found:
            return nn
        if nn is node:
            found = True
    return find_next_sibling(node.parent)


def transform_code(code: str, xformer: "ASTMigrator") -> str:
    """Apply a transformer to a given chunk of source code

    This will parse the code using the AST and find the expressions that are interesting according to xformer.

    If those are found the resulting statements will be rewritten and merged into the final source code
    """

    line_ends = list(accumulate([len(x) for x in code.splitlines(keepends=True)]))
    line_starts = [0] + [x for x in line_ends[:-1]]

    try:
        tree = horast.parse(code)
    except Exception as e_horast:
        # fallback to regular typed ast
        try:
            tree = ast.parse(code)
        except Exception as e:
            raise CantParseException(str(e), code)

    matched = list(xformer.scan_ast(tree))

    astmonkey.transformers.ParentChildNodeTransformer().visit(tree)

    def node_to_code_offset(node, use_col_offset=True):
        return line_starts[node.lineno - 1] + use_col_offset * node.col_offset

    # Replace the matched patterns in reverse line order
    for match in sorted(
        matched, key=lambda node: (node.lineno, node.col_offset), reverse=True
    ):
        xformer.transform_match(match)

        parent_statement = find_parent_statement(match)
        next_statement = find_next_sibling(parent_statement)

        code_start = node_to_code_offset(parent_statement)
        if next_statement:
            code_end = node_to_code_offset(next_statement, use_col_offset=False)
        else:
            code_end = len(code)

        new_code = horast.unparse(parent_statement)
        new_code = new_code.strip()

        code = code[:code_start] + new_code + "\n" + code[code_end:]

    return code


class ASTMigrator(object, metaclass=abc.ABCMeta):

    pattern = NotImplemented
    examples: Dict[str, Union[str, NotMatchedType]]

    def __init__(self):
        self._pattern = astsearch.prepare_pattern(self.pattern)
        self._finder = astsearch.ASTPatternFinder(self._pattern)

    @classmethod
    def name(cls):
        return f"{cls.__module__}.{cls.__qualname__}"

    def filter_node(self, node: ast.AST):
        """Post-process the ast nodes to find the one that matches.  This is needed since the expression does not always
        capture the correct behavior"""
        return True

    def scan_ast(self, tree: ast.AST) -> Sequence[ast.stmt]:
        return [n for n in self._finder.scan_ast(tree) if self.filter_node(n)]

    def scan_code(self, code: str) -> Sequence[ast.AST]:
        try:
            # horast can parse and preserve comments
            tree = horast.parse(code)
        except (ValueError, TypeError):
            # fallback to regular typed ast
            tree = ast.parse(code)
        return self.scan_ast(tree)

    def matches_code(self, code: str):
        if len(self.scan_code(code)) == 0:
            return NotMatched
        else:
            return True

    @abc.abstractmethod
    def transform_match(self, node: ast.AST) -> None:
        """Transform this node"""
        pass

    def transform_code(self, code: str):
        return transform_code(code, self)
