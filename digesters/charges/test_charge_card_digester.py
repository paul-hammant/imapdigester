from unittest import TestCase

import sys
from mock import Mock, call
from mockextras import stub

from digesters.charges.charge_card_digester import ChargeCardDigester
from digesters.jira.jira_notification_digester import JiraNotificationDigester
from digesters.digestion_processor import DigestionProcessor


MAIL_HDR = """From: "Atlassian JIRA" <ph@example.com>
Content-Transfer-Encoding: 8bit
Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY-5678"
MIME-Version: 1.0
This is a multi-part message in MIME format.
-----NOTIFICATION_BOUNDARY-5678
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: 8bit


"""

class NotificationsStore(object):

    def __init__(self, cls=object):
        self._cls = cls
        self.notifications = None

    def __eq__(self, other):
        self.notifications = other
        return True

    def __ne__(self, other):
        return False

    def __repr__(self):
        return "NotificationsStore(..)"


class TestChargeCardDigester(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestChargeCardDigester, self).__init__(methodName)
        reload(sys)
        sys.setdefaultencoding('utf8')


    def test_two_related_charges_can_be_digested(self):

        notification_store = {
                "charges": {
                    1460184000: {
                        "a": "b"
                    }
                },
                "most_recent_seen": 1460183824
        }

        final_notifications_store = NotificationsStore()

        store_writer = Mock()
        store_writer.get_from_binary.side_effect = stub(
            (call('charges'), notification_store),
            (call('most-recently-seen'), 1460183824)
        )
        store_writer.store_as_binary.side_effect = stub(
            (call('charges', final_notifications_store), True),
            (call('most-recently-seen', 1460183824), True)
        )

        digester = ChargeCardDigester(store_writer)  ## What we are testing

        expected_payload = "FOO"

        expected_message = ("Subject: Notification Digest: 1 new notification(s)\n"
                            + MAIL_HDR + expected_payload + "\n\n-----NOTIFICATION_BOUNDARY-5678")

        digest_inbox_proxy = Mock()
        digest_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
        digest_inbox_proxy.append.side_effect = stub((call(expected_message), True))

        digester.new_charge_summary = {
                1460185000: {
                    "a": "b"
                }
        }

        digester.rewrite_digest_emails(digest_inbox_proxy, False, False, "foo@bar.com")

        self.assertEquals(digest_inbox_proxy.mock_calls,
                          [call.delete_previous_message(), call.append(expected_message)])

        calls = store_writer.mock_calls
        self.assertEquals(calls, [
            call.get_from_binary('charges'),
            call.get_from_binary('most-recently-seen'),
            call.store_as_binary('charges', {
                1461123240: {u'comment': u'Great idea, Paul',
                             u'project_name': u'unknown',
                             u'who': u'Paul Hammant',
                             u'kvtable': [],
                             u'issue_id': u'JRA-60612',
                             u'event': u'Paul Hammant commented on  JRA-60612',
                             u'issue_url': u'https://jira.atlassian.com/browse/JRA-60612'},
                1460652660: {u'comment': u'Can you awesome folks add a text/json multipart to the...',
                             u'project_name': u'HipChat',
                             u'who': u'Paul Hammant',
                             u'kvtable': [{u'k': u'Change By', u'v': u'Paul Hammant'}],
                             u'issue_id': u'HCPUB-579',
                             u'event': u'Paul Hammant updated an issue',
                             u'issue_url': u'https://jira.atlassian.com/browse/HCPUB-579'},
                1460652300: {u'comment': u'Can you awesome folks add a text/json multipart to the...',
                             u'project_name': u'HipChat',
                             u'line_here': True,
                             u'who': u'Paul Hammant',
                             u'kvtable': [{u'k': u'Issue Type', u'v': u'Suggestion'},
                                          {u'k': u'Assignee', u'v': u'Unassigned'},
                                          {u'k': u'Components', u'v': u'Notifications - email'},
                                          {u'k': u'Created', u'v': u'14/Apr/2016 4'}],
                             u'issue_id': u'HCPUB-579',
                             u'event': u'Paul Hammant created an issue',
                             u'issue_url': u'https://jira.atlassian.com/browse/HCPUB-579'}}),
            call.store_as_binary('most-recently-seen', 1460183824)])
        self.assertEquals(len(final_notifications_store.notifications), 3)