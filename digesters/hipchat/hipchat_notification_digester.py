# coding=utf-8
from __future__ import unicode_literals

import arrow
from bs4 import BeautifulSoup

from digesters.base_digester import BaseDigester

TEMPLATE = """<html>
<head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
    <title>Atlassian HipChat</title>
</head>
<body style="box-sizing: border-box; height: 100%; width: 100%;">
<table bgcolor="#f5f5f5" border="0" cellpadding="0" cellspacing="0" class="container wrapper_shrink"
       style="_padding: 20px; padding: 3%;" width="640">
    <tr>
        <td valign="top">
            <table bgcolor="#ffffff" border="0" cellpadding="0" cellspacing="0" class="inner-container table_shrink"
                   id="email_content"
                   style="-khtml-border-radius: 6px; -moz-border-radius: 6px; -webkit-border-radius: 6px; border: 1px solid #dadada; border-radius: 6px; width: 100% !important; margin-top: 15px;"
                   width="600">
                <tr>
                    <td class="td top-spacer"
                        style="font-size: 15px; line-height: 4px; padding-left: 20px; padding-right: 10px !important;"
                        valign="top">
                    </td>
                </tr>
                <tr>
                    <td>
                        <div class="history_container history_email" id="chats" style="padding-right: 0px !important;">
                            <InsertHere/>
                        </div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
</body>
</html>"""


class HipchatNotificationDigester(BaseDigester):
    def __init__(self, store_writer):
        super(HipchatNotificationDigester, self).__init__()
        self.store_writer = store_writer
        self.new_message_count = 0
        self.new_articles = 0
        self.hc_notifications = self.store_writer.get_from_binary("hipchat-notifications")
        if self.hc_notifications is None:
            self.hc_notifications = {}

        self.most_recently_seen = self.store_writer.get_from_binary("most-recently-seen")
        if self.most_recently_seen is None:
            self.most_recently_seen = 0

        self.new_notifications = {}

        self.previously_notified_article_count = len(self.hc_notifications)
        if self.previously_notified_article_count > 0:
            self.previously_notified_article_most_recent = max(self.hc_notifications)
        else:
            self.previously_notified_article_most_recent = 0

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        self.new_message_count += 1
        subject = msg['Subject']
        if "sent you a 1-1 message" in subject:
            room = "Direct Message"
        else:
            room = "Room: " + subject.split('"')[1]
        when = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ').timestamp

        if html_message:
            soup = BeautifulSoup(html_message, 'html.parser')
            div = soup.find("div", {"id": "chats"}).find("div")

            self.hc_notifications[when] = {
                "room": room,
                "div": str(div)
            }
            return True

        return False

    def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if self.previously_notified_article_count == len(self.hc_notifications):
            return


        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Rollup again.
        if has_previous_message == False:
            self.hc_notifications = {}

        if has_previous_message == False:
            if self.previously_notified_article_count > 0:
                self.most_recently_seen = self.previously_notified_article_most_recent

        template_end, template_start = self.get_template_start_and_end(TEMPLATE)

        past_bookmark = 0
        unseen = 0
        for when in sorted(self.hc_notifications.iterkeys(), reverse=True):
            mostRecentSeen = self.most_recently_seen
            if when < mostRecentSeen:
                past_bookmark += 1
            else:
                unseen += 1
            if past_bookmark > 30:  # only show thirty after the bookmark
                self.hc_notifications.pop(when, None)

        email_html = self.make_html_payload(template_end, template_start, self.hc_notifications).replace("<br/>","")

        # Delete previous email, and write replacement
        if has_previous_message:
            digest_folder_proxy.delete_previous_message()
        digest_folder_proxy.append(self.make_new_raw_so_email(email_html, unseen, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("hipchat-notifications", self.hc_notifications)
        self.store_writer.store_as_binary("most-recently-seen", self.most_recently_seen)

    def matching_incoming_headers(self):
        return ["From: HipChat <donotreply@hipchat.com>"]

    def matching_digest_subject(self):
        return 'Hipchat Rollup'

    def print_summary(self):
        print "Hipchat: New hipchat notifications: " + str(self.new_message_count)

    def get_template_start_and_end(self, template):
        template_start = template[:template.find("<InsertHere/>")]
        template_end = template[template.find("<InsertHere/>") + len("<InsertHere/>"):]
        return template_end, template_start

    def make_html_payload(self, template_end, template_start, hc_notifications):
        email_html = template_start

        ix = 0
        for anum in sorted(hc_notifications.iterkeys(), reverse=True):
            if anum == self.most_recently_seen and ix > 0:
                email_html += '<div style="border-bottom: 1.5pt solid red; border-top: 1.5pt solid red;"><center>^ New Questions Since You Last Checked ^</center></div>\n'
            email_html += '<div class="ecxhc-chat-from" style="margin-left: 150px;text-align:left;width:200px;padding:10px 0 10px 10px;">' + hc_notifications[anum]["room"] + '</div>\n'
            email_html += "<div>\n" + hc_notifications[anum]["div"] + "</div>\n"
            ix = + 1
        email_html += template_end

        return email_html

    def make_new_raw_so_email(self, email_html, count, sender_to_implicate):
        new_message = 'Subject: ' + self.matching_digest_subject() + ": " + str(count) + ' new notification(s)\n'
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

        return new_message
