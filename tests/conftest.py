import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--with-scanner",
        action="store_true",
        default=False,
        help="run tests using an actual scanner"
    )
