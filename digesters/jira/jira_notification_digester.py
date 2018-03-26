# coding=utf-8


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

            key_vals = []

            kvtable_elem = soup.find("table", {"class": "keyvalue-table"})
            if kvtable_elem:
                kvtable = kvtable_elem.text.strip()\
                    .replace(":\n", ":")\
                    .replace("\n\n\n", "\n")
                if "Reporter:" in kvtable:
                    kvtable = kvtable[:kvtable.index("Reporter:")].strip()

                for kv in kvtable.split("\n"):
                    k_and_v = kv.split(":")
                    if len(k_and_v) > 1:
                        key_vals.append({ "k" : k_and_v[0].strip(), "v" : k_and_v[1].strip() })

            project_td = soup.find("td", {"class": "page-title-pattern-first-line"})
            if project_td:
                project_td_anchors = project_td.find_all("a")
                project_name = project_td_anchors[0].text
                issue_url = project_td_anchors[2].attrs["href"]
                issue_id = project_td_anchors[2].text.strip()
            else:
                header_td = soup.find("td", {"id": "header-text-container"})
                header_td_anchors = header_td.find_all("a")
                project_name = "unknown"
                issue_url = header_td_anchors[1].attrs["href"]
                issue_id = header_td_anchors[1].text.strip()

            comment = None
            comment_td = soup.find("td", {"class": "text-paragraph-pattern-container"})
            if comment_td:
                raw_comment = comment_td.text.strip()
                comment = raw_comment[:55].strip()
                if len(raw_comment) > 55:
                    comment += "..."

            ##
            self.jira_notifications[when] = {
                 "project_name": project_name,
                 "who": who,
                 "issue_id": issue_id,
                 "issue_url": issue_url,
                 "event": event_text,
                 "kvtable" : key_vals,
                 "comment" : comment
            }

            # print simplejson.dumps(self.jira_notifications[when], sort_keys=True) + "\n\n"

            return True
        else:
            print("Was expecting HTML for \"" + msg['Subject'] + "\" - not processing")

        return False

    def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if self.previously_notified_article_count == len(self.jira_notifications):
            return

        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Digest again.
        if not has_previous_message:
            if self.previously_notified_article_count > 0:
                self.most_recently_seen = self.previously_notified_article_most_recent

        templ = """<html><body>{% if not_first_email %}<span>You have previously read notifications up to: {{most_recent_seen_str}}</span>{% endif %}
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
                    {% if notif['kvtable']|length > 0 %}
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
                    {% endif %}
                    {% if notif['comment'] %}
                    <tr>
                        <td>Comment:</td>
                        <td>
                            {{notif['comment'].replace('\\n','<br/>')}}
                        </td>
                    </tr>
                    {% endif %}
                </table>
            </td>
          </tr>{% endfor %}
        </table></body></html>""".replace("\n        ", "\n")

        template = Template(templ)

        cnt = 0
        for when in sorted(iter(self.jira_notifications.keys()), reverse=True):
            cnt += 1
            if 90 < cnt:  # only show thirty
                self.jira_notifications.pop(when, None)

        num_messages_since_last_seen = self.add_line_for_notifications_seen_already()

        seen_formated = arrow.get(self.most_recently_seen).to("local").format("MMM DD YYYY hh:mm A")
        email_html = template.render(notifs_to_print=self.jira_notifications,
                             most_recent_seen= self.most_recently_seen,
                             most_recent_seen_str= seen_formated, not_first_email=(self.most_recently_seen > 0))

        email_html = self.remove_lines_that_are_fully_whitespace(email_html)

        # Delete previous email, and write replacement
        if has_previous_message:
            digest_folder_proxy.delete_previous_message()
        digest_folder_proxy.append(self.make_new_raw_email(email_html,
                                                           num_messages_since_last_seen, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("jira-notifications", self.jira_notifications)
        self.store_writer.store_as_binary("most-recently-seen", self.most_recently_seen)

    def add_line_for_notifications_seen_already(self):
        num_messages_since_last_seen = 0
        line_here_done = False
        for ts0, notif in sorted(iter(self.jira_notifications.items()), reverse=False):
            if self.most_recently_seen != 0 and ts0 >= self.most_recently_seen and line_here_done is False:
                notif['line_here'] = True
                line_here_done = True
                num_messages_since_last_seen += 1
        if self.most_recently_seen == 0:
            num_messages_since_last_seen = len(self.jira_notifications)

        return num_messages_since_last_seen

    def matching_incoming_headers(self):
        return ["From: .* <" + self.from_email_address + ">"]

    def matching_digest_subject(self):
        return 'Notification Digest'

    def matching_digest_sender(self):
        return self.jira_short_name + " JIRA"

    def print_summary(self):
        print("Jira: New JIRA notifications: " + str(self.new_message_count))

    def make_new_raw_email(self, email_html, count, sender_to_implicate):

        new_message = 'Subject: ' + self.matching_digest_subject() + ": " + str(count) + ' new notification(s)\n'
        new_message += 'From: \"' + self.jira_short_name + ' JIRA\" <' + sender_to_implicate + '>\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n'
        new_message += 'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY' \
                       + self.notification_boundary_rand + '"\n'
        new_message += 'MIME-Version: 1.0\n'
        new_message += 'This is a multi-part message in MIME format.\n'
        new_message += '-----NOTIFICATION_BOUNDARY' + self.notification_boundary_rand \
                       + '\nContent-Type: text/html; charset="utf-8"\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n\n\n'
        new_message += email_html.replace("\n\n\n", "\n").replace("\n\n", "\n")
        new_message += '\n\n-----NOTIFICATION_BOUNDARY' + self.notification_boundary_rand

        return new_message
