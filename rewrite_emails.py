from imapclient import IMAPClient
from optparse import OptionParser
import sys
import time
from socket import gaierror

from digester import Digester

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

    # Read and mark for deletion items from notification inbox.
    inqueue_folder = None
    try:
        inqueue_folder = IMAPClient(options.notifications_imap, use_uid=True, ssl=(True))
    except gaierror:
        print "CAN'T FIND IMAP SERVER"
        exit(10)
    try:
        inqueue_folder.login(options.notifications_user, options.notifications_pw)
    except:
        time.sleep(5)
        inqueue_folder = IMAPClient(options.notifications_imap, use_uid=True, ssl=(True))
        try:
            inqueue_folder.login(options.notifications_user, options.notifications_pw)
        except:
            print "CAN'T LOG IN to IN IMAP SERVER"
            exit(10)
    time.sleep(1)
    inqueue_folder.select_folder('INBOX')

    rollup_folder = IMAPClient(options.rollup_imap, use_uid=True, ssl=(True))
    rollup_folder.login(options.rollup_user, options.rollup_pw)
    rollup_folder.select_folder('INBOX')

    Digester(inqueue_folder, rollup_folder, options).doit()

