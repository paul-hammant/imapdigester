# coding=utf-8
from __future__ import unicode_literals

import re
import arrow

from digesters.base_digester import BaseDigester

class FidelityNotificationDigester(BaseDigester):
    def __init__(self, store_writer):
        super(FidelityNotificationDigester, self).__init__()
        self.store_writer = store_writer
        self.new_message_count = 0
        self.balances = self.store_writer.get_from_binary("fidelity-balances")
        if self.balances is None:
            self.balances = {}
        self.previously_notified_article_count = len(self.balances)

    def process_new_notification(self, rfc822content, msg, html_message, text_message):
        a_balance = re.search('Total Account Value:\s+\$\s+(.*)\n', rfc822content)
        if a_balance:
            self.new_message_count += 1
            balance =  ''.join(c for c in a_balance.group(1) if ord(c) >= 32)
            when = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ').timestamp
            self.balances[when] = balance
            return True

        return False

    def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):
        if self.previously_notified_article_count == len(self.balances):
            return
        content = ""
        first = " <- most recent"
        for when, bal in sorted(self.balances.items(), reverse=True):
            line = arrow.get(when).to("local").format("MMM DD YYYY") + " $" + bal + first + "\n"
            content += line
            first = ""

        # Delete previous email, and write replacement
        if has_previous_message:
            digest_folder_proxy.delete_previous_message()
        digest_folder_proxy.append(self.make_new_raw_email(content, self.new_message_count, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("fidelity-balances", self.balances)

    def matching_incoming_headers(self):
        return ["From: Fidelity Investments<Fidelity.Alerts@Fidelity.com>"]

    def matching_digest_subject(self):
        return 'Balances Digest'

    def matching_digest_sender(self):
        return "Fidelity"

    def print_summary(self):
        print "Fidelity: New Balance notifications: " + str(self.new_message_count)

    def make_new_raw_email(self, content, count, sender_to_implicate):
        new_message = 'Subject: ' + self.matching_digest_subject() + "\n"
        new_message += 'From: \"Fidelity\" <' + sender_to_implicate + '>\n\n'
        new_message += content
        return new_message
