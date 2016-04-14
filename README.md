# ImapDigester

Reads all* your robot-sent notifications and digests them into a single rollup email, that has some smarts how much
you've read previously or not.

 * all, cough, means three types of credit card alerts, and notifications from github and stackexchange so far

For this to work, you need two dedicated email addresses:

1. For incoming machine-to-human notifications to send to, you **don't ever tell anyone else about it**, as it is not 
what you correspond with people through. It is dedicated to this process. 
You pass it to applications that issue notitifactions. You're going  to a script (see below) that reads and 
deletes from inbox for you. Lets call this the **notification inbox**.

2. For Rollup emails to be written/rewritten to. That script (below) is going to look after the 
inbox for this one. This email address is totally private to you - not even other machines know about it. 
Just you, software-daemons you deployed and your email client(s). Let's call this the **rollup inbox**. It could be
your regular email address, but what if there's a bug and it deletes all you email - yup, that's right, use a 
dedicated email accound for this one too too.

Maybe grabbing two email addresses from a major email provider the above two is best. Your email client (desktop or 
mobile) may be able to show and "all inboxes" view of your regular email, and your **rollup inbox** just fine.  
The Outlook client on the iPhone certainly can.

# Deploying your daemon

I have mine on a Raspberry Pi Zero that's just dangling out of a power socket at home.  If I were you I'd fork this
repo, make mods for `my_digesters_setup.py` (or copy it, and change the ref in `digest_emails.py`) for yourself (not
for PR back to me until I can engineer a better customization design).

## Installation Prerequisites

Python 2.7:

```
brew install python
# apt-get for Linux
# you might have to force link that

pip install BeautifulSoup4
pip install imapclient==0.13
pip install arrow
pip install jinja2
pip install simplejson
pip install mockextras
```

## Imapclient sadness

Imapclient's latest release is broken for me, this I'm choosing a non-current imapclient library (0.13). 
It is broken for others, too:
http://stackoverflow.com/questions/34780726/imapclient-error-diff-version-python-and-windows

Also refer https://bitbucket.org/mjs0/imapclient/issues/201/segfault-11-on-mac-10105-with-python-344 as well as 
https://github.com/alekstorm/backports.ssl/issues/14, https://github.com/alekstorm/backports.ssl/issues/15, 
https://github.com/alekstorm/backports.ssl/issues/16

# Running it on the Pi Zero for less than $2/year in electricity

In `/home/pi`, git clone this repo.

Make a script `run_imapdigester.sh`, and customize as appropriate below for your email provider and account details:

```
#!/bin/sh

cd /home/pi/imapdigester/
/usr/bin/python digest_emails.py --notifications_imap imap-mail.emailprovider.com \
     --notifications_user secret_email_address_for_notifications@emailprovider.com --notifications_pw '123456' \
     --rollup_imap imap-mail.emailprovider.com \
     --rollup_user another_email_address_for_rollups@emailprovider.com --rollup_pw p4ssw0rd \
     --implicate '"ImapDigester" <imapdigester@it_does_not_matter>' \
     --move_unmatched  >> imapdigester_output.txt 2>&1
```

Make it executable: `chmod +x run_imapdigester.sh`

If you run that shell script, you should be able it's output in `imapdigester_output.txt`.

Note the $2 is 0.8 Watt for 8760 (a year) at current electricity prices (18c/KWh), rounded up.

## Scheduling it with Cron

In `/etc/cron.d` make a file (sudo needed):

```
*/10 * * * * pi /home/pi/imapdigester/runimapdigester.sh
```

Make sure you added a newline to the end of that line.

The setup above will cause cron to run imapdigester every ten minutes.**

Reboot the cron system, to start it, like so:

```
sudo /etc/init.d/rsyslog restart
```

If that file does not appear within 10 mins (zero bytes), then you can change cron to log by editing a line in `/etc/rsyslog.conf` that is about cron's logging, then tail `/var/log/cron.log` which may give an insight as to what is wrong.

## Setup Choices

The Inbox for the accounts is the default, but via `--notifications_folder` and `--rollup_folder` you could specify
a different folder for processing. Case might be important.

You can have the same email account for **notifications** and **rollup**. I choose not to, because I'm a chicken.
Similarly, you can have the same folder within the same email account if you want to.

If you leave out `--notifications_pw` or `--rollup_pw` you will be prompted at startup to enter them.
If **notifications** and **rollup** use the same email account, you'll only be prompted once.

# Rewritten emails are available for:

## Credit Card usages.

A single email that can, so far, pull in transactions from American Express (US), Citibank (US) and Chase (US).
Ordered by most recent first. These guys made it hard. For want of a text/json multi-part chunk (that includes a 
transaction ref for correlation).

![](http://paulhammant.com/images/cc_rollup.jpg)

[Read more](https://github.com/paul-hammant/imapdigester/wiki/Charge-and-credit-card-alerts)

## Stack Exchange Notifications

In the StackOverflow/StackExchange web interface you'll need to setup a notification filter. Do that to the dedicated 
email address (#1 above), and remember to confirm you filter changes, by clicking in a confirmation email (that SE/SO 
does't explicitly inform you about in the web interface). If you want, you can choose the every-15-mins varient of 
SO/SE notifications.

![](http://paulhammant.com//images/so_rollup.jpg)

If you're going to do the every-15-mins varient of SO/SE notifications run this python script every 15 mins or less 
so you're never too far behind.

Go to http://stackexchange.com/filters to see/setup your filters.

Note if you filter on just one tag, this digester will not work (it won't recognize the subject line of the incoming
emails. Therefore have AT LEAST TWO - like so http://imgur.com/YswesOB

## Github Repo Notifications

Whatever you're watching in terms of repo, will be distilled into a single email. This gets longer and longer as an 
email, with new notification gravitating to the top of the email. Versus the last time the email 
was written:

![](http://paulhammant.com/images/gh_rollup.jpg)

- If there's new notifications the email will be rewitten. 
- If not the email is left alone (including the date of the email, which means it drifts down your inbox)

Versus whether you've read the email or not:

- A line appears in the email showing what notifications (relating to topics) that have you have read versus what you have not.

If you delete the email, the server deletes all the things you've read from the accumlated list of notifications too. 
i.e. it appears to start over.

Note - there is grouping around topic (repo-issue, repo-PR, repo-commit-comment).

### You can configure a GithubEnterprise usage too

In `my_digester_setup.py` have a line like so:

```
digesters.append(GithubNotificationDigester(MetaStore("ghe_notifications"),
        return_path_email="noreply-ghe@yourcompany.com",
        from_email="ghe-notifications@yourcompany.com",
        site="ghe.yourcompany.com",
        known_as="GHE"))
```

## Hipchat Notifications

Both 1-1 messages and Room mentions are rolled up into a single most-recent-first email.

## Linkedin Invitations

Invitations are rolled up into a single most-recent-first email.

Even though Linkedin can capture second/third/fourth addresses, it only allows you to use your "primary" for notifications :-(

TODO - unilaterally add "reject" button.

## Confluence Notifications

Motifications are rolled up into a single most-recent-first email:

- User X commented on page (done)
- User X changed a page (done)
- User X added a page (done)

# Yet to do

- More Integration tests (samples of emails need to be sanitized and copied into `testdata/`).
