# coding=utf-8
import sys
import unittest
from unittest import TestCase
from importlib import reload

from mockextras import stub

from mock import Mock, call
import os

from digesters.reddit.reddit_notification_digester import RedditNotificationDigester

sys.path = [os.path.abspath(os.path.join('..', os.pardir))] + sys.path

from digesters.digestion_processor import DigestionProcessor
from digesters.github.github_notification_digester import GithubNotificationDigester

MAIL_HDR = """From: \"Our inhouse GH\" <ph@example.com>
Content-Transfer-Encoding: 8bit
Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY-5678"
MIME-Version: 1.0
This is a multi-part message in MIME format.
-----NOTIFICATION_BOUNDARY-5678
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: 8bit

"""

class NotifsStore(object):

    def __init__(self, cls=object):
        self._cls = cls
        self.notifs = None

    def __eq__(self, other):
        self.notifs = other
        return True

    def __ne__(self, other):
        return False

    def __repr__(self):
        return "NotifsStore(..)"


class TestRedditNotifications(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestRedditNotifications, self).__init__(methodName)
        reload(sys)
        # sys.setdefaultencoding('utf8')


    def test_messages_for_one_recipient(self):

        stored_notifs_expectations = {1522050604.0: {
            'message': '<div class="mmessage">\n<h2>Private message from /u/paul_h • \n  \n  <a class="link" href="https://www.reddit.com/message/messages/bak608?utm_medium=message_notification&amp;utm_source=email&amp;utm_name1d1e473eb033&amp;utm_content=private_message&amp;utm_term=0" style="color:#0079d3;\n            text-decoration:none" target="_blank">view\n  </a>\n</h2>\n<!-- SC_OFF --><p>Hello</p>\n<!-- SC_ON -->\n<!-- SC_OFF --><div class="md"><p>How are you?</p>\n<p><strong>you</strong></p>\n<p><a href="http://example.com/you">you</a></p>\n<p>you\n   you</p>\n</div><!-- SC_ON -->\n</div>'},
            1522050604.1: {
                'message': '<div class="mmessage">\n<h2>Comment reply from /u/paul_h • \n  \n  <div> on /r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a <a class="link" href="https://www.reddit.com/r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a/dwaqvtx/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=e473eeb033&amp;utm_content=comment_reply&amp;utm_term=1" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>Came here to say that!</p>\n</div><!-- SC_ON -->\n</div>'},
            1522050604.2: {
                'message': '<div class="mmessage">\n<h2>Comment reply from /u/paul_h • \n  \n  <div> on /r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a <a class="link" href="https://www.reddit.com/r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a/dwar0tm/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=473033&amp;utm_content=comment_reply&amp;utm_term=2" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>The article author chimed in to say the same in a comment above.</p>\n</div><!-- SC_ON -->\n</div>'},
            1522135001.0: {
                'message': '<div class="mmessage">\n<h2>Comment reply from /u/sdjhfsdfwewer • \n  \n  <div> on /r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a <a class="link" href="https://www.reddit.com/r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a/dwcohkb/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=3f802b316a8a894b9c0daa7ed2ed1f3618772171&amp;utm_content=comment_reply&amp;utm_term=0" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>TornadoFX is not by JetBrains but is made with their support.</p>\n</div><!-- SC_ON -->\n</div>'}}

        expected_message = 'Subject: ph555: Reddit Messages Digest: 4 new notifications(s)\nFrom: "Reddit" <ph@example.com>\nContent-Transfer-Encoding: 8bit\nContent-Type: ' \
                    'multipart/alternative; boundary="---NOTIFICATION_BOUNDARY-5678"\nMIME-Version: 1.0\nThis is a multi-part message in MIME ' \
                    'format.\n-----NOTIFICATION_BOUNDARY-5678\nContent-Type: text/html; charset="utf-8"\nContent-Transfer-Encoding: 8bit\n\n\n<html><body>\n        <table>\n          <tr style="background-color: #acf;">\n            <th colspan="2">Messages</th>\n          </tr>\n          <!--2--><tr style="">\n            <td></td>\n            <td>                      \n              <div class="mmessage">\n<h2>Comment reply from /u/sdjhfsdfwewer • \n  \n  <div> on /r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a <a class="link" href="https://www.reddit.com/r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a/dwcohkb/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=3f802b316a8a894b9c0daa7ed2ed1f3618772171&amp;utm_content=comment_reply&amp;utm_term=0" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>TornadoFX is not by JetBrains but is made with their support.</p>\n</div><!-- SC_ON -->\n</div>\n            </td>\n          </tr><!--cl2-->          <!--2--><tr style="background-color: #def;">\n            <td></td>\n            <td>                      \n              <div class="mmessage">\n<h2>Comment reply from /u/paul_h • \n  \n  <div> on /r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a <a class="link" href="https://www.reddit.com/r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a/dwar0tm/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=473033&amp;utm_content=comment_reply&amp;utm_term=2" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>The article author chimed in to say the same in a comment above.</p>\n</div><!-- SC_ON -->\n</div>\n            </td>\n          </tr><!--cl2-->          <!--2--><tr style="">\n            <td></td>\n            <td>                      \n              <div class="mmessage">\n<h2>Comment reply from /u/paul_h • \n  \n  <div> on /r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a <a class="link" href="https://www.reddit.com/r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a/dwaqvtx/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=e473eeb033&amp;utm_content=comment_reply&amp;utm_term=1" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>Came here to say that!</p>\n</div><!-- SC_ON -->\n</div>\n            </td>\n          </tr><!--cl2-->          <!--2--><tr style="background-color: #def;">\n            <td></td>\n            <td>                      \n              <div class="mmessage">\n<h2>Private message from /u/paul_h • \n  \n  <a class="link" href="https://www.reddit.com/message/messages/bak608?utm_medium=message_notification&amp;utm_source=email&amp;utm_name1d1e473eb033&amp;utm_content=private_message&amp;utm_term=0" style="color:#0079d3;\n            text-decoration:none" target="_blank">view\n  </a>\n</h2>\n<!-- SC_OFF --><p>Hello</p>\n<!-- SC_ON -->\n<!-- SC_OFF --><div class="md"><p>How are you?</p>\n<p><strong>you</strong></p>\n<p><a href="http://example.com/you">you</a></p>\n<p>you\n   you</p>\n</div><!-- SC_ON -->\n</div>\n            </td>\n          </tr><!--cl2-->\n        </table></body></html>\n\n-----NOTIFICATION_BOUNDARY-5678'

        self.doit_with_three_incoming_emails("ph555", expected_message, stored_notifs_expectations, "[1234, 1236]")

    def test_same_messages_for_different_recipient(self):

        stored_notifs_expectations = {1522136236.0: {'message': '<div class="mmessage">\n<h2>Comment reply from /u/paul_h • \n  \n  <div> on /r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a <a class="link" href="https://www.reddit.com/r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a/dwcoo78/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=cf880d1&amp;utm_content=comment_reply&amp;utm_term=0" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>A larger community is always needed for these things. For the project page stated "Important: TornadoFX is not yet compatible with Java 9", and that may take multiple sets of eyes to solve.</p>\n</div><!-- SC_ON -->\n</div>'}, 1522136236.1: {'message': '<div class="mmessage">\n<h2>\n                    /u/paul_h mentioned you in <span> a Thread </span>\n                    • \n  \n  <div> on /r/test/comments/876rgc/test <a class="link" href="https://www.reddit.com/r/test/comments/876rgc/test/dwcow3u/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=a1a20d1&amp;utm_content=username_mention&amp;utm_term=1" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>Imma going to test mentions here, <del>pls ignore me</del></p>\n<p><a href="https://www.reddit.com/u/sdjhfsdfwewer">/u/sdjhfsdfwewer</a></p>\n</div><!-- SC_ON -->\n</div>'}, 1522136236.2: {'message': '<div class="mmessage">\n<h2>\n                    /u/paul_h mentioned you in <span> a Thread </span>\n                    • \n  \n  <div> on /r/test/comments/876rgc/test <a class="link" href="https://www.reddit.com/r/test/comments/876rgc/test/dwcp46n/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=a1a20d1&amp;utm_content=username_mention&amp;utm_term=2" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>Imma going to test mentions here, <del>pls ignore me</del></p>\n<p><a href="https://www.reddit.com/u/sdjhfsdfwewer">/u/sdjhfsdfwewer</a></p>\n</div><!-- SC_ON -->\n</div>'}, 1522136236.3: {'message': '<div class="mmessage">\n<h2>Private message from /u/paul_h • \n  \n  <a class="link" href="https://www.reddit.com/message/messages/bay5nk?utm_medium=message_notification&amp;utm_source=email&amp;utm_name=cf880d1&amp;utm_content=private_message&amp;utm_term=3" style="color:#0079d3;\n            text-decoration:none" target="_blank">view\n  </a>\n</h2>\n<!-- SC_OFF --><p>Complete list of European Special Characters</p>\n<!-- SC_ON -->\n<!-- SC_OFF --><div class="md"><p>Working on a german project with dynamic Textfields or forms is no problem for me: there are six »Umlaute« and one ligature, that I use every day. English forms are even easier: no special characters at all (how unimaginative ;-)…\nBut at the moment the project’s scope is widened to East- or West-Europe, problems begin if you weren’t attentive in school: In Spanish questions start with this upsidedown questionmark, don’t they? In French there are accents, but what directions and on which letters? And does anyone had Czech or Hungarian in school?</p>\n<p>This is for all developers, making forms or dynamic textfields for the western hemisphere (no Cyrillic or Greek characters).</p>\n<pre><code>¡¿\nÄäÀàÁáÂâÃãÅåǍǎĄąĂăÆæĀā\nÇçĆćĈĉČč\nĎđĐďð\nÈèÉéÊêËëĚěĘęĖėĒē\nĜĝĢģĞğ\nĤĥ\nÌìÍíÎîÏïıĪīĮį\nĴĵ\nĶķ\nĹĺĻļŁłĽľ\nÑñŃńŇňŅņ\nÖöÒòÓóÔôÕõŐőØøŒœ\nŔŕŘř\nẞßŚśŜŝŞşŠšȘș\nŤťŢţÞþȚț\nÜüÙùÚúÛûŰűŨũŲųŮůŪū\nŴŵ\nÝýŸÿŶŷ\nŹźŽžŻż\n</code></pre>\n</div><!-- SC_ON -->\n</div>'}}

        expected_message = 'Subject: sdjhfsdfwewer: Reddit Messages Digest: 4 new notifications(s)\nFrom: "Reddit" <ph@example.com>\nContent-Transfer-Encoding: 8bit\nContent-Type: ' \
                    'multipart/alternative; boundary="---NOTIFICATION_BOUNDARY-5678"\nMIME-Version: 1.0\nThis is a multi-part message in MIME format.\n-----NOTIFICATION_BOUNDARY-5678\nContent-Type: text/html; charset="utf-8"\nContent-Transfer-Encoding: 8bit\n\n\n<html><body>\n        <table>\n          <tr style="background-color: #acf;">\n            <th colspan="2">Messages</th>\n          </tr>\n          <!--2--><tr style="">\n            <td></td>\n            <td>                      \n              <div class="mmessage">\n<h2>Private message from /u/paul_h • \n  \n  <a class="link" href="https://www.reddit.com/message/messages/bay5nk?utm_medium=message_notification&amp;utm_source=email&amp;utm_name=cf880d1&amp;utm_content=private_message&amp;utm_term=3" style="color:#0079d3;\n            text-decoration:none" target="_blank">view\n  </a>\n</h2>\n<!-- SC_OFF --><p>Complete list of European Special Characters</p>\n<!-- SC_ON -->\n<!-- SC_OFF --><div class="md"><p>Working on a german project with dynamic Textfields or forms is no problem for me: there are six »Umlaute« and one ligature, that I use every day. English forms are even easier: no special characters at all (how unimaginative ;-)…\nBut at the moment the project’s scope is widened to East- or West-Europe, problems begin if you weren’t attentive in school: In Spanish questions start with this upsidedown questionmark, don’t they? In French there are accents, but what directions and on which letters? And does anyone had Czech or Hungarian in school?</p>\n<p>This is for all developers, making forms or dynamic textfields for the western hemisphere (no Cyrillic or Greek characters).</p>\n<pre><code>¡¿\nÄäÀàÁáÂâÃãÅåǍǎĄąĂăÆæĀā\nÇçĆćĈĉČč\nĎđĐďð\nÈèÉéÊêËëĚěĘęĖėĒē\nĜĝĢģĞğ\nĤĥ\nÌìÍíÎîÏïıĪīĮį\nĴĵ\nĶķ\nĹĺĻļŁłĽľ\nÑñŃńŇňŅņ\nÖöÒòÓóÔôÕõŐőØøŒœ\nŔŕŘř\nẞßŚśŜŝŞşŠšȘș\nŤťŢţÞþȚț\nÜüÙùÚúÛûŰűŨũŲųŮůŪū\nŴŵ\nÝýŸÿŶŷ\nŹźŽžŻż\n</code></pre>\n</div><!-- SC_ON -->\n</div>\n            </td>\n          </tr><!--cl2-->          <!--2--><tr style="background-color: #def;">\n            <td></td>\n            <td>                      \n              <div class="mmessage">\n<h2>\n                    /u/paul_h mentioned you in <span> a Thread </span>\n                    • \n  \n  <div> on /r/test/comments/876rgc/test <a class="link" href="https://www.reddit.com/r/test/comments/876rgc/test/dwcp46n/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=a1a20d1&amp;utm_content=username_mention&amp;utm_term=2" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>Imma going to test mentions here, <del>pls ignore me</del></p>\n<p><a href="https://www.reddit.com/u/sdjhfsdfwewer">/u/sdjhfsdfwewer</a></p>\n</div><!-- SC_ON -->\n</div>\n            </td>\n          </tr><!--cl2-->          <!--2--><tr style="">\n            <td></td>\n            <td>                      \n              <div class="mmessage">\n<h2>\n                    /u/paul_h mentioned you in <span> a Thread </span>\n                    • \n  \n  <div> on /r/test/comments/876rgc/test <a class="link" href="https://www.reddit.com/r/test/comments/876rgc/test/dwcow3u/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=a1a20d1&amp;utm_content=username_mention&amp;utm_term=1" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>Imma going to test mentions here, <del>pls ignore me</del></p>\n<p><a href="https://www.reddit.com/u/sdjhfsdfwewer">/u/sdjhfsdfwewer</a></p>\n</div><!-- SC_ON -->\n</div>\n            </td>\n          </tr><!--cl2-->          <!--2--><tr style="background-color: #def;">\n            <td></td>\n            <td>                      \n              <div class="mmessage">\n<h2>Comment reply from /u/paul_h • \n  \n  <div> on /r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a <a class="link" href="https://www.reddit.com/r/programming/comments/872bgr/reacts_tictactoe_tutorial_in_kotlinjavafx_a/dwcoo78/?context=3&amp;utm_medium=message_notification&amp;utm_source=email&amp;utm_name=cf880d1&amp;utm_content=comment_reply&amp;utm_term=0" style="color:#0079d3;\n            text-decoration:none" target="_blank">reply\n  </a></div>\n</h2>\n<!-- SC_OFF --><div class="md"><p>A larger community is always needed for these things. For the project page stated "Important: TornadoFX is not yet compatible with Java 9", and that may take multiple sets of eyes to solve.</p>\n</div><!-- SC_ON -->\n</div>\n            </td>\n          </tr><!--cl2-->\n        </table></body></html>\n\n-----NOTIFICATION_BOUNDARY-5678'

        self.doit_with_three_incoming_emails("sdjhfsdfwewer", expected_message, stored_notifs_expectations, "[1235]")

    def doit_with_three_incoming_emails(self, userId, expected_message, stored_notifs_expectations, expected_message_ids):

        notification_store = {}

        final_notifs_store = NotifsStore()

        store_writer = Mock()
        store_writer.get_from_binary.side_effect = stub(
            (call('reddit-notifications'), notification_store),
            (call('reddit-recently-seen'), 0)
        )
        store_writer.store_as_binary.side_effect = stub(
            (call('reddit-notifications', final_notifs_store), True),
            (call('reddit-recently-seen', 0), True)
        )

        with open("sampleEmail.txt", "r") as testEmailFile:
            testEmail1 = testEmailFile.read()

            with open("sampleEmail2.txt", "r") as testEmailFile2:
                testEmail2 = testEmailFile2.read()

                with open("sampleEmail3.txt", "r") as testEmailFile3:
                    testEmail3 = testEmailFile3.read()

                    digest_inbox_proxy = Mock()
                    digest_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
                    digest_inbox_proxy.append.side_effect = stub((call(expected_message), True))

                    digesters = []
                    digester = RedditNotificationDigester(store_writer, userId=userId)  ## What we are testing
                    digester.notification_boundary_rand = "-5678"  # no random number for the email's notification boundary
                    digesters.append(digester)

                    digestion_processor = DigestionProcessor(None, None, digesters, False, "ph@example.com", False, "INBOX")

                    unmatched_to_move = []
                    to_delete_from_notification_folder = []

                    digestion_processor.process_incoming_notification(1234, digesters, testEmail1, to_delete_from_notification_folder, unmatched_to_move, False)
                    digestion_processor.process_incoming_notification(1235, digesters, testEmail2, to_delete_from_notification_folder, unmatched_to_move, False)
                    digestion_processor.process_incoming_notification(1236, digesters, testEmail3, to_delete_from_notification_folder, unmatched_to_move, False)

                    digester.rewrite_digest_emails(digest_inbox_proxy, has_previous_message=True,
                                                   previously_seen=False, sender_to_implicate="ph@example.com")
                    self.assertEqual(digest_inbox_proxy.mock_calls, [call.delete_previous_message(), call.append(expected_message)])

                    self.assertEqual(store_writer.mock_calls, [
                        call.get_from_binary('reddit-notifications'),
                        call.get_from_binary('reddit-recently-seen'),
                        call.store_as_binary('reddit-notifications', stored_notifs_expectations),
                        call.store_as_binary('reddit-recently-seen', 0)])
                    self.assertEqual(len(unmatched_to_move), 0)
                    self.assertEqual(str(to_delete_from_notification_folder), expected_message_ids)
                    self.assertEqual(len(final_notifs_store.notifs), 4)


if __name__ == '__main__':
    unittest.main()
