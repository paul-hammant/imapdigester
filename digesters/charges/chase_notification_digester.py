from __future__ import unicode_literals
import re
import arrow as arrow
import dateutil
from decimal import Decimal

from digesters.charges.base_charge_card_digester import BaseChargeCardDigester


class ChaseNotificationDigester(BaseChargeCardDigester):
    def __init__(self, charges):
        super(ChaseNotificationDigester, self).__init__()
        self.charges = charges
        self.new_message_count = 0
        self.new_chase = 0

    def process_new_notification(self, rfc822content, msg, html_message, text_message):
        acct = re.search("credit card account ending in ([0-9]{4})", text_message).group(1)

        a_charge = re.search('A charge of \((.*)\) (.*) at (.*) has been authorized on (.*).', text_message)
        if a_charge:
            amt, curr, vendor, when = self.pull_out_fields(a_charge)
            if (acct is None or acct is "") or (amt is None or amt is "") or (curr is None or curr is "") \
                    or (vendor is None or vendor is ""):
                pass
            else:
                chg = self.make_or_get_charge_entry(when)
                chg["type"] = "Charge"
                chg["amt"] = Decimal(amt)
                chg["curr"] = curr[1:]
                chg["vendor"] = vendor
                chg["card"] = "Chase " + acct
                self.new_chase += 1
                return True

        this_intl_charge = \
            re.search('ternational charge. This charge of \((.*)\) (.*) was authorized at (.*) on (.*).', text_message)
        if this_intl_charge:
            amt, curr, vendor, when = self.pull_out_fields(this_intl_charge)
            if (acct is None or acct is "") or (amt is None or amt is "") or (curr is None or curr is "") \
                    or (vendor is None or vendor is ""):
                pass
            else:
                chg = self.make_or_get_charge_entry(when)
                chg["vendor"] = vendor
                chg["curr"] = curr
                chg["amt"] = amt
                chg["card"] = "Chase " + acct
                if "type" in chg and "Virtual" in chg["type"]:
                    chg["type"] = "Virtual, Intl. Charge"
                else:
                    chg["type"] = "Intl. Charge"
                return True

        this_intl_charge = re.search('online, phone or mail order charge. \
                                     A charge of \((.*)\) (.*) was authorized at (.*) on (.*).', text_message)
        if this_intl_charge:
            amt, curr, vendor, when = self.pull_out_fields(this_intl_charge)
            if (acct is None or acct is "") or (amt is None or amt is "") or (curr is None or curr is "") \
                    or (vendor is None or vendor is ""):
                pass
            else:
                chg = self.make_or_get_charge_entry(when)
                chg["vendor"] = vendor
                chg["curr"] = curr
                chg["card"] = "Chase " + acct
                chg["amt"] = amt
                if "type" in chg and "Virtual" in chg["type"]:
                    chg["type"] = "Virtual, Intl. Charge"
                else:
                    chg["type"] = "Virtual Charge"
                return True
        return False

    def make_or_get_charge_entry(self, when):
        if when not in self.charges:
            self.charges[when] = {}
        return self.charges[when]

    def pull_out_fields(self, a_charge):
        curr = a_charge.group(1)
        amt = a_charge.group(2)
        vendor = a_charge.group(3).strip()
        rstrip = a_charge.group(4).rsplit(' ', 1)[0]
        tz = a_charge.group(4).rstrip('.').rsplit(' ', 1)[1]
        when = arrow.get(rstrip, 'MM/DD/YYYY h:mm:ss A').replace(tzinfo=dateutil.tz.gettz(tz)).timestamp
        return amt, curr, vendor, when

    def matching_incoming_headers(self):
        return ["Subject: (.*) Alert from Chase"]

    def print_summary(self):
        print "New Chase Messages/Charges: " + str(self.new_chase)
