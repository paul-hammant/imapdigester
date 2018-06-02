# ImapDigester

Reads all* your robot-sent notifications and digests them into a **single** digest email, that has some smarts: how much
you've read previously or not.

 * all, means three types of credit card alerts, and notifications from Github, Linkedin, Hipchat, Confluence,
  Jira, and StackExchange **so far**.

To reiterate: this tech perpetually rewrites emails directly in your Inbox with 'sending' (SMTP) emails at all.

![image](https://user-images.githubusercontent.com/82182/32691583-e7d552f4-c6d7-11e7-936a-42d8eed99bfd.png)

# Rationale

I've been blogging for a while towards this better **pervasive inbox**:

- April 4th, 2016 » [Reducing My Robo-Emails To A Handful of Digest Emails Every Few Minutes (IMAP Rewriting With Python)](http://paulhammant.com/2016/04/04/reducing-my-robo-emails-to-a-handful-of-rollup-emails-every-few-minutes/)
- September 3rd, 2015 » [Resurrecting a small piece of Google Wave](http://paulhammant.com/2015/09/03/resurrecting-a-small-piece-of-google-wave/)
- May 4th, 2015 » [Treating IMAP as a store: rewriting emails](http://paulhammant.com/2015/05/04/treating-imap-as-a-store-rewriting-emails/)
- October 27th, 2014 » [The Pervasive Inbox](http://paulhammant.com/2014/10/27/the-pervasive-inbox/)
- January 30th, 2014 » [It is Time for Email Apps to Support JavaScript](http://paulhammant.com/2014/01/30/its-time-for-email-apps-to-support-javascript/)


# General Setup

For this to work, you need two dedicated email addresses:

1. For incoming machine-to-human notifications to send to, you **don't ever tell anyone else about it**, as it is not
what you correspond with people through. It is dedicated to this process.
You pass it to applications that issue notifications. You're going  to a script (see below) that reads and
deletes from inbox for you. Lets call this the **notification inbox**.

2. For Digest emails to be written/rewritten to. That script (below) is going to look after the
inbox for this one. This email address is totally private to you - not even other machines know about it.
Just you, software-daemons you deployed and your email client(s). Let's call this the **digest inbox**. It could be
your regular email address, but what if there's a bug and it deletes all you email - yup, that's right, use a
dedicated email account for this one too too.

Maybe grabbing two email addresses from a major email provider the above two is best. Your email client (desktop or
mobile) may be able to show and "all inboxes" view of your regular email, and your **digest inbox** just fine.
The Outlook client on the iPhone certainly can.

# Deploying your ImapDigester process

## Installation Prerequisites

### Install Python 3.6 or above:

```
brew install python3
# (you might have to force link that)
# apt-get for Linux
```

### Then Python packages, via pip3:

```
pip3 install lxml BeautifulSoup4 IMAPClient arrow jinja2 simplejson mockextras jsonpickle
```

## Installing it on a Pi Zero, and running it for $1.10 a year (electricity)

In `/home/pi`, git clone the repo, and cd into that folder in order to copy a shell script (make it executable too):

```
git clone https://github.com/paul-hammant/imapdigester.git
cd imapdigester
cp cron_run_imapdigester_sample.sh cron_run_imapdigester.sh
chmod +x cron_run_imapdigester.sh
```

Then customize `cron_run_imapdigester.sh` as appropriate for your email provider and account details. If you run that shell script, you should be able it's output in `imapdigester_output.txt`.

You also have a `my_digesters_setup_sample.py` in the root folder that should be copied to `my_digesters_setup.py` and
then edited to customize. You don't have to delete th digiesters you're not needing (they only tak a small amount of cpu
time per notification email and are effectively benign if they don't match against the headers of the email. You
would add new digesters here too, as well as change parameters for individual digesters that you do want.

## Scheduling the job with Cron

In `/etc/cron.d` make a file `run_imapdigester` (sudo needed):

```
*/10 * * * * pi /home/pi/imapdigester/runimapdigester.sh
```

Make sure you added a newline to the end of that line.

The setup above will cause cron to run imapdigester every ten minutes.

Reboot the cron system, to start it, like so:

```
sudo /etc/init.d/rsyslog restart
```

If that file does not appear within 10 mins (zero bytes), then you can change cron to log by editing a line
in `/etc/rsyslog.conf` that is about cron's logging, then tail `/var/log/cron.log` which may give an insight as to
what is wrong.

## Setup Choices

The Inbox for the accounts is the default, but via `--notifications-folder` and `--digest-folder` you could specify
a different folder for processing. Case might be important.

You can have the same email account for **notifications** and **digests**. I choose not to, because I'm a chicken.
Similarly, you can have the same folder within the same email account if you want to.

If you leave out `--notifications-pw` or `--digest-pw` you will be prompted at startup to enter them.
If **notifications** and **digest** use the same email account, you'll only be prompted once.

If you're using a self-signed IMAP server use `--digest-cert-check-skip` and/or `--notifications-cert-check-skip` to turn
off the verification of the certificate for the IMAP server

If your IMAP server isn't over SSL (port 993) at all, then you can specify `--notifications-no-ssl` and `--digest-no-ssl`
to unencrypted IMAP (port 143).

# The One Dollar & Ten Cents claim?

The $1.10 referenced is 0.7 Watt for 8760 hours (one year) at current electricity prices (18c/KWh). The Pi Zero on its
own consumes a quarter of that, and the rest is the USB wifi dongle. Inefficiency of a 110V to 5V transformer is not
factored in. Refer a [Pi power usage page](http://www.pidramble.com/wiki/benchmarks/power-consumption).

# Digest emails are available for these services

## Credit Card usages.

A single email that can, so far, pull in transactions from American Express (US), Citibank (US) and Chase (US).
Ordered by most recent first. These guys made it hard. For want of a text/json multi-part chunk (that includes a
transaction ref for correlation).

![](http://paulhammant.com/images/cc_rollup.jpg)

[Read more](https://github.com/paul-hammant/imapdigester/wiki/Charge-and-credit-card-alerts)

## Stack Exchange Notifications

[Read more](https://github.com/paul-hammant/imapdigester/wiki/StackExchange-Filter-Notifications)

## Github Repo Notifications

Whatever you're watching in terms of repo, will be distilled into a single email. This gets longer and longer as an
email, with new notification gravitating to the top of the email. Versus the last time the email
was written:

![](http://paulhammant.com/images/gh_rollup.jpg)

- If there's new notifications the email will be rewitten.
- If not the email is left alone (including the date of the email, which means it drifts down your inbox)

Versus whether you've read the email or not:

- A line appears in the email showing what notifications (relating to topics) that have you have read versus what
you have not.

If you delete the email, the server deletes all the things you've read from the accumlated list of notifications too.
i.e. it appears to start over.

Note - there is grouping around topic (repo-issue, repo-PR, repo-commit-comment).

You can configure a GithubEnterprise usage too - just edit `my_digesters_setup.py` (hopefully you already copied it
from `my_digesters_setup_sample.py`) - to set domain names, emails etc.

## Hipchat Notifications

Both 1-1 messages and Room mentions are rolled up into a single most-recent-first email.

If you're interested in increasing the support for Hipchat - [please vote on feature request #579](https://jira.atlassian.com/browse/HCPUB-579)

## Linkedin Invitations

[See wiki page](https://github.com/paul-hammant/imapdigester/wiki/Linkedin-Invitations)

## Confluence Notifications

Notifications are rolled up into a single most-recent-first email:

- User X commented on page (done)
- User X changed a page (done)
- User X added a page (done)

You must configure `my_digesters_setup.py` (hopefully you already copied it from `my_digesters_setup_sample.py`) to
set the emails confluence uses to notify you, and a short name for that instance.

If you're interested in increasing the support for Confluence - [please vote on feature request #41391](https://jira.atlassian.com/browse/CONF-41391)

## Jira Notifications

Notifications are rolled up into a single most-recent-first email:

- User X created an issue (done)
- User X changed an issue (done)
- User X commented on an issue (done)

You must configure `my_digesters_setup.py` (hopefully you already copied it from `my_digesters_setup_sample.py`) to
set the emails confluence uses to notify you, and a short name for that instance.

Refer too https://jira.atlassian.com/browse/JRA-60611 and https://jira.atlassian.com/browse/JRA-60612

## Reddit Notifications

TODO

# Command emails

If you email the subject line `git-pull` to the digest email address, the daemon will update itself from git
(provided there are no merge conflicts).

If you email the subject-line `pause` to the digest email address, the daemon will pause the digesting of notifications.

If you email the subject-line `resume` to the digest email address, the daemon will resume from it's paused state.

Each command email is deleted as soon as it is acted upon

# Yet to do

- More Integration tests (samples of emails need to be sanitized and copied into `testdata/` or tests).
