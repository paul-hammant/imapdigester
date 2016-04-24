from __future__ import unicode_literals

import StringIO
import re
from email.header import decode_header

import arrow
from jinja2 import Template

from digesters.base_digester import BaseDigester


class GithubNotificationDigester(BaseDigester):
    def __init__(self, store_writer, return_path_email="noreply@github.com", from_email="notifications@github.com",
                 site="github.com", known_as="Github"):
        super(GithubNotificationDigester, self).__init__()
        self.site = site
        self.known_as = known_as
        self.from_email = from_email
        self.return_path_email = return_path_email
        self.store_writer = store_writer
        self.new_message_count = 0
        self.new_articles = 0
        self.github_notifications = self.store_writer.get_from_binary("github-notifications")
        if self.github_notifications is None:
            self.github_notifications = {}

        self.most_recently_seen = self.store_writer.get_from_binary("most-recently-seen")
        if self.most_recently_seen is None:
            self.most_recently_seen = 0

        self.new_notifications = {}

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        self.new_message_count += 1
        subj = msg['Subject'].replace("Re: ", "")
        nick = msg['X-GitHub-Sender'].strip()
        who = msg['From']
        who = who[:who.index('<notifications')].strip()
        if who.startswith("=?"):
            who, encoding = decode_header(who)[0]

        origArrivalTime = msg['X-OriginalArrivalTime']
        origArrivalTime = origArrivalTime[:origArrivalTime.index(' (UTC')]
        when = arrow.get(origArrivalTime, 'DD MMM YYYY HH:mm:ss.SSSS')
        closedVia = re.search('^Closed #\d* via ', text_message)
        closed = re.search('^Closed #\d*\.', text_message)
        issueComment = re.search('\nhttps:\/\/github\.com\/.*\/.*\/issues\/\d*#issuecomment', text_message)
        commitComment = re.search('\nhttps:\/\/github\.com\/.*\/.*\/commit\/.*#commitcomment', text_message)
        prComment = re.search('\nhttps:\/\/github\.com\/.*\/.*\/pull\/\d*#issuecomment', text_message)
        review = re.search('\nhttps:\/\/github\.com\/.*\/.*\/pull\/\d*\/files\/', text_message)
        inReplyTo = msg['In-Reply-To']
        inReplyToMatch = None
        if inReplyTo:
            inReplyToMatch = re.search('<(.*)>', inReplyTo)
        messageId = re.search('<(.*)>', msg['Message-ID'])
        nolines = ' '.join(text_message.split())
        message = ""

        openPR = re.search(".*You can view.*Commit Summary.*File Changes.*Patch Links.*---", nolines)
        if openPR is None:
            message = self.extract_message(text_message, subj)

        if (inReplyToMatch):
            topic = inReplyToMatch.group(1)
        else:
            topic = messageId.group(1)

        n = self.make_new_noticiation(closedVia, closed, issueComment, commitComment, message, nick, openPR,
                                                prComment, review, subj, topic, who)
        self.new_notifications[when.timestamp] = n

        return True

    @staticmethod
    def make_new_noticiation(closedVia, closed, issueComment, commitComment, message, nick, openPR, prComment,
                             review, subj, topic, who):
        return {
            "who": nick + (": " + who if who != nick else ""),
            "topic": topic.strip(),
            "subj": subj.strip(),
            "what": (
                "closed" if (closedVia or closed) else "comment" if (
                    issueComment or prComment) else "review" if review else "opened" if openPR else "commit comment" if commitComment else "uncategorized comment"
            ),
            "msg": message

            # Note - "uncategorized" - https://github.com/Homebrew/homebrew/issues/50430#issue-143647730
            # - was sent to me without the word "comment" in the email's raw source anywhere, yet it was a comment
        }

    @staticmethod
    def extract_message(body, subj):

        message = ""
        quoted = False
        ddd = False
        s = StringIO.StringIO(body)
        for line in s:
            if line.startswith("> "):
                quoted = True
                continue
            if line.strip() == "":
                continue
            if message == "":
                message = unicode(line[:55].strip(), errors='replace')
                if len(line) > 55:
                    ddd = True
                continue
            if line.strip() == "---":
                break
            ddd = True
            break
        if quoted:
            message = "[quoted block] " + message
        if ddd:
            message += "..."
        return message

    def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if len(self.new_notifications) == 0:
            return

        # print ">>> Previous githubNotifications: " + json.dumps(self.githubNotifications, sort_keys=True) + "\n\n"

        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Rollup again.
        if has_previous_message == False:
            self.github_notifications = {}

        # If the last mail has been read, then everything in it has been seen
        if previously_seen:
            for topic, detail in self.github_notifications.iteritems():
                if (detail["mostRecent"] > self.most_recently_seen):
                    self.most_recently_seen = detail["mostRecent"]

        # print ">>> newNotifications: " + json.dumps(self.newNotifications, sort_keys=True) + "\n\n"

        self.add_new_notifications_to_those_grouped_by_topic_and_calc_most_recent_for_each_topic()

        # print ">>> Resulting githubNotifications: " + json.dumps(self.githubNotifications, sort_keys=True) + "\n\n"

        notifs_to_print = self.map_topics_by_their_most_recent_notification()

        num_messages_since_last_seen = self.add_time_differences_and_line_to(notifs_to_print)

        templ = """
{% if not_first_email %}<span>You have previously read notifications up to: {{most_recent_seen_str}}</span>{% endif %}
<table>
  <tr style="background-color: #acf;">
    <th>When</th><th>Issues/Pull Requests &amp; Their Notifications</th>
  </tr>
{% for when, topic in notifs_to_print|dictsort(false, by='key')|reverse %}
{% if topic['line_here'] %}
  <tr><td colspan="2" style="border-bottom: 1pt solid red; border-top: 1pt solid red;"><center>^ New/Updated Notifications Since You Last Checked ^</center></td></tr>
{% endif %}
  <tr style="{{loop.cycle('','background-color: #def;')}}">
    <td valign="top">{{ topic.when.replace('---','<br/>') }}</td>
    <td>
      <table style="border-top: none">
        <tr>
          <td style="border-bottom: 2px solid lightgrey;">
            <a href="https://{{site}}/{{topic['path']}}">{{ topic['type'] }}: {{ topic['subj'] }}</a>
          </td>
        </tr>
{% for t, detail in topic['ts']|dictsort(false, by='key')|reverse %}
        <tr>
          <td{{' style="font-weight: bold;"' if t>most_recent_seen}}>{{ detail['who'] }} ({{ detail['what'] }}{{ detail['diff'] }}) {{detail["msg"]}}</td>
        </tr>
{% endfor %}
       </table>
    </td>
  </tr>
{% endfor %}
</table>"""

        template = Template(templ)
        seen_formated = arrow.get(self.most_recently_seen).to("local").format("MMM DD YYYY hh:mm A")
        email_html = template.render(notifs_to_print=notifs_to_print,
                                     site=self.site,
                                     most_recent_seen=self.most_recently_seen,
                                     most_recent_seen_str=seen_formated,
                                     not_first_email=(self.most_recently_seen > 0))

        new_message = 'Subject: ' + self.matching_digest_subject() + ' (' + str(
            num_messages_since_last_seen) + ' new)\n'
        new_message += 'From: ' + sender_to_implicate + '\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n'
        new_message += 'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY' \
                       + self.notification_boundary_rand + '"\n'
        new_message += 'MIME-Version: 1.0\n'
        new_message += 'This is a multi-part message in MIME format.\n'
        new_message += '-----NOTIFICATION_BOUNDARY' + self.notification_boundary_rand \
                       + '\nContent-Type: text/html; charset="utf-8"\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n\n'
        email_ascii = email_html.replace("\n\n\n", "\n").replace("\n\n", "\n").encode('utf-8', 'replace')
        # Ugly hack
        email_ascii = "".join(i for i in email_ascii if ord(i) < 128)
        new_message += email_ascii
        new_message += '\n\n-----NOTIFICATION_BOUNDARY' + self.notification_boundary_rand

        # Delete previous email, and write replacement
        if has_previous_message:
            digest_folder_proxy.delete_previous_message()
        digest_folder_proxy.append(new_message)
        # Save
        self.store_writer.store_as_binary("github-notifications", self.github_notifications)
        self.store_writer.store_as_binary("most-recently-seen", self.most_recently_seen)

    def add_new_notifications_to_those_grouped_by_topic_and_calc_most_recent_for_each_topic(self):
        for ts, notif in self.new_notifications.iteritems():
            if (notif["topic"] not in self.github_notifications):
                self.github_notifications[notif["topic"]] = {"ts": {}, "mostRecent": 0}
            if (ts > self.github_notifications[notif["topic"]]["mostRecent"]):
                self.github_notifications[notif["topic"]]["mostRecent"] = ts
            self.github_notifications[notif["topic"]]["subj"] = notif["subj"]
            self.github_notifications[notif["topic"]]["ts"][ts] = {
                "who": notif["who"],
                "what": notif["what"],
                "msg": notif["msg"]
            }

    def map_topics_by_their_most_recent_notification(self):
        # map topics by their most recent notification
        notifsToPrint = {}
        for topic, detail in self.github_notifications.iteritems():
            notifsToPrint[detail["mostRecent"]] = {
                "when": arrow.get(detail["mostRecent"]).to("local").format("MMM DD YYYY---hh:mm A"),
                "path": topic[:topic.index("@")],
                "type": "Pull Request" if topic.find("/pull/") > 0 else "Issue" if topic.find(
                    "/issues/") > 0 else "Commit" if topic.find(
                    "/commit/") > 0 else "???",
                "subj": detail["subj"],
                "ts": detail["ts"]
            }
        return notifsToPrint

    def add_time_differences_and_line_to(self, notifsToPrint):
        num_messages_since_last_seen = 0
        line_here_done = False
        mostRecentNotification = None
        for ts0, notif in sorted(notifsToPrint.iteritems(), reverse=False):
            mostRecentNotification = notif
            if self.most_recently_seen != 0 and ts0 >= self.most_recently_seen and line_here_done == False:
                notif['line_here'] = True
                line_here_done = True
            lastTs = 0
            for ts, detail in sorted(notif["ts"].iteritems(), reverse=True):
                if (ts > self.most_recently_seen):
                    num_messages_since_last_seen += 1
                if lastTs != 0:
                    secsDiff = abs(ts - lastTs)
                    if secsDiff < 200:
                        detail["diff"] = " " + str(round(secsDiff, 0)) + " secs earlier"
                    elif secsDiff < 7000:
                        detail["diff"] = " " + str(round((secsDiff / 60), 0)) + " mins earlier"
                    elif secsDiff < 177000:
                        detail["diff"] = " " + str(round((secsDiff / 60 / 60), 0)) + " hours earlier"
                    else:
                        detail["diff"] = " " + str(round((secsDiff / 60 / 60 / 24), 0)) + " days earlier"
                else:
                    detail["diff"] = ""
                lastTs = ts
        # The most recent one can't have any above it.
        mostRecentNotification['line_here'] = False
        return num_messages_since_last_seen

    def matching_incoming_headers(self):
        return ["\nReturn-Path: " + self.return_path_email, "\nFrom: .* <" + self.from_email + ">"]

    def matching_digest_subject(self):
        return self.known_as + ' Rollup'

    def print_summary(self):
        print "New " + self.known_as + " notifications: " + str(self.new_message_count)
