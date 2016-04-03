from unittest import TestCase

from mock import Mock, call
from mockextras import stub


class Appender:

    def __init__(self):
        self.appended = []

    def append(self, message):
        self.appended.append(message)
        return True

class AppenderTest(TestCase):

    def test_this_one_works(self):

        foo = Mock()
        appended = "a"
        foo.append.side_effect = stub((call(appended), True))
        foo.append("a")
        self.assertEquals(foo.mock_calls, [call.append(appended)])

    def test_this_one_barfs_with_KeyError_but_should_really_be_more_helpful(self):

        foo = Mock()
        appended = "a a"
        foo.append.side_effect = stub((call(appended), True))
        foo.append("a")
        self.assertEquals(foo.mock_calls, [call.append(appended)])

