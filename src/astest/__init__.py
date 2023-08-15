"""astest - The quick, easy way to write tests in Python.."""
import ast
import code
from functools import cache
import os
import sys
import time
from typing import Any, Mapping


class AstestConverter(ast.NodeTransformer):
    def __init__(self, filepath: str, debug_mode: bool) -> None:
        self.filepath = filepath
        self.debug_mode = debug_mode

    def visit_Assert(self, node: ast.Assert) -> ast.Expr:
        test_call = ast.Call(
            func=ast.Name("$test", ctx=ast.Load()),
            args=[node.test],
            keywords=[
                ast.keyword("filepath", ast.Constant(self.filepath)),
                ast.keyword("line", ast.Constant(node.lineno)),
                ast.keyword("column", ast.Constant(node.col_offset)),
                ast.keyword("endline", ast.Constant(node.end_lineno)),
                ast.keyword("endcolumn", ast.Constant(node.end_col_offset)),
            ],
        )
        if self.debug_mode:
            test_call = ast.Call(
                func=ast.Name("$debugger", ctx=ast.Load()),
                args=[test_call],
                keywords=[
                    ast.keyword(
                        "locals",
                        ast.Call(
                            func=ast.Name("locals", ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        ),
                    ),
                ],
            )

        return ast.Expr(test_call)


@cache
def get_source(filepath: str) -> str:
    with open(filepath) as file:
        return file.read()


def red(msg: str) -> str:
    return f"\033[1;31m{msg}\033[m"


def green(msg: str) -> str:
    return f"\033[1;32m{msg}\033[m"


test_count = 0
pass_count = 0


def run(filepath: str, debug_mode: bool) -> None:
    """Run the given file as a test file."""
    if not os.path.isfile(filepath):
        print(red("Error:"), f"{filepath!r} doesn't exist.")
        sys.exit(2)

    start_time = time.monotonic()

    source = get_source(filepath)
    tree = ast.parse(source)

    test_tree = AstestConverter(filepath, debug_mode).visit(tree)
    ast.fix_missing_locations(test_tree)

    test_code_object = compile(test_tree, filepath, mode="exec")
    exec(test_code_object, {"$test": _test, "$debugger": _debugger})

    end_time = time.monotonic()

    if test_count == 0:
        print(red("Error:"), "No tests ran. Make sure the code does some `assert`s.")
        sys.exit(3)

    time_taken = f"{end_time - start_time:.2f} seconds"

    if pass_count == test_count:
        summary = green(f" {pass_count} passed in {time_taken} ")
    else:
        fail_count = test_count - pass_count
        summary = red(f" {fail_count} failed, {pass_count} passed in {time_taken} ")

    terminal_width, _ = os.get_terminal_size()
    # \033[1;32m and \033[m add 7+3 = 10 characters to the string length
    ansi_padding = 10
    print(f"{summary:=^{terminal_width + ansi_padding}}")


def get_source_snippet(
    filepath: str, line: int, column: int, endline: int, endcolumn: int
) -> str:
    source_lines = get_source(filepath).splitlines()

    snippet_lines = source_lines[line - 1 : endline]
    snippet_lines[0] = snippet_lines[0][column:]
    snippet_lines[-1] = snippet_lines[-1][:endcolumn]

    return "\n".join(snippet_lines)


def _test(
    condition: bool,
    *,
    filepath: str,
    line: int,
    column: int,
    endline: int,
    endcolumn: int,
) -> bool:
    global test_count, pass_count

    test_count += 1
    condition == bool(condition)

    terminal_width, _ = os.get_terminal_size()
    test_message_length = terminal_width - 6  # to keep space for PASSED / FAILED msg
    test_message = format(f"Test {test_count}", f".<{test_message_length}")

    passed = green("PASSED")
    failed = red("FAILED")

    if condition is True:
        print(test_message + passed)
        pass_count += 1
    else:
        print(test_message + failed)
        print(
            "Failing test:",
            red(get_source_snippet(filepath, line, column, endline, endcolumn)),
        )

    # Used in _debugger()
    return condition


def _debugger(condition: bool, locals: Mapping[str, Any]) -> None:
    if condition is False:
        code.interact(local=locals, banner=red("Starting debug session:"), exitmsg="")
