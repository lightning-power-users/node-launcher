import PySide2.QtCore


class TestPySide2(object):
    def test_version(self):
        version = PySide2.__version__
        assert(version.startswith('5.1'))
