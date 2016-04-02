import email
import imaplib
import re

from my_processor_setup import add_processors
from utils import Utils


class RollupServer(object):

    def __init__(self, server, mid):
        self.rollup_inbox = server
        self.previous_message_id = mid

    def delete_previous_message(self):
        self.rollup_inbox.delete_messages([self.previous_message_id])

    def append(self, message):
        self.rollup_inbox.append("INBOX", message)


class Digester(object):

    def __init__(self, inqueue_server, rollup_inbox, options):
        super(Digester, self)
        self.options = options
        self.rollup_inbox = rollup_inbox
        self.inqueue_server = inqueue_server

    def doit(self):

        # Add Processors
        processors = []
        add_processors(processors)

        messages = self.inqueue_server.search(['NOT DELETED'])
        response = self.inqueue_server.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
        unmatched_to_move = []
        to_delete = []
        for msgid, data in response.iteritems():
            rfc822content = self.inqueue_server.fetch(msgid, ["INTERNALDATE", "BODY", "RFC822"])[msgid]['RFC822']
            msg = email.message_from_string(rfc822content)
            html_message = Utils.get_decoded_email_body(msg, True)
            text_message = Utils.get_decoded_email_body(msg, False)
            processed = False
            for processor in processors:
                if processed:
                    break
                matching_incoming_headers = processor.matching_incoming_headers()
                for matching_header in matching_incoming_headers:
                    if re.search(matching_header, rfc822content) is not None:
                        processed = processor.process_new_notification(rfc822content, msg, html_message, text_message)
                        break
            if processed:
                to_delete.append(msgid)
            else:
                if self.options.move_unmatched:
                    unmatched_to_move.append(rfc822content)
                    to_delete.append(msgid)
                else:
                    print "Unmatched email from: " + msg['From'].strip() + ", subject: " + msg['Subject'].strip()

        # Rewrite emails in the rollup Inbox (the one the end-user actually reads)
        for processor in processors:
            subj_to_match = 'HEADER Subject "' + processor.matching_rollup_subject() + '"'
            from_to_match = 'HEADER From "' + self.options.sender_to_implicate.split(" ")[-1]\
                .replace("<", "").replace(">", "") + '"'
            try:
                messages = self.rollup_inbox.search(['NOT DELETED', subj_to_match, from_to_match])
            except imaplib.IMAP4.abort:
                messages = self.rollup_inbox.search(['NOT DELETED', subj_to_match, from_to_match])
            response = self.rollup_inbox.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
            previously_seen = False
            previous_message_id = None
            for msgid, data in response.iteritems():
                previous_message_id = msgid
                previously_seen = '\\Seen' in data[b'FLAGS']
            rollup_inbox_proxy = RollupServer(self.rollup_inbox, previous_message_id)
            processor.rewrite_rollup_emails(rollup_inbox_proxy, previous_message_id is not None, previously_seen,
                                            self.options.sender_to_implicate)

        # Move Unmatched files so the human can see them

        for unm in unmatched_to_move:
            unm = re.sub("\nFrom: .*\r\n", "\nFrom: " + self.options.sender_to_implicate + "\r\n", unm)
            unm = re.sub("\nTo: .*\r\n", "\nTo: " + self.options.sender_to_implicate + "\r\n", unm)
            self.rollup_inbox.append("INBOX", unm)

        self.rollup_inbox.expunge()
        self.rollup_inbox.logout()

        # Delete Originals

        self.inqueue_server.delete_messages(to_delete)
        self.inqueue_server.expunge()
        self.inqueue_server.logout()

        # Print summary for posterity

        if self.options.print_summary:
            for processor in processors:
                processor.print_summary()
