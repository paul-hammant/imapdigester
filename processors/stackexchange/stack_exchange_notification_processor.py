from __future__ import unicode_literals
import base64

from base_notification_processor import BaseNotificationProcessor
from utils import Utils
from bs4 import BeautifulSoup
import re


class StackExchangeNotificationProcessor(BaseNotificationProcessor):
    # Go to http://stackexchange.com/filters to see/setup your filters.

    # Note if you filter on just one tag, this processor will not work
    # (it won't recognize the subject line of the incoming emails)
    # Therefore have AT LEAST TWO - like so http://imgur.com/YswesOB

    def __init__(self, store_writer, filter_name):
        self.store_writer = store_writer
        self.filter_name = filter_name
        self.new_message_count = 0
        self.deleted_articles_count = 0
        self.new_articles = 0
        self.last_stack_exchange_article_list = self.store_writer.get_from_binary("lastStackExchangeArticleList")
        if self.last_stack_exchange_article_list is None:
            self.last_stack_exchange_article_list = ""

        self.article_dict = store_writer.get_from_binary("articles")

        if self.article_dict is None:
            self.article_dict = {}
            self.article_dict["articles"] = {}
            self.article_dict["most_recent_seen"] = 0

        self.previously_notified_article_count = len(self.article_dict["articles"])
        if self.previously_notified_article_count > 0:
            self.previously_notified_article_most_recent = max(self.article_dict["articles"])
        else:
            self.previously_notified_article_most_recent = 0

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        body = Utils.get_decoded_email_body(msg, True)
        self.new_message_count += 1
        self.extract_articles_from_html(body)
        return True

    def extract_articles_from_html(self, html_email):

        soup = BeautifulSoup(html_email, 'html.parser')

        # the first table isn't the one we are interested in
        secondTable = soup.select('table[width=90%]')[1]

        # get rows that are actually article links
        postingTrs = secondTable.select('tbody')[0].find_all('tr', recursive=False)

        # Last in sequence of <tr> is not an link to a article, it's an unsubscribe message
        new_articles = {}
        for x in range(0, len(postingTrs) - 1):
            href_ = postingTrs[x].select('p[class=item-link]')[0].find("a")['href'][7:]
            article_num = re.findall(r'\d+', href_)[0]

            text = postingTrs[x].encode_contents()

            self.article_dict["articles"][article_num] = text

    def rewrite_rollup_emails(self, rollup_inbox_proxy, has_previous_message, previously_seen, sender_to_implicate):

        if self.previously_notified_article_count == len(self.article_dict["articles"]):
            return

        # Deleted email (by the user) means they don't want to see THOSE notifications listed in a Rollup again.
        if has_previous_message == False:
            if self.previously_notified_article_count > 0:
                self.article_dict["most_recent_seen"] = self.previously_notified_article_most_recent

        with open("processors/stackexchange/template.html", "r") as templateFile:
            template = templateFile.read()
        template_end, template_start = self.get_template_start_and_end(template)

        past_bookmark = 0
        unseen = 0
        for anum in sorted(self.article_dict["articles"].iterkeys(), reverse=True):
            mostRecentSeen = self.article_dict["most_recent_seen"]
            if anum < mostRecentSeen:
                past_bookmark += 1
            else:
                unseen += 1
            if past_bookmark > 30:  # only show thirty after the bookmark
                self.article_dict["articles"].pop(anum, None)

        email_html = self.make_html_payload(template_end, template_start, self.article_dict)

        # Delete previous email, and write replacement
        if has_previous_message:
            rollup_inbox_proxy.delete_previous_message()
        rollup_inbox_proxy.append(self.make_new_raw_so_email(email_html, unseen, self.filter_name, sender_to_implicate))
        # Save
        self.store_writer.store_as_binary("articles", self.article_dict)

    def make_new_raw_so_email(self, email_html, count, filter_name, sender_to_implicate):
        new_message = 'Subject: ' + self.matching_rollup_subject() + ": " + str(count) + ' new posting(s)\n'
        new_message += 'From: ' + sender_to_implicate + '\n'
        #        new_message += 'To: ' + sender_to_implicate + '\n'
        new_message += 'Content-Transfer-Encoding: 8bit\n'
        new_message += 'Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"\n'
        new_message += 'MIME-Version: 1.0\n'
        new_message += 'This is a multi-part message in MIME format.\n'
        new_message += '-----NOTIFICATION_BOUNDARY\nContent-Type: text/html; charset="utf-8"\n'
        new_message += 'Content-Transfer-Encoding: base64\n\n'
        new_message += base64.b64encode(email_html)
        return new_message

    def make_html_payload(self, template_end, template_start, article_dict):
        email_html = template_start

        ix = 0
        for anum in sorted(article_dict["articles"].iterkeys(), reverse=True):
            if anum == article_dict["most_recent_seen"] and ix > 0:
                email_html += '<tr><td colspan="2" style="border-bottom: 1.5pt solid red; border-top: 1.5pt solid red;"><center>^ New Questions Since You Last Checked ^</center></td></tr>\n'
            email_html += "<tr>\n" + article_dict["articles"][anum] + "</tr>\n"
            ix = + 1
        email_html += template_end

        return email_html

    def get_article_snippet(self, article_snippet_filename):
        with open(article_snippet_filename, "r") as myfile:
            article_snippet = myfile.read()
        return article_snippet

    def get_template_start_and_end(self, template):
        template_start = template[:template.find("<InsertHere/>")]
        template_end = template[template.find("<InsertHere/>") + len("<InsertHere/>"):]
        return template_end, template_start

    def matching_incoming_headers(self):
        return ["Subject: New questions in " + self.filter_name + " filter"]

    def matching_rollup_subject(self):
        return 'S/Exchg Rollup for \'' + self.filter_name + '\''

    def print_summary(self):
        print "StackExchange: New StackExchange messages: " + str(
            self.new_message_count) + ", new articles: ?, " + "deleted articles (email was marked as read): " + str(
            self.deleted_articles_count)
