import getpass
import os
import sys
import time
from optparse import OptionParser
from socket import gaierror

from imapclient import IMAPClient

from digesters.digestion_processor import DigestionProcessor


def commands_instead():
    retval = False
    messages = rollup_folder.search('SUBJECT "git-pull"')
    response = rollup_folder.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
    for msgid, data in response.iteritems():
        f = open("imapdigester_commands_next_time.sh", 'w+')
        f.write("\ngit pull")
        f.close()
        rollup_folder.delete_messages([msgid])
        retval = True
    return retval

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    # Command Line Args

    parser = OptionParser()
    parser.add_option("--notifications_imap", dest="notifications_imap",
                      help="IMAP to use for incoming notifications mail server (SSL assumed)")
    parser.add_option("--notifications_user", dest="notifications_user",
                      help="User ID for incoming notifications mail server")
    parser.add_option("--notifications_pw", dest="notifications_pw",
                      help="User's password for incoming notifications mail server")
    parser.add_option("--notifications_folder", dest="notifications_folder_name", default="INBOX",
                      help="The Imap folder to pull notification from, e.g. INBOX")
    parser.add_option("--rollup_imap", dest="rollup_imap",
                      help="IMAP to use for outgoing rollup (rewrite) mail server (SSL assumed)")
    parser.add_option("--rollup_user", dest="rollup_user", help="User ID for outgoing rollup (rewrite) mail server")
    parser.add_option("--rollup_pw", dest="rollup_pw",
                      help="User's password for outgoing rollup (rewrite) mail server")
    parser.add_option("--rollup_folder", dest="rollup_folder_name", default="INBOX",
                      help="The Imap folder to pull/push rollup from/to, e.g. INBOX")
    parser.add_option("--implicate", dest="sender_to_implicate",
                      help="Who to name in rollup emails, e.g. \"Imap Digester\" <imapdigester@example.com>")
    parser.add_option("--move_unmatched", action="store_true", dest="move_unmatched",
                      help="Move unmatched emails to rollup inbox")
    parser.add_option("--print_summary", action="store_true", dest="print_summary", help="Print Summary")

    (options, args) = parser.parse_args()

    if options.notifications_pw is None:
        print "Enter notifications user password:"
        options.notifications_pw = getpass.getpass()

    if options.rollup_pw is None:
        if options.notifications_imap == options.rollup_imap and options.notifications_user == options.rollup_user:
            options.rollup_pw = options.notifications_pw
        else:
            print "Enter rollup user password:"
            options.rollup_pw = getpass.getpass()

    # Read and mark for deletion items from notification inbox.
    notification_folder = None
    try:
        notification_folder = IMAPClient(options.notifications_imap, use_uid=True, ssl=True)
    except gaierror:
        print "CAN'T FIND IMAP SERVER"
        exit(10)
    try:
        notification_folder.login(options.notifications_user, options.notifications_pw)
    except:
        time.sleep(5)
        notification_folder = IMAPClient(options.notifications_imap, use_uid=True, ssl=True)
        try:
            notification_folder.login(options.notifications_user, options.notifications_pw)
        except:
            print "CAN'T LOG IN to IN IMAP SERVER"
            exit(10)
    time.sleep(1)
    notification_folder.select_folder(options.notifications_folder_name)

    rollup_folder = IMAPClient(options.rollup_imap, use_uid=True, ssl=True)
    rollup_folder.login(options.rollup_user, options.rollup_pw)
    rollup_folder.select_folder(options.rollup_folder_name)

    if not commands_instead():
        digesters = []

        if os.path.isfile("my_digesters_setup.py"):
            from my_digesters_setup import add_digesters
        else:
            # Copy this to the above, if you're running ImapDigester and want to customize the digesters.
            from my_digesters_setup_template import add_digesters

        # Get Digesters from my_digesters_setup.py
        add_digesters(digesters)

        DigestionProcessor(notification_folder, rollup_folder, digesters, options.print_summary,
                           options.sender_to_implicate, options.move_unmatched, options.rollup_folder_name)\
            .doit()

    rollup_folder.expunge()
    rollup_folder.logout()

    notification_folder.expunge()
    notification_folder.logout()
