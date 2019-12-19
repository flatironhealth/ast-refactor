from .core import ASTReplacer, NotMatched

import pytest
from . import legacy_pandas


def run_generic_test(replacer: ASTReplacer):

    for code, expected in replacer.examples.items():
        match = replacer.matches_code(code)
        if expected is NotMatched:
            assert match is NotMatched
            continue
        else:
            assert match

        transformed = replacer.transform_code(code)
        if isinstance(expected, str):
            assert transformed.strip().replace(
                "\n\n", "\n"
            ) == expected.strip().replace("\n\n", "\n")


@pytest.mark.parametrize(
    "replacer",
    [
        legacy_pandas.PandasPivotTable,
        legacy_pandas.PandasSort,
        legacy_pandas.PandasDropDuplicatesLegacyArg,
        legacy_pandas.PandasToCsvLegacyArg,
        legacy_pandas.PandasLegacyIndex,
    ],
)
def test_generic(replacer):
    run_generic_test(replacer())
