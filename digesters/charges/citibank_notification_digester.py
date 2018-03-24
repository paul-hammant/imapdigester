import re
import arrow
from decimal import Decimal

from digesters.charges.base_charge_card_digester import BaseChargeCardDigester


class CitibankNotificationDigester(BaseChargeCardDigester):
    def __init__(self, charges):
        super(CitibankNotificationDigester, self).__init__()
        self.charges = charges
        self.new_citi = 0

    def print_summary(self):
        print("New Citibank Charges: " + str(self.new_citi))

    def matching_incoming_headers(self):
        return ["From: Citi Alerts <alerts@citibank.com>"]

    def process_new_notification(self, rfc822content, msg, html_message, text_message):
        cdate = msg["Date"].split(',', 1)[1].strip()
        when = arrow.get(cdate, 'D MMM YYYY HH:mm:ss Z').timestamp

        a_charge = re.search("^Account #: (.*) \$(.*) at (.*) on (.*) exceeds", text_message)

        if a_charge:
            acct, amt, curr, vendor = self.get_fields(a_charge)
            if (acct is None or acct is "") \
                    or (amt is None or amt is "") \
                    or (curr is None or curr is "") \
                    or (vendor is None or vendor is ""):
                pass
            else:
                chg = self.make_or_get_charge_entry(when)
                chg["type"] = "Charge"
                chg["amt"] = Decimal(amt)
                chg["curr"] = curr
                chg["vendor"] = vendor.strip()
                chg["card"] = "Citi " + acct
                self.new_citi += 1
                return True
        return False

    def make_or_get_charge_entry(self, when):
        if when not in self.charges:
            self.charges[when] = {}
        return self.charges[when]

    def get_fields(self, a_charge):
        # card num in the notification is written like so XXXX1234
        acct = a_charge.group(1).replace("XXXX", "")
        # For me, the date in payload ends with "ET" which is not a timezone :(
        vendor = re.sub(' +', ' ', a_charge.group(3))
        amt = Decimal(a_charge.group(2))
        curr = "USD"
        return acct, amt, curr, vendor
