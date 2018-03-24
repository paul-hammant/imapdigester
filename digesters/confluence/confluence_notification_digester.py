# coding=utf-8


import re
from email.header import decode_header
import arrow
import simplejson
from bs4 import BeautifulSoup
from jinja2 import Template
from collections import Counter

from digesters.base_digester import BaseDigester


class ConfluenceNotificationDigester(BaseDigester):
    def __init__(self, store_writer, from_email_address, confluence_short_name):
        super(ConfluenceNotificationDigester, self).__init__()
        self.confluence_short_name = confluence_short_name
        self.from_email_address = from_email_address
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

        from_ = msg['From']
        if from_.startswith("=?"):
            from_, encoding = decode_header(from_)[0]
        who = re.search('(.*) \(Confluence\)', from_).group(1).replace('"','')

        try:
            if html_message:
                soup = BeautifulSoup(html_message, 'html.parser')
                # print "soup:" + str(soup.prettify())
                event_text = soup.find("td", {"id": "header-text-container"}).text
                doc_elem = soup.find("td", {"id": "page-title-pattern-header-container"}).find("span").find("a")
                doc_url = doc_elem.attrs["href"]
                doc_url = doc_url[:doc_url.find("&")]
                if "#" in doc_url:
                    doc_url = doc_url[:doc_url.find("#")]

                anchors =  soup.findAll("a")
                space = "UNKNOWN"
                for anchor in anchors:
                    if "href" in anchor.attrs:
                        href_ = anchor.attrs["href"]
                        if "spaceKey=" in href_:
                            space = re.search('spaceKey=(.*)', href_).group(1)
                            if "&" in space:
                                space = space[:space.index("&")]

                doc_text = str(doc_elem.text)

                if "edited a page" in event_text:
                    if "?" in doc_url:
                        doc_url = doc_url[:doc_url.find("?")]
                    added = len(soup.findAll("span", {"class", "diff-html-added"}))
                    added += len(soup.findAll("span", {"class", "x_diff-html-added"}))
                    removed = len(soup.findAll("span", {"class", "diff-html-removed"}))
                    removed += len(soup.findAll("span", {"class", "x_diff-html-removed"}))
                    changed = len(soup.findAll("span", {"class", "diff-html-changed"}))
                    changed += len(soup.findAll("span", {"class", "x_diff-html-changed"}))
                    excerpt = "Page nodes added: " + str(added) \
                                                   + ", removed: " + str(removed) \
                                                   + ", changed: " + str(changed)
                elif "created a page" in event_text:
                    contents = soup.find("td", {"class": "email-content-main mobile-expand"})
                    words_in_new_page = Counter(contents.text).elements()
                    excerpt = "Page added with " + str(len(list(words_in_new_page))) + " words."
                else:
                    blurb = str(soup.find("table", {"class": "content-excerpt-pattern"}).text.strip())
                    excerpt = blurb[:55].strip()
                    if len(excerpt) > 55:
                        excerpt += "..."


                self.confluence_notifications[when] = {
                     "doc_url": doc_url,
                     "who": who,
                     "space": space,
                     "doc_text": doc_text,
                     "event": event_text,
                     "excerpt": excerpt
                }

                # print simplejson.dumps(self.confluence_notifications[when], sort_keys=True) + "\n\n"

                return True
        except AttributeError:
            print("AttributeError processing confluence message")
            pass

        return False

    def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if self.previously_notified_article_count == len(self.confluence_notifications):
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
              What: {{notif['event']}}<br/>
              Space: {{notif['space']}}:<br/>
              Page: <a href="{{notif['doc_url']}}">{{notif['doc_text'].replace('\n','<br/>')}}</a><br/>
              Excerpt: {{notif['excerpt'].replace('\n','<br/>')}}
            </td>
          </tr>{% endfor %}
        </table></body></html>""".replace("\n        ", "\n")

        template = Template(templ)

        cnt = 0
        for when in sorted(iter(self.confluence_notifications.keys()), reverse=True):
            cnt += 1
            if 90 < cnt:  # only show thirty
                self.confluence_notifications.pop(when, None)

        num_messages_since_last_seen = self.add_line_for_notifications_seen_already()

        seen_formated = arrow.get(self.most_recently_seen).to("local").format("MMM DD YYYY hh:mm A")
        email_html = template.render(notifs_to_print=self.confluence_notifications,
                             most_recent_seen= self.most_recently_seen,
                             most_recent_seen_str= seen_formated, not_first_email=(self.most_recently_seen > 0))

        # Delete previous email, and write replacement
        if has_previous_message:
            digest_folder_proxy.delete_previous_message()
        digest_folder_proxy.append(self.make_new_raw_email(email_html,
                                                           num_messages_since_last_seen, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("confluence-notifications", self.confluence_notifications)
        self.store_writer.store_as_binary("most-recently-seen", self.most_recently_seen)

    def add_line_for_notifications_seen_already(self):
        num_messages_since_last_seen = 0
        line_here_done = False
        for ts0, notif in sorted(iter(self.confluence_notifications.items()), reverse=False):
            if self.most_recently_seen != 0 and ts0 >= self.most_recently_seen and line_here_done is False:
                notif['line_here'] = True
                line_here_done = True
                num_messages_since_last_seen += 1
        if self.most_recently_seen == 0:
            num_messages_since_last_seen = len(self.confluence_notifications)

        return num_messages_since_last_seen

    def matching_incoming_headers(self):
        return ["From: .* <" + self.from_email_address + ">"]

    def matching_digest_subject(self):
        return  'Notification Digest'

    def matching_digest_sender(self):
        return self.confluence_short_name + " Confluence"

    def print_summary(self):
        print("Confluence: New Confluence notifications: " + str(self.new_message_count))

    def make_new_raw_email(self, email_html, count, sender_to_implicate):

        email_ascii = email_html.replace("\n\n\n", "\n").replace("\n\n", "\n").encode('utf-8', 'replace')

        # Ugly hack
        email_ascii = "".join(i for i in email_ascii if ord(i) < 128)


        new_message = 'Subject: ' + self.matching_digest_subject() + ": " + str(count) + ' new notification(s)\n'
        new_message += 'From: "' + self.matching_digest_sender() + '" <' + sender_to_implicate + '>\n'
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
