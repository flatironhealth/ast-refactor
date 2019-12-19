from textwrap import dedent

from typed_ast import ast3 as ast

from .core import ASTReplacer, NotMatched


class PandasPivotTable(ASTReplacer):
    pattern = "?.pivot_table(??, rows=?)"

    examples = {
        "df.pivot_table(rows=['a'], cols=['b'], values=['some_field']).reset_index()": "df.pivot_table(index=['a'], columns=['b'], values=['some_field']).reset_index()",
        "df.pivot_table(index=['a'], columns=['b'], values=['some_field'])": NotMatched,
    }

    def transform_match(self, node: ast.AST) -> None:
        assert isinstance(node, ast.Call)
        for kw in node.keywords:
            if kw.arg == "rows":
                kw.arg = "index"
            if kw.arg == "cols":
                kw.arg = "columns"


class PandasSort(ASTReplacer):
    pattern = "?.sort(??)"

    examples = {
        'df.sort("somecol")': "df.sort_values('somecol')",
        dedent(
            """
        def f(scores):
            scores_df = pd.DataFrame(scores)
            return scores_df.sort(['score'], ascending=False).reset_index(drop=True)

        def g(df):
            def inner():
                df.sort(['some_arg'], inplace=True)

            inner()
            return df
        """
        ): dedent(
            """
            def f(scores):
                scores_df = pd.DataFrame(scores)
                return scores_df.sort_values(['score'], ascending=False).reset_index(drop=True)

            def g(df):
                def inner():
                    df.sort_values(['some_arg'], inplace=True)

                inner()
                return df
            """
        ),
        "df.sort()": NotMatched,
    }

    def transform_match(self, node: ast.AST) -> None:
        assert isinstance(node, ast.Call)
        # determine if this might be pandas
        node.func.attr = "sort_values"  # type: ignore

    def filter_node(self, node: ast.AST):
        assert isinstance(node, ast.Call)
        if len(node.args) == 0 and len(node.keywords) == 0:
            return False
        else:
            return True


class PandasToCsvLegacyArg(ASTReplacer):
    pattern = "?.to_csv(??, cols=?)"
    examples = {
        "df.to_csv(filename, cols=['a', 'b', 'c'])": "df.to_csv(filename, columns=['a', 'b', 'c'])",
        "df.to_csv(filename, columns=['a', 'b', 'c'])": NotMatched,
        "df.to_csv(filename, sep='\x01')": NotMatched,
    }

    def transform_match(self, node: ast.AST) -> None:
        assert isinstance(node, ast.Call)
        for kw in node.keywords:
            if kw.arg == "cols":
                kw.arg = "columns"


class PandasDropDuplicatesLegacyArg(ASTReplacer):
    pattern = "?.drop_duplicates(??, cols=?)"
    examples = {"df.drop_duplicates(cols=['a'])": "df.drop_duplicates(columns=['a'])"}

    def transform_match(self, node: ast.AST) -> None:
        assert isinstance(node, ast.Call)
        for kw in node.keywords:
            if kw.arg == "cols":
                kw.arg = "columns"


class PandasLegacyIndex(ASTReplacer):
    """Replace all .ix locations with .loc,  This may not be correct, as .ix is fuzzy in what it does!"""

    pattern = "?.ix[??]"
    examples = {"df.ix[somevalues].sum()": "df.loc[somevalues].sum()"}

    def transform_match(self, node: ast.AST) -> None:
        assert isinstance(node, ast.Subscript)
        node.value.attr = "loc"  # type: ignore
