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
     /usr/bin/python digest_emails.py --notifications_imap imap-mail.emailprovider.com \
     --notifications_user secret_email_address_for_notifications@emailprovider.com \
     --notifications_pw '123456' \
     --rollup_imap imap-mail.emailprovider.com \
     --rollup_user another_email_address_for_rollups@emailprovider.com \
     --rollup_pw p4ssw0rd \
     --implicate '"ImapDigester" <imapdigester@it_does_not_matter.com>' \
     --move_unmatched  >> imapdigester_output.txt 2>&1
}

do_it
if [ $? -eq 202 ]
then
  # Perhaps there was a command to do 'git pull'
  do_it
fi

