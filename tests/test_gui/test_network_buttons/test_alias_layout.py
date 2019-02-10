import pytest

from node_launcher.gui.settings.alias_layout import AliasLayout


@pytest.fixture
def alias_layout() -> AliasLayout:
    alias_layout = AliasLayout()
    return alias_layout


class TestAliasLayout(object):
    def test_set_alias(self, alias_layout: AliasLayout):
        pass
