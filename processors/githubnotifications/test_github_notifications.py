from unittest import TestCase

import sys

from mock import Mock, call
from mockextras import stub, Any
from digester import Digester
from processors.githubnotifications.github_notification_processor import GithubNotificationProcessor


class NotifsStore(object):

    def __init__(self, cls=object):
        self._cls = cls
        self.notifs = None

    def __eq__(self, other):
        self.notifs = other
        return True

    def __ne__(self, other):
        return False

    def __repr__(self):
        return "NotifsStore(..)"


class TestGithubNotifications(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestGithubNotifications, self).__init__(methodName)
        reload(sys)
        sys.setdefaultencoding('utf8')

    def test_two_related_notifs_can_be_rolled_up(self):

        expected_payload = """<table>
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

        notification_store = {}

        final_notifs_store = NotifsStore()

        store_writer = Mock()
        store_writer.get_from_binary.side_effect = stub(
            (call('github-notifications'), notification_store),
            (call('most-recently-seen'), 0)
        )
        store_writer.store_as_binary.side_effect = stub(
            (call('github-notifications', final_notifs_store), True),
            (call('most-recently-seen', 0), True)
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

        expected_message = "Subject: Github Rollup (2 new)\n" + expected_message + expected_payload

        rollup_inbox_proxy = Mock()
        rollup_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
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

        processor.rewrite_rollup_emails(rollup_inbox_proxy, has_previous_message=True,
                                        previously_seen=False, sender_to_implicate="P H <ph@example.com>")

        self.assertEquals(rollup_inbox_proxy.mock_calls, [call.delete_previous_message(), call.append(expected_message)])

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
            call.store_as_binary('most-recently-seen', 0)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(str(to_delete_from_inqueue), "[1234, 1235]")
        self.assertEquals(len(final_notifs_store.notifs), 1)

    def test_two_related_notifis_can_be_rolled_up_with_a_prior_notification(self):

        expected_payload = """<span>You have previously read notifications up to: Apr 01 2016 09:20 PM</span>
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
  <tr><td colspan="2" style="border-bottom: 1pt solid red; border-top: 1pt solid red;"><center>^ New/Updated Notifications Since You Last Checked ^</center></td></tr>
  <tr style="background-color: #def;">
    <td valign="top">Apr 01 2016<br/>09:20 PM</td>
    <td>
      <table style="border-top: none">
        <tr>
          <td style="border-bottom: 2px solid lightgrey;">
            <a href="https://github.com/aaa/bbb/pull/1111">Pull Request: [aaa/bbb] ired 0.5.0 (#1234)</a>
          </td>
        </tr>
        <tr>
          <td >xxx: x xx (comment) Hello, how are you?</td>
        </tr>
       </table>
    </td>
  </tr>
</table>"""

        initial_notification_store = {
            'aaa/bbb/pull/1111@github.com': {
                u'subj': u'[aaa/bbb] ired 0.5.0 (#1234)',
                u'ts': {
                    1459560000: {
                        u'msg': u'Hello, how are you?',
                        u'diff': u'',
                        u'what': u'comment',
                        u'who': u'xxx: x xx'
                    }
                },
            u'mostRecent': 1459560000
            }
        }

        final_notifs_store = NotifsStore()

        store_writer = Mock()
        store_writer.get_from_binary.side_effect = stub(
            (call('github-notifications'), initial_notification_store),
            (call('most-recently-seen'), 0)
        )
        store_writer.store_as_binary.side_effect = stub(
            (call('github-notifications', final_notifs_store), True),
            (call('most-recently-seen', 1459560000), True)
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

        expected_message = "Subject: Github Rollup (2 new)\n" + expected_message + expected_payload

        rollup_inbox_proxy = Mock()
        rollup_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
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

        processor.rewrite_rollup_emails(rollup_inbox_proxy, has_previous_message=True,
                                        previously_seen=True, sender_to_implicate="P H <ph@example.com>")

        self.assertEquals(rollup_inbox_proxy.mock_calls, [call.delete_previous_message(), call.append(expected_message)])

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
                },
                'aaa/bbb/pull/1111@github.com': {
                    u'subj': u'[aaa/bbb] ired 0.5.0 (#1234)',
                    u'ts': {
                        1459560000: {
                            u'msg': u'Hello, how are you?',
                            u'diff': u'',
                            u'what': u'comment',
                            u'who': u'xxx: x xx'
                        }
                    },
                    u'mostRecent': 1459560000
                }
            }),
            call.store_as_binary('most-recently-seen', 1459560000)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(str(to_delete_from_inqueue), "[1234, 1235]")
        self.assertEquals(len(final_notifs_store.notifs), 2)

    def test_two_related_notifs_can_be_rolled_up_where_one_was_previously_seen(self):

        expected_payload = """<span>You have previously read notifications up to: Apr 02 2016 02:14 AM</span>
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
</table>"""

        notification_store = {}

        final_notifs_store = NotifsStore()

        store_writer = Mock()
        store_writer.get_from_binary.side_effect = stub(
            (call('github-notifications'), notification_store),
            (call('most-recently-seen'), 1459577657)
        )
        store_writer.store_as_binary.side_effect = stub(
            (call('github-notifications', final_notifs_store), True),
            (call('most-recently-seen', 1459577657), True)
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

        expected_message = "Subject: Github Rollup (1 new)\n" + expected_message + expected_payload

        rollup_inbox_proxy = Mock()
        rollup_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
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

        processor.rewrite_rollup_emails(rollup_inbox_proxy, has_previous_message=True,
                                        previously_seen=False, sender_to_implicate="P H <ph@example.com>")

        self.assertEquals(rollup_inbox_proxy.mock_calls, [call.delete_previous_message(), call.append(expected_message)])

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
            call.store_as_binary('most-recently-seen', 1459577657)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(str(to_delete_from_inqueue), "[1234, 1235]")
        self.assertEquals(len(final_notifs_store.notifs), 1)
