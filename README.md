# ast-refactor

Apply structured migrations to existing python source code easily.

This is intended to be used to migrate from older code patterns
to modern supported ones.  

For library authors this can assist in providing migration tools so that 
users can migrate to newer versions of your library more easily.  

ast-refactor *will* modify your source code if you run it, so be sure to 
run it on a repository that doesn't have code that is not checked in.

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
