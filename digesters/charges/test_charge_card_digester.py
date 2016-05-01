from decimal import Decimal
from unittest import TestCase

import sys
from mock import Mock, call
from mockextras import stub

from digesters.charges.charge_card_digester import ChargeCardDigester

MAIL_HDR = """From: "Charge Cards" <foo@bar.com>
Date: Sat, 09 Apr 2016 06:56:40 -0000
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


    def test_no_previous_email_yet_one_old_and_one_new_charge_yields_only_the_newer_charge_in_the_email(self):

        notification_store = {
                "charges": {
                    1460184000: {
                        "amt": Decimal(5.00),
                        "type": "Charge",
                        "curr": "USD",
                        "vendor": "PiHut",
                        "card": "Amex 1234"
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

        expected_payload = """<table>
  <tr style="background-color: #acf;">
    <th>Type</th><th>Vendor</th><th>When</th><th>Curr</th><th>Amt</th><th>Card</th>
  </tr>
  <tr style="">
    <td>Charge</td>
    <td>Pimoroni</td>
    <td>Apr&nbsp;09 02:56</td>
    <td>GBP</td>
    <td style="text-align: right;"><b>4</b></td>
    <td>Amex 1234</td>
  </tr>
</table>"""

        expected_message = ("Subject: Spending Digest\n"
                            + MAIL_HDR + expected_payload + "\n\n-----NOTIFICATION_BOUNDARY-5678")

        digest_inbox_proxy = Mock()
        digest_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
        digest_inbox_proxy.append.side_effect = stub((call(expected_message), True))

        digester.new_charge_summary = {
            1460185000: {
                "amt": Decimal(4.00),
                "type": "Charge",
                "curr": "GBP",
                "vendor": "Pimoroni",
                "card": "Amex 1234"
            }

        }

        digester.notification_boundary_rand = "5678"
        digester.rewrite_digest_emails(digest_inbox_proxy, False, False, "foo@bar.com")

        self.assertEquals(digest_inbox_proxy.mock_calls,
                          [call.append(expected_message)])

        calls = store_writer.mock_calls
        self.assertEquals(calls, [
            call.get_from_binary('charges'),
            call.store_as_binary('charges', {
                'charges': {
                    1460185000: {
                        'curr': 'GBP',
                        'when_str': u'Apr---09 02:56',
                        'vendor': 'Pimoroni',
                        'type': 'Charge',
                        'amt': Decimal('4'),
                        'card': 'Amex 1234'
                    }
                },
                'most_recent_seen': 1460183824
            })
        ])
        self.assertEquals(len(final_notifications_store.notifications), 2)

    def test_with_a_previous_email_and_one_old_and_one_new_charge_yields_both_charges_in_the_email(self):

        notification_store = {
                "charges": {
                    1460184000: {
                        "amt": Decimal(5.00),
                        "type": "Charge",
                        "curr": "USD",
                        "vendor": "PiHut",
                        "card": "Amex 1234"
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

        expected_payload = """<table>
  <tr style="background-color: #acf;">
    <th>Type</th><th>Vendor</th><th>When</th><th>Curr</th><th>Amt</th><th>Card</th>
  </tr>
  <tr style="">
    <td>Charge</td>
    <td>Pimoroni</td>
    <td>Apr&nbsp;09 02:56</td>
    <td>GBP</td>
    <td style="text-align: right;"><b>4</b></td>
    <td>Amex 1234</td>
  </tr>
  <tr style="background-color: #def;">
    <td>Charge</td>
    <td>PiHut</td>
    <td>Apr&nbsp;09 02:40</td>
    <td>USD</td>
    <td style="text-align: right;"><b>5</b></td>
    <td>Amex 1234</td>
  </tr>
</table>"""

        expected_message = ("Subject: Spending Digest\n"
                            + MAIL_HDR + expected_payload + "\n\n-----NOTIFICATION_BOUNDARY-5678")

        digest_inbox_proxy = Mock()
        digest_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
        digest_inbox_proxy.append.side_effect = stub((call(expected_message), True))

        digester.new_charge_summary = {
            1460185000: {
                "amt": Decimal(4.00),
                "type": "Charge",
                "curr": "GBP",
                "vendor": "Pimoroni",
                "card": "Amex 1234"
            }

        }

        digester.notification_boundary_rand = "5678"
        digester.rewrite_digest_emails(digest_inbox_proxy, True, False, "foo@bar.com")

        self.assertEquals(digest_inbox_proxy.mock_calls,
                          [call.delete_previous_message(), call.append(expected_message)])

        calls = store_writer.mock_calls
        self.assertEquals(calls, [
            call.get_from_binary('charges'),
            call.store_as_binary('charges', {'charges': {
                1460184000: {'vendor': 'PiHut', 'when_str': u'Apr---09 02:40', 'curr': 'USD', 'type': 'Charge',
                             'amt': Decimal('5'), 'card': 'Amex 1234'},
                1460185000: {'vendor': 'Pimoroni', 'when_str': u'Apr---09 02:56', 'curr': 'GBP', 'type': 'Charge',
                             'amt': Decimal('4'), 'card': 'Amex 1234'}},
                'most_recent_seen': 1460183824
            })
        ])
        self.assertEquals(len(final_notifications_store.notifications), 2)