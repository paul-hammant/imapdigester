import sys
from unittest import TestCase

from mock import Mock, call
from mockextras import stub

from digesters.digestion_processor import DigestionProcessor
from digesters.hipchat.hipchat_notification_digester import HipchatNotificationDigester

MAIL_HDR = """From: "HipChat" <ph@example.com>
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


class TestHipchatNotifications(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestHipchatNotifications, self).__init__(methodName)
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
          <div style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px;">
                Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.<br><br>
          It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using \'Content here, content here\', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for \'lorem ipsum\' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).<br><br><br>
          Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.<br><br>
          The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form, accompanied by English versions from the 1914 translation by H. Rackham.<br><br>
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

        expected_message = "Subject: Notification Digest: 2 new notification(s)\n" + MAIL_HDR + expected_payload + \
                           "\n\n-----NOTIFICATION_BOUNDARY-5678"

        digest_inbox_proxy = Mock()
        digest_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
        digest_inbox_proxy.append.side_effect = stub((call(expected_message), True))

        digesters = []
        digester = HipchatNotificationDigester(store_writer)  ## What we are testing
        digester.notification_boundary_rand = "-5678"  # no random number for the email's notification boundary
        digesters.append(digester)

        digestion_processor = DigestionProcessor(None, None, digesters, False, "ph@example.com", False, "INBOX")

        unmatched_to_move = []
        to_delete_from_notification_folder = []

        digestion_processor.process_incoming_notification(1234, digesters, HIPCHAT_MENTION_IN_ROOM, to_delete_from_notification_folder, unmatched_to_move, False)
        digestion_processor.process_incoming_notification(1235, digesters, HIPCHAT_ONE_TO_ONE, to_delete_from_notification_folder, unmatched_to_move, False)

        digester.rewrite_digest_emails(digest_inbox_proxy, has_previous_message=True,
                                       previously_seen=False, sender_to_implicate="ph@example.com")

        self.assertEquals(digest_inbox_proxy.mock_calls, [call.delete_previous_message(), call.append(expected_message)])

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
<div style="display: table-cell; font-size: 13px; margin-bottom: 15px; margin-top: 15px;">\n\
      Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.<br><br>\n\
It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using \'Content here, content here\', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for \'lorem ipsum\' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).<br><br><br>\n\
Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.<br><br>\n\
The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form, accompanied by English versions from the 1914 translation by H. Rackham.<br><br>\n\
There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don\'t look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn\'t anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc.    </br></br></br></br></br></br></br></br></br></div>\n\
</div>\n\
<div class="hc-chat-time" style="display: table-cell; font-size: 10px !important; margin-bottom: 15px; margin-top: 15px; color: #888; text-align: right; vertical-align: top; white-space: nowrap; width: 40px; padding: 10px 10px 10px 0;">7:49 PM</div>\n\
</div>', u'room': u'Direct Message'}} ),
            call.store_as_binary('most-recently-seen', 0)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(str(to_delete_from_notification_folder), "[1234, 1235]")
        self.assertEquals(len(final_notifs_store.notifs), 2)

HIPCHAT_ONE_TO_ONE = """To: "" <paul_hamm@example.com>
Subject: Paul Hammant sent you a 1-1 message
Message-ID: <7a96cdc0bde724048191c72a9b7b6177@localhost>
Date: Mon, 4 Apr 2016 23:49:11 +0000
From: HipChat <donotreply@hipchat.com>
Content-Type: multipart/alternative;
 boundary="_=_swift_v4_1459813751_afa34d50633b0a830cd6f4cde61f8f75_=_"
MIME-Version: 1.0

--_=_swift_v4_1459813751_afa34d50633b0a830cd6f4cde61f8f75_=_
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable


Hi test2,

Paul Hammant just sent you a 1-1 message but you're offline:
  [7:49 PM] Paul Hammant: Lorem Ipsum is simply dummy text of the printing =
and typesetting industry. Lorem Ipsum has been the industry's standard dumm=
y text ever since the 1500s, when an unknown printer took a galley of type =
and scrambled it to make a type specimen book. It has survived not only fiv=
e centuries, but also the leap into electronic typesetting, remaining essen=
tially unchanged. It was popularised in the 1960s with the release of Letra=
set sheets containing Lorem Ipsum passages, and more recently with desktop =
publishing software like Aldus PageMaker including versions of Lorem Ipsum.


