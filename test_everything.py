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

        appended = u'Subject: Github Rollup (1 new)\nFrom: P H <ph@example.com>\nContent-Transfer-Encoding: 8bit\nContent-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"\nMIME-Version: 1.0\nThis is a multi-part message in MIME format.\n-----NOTIFICATION_BOUNDARY\nContent-Type: text/html; charset="utf-8"\nContent-Transfer-Encoding: utf-8\n\n\n<table>\n  <tr style="background-color: #acf;">\n    <th>When</th><th>Issues/Pull Requests &amp; Their Notifications</th>\n  </tr>\n  <tr style="">\n    <td valign="top">Apr 02 2016<br/>02:14 AM</td>\n    <td>\n      <table style="border-top: none">\n        <tr>\n          <td style="border-bottom: 2px solid lightgrey;">\n            <a href="https://github.com/Homebrew/homebrew/pull/50441">Pull Request: [Homebrew/homebrew] ired 0.5.0 (#50441)</a>\n          </td>\n        </tr>\n        <tr>\n          <td style="font-weight: bold;">dholm: David Holm (comment) @dunn Fixed.</td>\n        </tr>\n       </table>\n    </td>\n  </tr>\n</table>'

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
