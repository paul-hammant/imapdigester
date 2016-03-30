from imapclient import IMAPClient
from optparse import OptionParser
import re
import sys
import time
import email
from socket import gaierror

from my_processor_setup import add_processors
from utils import Utils


class RollupServer(object):

    def __init__(self, server, mid):
        self.rollup_inbox = server
        self.previous_message_id = mid

    def delete_previous_message(self):
        rollup_inbox.delete_messages([previous_message_id])

    def append(self, message):
        rollup_inbox.append("INBOX", message)

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    # Command Line Args

    parser = OptionParser()
    parser.add_option("--notifications_imap", dest="notifications_imap", help="IMAP to use for incoming notifications mail server (SSL assumed)")
    parser.add_option("--notifications_user", dest="notifications_user", help="User ID for incoming notifications mail server")
    parser.add_option("--notifications_pw", dest="notifications_pw", help="User's password for incoming notifications mail server")
    parser.add_option("--rollup_imap", dest="rollup_imap",
                      help="IMAP to use for outgoing rollup (rewrite) mail server (SSL assumed)")
    parser.add_option("--rollup_user", dest="rollup_user", help="User ID for outgoing rollup (rewrite) mail server")
    parser.add_option("--rollup_pw", dest="rollup_pw", help="User's password for outgoing rollup (rewrite) mail server")
    parser.add_option("--implicate", dest="sender_to_implicate",
                      help="Who to name in rollup emails, e.g. \"Imap Digester\" <imapdigester@example.com>")
    parser.add_option("--move_unmatched", action="store_true", dest="move_unmatched",
                      help="Move unmatched emails to rollup inbox")
    parser.add_option("--print_summary", action="store_true", dest="print_summary", help="Print Summary")

    (options, args) = parser.parse_args()

    # Add Processors

    processors = []
    add_processors(processors)

    # Read and mark for deletion items from notification inbox.
    inqueue_server = None
    try:
        inqueue_server = IMAPClient(options.notifications_imap, use_uid=True, ssl=(True))
    except gaierror:
        print "CAN'T FIND IMAP SERVER"
        exit(10)
    try:
        inqueue_server.login(options.notifications_user, options.notifications_pw)
    except:
        time.sleep(5)
        inqueue_server = IMAPClient(options.notifications_imap, use_uid=True, ssl=(True))
        try:
            inqueue_server.login(options.notifications_user, options.notifications_pw)
        except:
            print "CAN'T LOG IN to IN IMAP SERVER"
            exit(10)
    time.sleep(1)
    inqueue_server.select_folder('INBOX')
    messages = inqueue_server.search(['NOT DELETED'])
    response = inqueue_server.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
    unmatched_to_move = []
    to_delete = []
    for msgid, data in response.iteritems():
        rfc822content = inqueue_server.fetch(msgid, ["INTERNALDATE", "BODY", "RFC822"])[msgid]['RFC822']
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
            if options.move_unmatched:
                unmatched_to_move.append(rfc822content)
                to_delete.append(msgid)
            else:
                print "Unmatched email from: " + msg['From'].strip() + ", subject: " + msg['Subject'].strip()

    # Rewrite emails in the rollup Inbox (the one the end-user actually reads)
    rollup_inbox = IMAPClient(options.rollup_imap, use_uid=True, ssl=(True))
    rollup_inbox.login(options.rollup_user, options.rollup_pw)
    rollup_inbox.select_folder('INBOX')
    for processor in processors:
        header_to_match = 'HEADER Subject "' + processor.matching_rollup_subject() + '"'
        messages = rollup_inbox.search(['NOT DELETED', header_to_match])
        response = rollup_inbox.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
        previously_seen = False
        previous_message_id = None
        for msgid, data in response.iteritems():
            previous_message_id = msgid
            previously_seen = '\\Seen' in data[b'FLAGS']
        rollup_inbox_proxy = RollupServer(rollup_inbox, previous_message_id)
        processor.rewrite_rollup_emails(rollup_inbox_proxy, previous_message_id is not None, previously_seen,
                                        options.sender_to_implicate)

    # Move Unmatched files so the human can see them

    for unm in unmatched_to_move:
        unm = re.sub("\nFrom: .*\r\n", "\nFrom: " + options.sender_to_implicate + "\r\n", unm)
        unm = re.sub("\nTo: .*\r\n", "\nTo: " + options.sender_to_implicate + "\r\n", unm)
        rollup_inbox.append("INBOX", unm)

    rollup_inbox.expunge()
    rollup_inbox.logout()

    # Delete Originals

    inqueue_server.delete_messages(to_delete)
    inqueue_server.expunge()
    inqueue_server.logout()

    # Print summary for posterity

    if options.print_summary:
        for processor in processors:
            processor.print_summary()
