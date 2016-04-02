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

    def __init__(self, inqueue_folder, rollup_folder, options):
        super(Digester, self)
        self.options = options
        self.rollup_folder = rollup_folder
        self.inqueue_folder = inqueue_folder

        # Add Processors
        self.processors = []
        add_processors(self.processors)


    def doit(self):

        messages = self.inqueue_folder.search(['NOT DELETED'])
        response = self.inqueue_folder.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
        unmatched_to_move = []
        to_delete = []

        # Loop through email in inqueue folder
        for msgid, data in response.iteritems():
            rfc822content = self.inqueue_folder.fetch(msgid, ["INTERNALDATE", "BODY", "RFC822"])[msgid]['RFC822']
            self.process_incoming_message(msgid, self.processors, rfc822content, to_delete,
                                          unmatched_to_move, self.options.move_unmatched)

        # Rewrite emails in the rollup folder (the one the end-user actually reads)
        for processor in self.processors:
            subj_to_match = 'HEADER Subject "' + processor.matching_rollup_subject() + '"'
            from_to_match = 'HEADER From "' + self.options.sender_to_implicate.split(" ")[-1]\
                .replace("<", "").replace(">", "") + '"'
            try:
                messages = self.rollup_folder.search(['NOT DELETED', subj_to_match, from_to_match])
            except imaplib.IMAP4.abort:
                messages = self.rollup_folder.search(['NOT DELETED', subj_to_match, from_to_match])
            response = self.rollup_folder.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
            previously_seen = False
            previous_message_id = None
            for msgid, data in response.iteritems():
                previous_message_id = msgid
                previously_seen = '\\Seen' in data[b'FLAGS']
            rollup_inbox_proxy = RollupServer(self.rollup_folder, previous_message_id)
            processor.rewrite_rollup_emails(rollup_inbox_proxy, previous_message_id is not None, previously_seen,
                                            self.options.sender_to_implicate)

        # Move Unmatched files so the human can see them

        for unm in unmatched_to_move:
            unm = re.sub("\nFrom: .*\r\n", "\nFrom: " + self.options.sender_to_implicate + "\r\n", unm)
            unm = re.sub("\nTo: .*\r\n", "\nTo: " + self.options.sender_to_implicate + "\r\n", unm)
            self.rollup_folder.append("INBOX", unm)

        self.rollup_folder.expunge()
        self.rollup_folder.logout()

        # Delete Originals

        self.inqueue_folder.delete_messages(to_delete)
        self.inqueue_folder.expunge()
        self.inqueue_folder.logout()

        # Print summary for posterity

        if self.options.print_summary:
            for processor in self.processors:
                processor.print_summary()

    def process_incoming_message(self, msgid, processors, rfc822content, to_delete,
                                 unmatched_to_move, move_unmatched):
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
            if move_unmatched:
                unmatched_to_move.append(rfc822content)
                to_delete.append(msgid)
            else:
                print "Unmatched email from: " + msg['From'].strip() + ", subject: " + msg['Subject'].strip()
