# coding=utf-8
from __future__ import unicode_literals

import re

import arrow
from bs4 import BeautifulSoup
from jinja2 import Template

from digesters.base_digester import BaseDigester


class LinkedinInvitationDigester(BaseDigester):
    def __init__(self, store_writer):
        super(LinkedinInvitationDigester, self).__init__()
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

        text_message = text_message.replace("\r\n", "\n")

        if msg["Subject"].endswith("invitation is waiting for your response") or \
            msg["Subject"].endswith("connections, experience, and more"):
            # No need to be reminded, bugged.
            return True

        self.new_message_count += 1
        when = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ').timestamp

        fromm = re.search('(.*) <invitations@linkedin.com>', msg["From"])
        if fromm is not None:
            who = fromm.group(1)
            spiel = text_message[:text_message.find('\nAccept:')].replace("\n\n","\n")
            accept_url = "https://" + re.search('\nAccept: https://(.*)\n', text_message).group(1)
            profile_url = "https://" + re.search('\nView profile: https://(.*)\n', text_message).group(1)

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

    def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if self.previously_notified_article_count == len(self.linkedin_invitations):
            return

        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Digest again.
        if has_previous_message == False:
            if self.previously_notified_article_count > 0:
                self.most_recently_seen = self.previously_notified_article_most_recent

        templ = """<html><body>{% if not_first_email %}<span>You have previously read invitations up to: {{most_recent_seen_str}}</span>{% endif %}
        <table>
          <tr style="background-color: #acf;">
            <th colspan="2">Invitations</th>
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
            digest_folder_proxy.delete_previous_message()
        digest_folder_proxy.append(self.make_new_raw_email(email_html, num_messages_since_last_seen, sender_to_implicate))
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
        return ["From: .* <invitations@linkedin.com>",  ## The invitation
                "From: .* <messages-noreply@linkedin.com>"]  ## Foo's invitation is waiting for your response ?

    def matching_digest_subject(self):
        return 'Invitation Digest'

    def matching_digest_sender(self):
        return "Linkedin"

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

    def make_new_raw_email(self, email_html, count, sender_to_implicate):
        new_message = 'Subject: ' + self.matching_digest_subject() + ": " + str(count) + ' new invitation(s)\n'
        new_message += 'From: \"' + self.matching_digest_sender() + '\" <' + sender_to_implicate + '>\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n'
        new_message += 'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY' \
                       + self.notification_boundary_rand + '"\n'
        new_message += 'MIME-Version: 1.0\n'
        new_message += 'This is a multi-part message in MIME format.\n'
        new_message += '-----NOTIFICATION_BOUNDARY' + self.notification_boundary_rand \
                       + '\nContent-Type: text/html; charset="utf-8"\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n\n\n'
        email_ascii = email_html.replace("\n\n\n", "\n").replace("\n\n", "\n").encode('utf-8', 'replace')
        # Ugly hack
        email_ascii = "".join(i for i in email_ascii if ord(i) < 128)
        new_message += email_ascii
        new_message += '\n\n-----NOTIFICATION_BOUNDARY' + self.notification_boundary_rand

        return new_message
