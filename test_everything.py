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

        appended = \
"""Subject: Github Rollup (2 new)
From: P H <ph@example.com>
Content-Transfer-Encoding: 8bit
Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"
MIME-Version: 1.0
This is a multi-part message in MIME format.
-----NOTIFICATION_BOUNDARY
Content-Type: text/html; charset="utf-7"
Content-Transfer-Encoding: utf-7


<table>
  <tr style="background-color: #acf;">
    <th>When</th><th>Issues/Pull Requests &amp; Their Notifications</th>
  </tr>
  <tr style="">
    <td valign="top">Apr 02 2016<br/>03:14 AM</td>
    <td>
      <table style="border-top: none">
        <tr>
          <td style="border-bottom: 2px solid lightgrey;">
            <a href="https://github.com/Homebrew/homebrew/pull/50441">Pull Request: [Homebrew/homebrew] ired 0.5.0 (#50441)</a>
          </td>
        </tr>
        <tr>
          <td style="font-weight: bold;">ppiper: Peter Piper (comment) Peter Piper picked a peck of pickled peppers....</td>
        </tr>
        <tr>
          <td style="font-weight: bold;">dholm: David Holm (comment 60.0 mins earlier) [quoted block] @dunn Fixed....</td>
        </tr>
       </table>
    </td>
  </tr>
</table>"""

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

        with open('testdata/github_2.txt', 'r') as myfile:
            notification_2_content = myfile.read().replace('\n', '\r\n')
        digester.process_incoming_message(1235, processors, notification_2_content, to_delete_from_inqueue, unmatched_to_move, False)


        processor.rewrite_rollup_emails(rollup_inbox_proxy, False, False, "P H <ph@example.com>")

        self.assertEquals(rollup_inbox_proxy.mock_calls, [call.append(appended)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(len(to_delete_from_inqueue), 2)
        self.assertEquals(to_delete_from_inqueue[0], 1234)
        self.assertEquals(to_delete_from_inqueue[1], 1235)
