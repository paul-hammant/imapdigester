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

        appended = u'Subject: Github Rollup (1 new)\nFrom: P H <ph@example.com>\nContent-Transfer-Encoding: 8bit\nContent-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"\nMIME-Version: 1.0\nThis is a multi-part message in MIME format.\n-----NOTIFICATION_BOUNDARY\nContent-Type: text/html; charset="utf-8"\nContent-Transfer-Encoding: base64\n\nCgo8dGFibGU+CiAgPHRyIHN0eWxlPSJiYWNrZ3JvdW5kLWNvbG9yOiAjYWNmOyI+CiAgICA8dGg+V2hlbjwvdGg+PHRoPklzc3Vlcy9QdWxsIFJlcXVlc3RzICZhbXA7IFRoZWlyIE5vdGlmaWNhdGlvbnM8L3RoPgogIDwvdHI+CgoKICA8dHIgc3R5bGU9IiI+CiAgICA8dGQgdmFsaWduPSJ0b3AiPkFwciAwMiAyMDE2PGJyLz4wMjoxNCBBTTwvdGQ+CiAgICA8dGQ+CiAgICAgIDx0YWJsZSBzdHlsZT0iYm9yZGVyLXRvcDogbm9uZSI+CiAgICAgICAgPHRyPgogICAgICAgICAgPHRkIHN0eWxlPSJib3JkZXItYm90dG9tOiAycHggc29saWQgbGlnaHRncmV5OyI+CiAgICAgICAgICAgIDxhIGhyZWY9Imh0dHBzOi8vZ2l0aHViLmNvbS9Ib21lYnJldy9ob21lYnJldy9wdWxsLzUwNDQxIj5QdWxsIFJlcXVlc3Q6IFtIb21lYnJldy9ob21lYnJld10gaXJlZCAwLjUuMCAoIzUwNDQxKTwvYT4KICAgICAgICAgIDwvdGQ+CiAgICAgICAgPC90cj4KCiAgICAgICAgPHRyPgogICAgICAgICAgPHRkIHN0eWxlPSJmb250LXdlaWdodDogYm9sZDsiPmRob2xtOiBEYXZpZCBIb2xtIChjb21tZW50KSBAZHVubiBGaXhlZC48L3RkPgogICAgICAgIDwvdHI+CgogICAgICAgPC90YWJsZT4KICAgIDwvdGQ+CiAgPC90cj4KCjwvdGFibGU+'

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
