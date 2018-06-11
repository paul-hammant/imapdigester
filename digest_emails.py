import getpass
import imp
import os
from optparse import OptionParser
from socket import gaierror

import imapclient
import sys
import time
from imapclient import IMAPClient

from digesters.digestion_processor import DigestionProcessor


def get_command():
    retval = None

    if check_for_command('git-pull'):
        with open("imapdigester_commands_next_time.sh", 'w+') as f:
            f.write("\ngit pull\nfind . -name \"*.pyc\" -exec rm -rf {} \;\n")
        retval = "BASH-OPERATIONS"

    elif check_for_command('pause'):
        with open("pause_if_present.txt", 'w') as f:
            f.write("")
        retval = "PAUSE"

    elif check_for_command('resume'):
        os.remove('pause_if_present.txt')

    elif os.path.isfile("pause_if_present.txt"):
        retval = "PAUSE"

    return retval


def check_for_command(cmd):
    messages = digests_folder.search('SUBJECT "%s"' % cmd)
    response = digests_folder.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
    retval = False
    for msgid, data in response.items():
        digests_folder.delete_messages([msgid])
        retval = True
    return retval

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

if __name__ == '__main__':

    imp.reload(sys)

    # Command Line Args

    parser = OptionParser()
    parser.add_option("--notifications-imap", dest="notifications_imap",
                      help="IMAP to use for incoming notifications mail server (SSL assumed)")
    parser.add_option("--notifications-user", dest="notifications_user",
                      help="User ID for incoming notifications mail server")
    parser.add_option("--notifications-pw", dest="notifications_pw",
                      help="User's password for incoming notifications mail server")
    parser.add_option("--notifications-folder", dest="notifications_folder_name", default="INBOX",
                      help="The IMAP folder to pull notification from, e.g. INBOX")
    parser.add_option("--notifications-cert-check-skip", action="store_true", dest="notifications_cert_check_skip",
                      help="Skip Certificate check notification imap server (say self-signed)")
    parser.add_option("--notifications-no-ssl", action="store_false", dest="notifications_ssl", default=True,
                      help="SSL True/False (port 993) for notifications IMAP? (True by default)")
    parser.add_option("--digests-imap", dest="digests_imap",
                      help="IMAP to use for outgoing digest (rewrite) mail server (SSL assumed)")
    parser.add_option("--digests-user", dest="digests_user", help="User ID for outgoing digest (rewrite) mail server")
    parser.add_option("--digests-pw", dest="digests_pw",
                      help="User's password for outgoing digest (rewrite) mail server")
    parser.add_option("--digests-folder", dest="digests_folder_name", default="INBOX",
                      help="The IMAP folder to pull/push digest from/to, e.g. INBOX")
    parser.add_option("--digests-cert-check-skip", action="store_true", dest="digests_cert_check_skip",
                      help="Skip Certificate check digest imap server (say self-signed)")
    parser.add_option("--digests-no-ssl", action="store_false", dest="digests_ssl", default=True,
                      help="SSL True/False (port 993) for digest IMAP? (True by default)")
    parser.add_option("--implicate", dest="sender_to_implicate",
                      help="Who to name in digest emails, e.g. imapdigester@example.com")
    parser.add_option("--move-unmatched", action="store_true", dest="move_unmatched",
                      help="Move unmatched emails to digest inbox")
    parser.add_option("--print-summary", action="store_true", dest="print_summary", help="Print Summary")

    (options, args) = parser.parse_args()

    old_imapclient = (imapclient.__version__ == "0.13")
    if old_imapclient and (options.digests_cert_check_skip or options.notifications_cert_check_skip):
        print("Can't do certificate check skipping on IMAPClient 0.13 with command line options " \
              "--digests-cert-check-skip or --notifications-cert-check-skip")
        exit(10)

    print("Notifications IMAP account: " + str(options.notifications_imap))
    print("Notifications IMAP account user: " + str(options.notifications_user))
    print("Notifications IMAP account password is set?: " + str(options.notifications_pw is not None))

    print("Digests IMAP account: " + str(options.digests_user))
    print("Digests IMAP account user: " + str(options.digests_user))
    print("Digests IMAP account password is set?: " + str(options.digests_pw is not None))

    if options.notifications_pw is None:
        print("Enter the user's password for the 'notifications' IMAP account:")
        options.notifications_pw = getpass.getpass()

    if options.digests_pw is None:
        if options.notifications_imap == options.digests_imap and options.notifications_user == options.digests_user:
            options.digests_pw = options.notifications_pw
        else:
            print("Enter the user's password for the 'digest' IMAP account:")
            options.digests_pw = getpass.getpass()

    # Read and mark for deletion items from notification inbox.
    notification_folder = None
    kwargs = {"use_uid": True, "ssl": options.notifications_ssl}
    if not old_imapclient and options.notifications_cert_check_skip:
        notifications_context = None
        notifications_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        notifications_context.check_hostname = False
        notifications_context.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = notifications_context

    try:
        notification_folder = IMAPClient(options.notifications_imap, **kwargs)
    except gaierror:
        print("CAN'T FIND IMAP SERVER")
        exit(10)
    try:
        notification_folder.login(options.notifications_user, options.notifications_pw)
    except:
        time.sleep(5)
        notification_folder = IMAPClient(options.notifications_imap, **kwargs)
        try:
            notification_folder.login(options.notifications_user, options.notifications_pw)
        except:
            print("CAN'T LOG IN TO IMAP SERVER")
            exit(10)
    time.sleep(1)
    notification_folder.select_folder(options.notifications_folder_name)

    kwargs = {"use_uid": True, "ssl": options.digests_ssl}
    if not old_imapclient and options.digests_cert_check_skip:
        digests_context = None
        digests_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        digests_context.check_hostname = False
        digests_context.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = digests_context
    digests_folder = IMAPClient(options.digests_imap, **kwargs)

    try:
        digests_folder.login(options.digests_user, options.digests_pw)
    except:
        time.sleep(5)
        digests_folder.login(options.digests_user, options.digests_pw)
    digests_folder.select_folder(options.digests_folder_name)

    command = get_command()
    if command is None:
        digesters = []

        if os.path.isfile("my_digesters_setup.py"):
            from my_digesters_setup import add_digesters
        else:
            print("#################################################################")
            print("##                                                             ##")
            print("##                        IMAP Digester                        ##")
            print("##                        -------------                        ##")
            print("##                                                             ##")
            print("##   You should really copy `my_digesters_setup_sample.py`     ##")
            print("##   to `my_digesters_setup.py` and customize it for you.      ##")
            print("##                                                             ##")
            print("#################################################################")
            from my_digesters_setup_sample import add_digesters

        # Get Digesters from my_digesters_setup.py
        add_digesters(digesters)

        DigestionProcessor(notification_folder, digests_folder, digesters, options.print_summary,
                           options.sender_to_implicate, options.move_unmatched, options.digests_folder_name)\
            .doit()

    try:
        digests_folder.expunge()
    except IMAPClient.AbortError as e:
        print("Error expunging digest folder:")
        e.print_exc()

    digests_folder.logout()

    try:
        notification_folder.expunge()
    except IMAPClient.AbortError as e:
        print("Error expunging notification folder")
    notification_folder.logout()

    if command is "BASH-OPERATIONS":
        sys.exit(202)  ## HTTP 'accepted' (FYI)
