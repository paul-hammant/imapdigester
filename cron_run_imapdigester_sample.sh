#! /bin/sh

do_it() {

    # Some bash commands can come in front of the IMAP digesting.
    # For example 'git pull' (as commanded)
    if [ -f "imapdigester_commands_next_time.sh" ]; then
        chmod +x imapdigester_commands_next_time.sh
        ./imapdigester_commands_next_time.sh
        rm imapdigester_commands_next_time.sh
    fi

    python3 digest_emails.py \
      --notifications-imap imap-mail.outlook.com \
      --notifications-user imap_tester1@outlook.com \
      --notifications-pw 'PASSWORD FOR THAT ACCOUNT' \
      --digests-imap imap-mail.outlook.com \
      --digests-user imap_tester2@outlook.com \
      --digests-pw 'PASSWORD FOR THAT ACCOUNT' \
      --implicate imapdigester@it_does_not_matter.com \
      --move-unmatched  >> imapdigester_output.txt 2>&1

      # --digests-cert-check-skip  (you're using a self-signed imap server)
      # --notifications-cert-check-skip  (you're using a self-signed imap server)

}

do_it
if [ $? -eq 202 ]
then
  # Perhaps there was a command to do 'git pull'
  do_it
fi
