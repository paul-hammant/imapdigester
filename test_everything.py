from unittest import TestCase

import sys

from mock import Mock, call
from mockextras import stub
from digester import Digester
from processors.githubnotifications.github_notification_processor import GithubNotificationProcessor


class TestEverything(TestCase):


    def __init__(self, methodName='runTest'):
        super(TestEverything, self).__init__(methodName)
        reload(sys)
        sys.setdefaultencoding('utf8')

    def test_github_notifications(self):

        notification_store = {}

        store_writer = Mock(
            get_from_binary = stub(
                (call(u'github-notifications'), notification_store),
                (call('most-recently-seen'), 0)
            )
        )
        rollup_inbox_proxy = Mock()

        appended = u'Subject: Github Rollup (1 new)\n' \
            u'From: P H <ph@example.com>\n' \
            u'Content-Transfer-Encoding: 8bit\n' \
            u'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"\n' \
            u'MIME-Version: 1.0\nThis is a multi-part message in MIME format.\n' \
            u'-----NOTIFICATION_BOUNDARY\n' \
            u'Content-Type: text/html; charset="utf-8"\nContent-Transfer-Encoding: base64\n' \
            u'\n' \
            u'Cgo8dGFibGU+CiAgPHRyIHN0eWxlPSJiYWNrZ3JvdW5kLWNvbG9yOiAjYWNmOyI+CiAgICA8dGg+V2hlbjwvdGg+PHRoPklzc3Vlcy9QdWxsIFJlcXVlc3RzICZhbXA7IFRoZWlyIE5vdGlmaWNhdGlvbnM8L3RoPgogIDwvdHI+CgogIAogIDx0ciBzdHlsZT0iIj4KICAgIDx0ZCB2YWxpZ249InRvcCI+QXByIDAyIDIwMTY8YnIvPjAyOjE0IEFNPC90ZD4KICAgIDx0ZD4KICAgICAgPHRhYmxlIHN0eWxlPSJib3JkZXItdG9wOiBub25lIj4KICAgICAgICA8dHI+CiAgICAgICAgICA8dGQgc3R5bGU9ImJvcmRlci1ib3R0b206IDJweCBzb2xpZCBsaWdodGdyZXk7Ij4KICAgICAgICAgICAgPGEgaHJlZj0iaHR0cHM6Ly9naXRodWIuY29tL0hvbWVicmV3L2hvbWVicmV3L3B1bGwvNTA0NDEiPlB1bGwgUmVxdWVzdDogW0hvbWVicmV3L2hvbWVicmV3XSBpcmVkIDAuNS4wICgjNTA0NDEpPC9hPgogICAgICAgICAgPC90ZD4KICAgICAgICA8L3RyPgoKICAgICAgICA8dHI+CiAgICAgICAgICA8dGQgc3R5bGU9ImZvbnQtd2VpZ2h0OiBib2xkOyI+ZGhvbG06IERhdmlkIEhvbG0gKGNvbW1lbnQpIEBkdW5uIEZpeGVkLjwvdGQ+CiAgICAgICAgPC90cj4KCiAgICAgICA8L3RhYmxlPgogICAgPC90ZD4KICA8L3RyPgoKPC90YWJsZT4='

        rollup_inbox_proxy.append.side_effect = stub((call(appended), True))

        processors = []
        processor = GithubNotificationProcessor(store_writer)
        processors.append(processor)

        digester = Digester(None, None, processors, False, "P H <ph@example.com>", False)

        unmatched_to_move = []
        to_delete_from_inqueue = []

        with open('testdata/github_1.txt', 'r') as myfile:
            notification_1_content = myfile.read().replace('\n', '\r\n')

        digester.process_incoming_message(1234, processors, notification_1_content, to_delete_from_inqueue, unmatched_to_move, False)

        processor.rewrite_rollup_emails(rollup_inbox_proxy, False, False, "P H <ph@example.com>")

        self.assertEquals(rollup_inbox_proxy.mock_calls, [call.append(appended)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(len(to_delete_from_inqueue), 1)
        self.assertEquals(to_delete_from_inqueue[0], 1234)
