import re
import arrow
import sys
from base_notification_processor import BaseNotificationProcessor
from bs4 import BeautifulSoup
from decimal import Decimal


class AmexNotificationProcessor(BaseNotificationProcessor):
    def __init__(self, charges):
        self.charges = charges
        self.new_amex = 0

    def print_summary(self):
        print "New Amex Charges: " + str(self.new_amex)

    def matching_incoming_headers(self):
        return ["From: \"American Express\" <AmericanExpress@welcome.aexp.com>",
                "From: \"American Express\" <americanexpress@member.americanexpress.com>"]

    def matching_rollup_subject(self):
        raise Exception("Should never get here")

    def rewrite_rollup_emails(self, rollup_inbox_proxy, has_previous_message, previously_seen, sender_to_implicate):
        raise Exception("Should never get here")

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        when = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ').timestamp

        # Amex processing needs to work on the HTML half of the email instead
        # of the plain-text half because the two things carry different data.
        # Specifically - merchant name is missing from the plain text half

        soup = BeautifulSoup(html_message, 'html.parser')
        body_html_as_text = soup.find("body").get_text()
        body_html_as_text = " ".join(body_html_as_text.split())  # rmv line breaks, squish double spaces

        # Then again, Location: for 'card not present' is only in the plain text half

        processed = self.maybe_card_not_present_purchase(text_message, when)
        if not processed:
            processed = self.maybe_process_merchant_credit(body_html_as_text, when)
        if not processed:
            processed = self.maybe_autopay_has_been_processed(body_html_as_text, soup, when)
        if not processed:
            processed = self.maybe_process_regular_charge(body_html_as_text, when)
        if not processed:
            processed = self.maybe_process_pending_charge(body_html_as_text, soup, when)
        if not processed:
            processed = self.maybe_process_pending_charge_has_posted(body_html_as_text, soup, when)
        if not processed:
            processed = self.maybe_process_pending_charge_has_not_posted(body_html_as_text, soup, when)
        if not processed:
            processed = self.maybe_things_i_dont_need(body_html_as_text, soup, when)
        return processed

    def maybe_process_pending_charge(self, body_html_as_text, soup, when):

        if "Your Pending Charge Is Being Monitored" not in body_html_as_text:
            return False

        is_monitoring = re.search('Description: (.*) Date: (.*) Amount: \$(.*)  We will.*Account Ending: (\d{5})',
                                  body_html_as_text)
        if is_monitoring:
            desc = is_monitoring.group(1)
            amt = Decimal(is_monitoring.group(3))
            card = is_monitoring.group(4)
            chg = self.make_or_get_charge_entry(when)
            if (amt is None or amt is "") or (desc is None or desc is ""):
                pass
            else:
                chg["type"] = "Pending Charge"
                chg["amt"] = amt
                chg["curr"] = "USD"
                chg["vendor"] = desc
                chg["card"] = "Amex " + card
                return True
        return False

    def maybe_process_pending_charge_has_posted(self, body_html_as_text, soup, when):

        if "Your Pending Charge Has Posted" not in body_html_as_text:
            return False

        has_posted = re.search('Description: (.*) Date: (.*) Amount: \$(.*)  Please review.*Account Ending: (\d{5})',
                               body_html_as_text)

        if has_posted:
            desc = has_posted.group(1)
            amt = Decimal(has_posted.group(3))
            card = has_posted.group(4)
            chg = self.make_or_get_charge_entry(when)
            if (amt is None or amt is "") or (desc is None or desc is ""):
                pass
            else:
                chg["type"] = "Pending Charge Has Posted"
                chg["amt"] = amt
                chg["curr"] = "USD"
                chg["vendor"] = desc
                chg["card"] = "Amex " + card
                return True
        return False

    def maybe_process_pending_charge_has_not_posted(self, body_html_as_text, soup, when):

        if "Your Pending Charge Has Not Been Posted" not in body_html_as_text:
            return False

        has_not_posted = re.search(
            'The pending \$(.*) charge from (.*) that was marked for monitoring on (.*) has not yet posted.*Account Ending: (\d{5})',
            body_html_as_text)

        if has_not_posted:
            desc = has_not_posted.group(2)
            amt = Decimal(has_not_posted.group(1))
            card = has_not_posted.group(4)
            chg = self.make_or_get_charge_entry(when)
            if (amt is None or amt is "") or (desc is None or desc is ""):
                pass
            else:
                chg["type"] = "Pending Charge Not Posted"
                chg["amt"] = amt
                chg["curr"] = "USD"
                chg["vendor"] = desc
                chg["card"] = "Amex " + card
                return True
        return False

    @staticmethod
    def maybe_things_i_dont_need(body_html_as_text, soup, when):

        # I don't need these retained at all.
        if "Save time, see your account at a glance" in body_html_as_text:
            return True
        if "Now your Year-End Summary includes" in body_html_as_text:
            return True
        if "Get the latest news, offers and more from your Card" in body_html_as_text:
            return True
        if "This email advertisement was sent to" in body_html_as_text:
            return True
        if "MANAGE YOUR ALERTS >" in body_html_as_text:
            return True
        if "About This Survey" in body_html_as_text:
            return True

        return False

    def maybe_autopay_has_been_processed(self, body_html_as_text, soup, when):

        if "AutoPay Payment Processed" not in body_html_as_text:
            return False

        autopay = re.search('(\d{5}) AutoPay.*Express Customer Care \$(.*) PROCESSED ON (.*) Available Credit',
                            body_html_as_text)

        if autopay:
            amt = Decimal(autopay.group(2).replace(',', ''))
            card = autopay.group(1)
            chg = self.make_or_get_charge_entry(when)
            if (amt is None or amt is ""):
                pass
            else:
                chg["type"] = "Payment"
                chg["amt"] = amt
                chg["curr"] = "USD"
                chg["vendor"] = "Amex AutoPay Processed"
                chg["card"] = "Amex " + card
                return True
        return False

    def maybe_process_merchant_credit(self, body_html_as_text, when):

        if "The following merchant credit has been posted to your American Express" not in body_html_as_text:
            return False

        is_merch_credit = re.search('Merchant Name:(.*)Credit Amount:(.*)Thank', body_html_as_text)
        if is_merch_credit:
            merchant = is_merch_credit.group(1).strip()
            amt = (Decimal(is_merch_credit.group(2).strip()[1:]) * Decimal(-1))
            chg = self.make_or_get_charge_entry(when)
            # should prob do de-morgan's..
            if (amt is None or amt is "") or (merchant is None or merchant is ""):
                pass
            else:
                chg["type"] = "Merchant Credit"
                chg["amt"] = amt
                chg["curr"] = "USD"
                chg["vendor"] = merchant
                chg["card"] = "Amex " + re.search("Account Ending:(\d{5}) View Account", body_html_as_text).group(1)
                return True
        else:
            pass
        return False

    def maybe_card_not_present_purchase(self, plain_text, when):

        if "You requested to be notified whenever your Card was not present at the time of a purchase" not in plain_text:
            return False

        plain_text = " ".join(plain_text.split())  # rmv line breaks, squish double spaces

        try:
            is_cnp_purchase = re.search('Amount: \$(.*) Merchant: Name (.*) Location: (.*) The am', plain_text)
            if is_cnp_purchase is None:
                is_cnp_purchase = re.search('Amount: \$(.*) Merchant Name: (.*) Location: (.*) The am', plain_text)

            if is_cnp_purchase:
                merchant = is_cnp_purchase.group(2).strip()
                location = is_cnp_purchase.group(3).strip()
                amt = Decimal(is_cnp_purchase.group(1).strip())
                chg = self.make_or_get_charge_entry(when)
                # should prob do de-morgan's..
                if (amt is None or amt is "") or (merchant is None or merchant is ""):
                    print "Amex.maybe_card_not_present_purchase amt is none or merch"
                    pass
                else:
                    chg["type"] = "Virtual Charge"
                    chg["amt"] = amt
                    chg["curr"] = "USD"
                    chg["vendor"] = merchant + " (" + location + ")"
                    chg["card"] = "Amex " + re.search("Account Ending: (\d{5})", plain_text).group(1)
                    return True
            else:
                print "Amex.maybe_card_not_present_purchase card_not_present regex didn't match"
                pass
        except:
            print "Amex.maybe_card_not_present_purchase: Unexpected error:", sys.exc_info()[0]
            print "--> " + plain_text
            return False

        print "--> Amex.maybe_card_not_present_purchase - unprocessed unexecptedly w/o exception -->" + plain_text
        return False

    def maybe_process_regular_charge(self, body_html_as_text, when):

        a_charge = re.search(
            'Account Ending:(.*)View AccountMake.*Transaction Date:(.*)Merchant Name:(.*)Purchase Amount:.*\$(.*)Credit Limit',
            body_html_as_text)
        if not a_charge:
            a_charge = re.search(
                'Account Ending:(.*)View AccountMake.*Transaction Date:(.*)Merchant Name:(.*)Purchase Amount:.*\$(.*)Some transactions',
                body_html_as_text)
            if not a_charge:
                return False
        acct, amt, curr, vendor = self.get_fields(a_charge)
        chg = self.make_or_get_charge_entry(when)
        if (acct is None or acct is "") or (amt is None or amt is "") or (curr is None or curr is "") or (
                        vendor is None or vendor is ""):
            pass
        else:
            chg["type"] = "Charge"
            chg["amt"] = Decimal(amt.strip())
            chg["curr"] = curr
            chg["vendor"] = vendor.strip()
            chg["card"] = "Amex " + acct.strip()
            self.new_amex += 1
            return True
        return False

    def make_or_get_charge_entry(self, when):
        if when not in self.charges:
            self.charges[when] = {}
        return self.charges[when]

    @staticmethod
    def get_fields(a_charge):
        acct = a_charge.group(1)
        # date in body doesn't include time element
        vendor = a_charge.group(3)
        amt = a_charge.group(4)
        curr = "USD"
        return acct, amt, curr, vendor
