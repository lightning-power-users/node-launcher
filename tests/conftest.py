import pytest
from pytestqt.exceptions import capture_exceptions, format_captured_exceptions
from pytestqt.qtbot import QtBot


@pytest.yield_fixture(scope="session")
def qtbot_session(qapp, request):
    result = QtBot(qapp)
    with capture_exceptions() as exceptions:
        yield result
    if exceptions:
        pytest.fail(format_captured_exceptions(exceptions))
