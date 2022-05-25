# ast-refactor

Apply structured migrations to existing python source code easily.

This is intended to be used to migrate from older code patterns
to modern supported ones.

For library authors this can assist in providing migration tools so that
users can migrate to newer versions of your library more easily.

ast-refactor *will* modify your source code if you run it, so be sure to
run it on a repository that doesn't have code that is not checked in.

## Why?

When dealing with large codebases it is common to encounter code that is using libraries in ways that are deprecated
(or removed) in newer versions of those libraries.

For example you have the following code that uses an older version of pandas (<0.17)

```python
df = pd.DataFrame({"A": ["foo", "foo", "foo", "foo", "foo",
                          "bar", "bar", "bar", "bar"],
                    "B": ["one", "one", "one", "two", "two",
                          "one", "one", "two", "two"],
                    "C": ["small", "large", "large", "small",
                          "small", "large", "small", "small",
                          "large"],
                    "D": [1, 2, 2, 3, 3, 4, 5, 6, 7],
                    "E": [2, 4, 5, 5, 6, 6, 8, 9, 9]})

table = (pd
    .pivot_table(
        df,
        rows=['A', 'B'],
        cols=['C'],
        values='D',
        aggfunc=np.sum)
    .sort("large")
)
```

The second statement uses two pandas functions with deprecated keyword arguments.  You can obviously fix this by hand, but if you have lots of code this is tedious and error prone.

`ast-refactor` provides you the tools to automatically convert that second statement into something that will work for modern versions of pandas.

```python
table = (pd
    .pivot_table(
        df,
        index=['A', 'B'],
        columns=['C'],
        values='D',
        aggfunc=np.sum)
    .sort_values("large")
)
```

This is intended as a tool to help library author and owners of large codebases migrate source code easily.

## Usage

For detailed usage documentation see [usage docs](https://github.com/flatironhealth/ast-refactor/blob/master/doc/using.md) and
[writing a migrator](https://github.com/flatironhealth/ast-refactor/blob/master/doc/writing_a_migrator.md) and

### as a python cli

The easiest way to install this tool is using
[pipx](https://pipxproject.github.io/pipx/).

```bash
$ pipx install \
    ast-refactor

$ ast-refactor run some/path/or/file
```

### as a docker container

Alternatively you can run it from a docker container

```bash
$ docker run \
    -e UID=$(id -u) \
    -e GID=$(id -u) \
    -v /some/path/or/file:/work \
    flatironhealth/ast-refactor \
    run \
    /work
```

## Building

### locally

```bash
$ pip install .
$ ast-refactor some/path/or/file
```

### docker

```bash
docker build -t ast-refactor .
```
