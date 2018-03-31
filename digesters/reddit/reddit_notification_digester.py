import io
import re
from email.header import decode_header

import arrow
from jinja2 import Template

from digesters.base_digester import BaseDigester


class RedditNotificationDigester(BaseDigester):
    def __init__(self, store_writer, userId):
        super(RedditNotificationDigester, self).__init__()
        self.store_writer = store_writer
        self.userId = userId
        self.new_message_count = 0
        self.new_articles = 0
        self.github_notifications = self.store_writer.get_from_binary("reddit-notifications")
        if self.github_notifications is None:
            self.github_notifications = {}

        self.most_recently_seen = self.store_writer.get_from_binary("reddit-recently-seen")
        if self.most_recently_seen is None:
            self.most_recently_seen = 0

        self.new_notifications = {}

    def process_new_notification(self, rfc822content, msg, html_message, text_message):

        # TODO

        return False  # TODO change this to true when you're sure you've parsed the entire html-email segment

    def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):

        # TODO

        pass

    def matching_incoming_headers(self):
        return ["From: Reddit <notifications@redditmail.com>",
                "Subject: [reddit] .* u/" + self.userId]

    def matching_digest_subject(self):
        return  self.userId + ': Reddit Messages Digest'

    def matching_digest_sender(self):
        return "Reddit"

    def print_summary(self):
        print("New " + self.userId + " notifications: " + str(self.new_message_count))
