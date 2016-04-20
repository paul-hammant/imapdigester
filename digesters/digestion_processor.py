import email
import imaplib
import re

from utils import Utils


class RollupServer(object):

    def __init__(self, server, mid, rollup_folder_name):
        self.rollup_folder_name = rollup_folder_name
        self.rollup_inbox = server
        self.previous_message_id = mid

    def delete_previous_message(self):
        self.rollup_inbox.delete_messages([self.previous_message_id])

    def append(self, message):
        try:
            # Ugly hack
            message = "".join(i for i in message if ord(i) < 128)
            self.rollup_inbox.append(self.rollup_folder_name, message)
        except UnicodeEncodeError:
            # Found this with attempts to utf-8 encode, but not utf-7
            print ">>>>UnicodeError>>>>" + message + "\n\n"
            raise


class DigestionProcessor(object):

    def __init__(self, notification_folder, rollup_folder, digesters,
                 print_summary, sender_to_implicate, move_unmatched, rollup_folder_name):
        super(DigestionProcessor, self)
        self.rollup_folder_name = rollup_folder_name
        self.digesters = digesters
        self.move_unmatched = move_unmatched
        self.sender_to_implicate = sender_to_implicate
        self.print_summary = print_summary
        self.rollup_folder = rollup_folder
        self.notification_folder = notification_folder

    def doit(self):

        messages = self.notification_folder.search('NOT DELETED')
        response = self.notification_folder.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
        unmatched_to_move = []
        to_delete = []

        # Loop through email in notification folder
        for msgid, data in response.iteritems():
            rfc822content = self.notification_folder.fetch(msgid, ["INTERNALDATE", "BODY", "RFC822"])[msgid]['RFC822']
            self.process_incoming_notification(msgid, self.digesters, rfc822content, to_delete,
                                               unmatched_to_move, self.move_unmatched)

        # Rewrite emails in the rollup folder (the one the end-user actually reads)
        for digester in self.digesters:
            subj_to_match = 'HEADER Subject "' + digester.matching_rollup_subject() + '"'
            from_to_match = 'HEADER From "' + self.sender_to_implicate.split(" ")[-1]\
                .replace("<", "").replace(">", "") + '"'
            try:
                messages = self.rollup_folder.search('NOT DELETED ' + subj_to_match + " " + from_to_match)
            except imaplib.IMAP4.abort:
                messages = self.rollup_folder.search('NOT DELETED ' + subj_to_match + " " + from_to_match)
            response = self.rollup_folder.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
            previously_seen = False
            previous_message_id = None
            for msgid, data in response.iteritems():
                previous_message_id = msgid
                previously_seen = '\\Seen' in data[b'FLAGS']
            rollup_inbox_proxy = RollupServer(self.rollup_folder, previous_message_id, self.rollup_folder_name)
            digester.rewrite_rollup_emails(rollup_inbox_proxy, previous_message_id is not None, previously_seen,
                                            self.sender_to_implicate)

        # Move Unmatched files so the human can see them

        for unm in unmatched_to_move:
            unm = re.sub("\nFrom: .*\r\n", "\nFrom: " + self.sender_to_implicate + "\r\n", unm)
            unm = re.sub("\nTo: .*\r\n", "\nTo: " + self.sender_to_implicate + "\r\n", unm)
            self.rollup_folder.append(self.rollup_folder_name, unm)

        # Delete Originals

        self.notification_folder.delete_messages(to_delete)

        # Print summary for posterity

        if self.print_summary:
            for digester in self.digesters:
                digester.print_summary()

    def process_incoming_notification(self, msgid, digesters, rfc822content, to_delete,
                                      unmatched_to_move, move_unmatched):
        msg = email.message_from_string(rfc822content)
        html_message = Utils.get_decoded_email_body(msg, True)
        text_message = Utils.get_decoded_email_body(msg, False)

        processed = False
        for digester in digesters:
            if processed:
                break
            matching_incoming_headers = digester.matching_incoming_headers()
            for matching_header in matching_incoming_headers:
                if re.search(matching_header, rfc822content) is not None:
                    processed = digester.process_new_notification(rfc822content, msg, html_message, text_message)
                    break
        if processed:
            to_delete.append(msgid)
        else:
            if move_unmatched:
                unmatched_to_move.append(rfc822content)
                to_delete.append(msgid)
            else:
                print "Unmatched email from: " + msg['From'].strip() + ", subject: " + msg['Subject'].strip()
