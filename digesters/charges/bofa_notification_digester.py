import re

import arrow
import dateutil
from bs4 import BeautifulSoup
from decimal import Decimal

from digesters.charges.base_charge_card_digester import BaseChargeCardDigester


class BankOfAmericaNotificationDigester(BaseChargeCardDigester):
    def __init__(self, charges):
        super(BankOfAmericaNotificationDigester, self).__init__()
        self.charges = charges
        self.new_notifs = 0

    def print_summary(self):
        print("New Bank Of America Charges: " + str(self.new_notifs))

    def matching_incoming_headers(self):
        return ['From: "Bank of America" <onlinebanking@ealerts.bankofamerica.com>']

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        email_date = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ')

        if html_message:
            self.get_charges(html_message, email_date)
            return True


    def get_charges(self, html_message, email_date):

        # Fix HTML corruption
        # matches = re.findall("([a-z])-[\r\n]+([a-z])", html_message)
        # for match in matches:
        #     html_message = re.sub(match[0] + "-[\r\n]+" + match[1], match[0] + "-" + match[1], html_message)
        # html_message = "\n".join([line for line in html_message.split("\n") if not line.startswith("body[yahoo]")])
        # ... but HTML corruption doesn't seem to faze the lxml parser.

        soup = BeautifulSoup(html_message, 'lxml', from_encoding="iso-8859-1")
        text = soup.find("body").get_text()
        text = " ".join(text.split())  # rmv line breaks, squish double spaces
        text = text[text.index("Amount:"):]
        # This comes after the Amounts (transaction):
        text = text[:text.index("View details If you don't recognize this transaction")]
        text = text.replace(" Amount:", "\nAmount:")
        for ix, line in enumerate(text.split("\n")):
            a_charge = re.search('Amount: \$ (.*) Credit card: .* ending in - (.*) Where: at (.*) Type: .* Transaction date: (.*)', line)
            if a_charge:
                amt, card, vendor, when = self.pull_out_fields(a_charge)

                when.replace(hour=email_date.hour, minute=email_date.minute, second=email_date.second)
                when = when.shift(seconds=ix)

                chg = self.make_or_get_charge_entry(when.timestamp)
                chg["type"] = "Charge"
                chg["amt"] = Decimal(amt)
                chg["curr"] = "$"
                chg["vendor"] = vendor
                chg["card"] = "BofA " + card


    def make_or_get_charge_entry(self, when):
        if when not in self.charges:
            self.charges[when] = {}
        return self.charges[when]


    def pull_out_fields(self, a_charge):
        amt = a_charge.group(1)
        card = a_charge.group(2)
        vendor = a_charge.group(3).strip()
        when = a_charge.group(4)
        tz = a_charge.group(4).rstrip('.').rsplit(' ', 1)[1]
        when = arrow.get(when, 'MMMM DD, YYYY').replace(tzinfo=dateutil.tz.gettz(tz))
        return amt, card, vendor, when
