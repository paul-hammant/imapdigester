import os
from abc import ABCMeta, abstractmethod
from random import random


class BaseDigester(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._notification_boundary_rand = str(random())

    @property
    def notification_boundary_rand(self):
        return self._notification_boundary_rand

    @notification_boundary_rand.setter
    def notification_boundary_rand(self, value):
        self._notification_boundary_rand = value

    @abstractmethod
    def process_new_notification(self, rfc822content, msg, html_message, text_message):
        """
        Process new email notification
        :rtype: True or False based on whether the email was processed or not
        """
        pass

    @abstractmethod
    def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):
        """
        Rewrite (or write, or don't at all) the digest email, in the digest email account
        :param sender_to_implicate: The From message is set to this "Firstname Secondname" <email@addr>
        :param previously_seen: True if the current digest email has been read
        :param has_previous_message:  True is there is a current digest for this at all (could have been deleted)
        :param digest_folder_proxy:  Use this to orchestrate delete and actual rewrite
        """
        pass

    @abstractmethod
    def matching_incoming_headers(self):
        """
        :rtype: List of headers that would mean a match, like: ["From: alerts@example.com"]
        """
        pass

    @abstractmethod
    def matching_digest_subject(self):
        """
        :rtype: 'Subject' that we're matching on, like "Foobar Digest"
        """
        pass

    @abstractmethod
    def matching_digest_sender(self):
        """
        :rtype: 'From' that we're matching on, like "Credit Cards"
        """
        pass

    @abstractmethod
    def print_summary(self):
        """
        :rtype: print a summary (or not) at the end
        """
        pass

    @staticmethod
    def remove_lines_that_are_fully_whitespace(email):
        return os.linesep.join([s for s in email.splitlines() if s.strip()])

