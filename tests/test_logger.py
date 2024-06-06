import pytest

from darc.logger import MASLogger


def test_singleton():
    logger_A = MASLogger()
    logger_B = MASLogger()

    assert logger_A is logger_B
