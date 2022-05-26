# User guide

Using ast-refactor is a cli tool.

## Importing migrators

Out of the box ast-refactor ships with no built-in migrators tools, but does have some examples.

```bash
$ ast-refactor available
** No converters found **
```

In order to use a migrator we have to import the module that contains the migrators.  This will add all the migrators that are found in that module to the available pool
that can be used.

```bash
$ ast-refactor \
    --import ast_refactor.legacy_pandas \
    available
ast_refactor.legacy_pandas.PandasPivotTable
ast_refactor.legacy_pandas.PandasSort
ast_refactor.legacy_pandas.PandasToCsvLegacyArg
ast_refactor.legacy_pandas.PandasDropDuplicatesLegacyArg
ast_refactor.legacy_pandas.PandasLegacyIndex
```

Sometimes you want to only run a particular migrator on a set of files.  You can filter out which ones are eligible by making use of a filtering regular expression.

```bash
$ ast-refactor \
    -i ast_refactor.legacy_pandas \
    --regex '.*sort' available
ast_refactor.legacy_pandas.PandasSort
```

## Running migrators on files

You can use the same sorting and importing rules for running migrators.

If the path passed is a directory then ast-refactor will run on all python files found in that directory, otherwise it will just run on the single file you specified.

```bash
ast-refactor -i ast_refactor.legacy_pandas --regex '.*sort' run /some/path/or/file
```

### Performance considerations

Due to some of the high computational costs of some of the underlying tools used by ast-refactor, we make use of [dask](https://dask.org/) in order to parallelize processing and make more effective use of the machine you run on.

To limit the amount of cpu that this consumes use the following argument

```
ast-refactor \
    -i ast_refactor.legacy_pandas \
    --regex '.*sort' \
    run \
    --ncores 1 \
    /some/path/or/file
```

