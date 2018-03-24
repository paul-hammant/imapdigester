#! /bin/sh

do_it() {

    # Some bash commands can come in front of the IMAP digesting.
    # For example 'git pull' (as commanded)
    if [ -f "imapdigester_commands_next_time.sh" ]; then
        chmod +x imapdigester_commands_next_time.sh
        ./imapdigester_commands_next_time.sh
        rm imapdigester_commands_next_time.sh
    fi

    # Do the IMAP digesting (python 2.7.11 or above)
     /usr/bin/python digest_emails.py \
     --notifications-imap imap-mail.outlook.com \
     --notifications-user imap_tester1@outlook.com \
     --notifications-pw 'Kailash.68' \
     --digest-imap imap-mail.outlook.com \
     --digest-user imap_tester2@outlook.com \
     --digest-pw 'Kailash.68' \
     --implicate imapdigester@it_does_not_matter.com \
     --move-unmatched  >> imapdigester_output.txt 2>&1

     # --digest-cert-check-skip  (you're using a self-signed imap server)
     # --notifications-cert-check-skip  (you're using a self-signed imap server)

}

do_it
if [ $? -eq 202 ]
then
  # Perhaps there was a command to do 'git pull'
  do_it
fi
