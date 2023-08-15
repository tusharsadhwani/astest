# astest: `assert` based testing

The quick, easy way to write tests in Python.

## Usage

Get the tool by installing it from `pip`:

```bash
pip install astest
```

The tool doesn't have to be installed in your project's environment, you can
also install it in your global Python (since it has no dependencies).

Then give it a file containing "tests" (explained below):

```bash
astest test_file.py
```

---

You can also easily run it via `pipx`:

```bash
pipx run astest test_file.py
```

### Test files

`astest` expects a file that does `assert`'s at runtime.

So to write a test for your code, simply do `assert`s in your file:

```python
from my_library import add

assert add(12, 13) == 25
assert add(33, 77) == 100  # This one is false
assert add(123, 123) == 246
```

Running this will look like this:

```console
$ astest examples/simple.py
Test 1..................................................................PASSED
Test 2..................................................................FAILED
Failing test: assert add(33, 77) == 100
Test 3..................................................................PASSED
===================== 1 failed, 2 passed in 0.00 seconds =====================
```

### Debugging

If a test fails and you wish to debug it, you can run `astest` with `--debug`:

```console
$ astest examples/simple.py
Test 1..................................................................PASSED
Test 2..................................................................FAILED
Failing test: assert add(33, 77) == 100
Starting debug session:
>>> add(33, 77)
110
>>> # Oh okay.
>>> ^D
Test 3..................................................................PASSED
===================== 1 failed, 2 passed in 0.00 seconds =====================
```

## Local Development / Testing

- Create and activate a virtual environment
- Run `pip install -r requirements-dev.txt` to do an editable install
- Run `pytest` to run tests

## Type Checking

Run `mypy .`

## Create and upload a package to PyPI

Make sure to bump the version in `setup.cfg`.

Then run the following commands:

```bash
rm -rf build dist
python setup.py sdist bdist_wheel
```

Then upload it to PyPI using [twine](https://twine.readthedocs.io/en/latest/#installation):

```bash
twine upload dist/*
```
