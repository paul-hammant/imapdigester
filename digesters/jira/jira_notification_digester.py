# coding=utf-8
from __future__ import unicode_literals

import os
import re
from email.header import decode_header
import arrow
import simplejson
from bs4 import BeautifulSoup
from jinja2 import Template
from collections import Counter

from digesters.base_digester import BaseDigester


class JiraNotificationDigester(BaseDigester):
    def __init__(self, store_writer, from_email_address, jira_short_name):
        super(JiraNotificationDigester, self).__init__()
        self.jira_short_name = jira_short_name
        self.from_email_address = from_email_address
        self.store_writer = store_writer
        self.new_message_count = 0
        self.new_articles = 0
        self.jira_notifications = self.store_writer.get_from_binary("jira-notifications")
        if self.jira_notifications is None:
            self.jira_notifications = {}

        self.most_recently_seen = self.store_writer.get_from_binary("most-recently-seen")
        if self.most_recently_seen is None:
            self.most_recently_seen = 0

        self.new_notifications = {}

        self.previously_notified_article_count = len(self.jira_notifications)
        if self.previously_notified_article_count > 0:
            self.previously_notified_article_most_recent = max(self.jira_notifications)
        else:
            self.previously_notified_article_most_recent = 0

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        self.new_message_count += 1
        when = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ').timestamp

        from_ = msg['From']
        if from_.startswith("=?"):
            from_, encoding = decode_header(from_)[0]
        who = re.search('(.*) \(JIRA\)', from_).group(1).replace('"','')

        if html_message:
            soup = BeautifulSoup(html_message, 'html.parser')

            event_text = soup.find("td", {"id": "header-text-container"}).text.strip()
            kvtable = soup.find("table", {"class": "keyvalue-table"}).text.strip()\
                .replace(":\n", ":")\
                .replace("\n\n\n", "\n")
            kvtable = kvtable[:kvtable.index("Reporter:")].strip()

            key_vals = []
            for kv in kvtable.split("\n"):
                k_and_v = kv.split(":")
                key_vals.append({ "k" : k_and_v[0].strip(), "v" : k_and_v[1].strip() })

            project_td_anchors = soup.find("td", {"class": "page-title-pattern-first-line"}).find_all("a")
            project_name = project_td_anchors[0].text
            issue_url = project_td_anchors[2].attrs["href"]
            issue_id = project_td_anchors[2].text.strip()

            self.jira_notifications[when] = {
                 "project_name": project_name,
                 "who": who,
                 "issue_id": issue_id,
                 "issue_url": issue_url,
                 "event": event_text,
                 "kvtable" : key_vals

            }

            # print simplejson.dumps(self.jira_notifications[when], sort_keys=True) + "\n\n"

            return True

        return False

    def rewrite_rollup_emails(self, rollup_inbox_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if self.previously_notified_article_count == len(self.jira_notifications):
            return

        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Rollup again.
        if not has_previous_message:
            if self.previously_notified_article_count > 0:
                self.most_recently_seen = self.previously_notified_article_most_recent

        templ = u"""<html><body>{% if not_first_email %}<span>You have previously read notifications up to: {{most_recent_seen_str}}</span>{% endif %}
        <table>
          <tr style="background-color: #acf;">
            <th>Notifications</th>
          </tr>
        {% for when, notif in notifs_to_print|dictsort(false, by='key')|reverse %}{% if notif['line_here'] %}          <tr><td colspan="2" style="border-bottom: 1pt solid red; border-top: 1pt solid red;"><center>^ New Notifications Since You Last Checked ^</center></td></tr>{% endif %}          <tr style="{{loop.cycle('','background-color: #def;')}}">
            <td>
                <table>
                    <tr>
                        <td>What:</td><td>{{notif['event']}}</td>
                    </tr>
                    <tr>
                        <td>Project:</td><td>{{notif['project_name']}}</td>
                    </tr>
                    <tr>
                        <td>Issue:</td><td><a href="{{notif['issue_url']}}">{{notif['issue_id']}}</a></td>
                    </tr>
                    <tr>
                        <td>Fields:</td>
                        <td>
                            <table>
                            {% for kv in notif['kvtable'] %}
                            <tr><td>{{kv['k']}}</td><td>{{kv['v']}}</td></tr>
                            {% endfor %}
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
          </tr>{% endfor %}
        </table></body></html>""".replace("\n        ", "\n")

        template = Template(templ)

        cnt = 0
        for when in sorted(self.jira_notifications.iterkeys(), reverse=True):
            cnt += 1
            if 90 < cnt:  # only show thirty
                self.jira_notifications.pop(when, None)

        num_messages_since_last_seen = self.add_line_for_notifications_seen_already()

        seen_formated = arrow.get(self.most_recently_seen).to("local").format("MMM DD YYYY hh:mm A")
        email_html = template.render(notifs_to_print=self.jira_notifications,
                             most_recent_seen= self.most_recently_seen,
                             most_recent_seen_str= seen_formated, not_first_email=(self.most_recently_seen > 0))

        email_html = os.linesep.join([s for s in email_html.splitlines() if s.strip()])

        # Delete previous email, and write replacement
        if has_previous_message:
            rollup_inbox_proxy.delete_previous_message()
        rollup_inbox_proxy.append(self.make_new_raw_email(email_html,
                                                          num_messages_since_last_seen, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("jira-notifications", self.jira_notifications)
        self.store_writer.store_as_binary("most-recently-seen", self.most_recently_seen)

    def add_line_for_notifications_seen_already(self):
        num_messages_since_last_seen = 0
        line_here_done = False
        for ts0, notif in sorted(self.jira_notifications.iteritems(), reverse=False):
            if self.most_recently_seen != 0 and ts0 >= self.most_recently_seen and line_here_done is False:
                notif['line_here'] = True
                line_here_done = True
                num_messages_since_last_seen += 1
        if self.most_recently_seen == 0:
            num_messages_since_last_seen = len(self.jira_notifications)

        return num_messages_since_last_seen

    def matching_incoming_headers(self):
        return ["From: .* <" + self.from_email_address + ">"]

    def matching_rollup_subject(self):
        return self.jira_short_name + ' Jira Notif. Rollup'

    def print_summary(self):
        print "Jira: New Jira notifications: " + str(self.new_message_count)

    def make_new_raw_email(self, email_html, count, sender_to_implicate):

        email_ascii = email_html.replace("\n\n\n", "\n").replace("\n\n", "\n").encode('utf-8', 'replace')

        # Ugly hack
        email_ascii = "".join(i for i in email_ascii if ord(i) < 128)


        new_message = 'Subject: ' + self.matching_rollup_subject() + ": " + str(count) + ' new notification(s)\n'
        new_message += 'From: ' + sender_to_implicate + '\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n'
        new_message += 'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY' \
                       + self.notification_boundary_rand + '"\n'
        new_message += 'MIME-Version: 1.0\n'
        new_message += 'This is a multi-part message in MIME format.\n'
        new_message += '-----NOTIFICATION_BOUNDARY' + self.notification_boundary_rand \
                       + '\nContent-Type: text/html; charset="utf-8"\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n\n\n'
        new_message += email_ascii
        new_message += '\n\n-----NOTIFICATION_BOUNDARY' + self.notification_boundary_rand

        return new_message
