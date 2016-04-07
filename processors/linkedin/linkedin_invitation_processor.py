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

class LinkedinInvitationProcessor(BaseNotificationProcessor):
    def __init__(self, store_writer):
        self.store_writer = store_writer
        self.new_message_count = 0
        self.new_articles = 0
        self.linkedin_invitations = self.store_writer.get_from_binary("linkedin-invitations")
        if self.linkedin_invitations is None:
            self.linkedin_invitations = {}

        self.most_recently_seen = self.store_writer.get_from_binary("most-recently-seen")
        if self.most_recently_seen is None:
            self.most_recently_seen = 0

        self.new_notifications = {}

        self.previously_notified_article_count = len(self.linkedin_invitations)
        if self.previously_notified_article_count > 0:
            self.previously_notified_article_most_recent = max(self.linkedin_invitations)
        else:
            self.previously_notified_article_most_recent = 0

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        self.new_message_count += 1
        when = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ').timestamp

        who = re.search('\nView (.*)\'s profile:', text_message).group(1)
        spiel = text_message[:text_message.find('\r\nAccept:')].replace("\r\n\r\n","\r\n").replace("\r\n","\n")
        accept_url = "https://" + re.search('\nAccept: https://(.*)\r\n', text_message).group(1)
        profile_url = "https://" + re.search('\nView ' + who + '\'s profile: https://(.*)\r\n', text_message).group(1)

        src = "x"
        if html_message:
            soup = BeautifulSoup(html_message, 'html.parser')
            headshot_img = soup.find("img", {"alt": who})
            if headshot_img:
                src_ = headshot_img['src']
                src = src_
            else:
                src = "https://upload.wikimedia.org/wikipedia/commons/8/85/Border_collie.jpg"

            self.linkedin_invitations[when] = {
                 "img_src": src,
                 "who": who,
                 "spiel": spiel,
                 "accept_url": accept_url,
                 "profile_url": profile_url
            }

            return True

        return False

    def rewrite_rollup_emails(self, rollup_inbox_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if self.previously_notified_article_count == len(self.linkedin_invitations):
            return

        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Rollup again.
        if has_previous_message == False:
            if self.previously_notified_article_count > 0:
                self.most_recently_seen = self.previously_notified_article_most_recent

        templ = """<html><body>{% if not_first_email %}<span>You have previously read invitations up to: {{most_recent_seen_str}}</span>{% endif %}
        <table>
          <tr style="background-color: #acf;">
            <th colspan="2">Who &plus; spiel &plus; actions</th>
          </tr>
{% for when, inv in invsToPrint|dictsort(false, by='key')|reverse %}{% if inv['line_here'] %}          <tr><td colspan="2" style="border-bottom: 1pt solid red; border-top: 1pt solid red;"><center>^ New Invitations Since You Last Checked ^</center></td></tr>{% endif %}          <tr style="{{loop.cycle('','background-color: #def;')}}">
            <td><img style="max-width:100px;height:auto" src="{{ inv['img_src']}}"/></td>
            <td>
              <strong>{{inv['who']}}</strong><br>
              {{inv['spiel'].replace('\n','<br/>\n')}}<br>
              <a href="{{inv['accept_url']}}">Accept Invitation</a>
              <a href="{{inv['profile_url']}}">View Profile</a>
            </td>
          </tr>{% endfor %}
        </table></body></html>""".replace("\n        ","\n")

        template = Template(templ)

        cnt = 0
        for when in sorted(self.linkedin_invitations.iterkeys(), reverse=True):
            cnt = cnt + 1
            if cnt > 30:  # only show thirty
                self.linkedin_invitations.pop(when, None)

        num_messages_since_last_seen = self.add_line_for_invitations_seen_already()

        seen_formated = arrow.get(self.most_recently_seen).to("local").format("MMM DD YYYY hh:mm A")
        email_html = template.render(invsToPrint=self.linkedin_invitations,
                             most_recent_seen=self.most_recently_seen,
                             most_recent_seen_str=seen_formated, not_first_email=(self.most_recently_seen > 0))

        # Delete previous email, and write replacement
        if has_previous_message:
            rollup_inbox_proxy.delete_previous_message()
        rollup_inbox_proxy.append(self.make_new_raw_li_email(email_html, num_messages_since_last_seen, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("linkedin-invitations", self.linkedin_invitations)
        self.store_writer.store_as_binary("most-recently-seen", self.most_recently_seen)


    def add_line_for_invitations_seen_already(self):
        num_messages_since_last_seen = 0
        line_here_done = False
        for ts0, inv in sorted(self.linkedin_invitations.iteritems(), reverse=False):
            if self.most_recently_seen != 0 and ts0 >= self.most_recently_seen and line_here_done == False:
                inv['line_here'] = True
                line_here_done = True
                num_messages_since_last_seen = num_messages_since_last_seen +1
        if self.most_recently_seen == 0:
            num_messages_since_last_seen = len(self.linkedin_invitations)

        return num_messages_since_last_seen

    def matching_incoming_headers(self):
        return ["From: .* <invitations@linkedin.com>"]

    def matching_rollup_subject(self):
        return 'Linkedin Inv. Rollup'

    def print_summary(self):
        print "Linkedin: New Linkedin invitations: " + str(self.new_message_count)

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

    def make_new_raw_li_email(self, email_html, count, sender_to_implicate):
        new_message = 'Subject: ' + self.matching_rollup_subject() + ": " + str(count) + ' new invitation(s)\n'
        new_message += 'From: ' + sender_to_implicate + '\n'
        new_message += 'Content-Transfer-Encoding: 7bit\n'
        new_message += 'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"\n'
        new_message += 'MIME-Version: 1.0\n'
        new_message += 'This is a multi-part message in MIME format.\n'
        new_message += '-----NOTIFICATION_BOUNDARY\nContent-Type: text/html; charset="utf-7"\n'
        new_message += 'Content-Transfer-Encoding: 7bit\n\n\n'
        new_message += email_html.replace("\n\n\n", "\n").replace("\n\n", "\n").encode('utf-7', 'replace')
        new_message += '\n\n-----NOTIFICATION_BOUNDARY'

        return new_message.replace("\n", "\r\n")
