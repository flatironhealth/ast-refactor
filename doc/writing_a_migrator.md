# Writing a migrator

In order to write a new migrator you need to subclass `ast_refactor.ASTMigrator`.

There are a few examples available in `ast_refactor.legacy_pandas`

```python
class PandasPivotTable(ASTMigrator):

    pattern = "?.pivot_table(??, rows=?)"

    def transform_match(self, node: ast.AST) -> None:
        assert isinstance(node, ast.Call)
        for kw in node.keywords:
            if kw.arg == "rows":
                kw.arg = "index"
            if kw.arg == "cols":
                kw.arg = "columns"

    examples = {
        "df.pivot_table(rows=['a'], cols=['b'], values=['some_field']).reset_index()": "df.pivot_table(index=['a'], columns=['b'], values=['some_field']).reset_index()",
        "df.pivot_table(index=['a'], columns=['b'], values=['some_field'])": NotMatched,
    }

```

There are three key components of this migrator.

## `pattern`

The pattern used to match an expression is matched using [astsearch](https://github.com/takluyver/astsearch).  This allows you to specify a pattern of code to attempt to match.
`?` and `??` are used a wildcards.  `??` is a more greedy variant which will match more.

## `transform_match`

This function gets passed the python AST node that is matched.  You can make changes to the code by altering the AST.  In this case here we have a `Call` node and can use this to alter some of the attributes of the node or to create new nodes.

The AST nodes passed to you have been augmented using [astmonkey.transformers.ParentChildNodeTransformer()](https://github.com/mutpy/astmonkey#transformersparentchildnodetransformer) in order to make traversing the AST easier.  This is useful if you have to replace an AST node with a more complex one, in order to have access to its parent.

For a good guide on what is present in the AST see [this guide](https://greentreesnakes.readthedocs.io/en/latest/nodes.html)

## `examples`

The examples here can serve as documentation and test cases on what your migrator can and cannot convert.
