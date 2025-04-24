import pytest
from spotify_syncer.events import EventBus

class Dummy:
    def __init__(self):
        self.called = False
        self.args = None

    def listener(self, *args, **kwargs):
        self.called = True
        self.args = (args, kwargs)

@pytest.fixture
def bus():
    return EventBus()

def test_subscribe_and_publish(bus):
    d = Dummy()
    bus.subscribe('test_event', d.listener)
    assert not d.called

    bus.publish('test_event', 1, key='value')
    assert d.called
    assert d.args[0] == (1,)
    assert d.args[1] == {'key': 'value'}

def test_publish_without_listeners(bus):
    # should not raise
    bus.publish('no_listeners')

# ensure multiple listeners are called
def test_multiple_listeners(bus):
    d1, d2 = Dummy(), Dummy()
    bus.subscribe('evt', d1.listener)
    bus.subscribe('evt', d2.listener)
    bus.publish('evt', 'a')
    assert d1.called and d2.called
    assert d1.args[0] == ('a',)
    assert d2.args[0] == ('a',)
