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

class LinkedinInvitationsProcessor(BaseNotificationProcessor):
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
        subject = msg['Subject']
        # if "sent you a 1-1 message" in subject:
        #     room = "Direct Message"
        # else:
        #     room = "Room: " + subject.split('"')[1]
        when = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ').timestamp

#>>>Hi Paul,
#I'd like to join your LinkedIn network.
#
#Steven Footle
#Principal Test Architect and Agile Leader - Certified ScrumMaster
#
#Accept: https://www.linkedin.com/comm/people/invite-accept?mboxid=I6122153781204434944_500&sharedKey=-aWVMgrZ&fr=false&invitationId=6122153757049446400&fe=true&trk=eml-comm_invm-b-accept-newinvite&midToken=AQHQ1w5V4ws4wA&trkEmail=eml-M2M_Invitation-null-5-null-null-1b3p5%7Eimjp489e%7Ejk
#
#View Steven Footle's profile: https://www.linkedin.com/comm/profile/view?id=AAsAAAAIW1gBCVPJFcvlZjm6AtEfNiLTNya_HqA&authType=name&authToken=F40O&invAcpt=2197625_I6122153781204434944_500&midToken=AQHQ1w5V4ws4wA&trk=eml-M2M_Invitation-hero-1-text%7Eprofile&trkEmail=eml-M2M_Invitation-hero-1-text%7Eprofile-null-1b3p5%7Eimjp489e%7Ejk



        #print ">0>>" + text_message.strip() + "<0<0<"

        who = re.search('\nView (.*)\'s profile:', text_message).group(1)
        spiel = text_message[:text_message.find('\r\nAccept:')].replace("\r\n\r\n","\r\n").replace("\r\n","\n")
        accept_url = "https://" + re.search('\nAccept: https://(.*)\r\n', text_message).group(1)
        profile_url = "https://" + re.search('\nView ' + who + '\'s profile: https://(.*)\r\n', text_message).group(1)

        # print "who =" + who + "<<"
        # print "accept_url =" + accept_url + "<<"
        # print "profile_url =" + profile_url + "<<\n\n"


        if html_message:
            soup = BeautifulSoup(html_message, 'html.parser')
            src = soup.find("img", {"alt": who})['src']

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

        templ = """{% if not_first_email %}<span>You have previously read invitations up to: {{most_recent_seen_str}}</span>{% endif %}
        <table>
          <tr style="background-color: #acf;">
            <th>When/who/spiel</th>
          </tr>
{% for when, inv in invsToPrint|dictsort(false, by='key')|reverse %}{% if inv['line_here'] %}          <tr><td colspan="2" style="border-bottom: 1pt solid red; border-top: 1pt solid red;"><center>^ New Invitations Since You Last Checked ^</center></td></tr>{% endif %}          <tr style="{{loop.cycle('','background-color: #def;')}}">
            <td><ing src="{{ inv['img_src']}}"/></td>
            <td>
              <strong>{{inv['who']}}</strong><br>
              {{inv['spiel']}}<br>
              <a href="{{inv['accept_url']}}">Accept Invitation</a>
              <a href="{{inv['profile_url']}}">View Profile</a>
            </td>
          </tr>{% endfor %}
        </table>""".replace("\n        ","\n")

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
        rollup_inbox_proxy.append(self.make_new_raw_so_email(email_html, num_messages_since_last_seen, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("linkedin-invitations", self.linkedin_invitations)
        self.store_writer.store_as_binary("most-recently-seen", self.most_recently_seen)


    def add_line_for_invitations_seen_already(self):
        num_messages_since_last_seen = 0
        line_here_done = False
        mostRecentNotification = None
        for ts0, inv in sorted(self.linkedin_invitations.iteritems(), reverse=False):
            mostRecentNotification = inv
            if ts0 >= self.most_recently_seen and line_here_done == False:
                inv['line_here'] = True
                line_here_done = True
                num_messages_since_last_seen = num_messages_since_last_seen +1

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

    def make_new_raw_so_email(self, email_html, count, sender_to_implicate):
        new_message = 'Subject: ' + self.matching_rollup_subject() + ": " + str(count) + ' new invitation(s)\n'
        new_message += 'From: ' + sender_to_implicate + '\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n'
        new_message += 'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"\n'
        new_message += 'MIME-Version: 1.0\n'
        new_message += 'This is a multi-part message in MIME format.\n'
        new_message += '-----NOTIFICATION_BOUNDARY\nContent-Type: text/html; charset="utf-7"\n'
        new_message += 'Content-Transfer-Encoding: utf-7\n\n'
        new_message += email_html.replace("\n\n\n", "\n").replace("\n\n", "\n").encode('utf-7', 'replace')
        return new_message
