from unittest import TestCase

import sys

from mock import Mock, call
from mockextras import stub, Any
from digester import Digester
from processors.githubnotifications.github_notification_processor import GithubNotificationProcessor


class TestEverything(TestCase):


    def __init__(self, methodName='runTest'):
        super(TestEverything, self).__init__(methodName)
        reload(sys)
        sys.setdefaultencoding('utf8')

    def test_two_related_github_notifications_can_be_rolled_up(self):
        self.two_related_github_notifications_can_be_rolled_up(0, 2,
"""<table>
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
</table>""")

    def test_two_related_github_notifications_can_be_rolled_up2(self):
        self.two_related_github_notifications_can_be_rolled_up(1459577657, 1,
"""<span>You have previously read notifications up to: Apr 02 2016 02:14 AM</span>
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
          <td >dholm: David Holm (comment 60.0 mins earlier) [quoted block] @dunn Fixed....</td>
        </tr>
       </table>
    </td>
  </tr>
</table>""")

    def two_related_github_notifications_can_be_rolled_up(self, previously_seen_per_test, how_many_new_expected, expected_payload):

        notification_store = {}
        
        store_writer = Mock()
        store_writer.get_from_binary.side_effect = stub(
            (call('github-notifications'), notification_store),
            (call('most-recently-seen'), previously_seen_per_test)
        )
        store_writer.store_as_binary.side_effect = stub(
            (call('github-notifications', Any()), True),
            (call('most-recently-seen', previously_seen_per_test), True)
        )

        expected_message = \
"""From: P H <ph@example.com>
Content-Transfer-Encoding: 8bit
Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"
MIME-Version: 1.0
This is a multi-part message in MIME format.
-----NOTIFICATION_BOUNDARY
Content-Type: text/html; charset="utf-7"
Content-Transfer-Encoding: utf-7


"""

        expected_message = "Subject: Github Rollup (" + str(how_many_new_expected) + " new)\n" + expected_message + expected_payload

        rollup_inbox_proxy = Mock()
        rollup_inbox_proxy.append.side_effect = stub((call(expected_message), True))

        processors = []
        processor = GithubNotificationProcessor(store_writer)  ## What we are testing
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

        processor.rewrite_rollup_emails(rollup_inbox_proxy, False, previously_seen_per_test > 0, "P H <ph@example.com>")

        self.assertEquals(rollup_inbox_proxy.mock_calls, [call.append(expected_message)])
        self.assertEquals(store_writer.mock_calls, [
            call.get_from_binary('github-notifications'),
            call.get_from_binary('most-recently-seen'),
            call.store_as_binary('github-notifications', {
                'Homebrew/homebrew/pull/50441@github.com': {
                    u'subj': u'[Homebrew/homebrew] ired 0.5.0 (#50441)',
                    u'ts': {
                        1459577656: {
                        u'msg': u'[quoted block] @dunn Fixed....',
                        u'diff': u' 60.0 mins earlier',
                        u'what': u'comment',
                        u'who': u'dholm: David Holm'
                    },
                        1459581256: {
                            u'msg': u'Peter Piper picked a peck of pickled peppers....',
                            u'diff': u'',
                            u'what': u'comment',
                            u'who': u'ppiper: Peter Piper'
                        }
                    },
                    u'mostRecent': 1459581256
                }
            }),
            call.store_as_binary('most-recently-seen', previously_seen_per_test)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(str(to_delete_from_inqueue), "[1234, 1235]")
        self.assertEquals(len(notification_store), 0)