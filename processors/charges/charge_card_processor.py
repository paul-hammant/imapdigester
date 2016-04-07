import re
from time import gmtime

import arrow
from jinja2 import Template

from base_notification_processor import BaseNotificationProcessor
from processors.charges.amex_notification_processor import AmexNotificationProcessor
from processors.charges.barclaycard_notification_processor import BarclaycardNotificationProcessor
from processors.charges.bofa_notification_processor import BankOfAmericaNotificationProcessor
from processors.charges.capitalone_notification_processor import CapitalOneNotificationProcessor
from processors.charges.chase_notification_processor import ChaseNotificationProcessor
from processors.charges.citibank_notification_processor import CitibankNotificationProcessor
from processors.charges.jpm_notification_processor import JPMorganNotificationProcessor


class ChargeCardProcessor(BaseNotificationProcessor):

    def __init__(self, store_writer):
        self.store_writer = store_writer
        self.processors = []

        self.charge_summary = store_writer.get_from_binary("charges")

        self.new_charge_summary = {}

        if self.charge_summary is None:
            self.charge_summary = {}
            self.charge_summary["charges"] = {}
            self.charge_summary["most_recent_seen"] = arrow.utcnow().replace(days=-365)

    def with_chase(self):
        self.processors.append(ChaseNotificationProcessor(self.new_charge_summary))
        return self

    def with_barclaycard(self):
        self.processors.append(BarclaycardNotificationProcessor(self.new_charge_summary))
        return self

    def with_bofa(self):
        self.processors.append(BankOfAmericaNotificationProcessor(self.new_charge_summary))
        return self

    def with_capitalone(self):
        self.processors.append(CapitalOneNotificationProcessor(self.new_charge_summary))
        return self

    def with_jpmorgan(self):
        self.processors.append(JPMorganNotificationProcessor(self.new_charge_summary))
        return self

    def with_amex(self):
        self.processors.append(AmexNotificationProcessor(self.new_charge_summary))
        return self

    def with_citi(self):
        self.processors.append(CitibankNotificationProcessor(self.new_charge_summary))
        return self

    def print_summary(self):
        for processor in self.processors:
            processor.print_summary()
        print "Total Charges: " + str(len(self.charge_summary["charges"]))

    def matching_incoming_headers(self):
        matching_terms = []
        for processor in self.processors:
            subordinates_matching_header = processor.matching_incoming_headers()
            for matching_header in subordinates_matching_header:
                matching_terms.append(matching_header)
        return matching_terms

    def matching_rollup_subject(self):
        return 'Charge Card Charges Rollup'

    def rewrite_rollup_emails(self, rollup_inbox_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if len(self.new_charge_summary) == 0:
             return

        if previously_seen:
            if len(self.charge_summary["charges"]) > 0:
                self.charge_summary["most_recent_seen"] = max(self.charge_summary["charges"])
            else:
                self.charge_summary["most_recent_seen"] = arrow.get(gmtime(0))

        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Rollup again.
        if has_previous_message == False:
            self.charge_summary["charges"] = {}

        # copy new items into main list
        for when, chg in self.new_charge_summary.iteritems():
            self.charge_summary["charges"][when] = chg

        all_the_same_year = True
        max_date = arrow.get(gmtime(0))
        if len(self.charge_summary["charges"]) > 0:
            min_date = min(self.charge_summary["charges"])
            max_date = max(self.charge_summary["charges"])
            if arrow.get(min_date).year == arrow.get(max_date).year:
                all_the_same_year = True

        # Update the string version of the charge time
        for when, chg in self.charge_summary["charges"].iteritems():
            chg["when_str"] = arrow.get(when).to('local').format("MMM---DD HH:mm" if all_the_same_year
                                                                 else "MMM---DD YYYY HH:mm")

        templ = """
<table>
  <tr style="background-color: #acf;">
    <th>Type</th><th>Vendor</th><th>When</th><th>Curr</th><th>Amt</th><th>Card</th>
  </tr>
{% for when, chg in charges|dictsort(false, by='key')|reverse %}
  {{ '<tr><td colspan="6" style="border-bottom: 1pt solid black; border-top: 1pt solid black;">
  <center>^ New Charges Since You Last checked ^</center></td></tr>' if when == most_recent_seen and not loop.first}}
  <tr style="{{loop.cycle('','background-color: #def;')}}">
    <td>{{ chg['type'] }}</td>
    <td>{{ chg['vendor'] }}</td>
    <td>{{ chg['when_str'].replace('---','&nbsp;') }}</td>
    <td>{{ chg['curr']  }}</td>
    <td style="text-align: right;"><b>{{ chg['amt'] }}</b></td>
    <td>{{ chg['card'] }}</td>
  </tr>
{% endfor %}
</table>"""

        # print ">>> charges: " + simplejson.dumps(self.charge_summary["charges"], sort_keys=True) + "\n\n"

        email_html = Template(templ).render(charges=self.charge_summary["charges"],
                                            most_recent_seen=self.charge_summary["most_recent_seen"])

        # Delete previous email, and write replacement
        if has_previous_message:
            rollup_inbox_proxy.delete_previous_message()
        rollup_inbox_proxy.append(self.make_new_raw_charge_email(email_html, max_date, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("charges", self.charge_summary)

    def process_new_notification(self, rfc822content, msg, html_message, text_message):
        processed = False
        for processor in self.processors:
            if not processed:
                matching_headers =  processor.matching_incoming_headers()
                for matching_header in matching_headers:
                    if re.search(matching_header, rfc822content) is not None:
                        processed = processor.process_new_notification(rfc822content, msg, html_message, text_message)
                        break
        return processed

    def make_new_raw_charge_email(self, email_html, when, sender_to_implicate):
        new_message = 'Subject: ' + self.matching_rollup_subject() + '\n'
        new_message += 'From: ' + sender_to_implicate + '\n'
        new_message += 'Date: ' + arrow.get(when).format('ddd, DD MMM YYYY HH:mm:ss Z') + '\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n'
        new_message += 'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"\n'
        new_message += 'MIME-Version: 1.0\n'
        new_message += 'This is a multi-part message in MIME format.\n'
        new_message += '-----NOTIFICATION_BOUNDARY\nContent-Type: text/html; charset="utf-8"\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n\n'
        new_message += email_html
        new_message += '\n\n-----NOTIFICATION_BOUNDARY'
        return new_message
