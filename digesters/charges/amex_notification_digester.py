import re
import arrow
import sys
from bs4 import BeautifulSoup
from decimal import Decimal

from digesters.charges.base_charge_card_digester import BaseChargeCardDigester


class AmexNotificationDigester(BaseChargeCardDigester):
    def __init__(self, charges):
        super(AmexNotificationDigester, self).__init__()
        self.charges = charges
        self.new_amex = 0

    def print_summary(self):
        print("New Amex Charges: " + str(self.new_amex))

    def matching_incoming_headers(self):
        return ["From: \"American Express\" <AmericanExpress@welcome.aexp.com>",
                "From: \"American Express\" <americanexpress@member.americanexpress.com>"]

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        when = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ').timestamp

        # Amex processing needs to work on the HTML half of the email instead
        # of the plain-text half because the two things carry different data.
        # Specifically - merchant name is missing from the plain text half

        if html_message:
            soup = BeautifulSoup(html_message, 'html.parser')
            text = soup.find("body").get_text()
            text = " ".join(text.split())  # rmv line breaks, squish double spaces
        else:
            text = text_message

        # Then again, Location: for 'card not present' is only in the plain text half

        processed = self.maybe_card_not_present_purchase(text_message, when)
        if not processed:
            processed = self.maybe_process_merchant_credit(text, when)
        if not processed:
            processed = self.maybe_autopay_has_been_processed(text, when)
        if not processed:
            processed = self.maybe_process_regular_charge(text, when)
        if not processed:
            processed = self.maybe_process_pending_charge(text, when)
        if not processed:
            processed = self.maybe_process_pending_charge_has_posted(text, when)
        if not processed:
            processed = self.maybe_process_pending_charge_has_not_posted(text, when)
        if not processed:
            processed = self.maybe_things_i_dont_need(text, when)
        return processed

    def maybe_process_pending_charge(self, text, when):

        if "Your Pending Charge Is Being Monitored" not in text:
            return False

        is_monitoring = re.search('Description: (.*) Date: (.*) Amount: \$(.*)  We will.*Account Ending: (\d{5})', text)
        if is_monitoring:
            desc = is_monitoring.group(1)
            amt = Decimal(is_monitoring.group(3).replace(",", ""))
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

    def maybe_process_pending_charge_has_posted(self, text, when):

        if "Your Pending Charge Has Posted" not in text:
            return False

        has_posted = re.search('Description: (.*) Date: (.*) Amount: \$(.*)  Please review.*Account Ending: (\d{5})',
                               text)

        if has_posted:
            desc = has_posted.group(1)
            amt = Decimal(has_posted.group(3).replace(",", ""))
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

    def maybe_process_pending_charge_has_not_posted(self, text, when):

        if "Your Pending Charge Has Not Been Posted" not in text:
            return False

        has_not_posted = re.search(
            'The pending \$(.*) charge from (.*) that was marked for monitoring on (.*) has not yet posted.*Account Ending: (\d{5})',
            text)

        if has_not_posted:
            desc = has_not_posted.group(2)
            amt = Decimal(has_not_posted.group(1).replace(",", ""))
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
    def maybe_things_i_dont_need(text, when):

        # I don't need these retained at all.
        if "Save time, see your account at a glance" in text:
            return True
        if "Now your Year-End Summary includes" in text:
            return True
        if "Get the latest news, offers and more from your Card" in text:
            return True
        if "This email advertisement was sent to" in text:
            return True
        if "MANAGE YOUR ALERTS >" in text:
            return True
        if "AutoPay Reminder" in text:
            return True
        if "About This Survey" in text:
            return True

        return False

    def maybe_autopay_has_been_processed(self, text, when):

        if "AutoPay Payment Processed" not in text:
            return False

        autopay = re.search('(\d{5}) AutoPay.*Express Customer Care \$(.*) PROCESSED ON (.*) Available Credit', text)

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

    def maybe_process_merchant_credit(self, text, when):

        if "The following merchant credit has been posted to your American Express" not in text:
            return False

        is_merch_credit = re.search('Merchant Name:(.*)Credit Amount:(.*)Thank', text)
        if is_merch_credit:
            merchant = is_merch_credit.group(1).strip()
            amt = (Decimal(is_merch_credit.group(2).strip()[1:].replace(",", "")) * Decimal(-1))
            chg = self.make_or_get_charge_entry(when)
            # should prob do de-morgan's..
            if (amt is None or amt is "") or (merchant is None or merchant is ""):
                pass
            else:
                chg["type"] = "Merchant Credit"
                chg["amt"] = amt
                chg["curr"] = "USD"
                chg["vendor"] = merchant
                chg["card"] = "Amex " + re.search("Account Ending:(\d{5}) View Account", text).group(1)
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
                amt = Decimal(is_cnp_purchase.group(1).strip().replace(",", ""))
                chg = self.make_or_get_charge_entry(when)
                # should prob do de-morgan's..
                if (amt is None or amt is "") or (merchant is None or merchant is ""):
                    print("Amex.maybe_card_not_present_purchase amt is none or merch")
                    return False
                else:
                    chg["type"] = "Virtual Charge"
                    chg["amt"] = amt
                    chg["curr"] = "USD"
                    chg["vendor"] = merchant + " (" + location + ")"
                    chg["card"] = "Amex " + re.search("Account Ending: (\d{5})", plain_text).group(1)
                    return True
            else:
                print("Amex.maybe_card_not_present_purchase card_not_present regex didn't match")
                return False
        except:
            print("Amex.maybe_card_not_present_purchase: Unexpected error:", sys.exc_info()[0])
            print("--> " + plain_text)
            return False

        print("--> Amex.maybe_card_not_present_purchase - unprocessed unexecptedly w/o exception -->" + plain_text)
        return False

    def maybe_process_regular_charge(self, text, when):

        a_charge = re.search(
            'Account Ending:(.*)View AccountMake.*Transaction Date:(.*)Merchant Name:(.*)Purchase Amount:.*\$(.*)Credit Limit',
            text)
        if not a_charge:
            a_charge = re.search(
                "Ending: (.*) Large purchase on your Card As you requested, we're letting you know that this purchase was above your notification amount of \$\d+\.\d+\. (.*) \$(.*)\*(.*) Available",
                text)
            if not a_charge:
                return False
        acct, amt, curr, vendor = self.get_fields(a_charge)
        chg = self.make_or_get_charge_entry(when)
        if (acct is None or acct is "") or (amt is None or amt is "") or (curr is None or curr is "") or (
                        vendor is None or vendor is ""):
            pass
        else:
            chg["type"] = "Charge"
            chg["amt"] = Decimal(amt.strip().replace(",", ""))
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
        vendor = a_charge.group(2)
        amt = a_charge.group(3)
        curr = "USD"
        return acct, amt, curr, vendor
