# coding=utf-8
from __future__ import unicode_literals
import arrow
import re

import simplejson
from bs4 import BeautifulSoup

from base_notification_processor import BaseNotificationProcessor
from jinja2 import Template
import StringIO
from email.header import decode_header

class ConfluenceNotificationProcessor(BaseNotificationProcessor):
    def __init__(self, store_writer):
        self.store_writer = store_writer
        self.new_message_count = 0
        self.new_articles = 0
        self.confluence_notifications = self.store_writer.get_from_binary("confluence-notifications")
        if self.confluence_notifications is None:
            self.confluence_notifications = {}

        self.most_recently_seen = self.store_writer.get_from_binary("most-recently-seen")
        if self.most_recently_seen is None:
            self.most_recently_seen = 0

        self.new_notifications = {}

        self.previously_notified_article_count = len(self.confluence_notifications)
        if self.previously_notified_article_count > 0:
            self.previously_notified_article_most_recent = max(self.confluence_notifications)
        else:
            self.previously_notified_article_most_recent = 0

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        self.new_message_count += 1
        when = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ').timestamp

        who = re.search('"(.*) \(Confluence\)', msg['From']).group(1)

        if html_message:
            soup = BeautifulSoup(html_message, 'html.parser')
            event_text = soup.find("td", {"id": "header-text-container"}).text
            find = soup.find("td", {"id": "page-title-pattern-header-container"}).find("span").find("a")
            docUrl = find.attrs["href"]
            docUrl = docUrl[:docUrl.find("&src=")]
            space = re.search("display/(.*)/", docUrl).group(1)
            docText = find.text

            excerpt = soup.find("td", {"class": "content-excerpt-pattern-container mobile-resize-text "}).text.strip()

            self.confluence_notifications[when] = {
                 "doc_url": docUrl,
                 "who": who,
                 "space": space,
                 "doc_text": docText,
                 "event": event_text,
                 "excerpt": excerpt
            }

            return True

        return False

    def rewrite_rollup_emails(self, rollup_inbox_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if self.previously_notified_article_count == len(self.confluence_notifications):
            return

        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Rollup again.
        if has_previous_message == False:
            if self.previously_notified_article_count > 0:
                self.most_recently_seen = self.previously_notified_article_most_recent

        templ = """<html><body>{% if not_first_email %}<span>You have previously read notifications up to: {{most_recent_seen_str}}</span>{% endif %}
        <table>
          <tr style="background-color: #acf;">
            <th>Notifications</th>
          </tr>
        {% for when, notif in notifsToPrint|dictsort(false, by='key')|reverse %}{% if notif['line_here'] %}          <tr><td colspan="2" style="border-bottom: 1pt solid red; border-top: 1pt solid red;"><center>^ New Notifications Since You Last Checked ^</center></td></tr>{% endif %}          <tr style="{{loop.cycle('','background-color: #def;')}}">
            <td>
              <a href="{{notif['doc_url']}}">{{notif['doc_text'].replace('\n','<br/>')}}</a><br/>
              {{notif['excerpt'].replace('\n','<br/>')}}
            </td>
          </tr>{% endfor %}
        </table></body></html>""".replace("\n        ","\n")

        template = Template(templ)

        cnt = 0
        for when in sorted(self.confluence_notifications.iterkeys(), reverse=True):
            cnt = cnt + 1
            if cnt > 30:  # only show thirty
                self.confluence_notifications.pop(when, None)

        num_messages_since_last_seen = self.add_line_for_notifications_seen_already()

        seen_formated = arrow.get(self.most_recently_seen).to("local").format("MMM DD YYYY hh:mm A")
        email_html = template.render(notifsToPrint=self.confluence_notifications,
                             most_recent_seen=self.most_recently_seen,
                             most_recent_seen_str=seen_formated, not_first_email=(self.most_recently_seen > 0))

        # Delete previous email, and write replacement
        if has_previous_message:
            rollup_inbox_proxy.delete_previous_message()
        rollup_inbox_proxy.append(self.make_new_raw_email(email_html, num_messages_since_last_seen, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("confluence-notifications", self.confluence_notifications)
        self.store_writer.store_as_binary("most-recently-seen", self.most_recently_seen)


    def add_line_for_notifications_seen_already(self):
        num_messages_since_last_seen = 0
        line_here_done = False
        for ts0, notif in sorted(self.confluence_notifications.iteritems(), reverse=False):
            if self.most_recently_seen != 0 and ts0 >= self.most_recently_seen and line_here_done == False:
                notif['line_here'] = True
                line_here_done = True
                num_messages_since_last_seen = num_messages_since_last_seen +1
        if self.most_recently_seen == 0:
            num_messages_since_last_seen = len(self.confluence_notifications)

        return num_messages_since_last_seen

    def matching_incoming_headers(self):
        return ["From: .* <confluence@apache.org>"]

    def matching_rollup_subject(self):
        return 'Confluence Notif. Rollup'

    def print_summary(self):
        print "Confluence: New Confluence notifications: " + str(self.new_message_count)

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

    def make_new_raw_email(self, email_html, count, sender_to_implicate):
        new_message = 'Subject: ' + self.matching_rollup_subject() + ": " + str(count) + ' new notification(s)\n'
        new_message += 'From: ' + sender_to_implicate + '\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n'
        new_message += 'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"\n'
        new_message += 'MIME-Version: 1.0\n'
        new_message += 'This is a multi-part message in MIME format.\n'
        new_message += '-----NOTIFICATION_BOUNDARY\nContent-Type: text/html; charset="utf-8"\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n\n\n'
        new_message += email_html.replace("\n\n\n", "\n").replace("\n\n", "\n").encode('utf-8', 'replace')
        new_message += '\n\n-----NOTIFICATION_BOUNDARY'

        return new_message
