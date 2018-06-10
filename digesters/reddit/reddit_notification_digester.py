import html

import arrow
from bs4 import BeautifulSoup
from jinja2 import Template

from digesters.base_digester import BaseDigester


class RedditNotificationDigester(BaseDigester):
    def __init__(self, store_writer, userId):
        super(RedditNotificationDigester, self).__init__()
        self.store_writer = store_writer
        self.userId = userId
        self.new_message_count = 0
        self.new_articles = 0
        self.reddit_notifications = self.store_writer.get_from_binary("reddit-notifications")
        if self.reddit_notifications is None:
            self.reddit_notifications = {}

        self.most_recently_seen = self.store_writer.get_from_binary("reddit-recently-seen")
        if self.most_recently_seen is None:
            self.most_recently_seen = 0

        self.new_notifications = {}

        self.previously_notified_article_count = len(self.reddit_notifications)
        if self.previously_notified_article_count > 0:
            self.previously_notified_article_most_recent = max(self.reddit_notifications)
        else:
            self.previously_notified_article_most_recent = 0

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        unescapedHtml = html.unescape(html_message.decode("UTF-8"))
        unescapedHtml = unescapedHtml.replace('<!-- Main -->', '<div id="mmain"><div class="mmessage">')
        unescapedHtml = unescapedHtml.replace('<!-- Separator -->', '</div>')
        unescapedHtml = unescapedHtml.replace('<!-- END Main -->', '</div>')
        unescapedHtml = unescapedHtml.replace('<!-- Button -->', '</div>')
        unescapedHtml = unescapedHtml.replace('<!-- END Separator -->', '<div class="mmessage">')
        unescapedHtml = unescapedHtml.replace('<hr>', '<hr/>')
        soup = BeautifulSoup(unescapedHtml, 'html.parser')
        forr = soup.find("strong", attrs = {"class": "call-to-action"}).text.split(" for u/")[1]

        if (forr != self.userId):
            return False

        self.new_message_count += 1
        whenStr = arrow.get(msg['Date'].split(',', 1)[1].strip(), 'D MMM YYYY HH:mm:ss ZZ')
        when = whenStr.timestamp

        anchors = soup.findAll("a")
        for anchor in anchors:
            href_ = anchor["href"]
            if anchor.text == "a thread":
                newtag = soup.new_tag("span")
                newtag.string = " a Thread "
                anchor.insert_before(newtag)
                anchor.decompose()
            elif "/comments/" in href_:
                newtag = soup.new_tag("div")
                endIx = href_.find("/?context=")
                endIx = href_[0:endIx].rfind("/")
                newtag.string = " on " + href_[href_.find("/r/"):endIx] + " "
                anchor.wrap(newtag)

        mmain = soup.find("div", attrs={"id": "mmain"})
        messagesHtml = str(BeautifulSoup(mmain.decode_contents(), 'html.parser'))

        messagesHtml = messagesHtml[0: messagesHtml.rfind("<!-- Button -->")]

        messages =  BeautifulSoup(messagesHtml, 'html.parser').findAll("div",  attrs = {"class": "mmessage"})
        for ctr, message in enumerate(messages):
            messageHtml = str(message)
            if len(messageHtml) > len('<div class="mmessage">\\n</div>'):
                self.reddit_notifications[when + ctr/10] = {
                    "message": messageHtml
                }

        return True

    def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if self.previously_notified_article_count == len(self.reddit_notifications):
            return

        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Digest again.
        if has_previous_message == False:
            if self.previously_notified_article_count > 0:
                self.most_recently_seen = self.previously_notified_article_most_recent

        templ = """<html><body>{% if not_first_email %}<span>You have previously messages up to: {{most_recent_seen_str}}</span>{% endif %}
                <table>
                  <tr style="background-color: #acf;">
                    <th colspan="2">Messages</th>
                  </tr>
        {% for when, message in notificationsToPrint|dictsort(false, by='key')|reverse %}{% if message['line_here'] %}          <!--1--><tr><td colspan="2" style="border-bottom: 1pt solid 
        red; 
        border-top: 1pt solid 
        red;"><center>^ New Messages Since You Last Checked ^</center></td></tr><!--cl1-->{% endif %}          <!--2--><tr style="{{loop.cycle('','background-color: #def;')}}">
                    <td></td>
                    <td>                      
                      {{message['message']}}
                    </td>
                  </tr><!--cl2-->{% endfor %}
                </table></body></html>""".replace("\n        ", "\n")

        template = Template(templ)

        cnt = 0
        for when in sorted(iter(self.reddit_notifications.keys()), reverse=True):
            cnt = cnt + 1
            if cnt > 30:  # only show thirty
                self.reddit_notifications.pop(when, None)

        num_messages_since_last_seen = self.add_line_for_messages_seen_already()

        seen_formated = arrow.get(self.most_recently_seen).to("local").format("MMM DD YYYY hh:mm A")
        email_html = template.render(notificationsToPrint = self.reddit_notifications,
                                     most_recent_seen=self.most_recently_seen,
                                     most_recent_seen_str=seen_formated,
                                     not_first_email=(self.most_recently_seen > 0))

        # Delete previous email, and write replacement
        if has_previous_message:
            digest_folder_proxy.delete_previous_message()
        digest_folder_proxy.append(self.make_new_raw_email(email_html, num_messages_since_last_seen, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("reddit-notifications", self.reddit_notifications)
        self.store_writer.store_as_binary("reddit-recently-seen", self.most_recently_seen)

    def add_line_for_messages_seen_already(self):
        num_messages_since_last_seen = 0
        line_here_done = False
        for ts0, messages in sorted(iter(self.reddit_notifications.items()), reverse=False):
            if self.most_recently_seen != 0 and ts0 >= self.most_recently_seen and line_here_done == False:
                messages['line_here'] = True
                line_here_done = True
                num_messages_since_last_seen = num_messages_since_last_seen +1
        if self.most_recently_seen == 0:
            num_messages_since_last_seen = len(self.reddit_notifications)

        return num_messages_since_last_seen


    def matching_incoming_headers(self):
        return ["From: Reddit &lt;notifications@redditmail.com&gt;",
                "Subject: [reddit] .* u/" + self.userId]

    def matching_digest_subject(self):
        return  self.userId + ': Reddit Messages Digest'

    def matching_digest_sender(self):
        return "Reddit"

    def print_summary(self):
        print("New " + self.userId + " notifications: " + str(self.new_message_count))

    def make_new_raw_email(self, email_html, count, sender_to_implicate):
        new_message = 'Subject: ' + self.matching_digest_subject() + ": " + str(count) + ' new notifications(s)\n'
        new_message += 'From: \"' + self.matching_digest_sender() + '\" <' + sender_to_implicate + '>\n'
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
