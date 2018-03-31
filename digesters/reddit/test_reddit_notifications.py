# coding=utf-8
import sys
import unittest
from unittest import TestCase
from importlib import reload


from mock import Mock, call
import os

sys.path = [os.path.abspath(os.path.join('..', os.pardir))] + sys.path

from digesters.digestion_processor import DigestionProcessor
from digesters.github.github_notification_digester import GithubNotificationDigester





class TestGithubNotifications(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestGithubNotifications, self).__init__(methodName)
        reload(sys)
        # sys.setdefaultencoding('utf8')

    def test_something(self):

        # TODO

        pass


if __name__ == '__main__':
    unittest.main()
