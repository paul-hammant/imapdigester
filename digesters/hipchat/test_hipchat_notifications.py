import sys
from unittest import TestCase

from mock import Mock, call
from mockextras import stub

from digesters.digestionprocessor import DigestionProcessor
from digesters.hipchat.hipchat_notification_digester import HipchatNotificationDigester

MAIL_HDR = """From: P H <ph@example.com>
Content-Transfer-Encoding: 7bit
Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY"
MIME-Version: 1.0
This is a multi-part message in MIME format.
-----NOTIFICATION_BOUNDARY
Content-Type: text/html; charset="utf-7"
Content-Transfer-Encoding: 7bit

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


class TestGithubNotifications(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestGithubNotifications, self).__init__(methodName)
        reload(sys)
        sys.setdefaultencoding('utf8')

    def test_two_related_notifs_can_be_rolled_up(self):

        expected_payload = """<html>
          <head>
              <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
              <title>Atlassian HipChat</title>
          </head>
          <body style="box-sizing: border-box; height: 100%; width: 100%;">
          <table bgcolor="#f5f5f5" border="0" cellpadding="0" cellspacing="0" class="container wrapper_shrink"
                 style="_padding: 20px; padding: 3%;" width="640">
              <tr>
                  <td valign="top">
                      <table bgcolor="#ffffff" border="0" cellpadding="0" cellspacing="0" class="inner-container table_shrink"
                             id="email_content"
                             style="-khtml-border-radius: 6px; -moz-border-radius: 6px; -webkit-border-radius: 6px; border: 1px solid #dadada; border-radius: 6px; width: 100% !important; margin-top: 15px;"
                             width="600">
                          <tr>
                              <td class="td top-spacer"
                                  style="font-size: 15px; line-height: 4px; padding-left: 20px; padding-right: 10px !important;"
                                  valign="top">
                                  +AKA
                              </td>
                          </tr>
                          <tr>
                              <td>
                                  <div class="history_container history_email" id="chats" style="padding-right: 0px !important;">
                                      <div class="ecxhc-chat-from" style="margin-left: 150px;text-align:left;width:200px;padding:10px 0 10px 10px;">Direct Message</div>
          <div>
          <div class="hc-chat-row hc-msg-nocolor" style="border-bottom: 1px solid #efefef; box-sizing: border-box; display: table; padding: 0; width: 600px !important; max-width: 600px !important;">
          <a name="a2f58d46-385e-4d7f-8bba-f8c0eb900d89" style="cursor: pointer; text-decoration: none;"></a>
          <div class="hc-chat-from" style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px; color: #888; max-width: 100px; overflow: hidden; text-align: right; text-overflow: ellipsis; vertical-align: top; white-space: nowrap; width: 100px; padding: 10px 0 10px 10px;">Paul Hammant</div>
          <div class="hc-chat-msg" style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px; line-height: 20px; padding: 10px; flex: 1;">
          <div style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px;">\r
                Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.<br><br>\r
          It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using \'Content here, content here\', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for \'lorem ipsum\' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).<br><br><br>\r
          Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.<br><br>\r
          The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form, accompanied by English versions from the 1914 translation by H. Rackham.<br><br>\r
          There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don\'t look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn\'t anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc.    </br></br></br></br></br></br></br></br></br></div>
          </div>
          <div class="hc-chat-time" style="display: table-cell; font-size: 10px !important; margin-bottom: 15px; margin-top: 15px; color: #888; text-align: right; vertical-align: top; white-space: nowrap; width: 40px; padding: 10px 10px 10px 0;">7:49 PM</div>
          </div></div>
          <div class="ecxhc-chat-from" style="margin-left: 150px;text-align:left;width:200px;padding:10px 0 10px 10px;">Room: Hammant</div>
          <div>
          <div class="hc-chat-row hc-msg-nocolor" style="border-bottom: 1px solid #efefef; box-sizing: border-box; display: table; padding: 0; width: 600px !important; max-width: 600px !important;">
          <a name="078141ad-2547-4cfc-a651-309c2a865692" style="cursor: pointer; text-decoration: none;"></a>
          <div class="hc-chat-from" style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px; color: #888; max-width: 100px; overflow: hidden; text-align: right; text-overflow: ellipsis; vertical-align: top; white-space: nowrap; width: 100px; padding: 10px 0 10px 10px;">Paul Hammant</div>
          <div class="hc-chat-msg" style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px; line-height: 20px; padding: 10px; flex: 1;">
          <div style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px;">
          <span class="atTag atTagMe" style="-moz-border-radius: 4px; -webkit-border-radius: 4px; background-color: #EFEFEF; border: 1px solid #4783BF; border-radius: 4px; display: inline-block; padding: 0 3px; background: #4282C1 url(/img/at_bg.png) repeat-x; color: #fff;">@test2</span> you suck    </div>
          </div>
          <div class="hc-chat-time" style="display: table-cell; font-size: 10px !important; margin-bottom: 15px; margin-top: 15px; color: #888; text-align: right; vertical-align: top; white-space: nowrap; width: 40px; padding: 10px 10px 10px 0;">7:45 PM</div>
          </div></div>
                                  </div>
                              </td>
                          </tr>
                      </table>
                  </td>
              </tr>
          </table>
          </body>
          </html>""".replace("\n          ","\n")

        notification_store = {}

        final_notifs_store = NotifsStore()

        store_writer = Mock()
        store_writer.get_from_binary.side_effect = stub(
            (call('hipchat-notifications'), notification_store),
            (call('most-recently-seen'), 0)
        )
        store_writer.store_as_binary.side_effect = stub(
            (call('hipchat-notifications', final_notifs_store), True),
            (call('most-recently-seen', 0), True)
        )

        expected_message = "Subject: Hipchat Rollup: 2 new notification(s)\n" + MAIL_HDR + expected_payload + \
                           "\n\n-----NOTIFICATION_BOUNDARY"

        rollup_inbox_proxy = Mock()
        rollup_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
        rollup_inbox_proxy.append.side_effect = stub((call(expected_message), True))

        digesters = []
        digester = HipchatNotificationDigester(store_writer)  ## What we are testing
        digesters.append(digester)

        digestion_processor = DigestionProcessor(None, None, digesters, False, "P H <ph@example.com>", False, "INBOX")

        unmatched_to_move = []
        to_delete_from_notification_folder = []

        notification_1_content, notification_2_content = self.get_hc_emailed_notifications()

        digestion_processor.process_incoming_notification(1234, digesters, notification_1_content, to_delete_from_notification_folder, unmatched_to_move, False)
        digestion_processor.process_incoming_notification(1235, digesters, notification_2_content, to_delete_from_notification_folder, unmatched_to_move, False)

        digester.rewrite_rollup_emails(rollup_inbox_proxy, has_previous_message=True,
                                        previously_seen=False, sender_to_implicate="P H <ph@example.com>")

        self.assertEquals(rollup_inbox_proxy.mock_calls, [call.delete_previous_message(), call.append(expected_message)])

        calls = store_writer.mock_calls
        self.assertEquals(calls, [
            call.get_from_binary('hipchat-notifications'),
            call.get_from_binary('most-recently-seen'),
            call.store_as_binary('hipchat-notifications', {1459813540: {u'div': '<div class="hc-chat-row hc-msg-nocolor" style="border-bottom: 1px solid #efefef; box-sizing: border-box; display: table; padding: 0; width: 600px !important; max-width: 600px !important;">\n\
<a name="078141ad-2547-4cfc-a651-309c2a865692" style="cursor: pointer; text-decoration: none;"></a>\n\
<div class="hc-chat-from" style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px; color: #888; max-width: 100px; overflow: hidden; text-align: right; text-overflow: ellipsis; vertical-align: top; white-space: nowrap; width: 100px; padding: 10px 0 10px 10px;">Paul Hammant</div>\n\
<div class="hc-chat-msg" style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px; line-height: 20px; padding: 10px; flex: 1;">\n\
<div style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px;">\n\
<span class="atTag atTagMe" style="-moz-border-radius: 4px; -webkit-border-radius: 4px; background-color: #EFEFEF; border: 1px solid #4783BF; border-radius: 4px; display: inline-block; padding: 0 3px; background: #4282C1 url(/img/at_bg.png) repeat-x; color: #fff;">@test2</span> you suck    </div>\n\
</div>\n\
<div class="hc-chat-time" style="display: table-cell; font-size: 10px !important; margin-bottom: 15px; margin-top: 15px; color: #888; text-align: right; vertical-align: top; white-space: nowrap; width: 40px; padding: 10px 10px 10px 0;">7:45 PM</div>\n\
</div>', u'room': u'Room: Hammant'}, 1459813751: {u'div': '<div class="hc-chat-row hc-msg-nocolor" style="border-bottom: 1px solid #efefef; box-sizing: border-box; display: table; padding: 0; width: 600px !important; max-width: 600px !important;">\n\
<a name="a2f58d46-385e-4d7f-8bba-f8c0eb900d89" style="cursor: pointer; text-decoration: none;"></a>\n\
<div class="hc-chat-from" style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px; color: #888; max-width: 100px; overflow: hidden; text-align: right; text-overflow: ellipsis; vertical-align: top; white-space: nowrap; width: 100px; padding: 10px 0 10px 10px;">Paul Hammant</div>\n\
<div class="hc-chat-msg" style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px; line-height: 20px; padding: 10px; flex: 1;">\n\
<div style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px;">\r\n\
      Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.<br><br>\r\n\
It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using \'Content here, content here\', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for \'lorem ipsum\' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).<br><br><br>\r\n\
Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.<br><br>\r\n\
The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form, accompanied by English versions from the 1914 translation by H. Rackham.<br><br>\r\n\
There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don\'t look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn\'t anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc.    </br></br></br></br></br></br></br></br></br></div>\n\
</div>\n\
<div class="hc-chat-time" style="display: table-cell; font-size: 10px !important; margin-bottom: 15px; margin-top: 15px; color: #888; text-align: right; vertical-align: top; white-space: nowrap; width: 40px; padding: 10px 10px 10px 0;">7:49 PM</div>\n\
</div>', u'room': u'Direct Message'}} ),
            call.store_as_binary('most-recently-seen', 0)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(str(to_delete_from_notification_folder), "[1234, 1235]")
        self.assertEquals(len(final_notifs_store.notifs), 2)

    def get_hc_emailed_notifications(self):
        with open('../../testdata/hc_mention_in_room', 'r') as myfile:
            notification_1_content = myfile.read().replace('\n', '\r\n')
        with open('../../testdata/hc_1to1', 'r') as myfile:
            notification_2_content = myfile.read().replace('\n', '\r\n')
        return notification_1_content, notification_2_content


