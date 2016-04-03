from base_notification_processor import BaseNotificationProcessor


class BarclaycardNotificationProcessor(BaseNotificationProcessor):
    def __init__(self, charges):
        self.charges = charges
        self.new_notifs = 0

    def print_summary(self):
        print "New Barclaycard Charges: " + str(self.new_notifs)

    def matching_incoming_headers(self):
        return ["From: alerts@barclaycard.com"]

    def matching_rollup_subject(self):
        raise Exception("Should never get here")

    def rewrite_rollup_emails(self, rollup_inbox_proxy, has_previous_message, previously_seen, sender_to_implicate):
        raise Exception("Should never get here")

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        # TODO - you'll need to understand the Barclaycard email alerts here.

        ## get 'when' (timestamp) from email
        # if when not in self.charges:
        #    self.charges[when] = {}
        # chg = self.charges[when]
        # chg["type"] = "Charge"
        # chg["amt"] = Decimal(amt)
        # chg["curr"] = curr
        # chg["vendor"] = vendor
        # chg["card"] = "B/card " + acct
        # self.new_notifs += 1

        return False  # True if processed