---
To change your notification preferences: https://www.hipchat.com/account/no=
tifications.
This message was intended for paul_hamm@example.com. If this was in error,
please contact us (https://www.hipchat.com/contact)
or opt out (https://www.hipchat.com/opt_out?email=3Dpaul_hamm%40example.com=
&token=3D49a33e4b536ac701deaac4e3c076aa3e9d98c62b).

--_=_swift_v4_1459813751_afa34d50633b0a830cd6f4cde61f8f75_=_
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"><?xml encodi=
ng=3D"utf-8"><html><head>
<meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8"><t=
itle>Atlassian HipChat</title></head><body style=3D"box-sizing: border-box;=
 height: 100%; width: 100%;">
<table class=3D"container wrapper_shrink" width=3D"640" cellpadding=3D"0" c=
ellspacing=3D"0" border=3D"0" bgcolor=3D"#f5f5f5" style=3D"_padding: 20px; =
padding: 3%;"><tr><td valign=3D"top">
        <table id=3D"email_header" class=3D"table_shrink" width=3D"600" cel=
lpadding=3D"0" cellspacing=3D"0" border=3D"0" style=3D"width: 100% !importa=
nt;"><tr><td>
      <a href=3D"https://www.hipchat.com/people/show/2106527?utm_medium=3De=
mail&amp;utm_source=3Doto_message_notification" style=3D"cursor: pointer; t=
ext-decoration: none;">Paul Hammant</a> just sent you a 1-1 message but you=
're offline:    </td>
  </tr></table><table id=3D"email_content" class=3D"inner-container table_s=
hrink" style=3D"-khtml-border-radius: 6px; -moz-border-radius: 6px; -webkit=
-border-radius: 6px; border: 1px solid #dadada; border-radius: 6px; width: =
100% !important; margin-top: 15px;" width=3D"600" cellpadding=3D"0" cellspa=
cing=3D"0" border=3D"0" bgcolor=3D"#ffffff"><tr><td class=3D"td top-spacer"=
 valign=3D"top" style=3D"font-size: 15px; line-height: 4px; padding-left: 2=
0px; padding-right: 10px !important;">
      &nbsp;
    </td>
  </tr><tr><td>
        <div id=3D"chats" class=3D"history_container history_email" style=
=3D"padding-right: 0px !important;">
                        <div class=3D"hc-chat-row hc-msg-nocolor" style=3D"=
border-bottom: 1px solid #efefef; box-sizing: border-box; display: table; p=
adding: 0; width: 600px !important; max-width: 600px !important;">
    <a name=3D"a2f58d46-385e-4d7f-8bba-f8c0eb900d89" style=3D"cursor: point=
er; text-decoration: none;"></a>

      <div class=3D"hc-chat-from" style=3D"display: table-cell; font-size: =
13px; margin-bottom: 15px; margin-top: 15px; color: #888; max-width: 100px;=
 overflow: hidden; text-align: right; text-overflow: ellipsis; vertical-ali=
gn: top; white-space: nowrap; width: 100px; padding: 10px 0 10px 10px;">Pau=
l Hammant</div>
 =20
    <div class=3D"hc-chat-msg" style=3D"display: table-cell; font-size: 13p=
x; margin-bottom: 15px; margin-top: 15px; line-height: 20px; padding: 10px;=
 flex: 1;">
            <div style=3D"display: table-cell; font-size: 13px; margin-bott=
om: 15px; margin-top: 15px;">
      Lorem Ipsum is simply dummy text of the printing and typesetting indu=
stry. Lorem Ipsum has been the industry's standard dummy text ever since th=
e 1500s, when an unknown printer took a galley of type and scrambled it to =
make a type specimen book. It has survived not only five centuries, but als=
o the leap into electronic typesetting, remaining essentially unchanged. It=
 was popularised in the 1960s with the release of Letraset sheets containin=
g Lorem Ipsum passages, and more recently with desktop publishing software =
like Aldus PageMaker including versions of Lorem Ipsum.<br><br>
It is a long established fact that a reader will be distracted by the reada=
ble content of a page when looking at its layout. The point of using Lorem =
Ipsum is that it has a more-or-less normal distribution of letters, as oppo=
sed to using 'Content here, content here', making it look like readable Eng=
lish. Many desktop publishing packages and web page editors now use Lorem I=
psum as their default model text, and a search for 'lorem ipsum' will uncov=
er many web sites still in their infancy. Various versions have evolved ove=
r the years, sometimes by accident, sometimes on purpose (injected humour a=
nd the like).<br><br><br>
Contrary to popular belief, Lorem Ipsum is not simply random text. It has r=
oots in a piece of classical Latin literature from 45 BC, making it over 20=
00 years old. Richard McClintock, a Latin professor at Hampden-Sydney Colle=
ge in Virginia, looked up one of the more obscure Latin words, consectetur,=
 from a Lorem Ipsum passage, and going through the cites of the word in cla=
ssical literature, discovered the undoubtable source. Lorem Ipsum comes fro=
m sections 1.10.32 and 1.10.33 of &quot;de Finibus Bonorum et Malorum&quot;=
 (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is =
a treatise on the theory of ethics, very popular during the Renaissance. Th=
e first line of Lorem Ipsum, &quot;Lorem ipsum dolor sit amet..&quot;, come=
s from a line in section 1.10.32.<br><br>
The standard chunk of Lorem Ipsum used since the 1500s is reproduced below =
for those interested. Sections 1.10.32 and 1.10.33 from &quot;de Finibus Bo=
norum et Malorum&quot; by Cicero are also reproduced in their exact origina=
l form, accompanied by English versions from the 1914 translation by H. Rac=
kham.<br><br>
There are many variations of passages of Lorem Ipsum available, but the maj=
ority have suffered alteration in some form, by injected humour, or randomi=
sed words which don't look even slightly believable. If you are going to us=
e a passage of Lorem Ipsum, you need to be sure there isn't anything embarr=
assing hidden in the middle of text. All the Lorem Ipsum generators on the =
Internet tend to repeat predefined chunks as necessary, making this the fir=
st true generator on the Internet. It uses a dictionary of over 200 Latin w=
ords, combined with a handful of model sentence structures, to generate Lor=
em Ipsum which looks reasonable. The generated Lorem Ipsum is therefore alw=
ays free from repetition, injected humour, or non-characteristic words etc.=
    </div>

      </div>

        <div class=3D"hc-chat-time" style=3D"display: table-cell; font-size=
: 10px !important; margin-bottom: 15px; margin-top: 15px; color: #888; text=
-align: right; vertical-align: top; white-space: nowrap; width: 40px; paddi=
ng: 10px 10px 10px 0;">7:49 PM</div>
  </div>


                    <span style=3D"color: #fff; font-size: 10px;">eMD4AMoTk=
S45ZRK</span>
        </div>
      </td>
    </tr><tr><td class=3D"td mobile-ad" valign=3D"top" style=3D"padding-rig=
ht: 10px!important; padding-left: 30px!important; line-height: 14px;">
      Get HipChat notifications on your phone! Download for
       or
      .
    </td>
  </tr><tr><td class=3D"td bottom-spacer" valign=3D"top" style=3D"font-size=
: 15px; line-height: 4px; padding-left: 20px; padding-right: 10px !importan=
t; padding-top: 10px;">
      &nbsp;
    </td>
  </tr></table></td>
  </tr><tr><td valign=3D"top">
      <table><tr><td width=3D"100%" class=3D"footer" style=3D"color: #99999=
9; font-family: Arial, sans-serif; font-size: 12px; line-height: 22px; padd=
ing-top: 10px; padding-left: 0px !important; padding-right: 0px !important;=
">
                        To change your notification preferences, click
              . <br>
            This message was intended for paul_hamm@example.com. If this wa=
s in error, please
               or
              . <br>
            HipChat's offices are located at 1098 Harrison St, San Francisc=
o, CA 94103 <br><br>

            Too many emails? You can .
                      </td>
          <td class=3D"logo-outer-container" rowspan=3D"2" valign=3D"top" s=
tyle=3D"padding: 0px; padding-left: 20px; vertical-align: top;">
            <table class=3D"logo-inner-container" style=3D"color: #333333;"=
><tbody><tr><td id=3D"footer_logo" style=3D"padding-top: 10px; padding-righ=
t: 0px !important;">
                  <img src=3D"http://image.mailer.atlassian.com/lib/fec2157=
377620c74/m/3/hipchat_email_logo_footer.png" width=3D"119px" height=3D"38px=
"></td>
              </tr></tbody></table></td>
        </tr></table></td>
  </tr></table>
<img src=3D"http://email.hipchat.com/wf/open?upn=3DozjFFozmjyjqypaS8eFG9CeW=
fsZXrUQW6OgWZuOvpR-2BOHOJ0AZrcUs85lRpiyu9zga0jbNan83S-2BF2GS84uSxrNGdO4Yn9Z=
h7qvNi2UJ9NvNBUBEkMgsqqNb7zhnlv-2FQiyOFtTch2dyQ7UoKR6PEbt9ub1GgQDRGKAw2618p=
fUbPJI9nUj-2FMTHFR0axdcNLvw3BnpEyHL1QFhdeF8XvKTpxcnGka1GLLUYm241aH177ihvUpm=
ocXhdvxoIDqs0GHoD-2B5UZulMx3Q8Zl9mca53A-3D-3D" alt=3D"" width=3D"1" height=
=3D"1" border=3D"0" style=3D"height:1px !important;width:1px !important;bor=
der-width:0 !important;margin-top:0 !important;margin-bottom:0 !important;m=
argin-right:0 !important;margin-left:0 !important;padding-top:0 !important;=
padding-bottom:0 !important;padding-right:0 !important;padding-left:0 !impo=
rtant;">
</body></html>



--_=_swift_v4_1459813751_afa34d50633b0a830cd6f4cde61f8f75_=_--"""

HIPCHAT_MENTION_IN_ROOM = """To: "" <paul_hamm@example.com>
Subject: Paul Hammant mentioned you in the room "Hammant"
Message-ID: <c67a9a80cb06298a0f2e0640e1f668c4@localhost>
Date: Mon, 4 Apr 2016 23:45:40 +0000
From: HipChat <donotreply@hipchat.com>
Reply-To: Paul Hammant <paul_hamm@example.com>
Content-Type: multipart/alternative;
 boundary="_=_swift_v4_1459813540_7a9621b909dae12bbf328c18ebf028b2_=_"
MIME-Version: 1.0

--_=_swift_v4_1459813540_7a9621b909dae12bbf328c18ebf028b2_=_
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable


Hi test2,

Paul Hammant just mentioned you in the room Hammant but you're offline:
=20=20
  [7:45 PM] Paul Hammant: @test2 you suck


---
To change your notification preferences: https://www.hipchat.com/account/no=
tifications.
This message was intended for paul_hamm@example.com. If this was in error,
please contact us (https://www.hipchat.com/contact)
or opt out (https://www.hipchat.com/opt_out?email=3Dpaul_hamm%40example.com=
&token=3D49a33e4b536ac701deaac4e3c076aa3e9d98c62b).

--_=_swift_v4_1459813540_7a9621b909dae12bbf328c18ebf028b2_=_
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"><?xml encodi=
ng=3D"utf-8"><html><head>
<meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8"><t=
itle>Atlassian HipChat</title></head><body style=3D"box-sizing: border-box;=
 height: 100%; width: 100%;">
<table class=3D"container wrapper_shrink" width=3D"640" cellpadding=3D"0" c=
ellspacing=3D"0" border=3D"0" bgcolor=3D"#f5f5f5" style=3D"_padding: 20px; =
padding: 3%;"><tr><td valign=3D"top">
        <table id=3D"email_header" class=3D"table_shrink" width=3D"600" cel=
lpadding=3D"0" cellspacing=3D"0" border=3D"0" style=3D"width: 100% !importa=
nt;"><tr><td>
              <a href=3D"https://www.hipchat.com/people/show/2106527?utm_me=
dium=3Demail&amp;utm_source=3Droom_mention" style=3D"cursor: pointer; text-=
decoration: none;">Paul Hammant</a>
            just mentioned you in the room
      <a href=3D"https://www.hipchat.com/rooms/show/1484371?utm_medium=3Dem=
ail&amp;utm_source=3Droom_mention" style=3D"cursor: pointer; text-decoratio=
n: none;">Hammant</a>
      but you're offline:    </td>
  </tr></table><table id=3D"email_content" class=3D"inner-container table_s=
hrink" style=3D"-khtml-border-radius: 6px; -moz-border-radius: 6px; -webkit=
-border-radius: 6px; border: 1px solid #dadada; border-radius: 6px; width: =
100% !important; margin-top: 15px;" width=3D"600" cellpadding=3D"0" cellspa=
cing=3D"0" border=3D"0" bgcolor=3D"#ffffff"><tr><td class=3D"td top-spacer"=
 valign=3D"top" style=3D"font-size: 15px; line-height: 4px; padding-left: 2=
0px; padding-right: 10px !important;">
        &nbsp;
      </td>
    </tr><tr><td>
          <div id=3D"chats" class=3D"history_container history_email" style=
=3D"padding-right: 0px !important;">
                            <div class=3D"hc-chat-row hc-msg-nocolor" style=
=3D"border-bottom: 1px solid #efefef; box-sizing: border-box; display: tabl=
e; padding: 0; width: 600px !important; max-width: 600px !important;">
    <a name=3D"078141ad-2547-4cfc-a651-309c2a865692" style=3D"cursor: point=
er; text-decoration: none;"></a>

      <div class=3D"hc-chat-from" style=3D"display: table-cell; font-size: =
13px; margin-bottom: 15px; margin-top: 15px; color: #888; max-width: 100px;=
 overflow: hidden; text-align: right; text-overflow: ellipsis; vertical-ali=
gn: top; white-space: nowrap; width: 100px; padding: 10px 0 10px 10px;">Pau=
l Hammant</div>
 =20
    <div class=3D"hc-chat-msg" style=3D"display: table-cell; font-size: 13p=
x; margin-bottom: 15px; margin-top: 15px; line-height: 20px; padding: 10px;=
 flex: 1;">
            <div style=3D"display: table-cell; font-size: 13px; margin-bott=
om: 15px; margin-top: 15px;">
      <span class=3D"atTag atTagMe" style=3D"-moz-border-radius: 4px; -webk=
it-border-radius: 4px; background-color: #EFEFEF; border: 1px solid #4783BF=
; border-radius: 4px; display: inline-block; padding: 0 3px; background: #4=
282C1 url(/img/at_bg.png) repeat-x; color: #fff;">@test2</span> you suck   =
 </div>

      </div>

        <div class=3D"hc-chat-time" style=3D"display: table-cell; font-size=
: 10px !important; margin-bottom: 15px; margin-top: 15px; color: #888; text=
-align: right; vertical-align: top; white-space: nowrap; width: 40px; paddi=
ng: 10px 10px 10px 0;">7:45 PM</div>
  </div>


                      </div>
          <span style=3D"color: #fff; font-size: 10px;">EFxvodZ9PQy8GVU</sp=
an>
        </td>
      </tr><tr><td class=3D"td mobile-ad" valign=3D"top" style=3D"padding-r=
ight: 10px!important; padding-left: 30px!important; line-height: 14px;">
        Get HipChat notifications on your phone! Download for
         or
        .
      </td>
    </tr><tr><td class=3D"td bottom-spacer" valign=3D"top" style=3D"font-si=
ze: 15px; line-height: 4px; padding-left: 20px; padding-right: 10px !import=
ant; padding-top: 10px;">
        &nbsp;
      </td>
    </tr></table></td>
  </tr><tr><td valign=3D"top">
      <table><tr><td width=3D"100%" class=3D"footer" style=3D"color: #99999=
9; font-family: Arial, sans-serif; font-size: 12px; line-height: 22px; padd=
ing-top: 10px; padding-left: 0px !important; padding-right: 0px !important;=
">
                        To change your notification preferences, click
              . <br>
            This message was intended for paul_hamm@example.com. If this wa=
s in error, please
               or
              . <br>
            HipChat's offices are located at 1098 Harrison St, San Francisc=
o, CA 94103 <br><br>

            Too many emails? You can .
                      </td>
          <td class=3D"logo-outer-container" rowspan=3D"2" valign=3D"top" s=
tyle=3D"padding: 0px; padding-left: 20px; vertical-align: top;">
            <table class=3D"logo-inner-container" style=3D"color: #333333;"=
><tbody><tr><td id=3D"footer_logo" style=3D"padding-top: 10px; padding-righ=
t: 0px !important;">
                  <img src=3D"http://image.mailer.atlassian.com/lib/fec2157=
377620c74/m/3/hipchat_email_logo_footer.png" width=3D"119px" height=3D"38px=
"></td>
              </tr></tbody></table></td>
        </tr></table></td>
  </tr></table>
</body></html>



--_=_swift_v4_1459813540_7a9621b909dae12bbf328c18ebf028b2_=_--"""