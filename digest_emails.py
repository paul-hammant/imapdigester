import getpass
import os
import sys
import time
import imp
from sys import version_info
from optparse import OptionParser
from socket import gaierror
import backports.ssl as ssl

import imapclient
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
    messages = digest_folder.search('SUBJECT "%s"' % cmd)
    response = digest_folder.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
    retval = False
    for msgid, data in response.items():
        digest_folder.delete_messages([msgid])
        retval = True
    return retval

if __name__ == '__main__':

    imp.reload(sys)
    # sys.setdefaultencoding('utf8')

    # Command Line Args

    parser = OptionParser()
    parser.add_option("--notifications-imap", dest="notifications_imap",
                      help="IMAP to use for incoming notifications mail server (SSL assumed)")
    parser.add_option("--notifications-user", dest="notifications_user",
                      help="User ID for incoming notifications mail server")
    parser.add_option("--notifications-pw", dest="notifications_pw",
                      help="User's password for incoming notifications mail server")
    parser.add_option("--notifications-folder", dest="notifications_folder_name", default="INBOX",
                      help="The Imap folder to pull notification from, e.g. INBOX")
    parser.add_option("--notifications-cert-check-skip", action="store_true", dest="notifications_cert_check_skip",
                      help="Skip Certificate check notification imap server (say self-signed)")
    parser.add_option("--notifications-no-ssl", action="store_false", dest="notifications_ssl", default=True,
                      help="SSL True/False (port 993) for notifications IMAP? (True by default)")
    parser.add_option("--digest-imap", dest="digest_imap",
                      help="IMAP to use for outgoing digest (rewrite) mail server (SSL assumed)")
    parser.add_option("--digest-user", dest="digest_user", help="User ID for outgoing digest (rewrite) mail server")
    parser.add_option("--digest-pw", dest="digest_pw",
                      help="User's password for outgoing digest (rewrite) mail server")
    parser.add_option("--digest-folder", dest="digest_folder_name", default="INBOX",
                      help="The Imap folder to pull/push digest from/to, e.g. INBOX")
    parser.add_option("--digest-cert-check-skip", action="store_true", dest="digest_cert_check_skip",
                      help="Skip Certificate check digest imap server (say self-signed)")
    parser.add_option("--digest-no-ssl", action="store_false", dest="digest_ssl", default=True,
                      help="SSL True/False (port 993) for digest IMAP? (True by default)")
    parser.add_option("--implicate", dest="sender_to_implicate",
                      help="Who to name in digest emails, e.g. imapdigester@example.com")
    parser.add_option("--move-unmatched", action="store_true", dest="move_unmatched",
                      help="Move unmatched emails to digest inbox")
    parser.add_option("--print-summary", action="store_true", dest="print_summary", help="Print Summary")

    (options, args) = parser.parse_args()

    old_imapclient = (imapclient.__version__ == "0.13")
    if old_imapclient and (options.digest_cert_check_skip or options.notifications_cert_check_skip):
        print("Can't do certificate check skipping on IMAPClient 0.13 with command line options " \
              "--digest-cert-check-skip or --notifications-cert-check-skip")
        exit(10)

    if options.notifications_pw is None:
        print("Enter notifications user password:")
        options.notifications_pw = getpass.getpass()

    if options.digest_pw is None:
        if options.notifications_imap == options.digest_imap and options.notifications_user == options.digest_user:
            options.digest_pw = options.notifications_pw
        else:
            print("Enter digest user password:")
            options.digest_pw = getpass.getpass()

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

    kwargs = {"use_uid": True, "ssl": options.digest_ssl}
    if not old_imapclient and options.digest_cert_check_skip:
        digest_context = None
        digest_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        digest_context.check_hostname = False
        digest_context.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = digest_context
    digest_folder = IMAPClient(options.digest_imap, **kwargs)

    try:
        digest_folder.login(options.digest_user, options.digest_pw)
    except:
        time.sleep(5)
        digest_folder.login(options.digest_user, options.digest_pw)
    digest_folder.select_folder(options.digest_folder_name)    

    command = get_command()
    if command is None:
        digesters = []

        if os.path.isfile("my_digesters_setup.py"):
            from my_digesters_setup import add_digesters
        else:
            # Copy my_digesters_setup_template.py to the my_digesters_setup.py,
            # if you're wanting to customize the digesters.
            from my_digesters_setup_sample import add_digesters

        # Get Digesters from my_digesters_setup.py
        add_digesters(digesters)

        DigestionProcessor(notification_folder, digest_folder, digesters, options.print_summary,
                           options.sender_to_implicate, options.move_unmatched, options.digest_folder_name)\
            .doit()

    try:
        print(digest_folder.expunge())
    except IMAPClient.AbortError as e:
        print("Error expunging digest folder")
    digest_folder.logout()

    try:
        notification_folder.expunge()
    except IMAPClient.AbortError as e:
        print("Error expunging notification folder")
    notification_folder.logout()

    if command is "BASH-OPERATIONS":
        sys.exit(202)  ## HTTP 'accepted' (FYI)
