from digesters.charges.base_charge_card_digester import BaseChargeCardDigester


class JPMorganNotificationDigester(BaseChargeCardDigester):
    def __init__(self, charges):
        super(JPMorganNotificationDigester, self).__init__()
        self.charges = charges
        self.new_notifs = 0

    def print_summary(self):
        print("New JPMorgan Charges: " + str(self.new_notifs))

    def matching_incoming_headers(self):
        return ["From: alerts@jpmorgan.com"]

    def process_new_notification(self, rfc822content, msg, html_message, text_message):
        # TODO - you'll need to understand the JPMorgan email alerts here.

        ## get 'when' (timestamp) from email
        # if when not in self.charges:
        #    self.charges[when] = {}
        # chg = self.charges[when]
        # chg["type"] = "Charge"
        # chg["amt"] = Decimal(amt)
        # chg["curr"] = curr
        # chg["vendor"] = vendor
        # chg["card"] = "JPM " + acct
        # self.new_notifs += 1

        return False  # True if processed
