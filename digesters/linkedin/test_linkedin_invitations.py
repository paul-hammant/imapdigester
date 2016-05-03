import sys
from unittest import TestCase

from mock import Mock, call
from mockextras import stub

from digesters.digestion_processor import DigestionProcessor
from digesters.linkedin.linkedin_invitation_digester import LinkedinInvitationDigester

MAIL_HDR = """From: "Linkedin" <ph@example.com>
Content-Transfer-Encoding: 8bit
Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY-5678"
MIME-Version: 1.0
This is a multi-part message in MIME format.
-----NOTIFICATION_BOUNDARY-5678
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: 8bit


"""


class InvitationsStore(object):

    def __init__(self, cls=object):
        self._cls = cls
        self.invitations = None

    def __eq__(self, other):
        self.invitations = other
        return True

    def __ne__(self, other):
        return False

    def __repr__(self):
        return "InvitationsStore(..)"


class TestLinkedinInvitations(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestLinkedinInvitations, self).__init__(methodName)
        reload(sys)
        sys.setdefaultencoding('utf8')

    def test_two_related_invitations_can_be_rolled_up(self):

        expected_payload = """<html><body><span>You have previously read invitations up to: Apr 01 2016 06:13 PM</span>
<table>
  <tr style="background-color: #acf;">
    <th colspan="2">Invitations</th>
  </tr>
          <tr style="">
    <td><img style="max-width:100px;height:auto" src="https://upload.wikimedia.org/wikipedia/commons/8/85/Border_collie.jpg"/></td>
    <td>
      <strong>Michael McAuliffe</strong><br>
      Hi Paul,<br/>
I\'d like to join your LinkedIn network.<br/>
Michael McAuliffe<br/>
Managing Director<br/>
View profile: https://www.linkedin.com/comm/profile/view?id=AAsAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&authType=name&authToken=eAsV&invAcpt=2197625_I6132985453227360256_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir<br/>
<br>
      <a href="https://www.linkedin.com/comm/people/invite-accept?mboxid=I6132985453227360256_500&sharedKey=48j6iM8P&fr=false&invitationId=6132985418842456064&fe=true&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta-null-1b3p5%7Einqenmmy%7Eir">Accept Invitation</a>
      <a href="https://www.linkedin.com/comm/profile/view?id=AAsAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&authType=name&authToken=eAsV&invAcpt=2197625_I6132985453227360256_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir">View Profile</a>
    </td>
  </tr>          <tr style="background-color: #def;">
    <td><img style="max-width:100px;height:auto" src="https://upload.wikimedia.org/wikipedia/commons/8/85/Border_collie.jpg"/></td>
    <td>
      <strong>Foo Bar</strong><br>
      Hi Paul,<br/>
I\'d like to join your LinkedIn network.<br/>
FOO BAR<br/>
Vice President<br/>
View profile: https://www.linkedin.com/comm/profile/view?id=AAsAAAFlvJcBCnnIlLvQhDO6ZBU5rdb7fAb_-IU&authType=name&authToken=95up&invAcpt=2197625_I6132926076281774083_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einq68641%7E1h<br/>
<br>
      <a href="https://www.linkedin.com/comm/people/invite-accept?mboxid=I6132926076281774083_500&sharedKey=w447gWge&fr=false&invitationId=6132926046288310272&fe=true&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta-null-1b3p5%7Einq68641%7E1h">Accept Invitation</a>
      <a href="https://www.linkedin.com/comm/profile/view?id=AAsAAAFlvJcBCnnIlLvQhDO6ZBU5rdb7fAb_-IU&authType=name&authToken=95up&invAcpt=2197625_I6132926076281774083_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einq68641%7E1h">View Profile</a>
    </td>
  </tr>          <tr><td colspan="2" style="border-bottom: 1pt solid red; border-top: 1pt solid red;"><center>^ New Invitations Since You Last Checked ^</center></td></tr>          <tr style="">
    <td><img style="max-width:100px;height:auto" src="https://upload.wikimedia.org/wikipedia/commons/8/85/Border_collie.jpg"/></td>
    <td>
      <strong>Aaaa Bbbb</strong><br>
      Hi Paul,<br/>
I\'d like to join your LinkedIn network.<br/>
Aaaa Bbbb<br/>
Managing Director<br/>
View profile: https://www.linkedin.com/comm/profile/view?id=AAsAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&authType=name&authToken=eAsV&invAcpt=2197625_I6132985453227360256_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir<br/>
<br>
      <a href="https://www.linkedin.com/comm/people/invite-accept?mboxid=I6132985453227360256_500&sharedKey=48j6iM8P&fr=false&invitationId=6132985418842456064&fe=true&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta-null-1b3p5%7Einqenmmy%7Eir">Accept Invitation</a>
      <a href="https://www.linkedin.com/comm/profile/view?id=AAsAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&authType=name&authToken=eAsV&invAcpt=2197625_I6132985453227360256_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir">View Profile</a>
    </td>
  </tr>
</table></body></html>"""

        notification_store = {}

        final_invitations_store = InvitationsStore()

        store_writer = Mock()
        store_writer.get_from_binary.side_effect = stub(
            (call('linkedin-invitations'), notification_store),
            (call('most-recently-seen'), 1459548811)
        )
        store_writer.store_as_binary.side_effect = stub(
            (call('linkedin-invitations', final_invitations_store), True),
            (call('most-recently-seen', 1459548811), True)
        )

        expected_message = ("Subject: Invitation Digest: 1 new invitation(s)\n" + MAIL_HDR + expected_payload + \
                           "\n\n-----NOTIFICATION_BOUNDARY-5678")

        digest_inbox_proxy = Mock()
        digest_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
        digest_inbox_proxy.append.side_effect = stub((call(expected_message), True))

        digesters = []
        digester = LinkedinInvitationDigester(store_writer)  ## What we are testing
        digester.notification_boundary_rand = "-5678"  # no random number for the email's notification boundary
        digesters.append(digester)

        digestion_processor = DigestionProcessor(None, None, digesters, False, "ph@example.com", False, "INBOX")

        unmatched_to_move = []
        to_delete_from_notification_folder = []

        notification_2_content = INCOMING_1.replace("Michael McAuliffe", "Aaaa Bbbb").replace("2 May 2016", "1 May 2016")

        digestion_processor.process_incoming_notification(1234, digesters, INCOMING_1, to_delete_from_notification_folder, unmatched_to_move, False)
        digestion_processor.process_incoming_notification(1235, digesters, notification_2_content, to_delete_from_notification_folder, unmatched_to_move, False)
        digestion_processor.process_incoming_notification(1236, digesters, FOOBAR, to_delete_from_notification_folder, unmatched_to_move, False)

        digester.rewrite_digest_emails(digest_inbox_proxy, has_previous_message=True,
                                       previously_seen=False, sender_to_implicate="ph@example.com")

        self.assertEquals(digest_inbox_proxy.mock_calls, [call.delete_previous_message(), call.append(expected_message)])

        calls = store_writer.mock_calls
        self.assertEquals(calls, [
            call.get_from_binary('linkedin-invitations'),
            call.get_from_binary('most-recently-seen'),
            call.store_as_binary('linkedin-invitations',
                                 {1462203530: {
                                     u'spiel': u"Hi Paul,\nI'd like to join your LinkedIn network.\nFOO BAR\nVice President\nView profile: https://www.linkedin.com/comm/profile/view?id=AAsAAAFlvJcBCnnIlLvQhDO6ZBU5rdb7fAb_-IU&authType=name&authToken=95up&invAcpt=2197625_I6132926076281774083_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einq68641%7E1h\n",
                                     u'accept_url': u'https://www.linkedin.com/comm/people/invite-accept?mboxid=I6132926076281774083_500&sharedKey=w447gWge&fr=false&invitationId=6132926046288310272&fe=true&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta-null-1b3p5%7Einq68641%7E1h',
                                     u'who': 'Foo Bar',
                                     u'img_src': u'https://upload.wikimedia.org/wikipedia/commons/8/85/Border_collie.jpg',
                                     u'profile_url': u'https://www.linkedin.com/comm/profile/view?id=AAsAAAFlvJcBCnnIlLvQhDO6ZBU5rdb7fAb_-IU&authType=name&authToken=95up&invAcpt=2197625_I6132926076281774083_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einq68641%7E1h'},
                                  1462131286: {
                                      u'accept_url': u'https://www.linkedin.com/comm/people/invite-accept?mboxid=I6132985453227360256_500&sharedKey=48j6iM8P&fr=false&invitationId=6132985418842456064&fe=true&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta-null-1b3p5%7Einqenmmy%7Eir',
                                      u'line_here': True, u'who': 'Aaaa Bbbb',
                                      u'spiel': u"Hi Paul,\nI'd like to join your LinkedIn network.\nAaaa Bbbb\nManaging Director\nView profile: https://www.linkedin.com/comm/profile/view?id=AAsAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&authType=name&authToken=eAsV&invAcpt=2197625_I6132985453227360256_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir\n",
                                      u'img_src': u'https://upload.wikimedia.org/wikipedia/commons/8/85/Border_collie.jpg',
                                      u'profile_url': u'https://www.linkedin.com/comm/profile/view?id=AAsAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&authType=name&authToken=eAsV&invAcpt=2197625_I6132985453227360256_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir'},
                                  1462217686: {
                                      u'spiel': u"Hi Paul,\nI'd like to join your LinkedIn network.\nMichael McAuliffe\nManaging Director\nView profile: https://www.linkedin.com/comm/profile/view?id=AAsAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&authType=name&authToken=eAsV&invAcpt=2197625_I6132985453227360256_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir\n",
                                      u'accept_url': u'https://www.linkedin.com/comm/people/invite-accept?mboxid=I6132985453227360256_500&sharedKey=48j6iM8P&fr=false&invitationId=6132985418842456064&fe=true&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-0-accept%7Ecta-null-1b3p5%7Einqenmmy%7Eir',
                                      u'who': 'Michael McAuliffe',
                                      u'img_src': u'https://upload.wikimedia.org/wikipedia/commons/8/85/Border_collie.jpg',
                                      u'profile_url': u'https://www.linkedin.com/comm/profile/view?id=AAsAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&authType=name&authToken=eAsV&invAcpt=2197625_I6132985453227360256_500&midToken=AQHQ1w5V4ws4wA&trk=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta&trkEmail=eml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir'}}
                                 ),
            call.store_as_binary('most-recently-seen', 1459548811)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(str(to_delete_from_notification_folder), "[1234, 1235, 1236]")
        self.assertEquals(len(final_invitations_store.invitations), 3)


INCOMING_1 = """From: Michael McAuliffe <invitations@linkedin.com>
Message-ID: <543052688.1354069.1462217686519.JavaMail.app@lva1-app3333.prod.linkedin.com>
Subject: Paul, please add me to your LinkedIn network
Content-Type: multipart/alternative;
	boundary="----=_Part_1354067_596425972.1462217686511"
To: Paul Hammant <Paul@Hammant.org>
Date: Mon, 2 May 2016 19:34:46 +0000 (UTC)
MIME-Version: 1.0

------=_Part_1354067_596425972.1462217686511
Content-Type: text/plain;charset=UTF-8
Content-Transfer-Encoding: quoted-printable
Content-ID: text-body

Hi Paul,

I'd like to join your LinkedIn network.

Michael McAuliffe
Managing Director

View profile: https://www.linkedin.com/comm/profile/view?id=3DAAsAAAJUVTYBW=
kKAZwppmyYBjwgm1AI0nKRyTwA&authType=3Dname&authToken=3DeAsV&invAcpt=3D21976=
25_I6132985453227360256_500&midToken=3DAQHQ1w5V4ws4wA&trk=3Deml-email_m2m_i=
nvite_single_01-hero-3-prof%7Ecta&trkEmail=3Deml-email_m2m_invite_single_01=
-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir

Accept: https://www.linkedin.com/comm/people/invite-accept?mboxid=3DI613298=
5453227360256_500&sharedKey=3D48j6iM8P&fr=3Dfalse&invitationId=3D6132985418=
842456064&fe=3Dtrue&midToken=3DAQHQ1w5V4ws4wA&trk=3Deml-email_m2m_invite_si=
ngle_01-hero-0-accept%7Ecta&trkEmail=3Deml-email_m2m_invite_single_01-hero-=
0-accept%7Ecta-null-1b3p5%7Einqenmmy%7Eir

.....................................

Unsubscribe: https://www.linkedin.com/e/v2?e=3D1b3p5-inqenmmy-ir&t=3Dlun&mi=
dToken=3DAQHQ1w5V4ws4wA&ek=3Demail_m2m_invite_single_01&li=3D10&m=3Dunsub&t=
s=3Dunsub&loid=3DAQEYGYigaB9xLgAAAVRy9zzAiKA6TSjt5qtue7m6n7C7x-67Bc2z6DzP-H=
IHX3HVoujjV4VE5dFOCqIvFw&eid=3D1b3p5-inqenmmy-ir

Help: https://www.linkedin.com/e/v2?e=3D1b3p5-inqenmmy-ir&a=3DcustomerServi=
ceUrl&midToken=3DAQHQ1w5V4ws4wA&ek=3Demail_m2m_invite_single_01&li=3D9&m=3D=
footer&ts=3Dhelp&articleId=3D67


You are receiving Invitation emails.

This email was intended for Paul Hammant (Senior Director of Engineering at=
 HedgeServ).
Learn why we included this: https://www.linkedin.com/e/v2?e=3D1b3p5-inqenmm=
y-ir&a=3DcustomerServiceUrl&midToken=3DAQHQ1w5V4ws4wA&ek=3Demail_m2m_invite=
_single_01&articleId=3D4788

=C2=A9 2016 LinkedIn Corporation, 2029 Stierlin Court, Mountain View CA 940=
43. LinkedIn and the LinkedIn logo are registered trademarks of LinkedIn.
------=_Part_1354067_596425972.1462217686511
Content-Type: text/html;charset=UTF-8
Content-Transfer-Encoding: quoted-printable
Content-ID: html-body

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.=
w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns=3D"http://www.w3.=
org/1999/xhtml" lang=3D"en" xml:lang=3D"en"><head>
<meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8"> <=
meta name=3D"HandheldFriendly" content=3D"true"> <meta name=3D"viewport" co=
ntent=3D"width=3Ddevice-width; initial-scale=3D0.666667; maximum-scale=3D0.=
666667; user-scalable=3D0"> <meta name=3D"viewport" content=3D"width=3Ddevi=
ce-width"> <title></title> <!--[if mso]><style type=3D"text/css">body {font=
-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;}.phoenix-email-con=
tainer {width: 512px !important;}</style><![endif]--> <!--[if IE]><style ty=
pe=3D"text/css">.phoenix-email-container {width: 512px !important;}</style>=
<![endif]--> <style type=3D"text/css">@media only screen and (max-width:32e=
m) { .phoenix-email-container { width:100% !important; } } @media only scre=
en and (max-width:20em) {} @media only screen and (max-device-width:30em) {=
} @media screen and (device-width:30em) and (device-height:22.5em), screen =
and (device-width:22.5em) and (device-height:30em), screen and (device-widt=
h:20em) and (device-height:15em) {} @media screen and (-webkit-min-device-p=
ixel-ratio:0) {} @media screen and (max-device-width:25.88em) and (max-devi=
ce-height:48.5em) {} </style> </head> <body style=3D"padding:0;margin:0 aut=
o;-webkit-text-size-adjust:100%;width:100% !important;-ms-text-size-adjust:=
100%;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;"> <div style=
=3D"overflow:hidden;color:transparent;visibility:hidden;mso-hide:all;width:=
0;font-size:0;opacity:0;height:0;"> Hi Paul, I'd like to join your LinkedIn=
 network. </div> <table align=3D"center" border=3D"0" cellspacing=3D"0" cel=
lpadding=3D"0" width=3D"100%" bgcolor=3D"#EDF0F3" style=3D"background-color=
:#EDF0F3;table-layout:fixed;-webkit-text-size-adjust:100%;mso-table-rspace:=
0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td alig=
n=3D"center" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;ms=
o-table-lspace:0pt;-ms-text-size-adjust:100%;"> <center style=3D"width:100%=
;"> <table border=3D"0" class=3D"phoenix-email-container" cellspacing=3D"0"=
 cellpadding=3D"0" width=3D"512" bgcolor=3D"#FFFFFF" style=3D"background-co=
lor:#FFFFFF;margin:0 auto;max-width:512px;-webkit-text-size-adjust:100%;mso=
-table-rspace:0pt;width:inherit;mso-table-lspace:0pt;-ms-text-size-adjust:1=
00%;"> <tbody> <tr> <td bgcolor=3D"#F6F8FA" style=3D"background-color:#F6F8=
FA;padding:12px;-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-tabl=
e-lspace:0pt;-ms-text-size-adjust:100%;border-bottom:1px solid #ECECEC;"> <=
table border=3D"0" cellspacing=3D"0" cellpadding=3D"0" width=3D"100%" style=
=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;width:100% !importan=
t;mso-table-lspace:0pt;-ms-text-size-adjust:100%;min-width:100% !important;=
"> <tbody> <tr> <td align=3D"left" valign=3D"middle" style=3D"-webkit-text-=
size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-ad=
just:100%;"><a href=3D"https://www.linkedin.com/comm/nhome/?midToken=3DAQHQ=
1w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-header-4-home&amp;trkEm=
ail=3Deml-email_m2m_invite_single_01-header-4-home-null-1b3p5%7Einqenmmy%7E=
ir" style=3D"cursor:pointer;color:#008CC9;-webkit-text-size-adjust:100%;dis=
play:inline-block;text-decoration:none;-ms-text-size-adjust:100%;"> <img al=
t=3D"LinkedIn" border=3D"0" src=3D"https://static.licdn.com/scds/common/u/i=
mages/email/phoenix/logos/logo_phoenix_header_blue_78x66_v1.png" height=3D"=
34" width=3D"40" style=3D"outline:none;-ms-interpolation-mode:bicubic;color=
:#FFFFFF;text-decoration:none;"></a></td> <td valign=3D"middle" width=3D"10=
0%" align=3D"right" style=3D"padding:0 0 0 10px;-webkit-text-size-adjust:10=
0%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"><a=
 href=3D"https://www.linkedin.com/comm/profile/view?id=3DAAsAAAAhiHkB2Xl5Qq=
Gw01CP-K2o5AvAA-e9my0&amp;midToken=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-email_m2m=
_invite_single_01-header-6-profile&amp;trkEmail=3Deml-email_m2m_invite_sing=
le_01-header-6-profile-null-1b3p5%7Einqenmmy%7Eir" style=3D"cursor:pointer;=
margin:0;color:#008CC9;-webkit-text-size-adjust:100%;display:inline-block;t=
ext-decoration:none;-ms-text-size-adjust:100%;"> <span style=3D"word-wrap:b=
reak-word;color:#4C4C4C;word-break:break-word;font-weight:400;-ms-word-brea=
k:break-all;font-size:14px;line-height:1.429;overflow-wrap:break-word;">Pau=
l Hammant</span></a></td> <td valign=3D"middle" width=3D"40" style=3D"-webk=
it-text-size-adjust:100%;mso-table-rspace:0pt;padding-left:10px;mso-table-l=
space:0pt;-ms-text-size-adjust:100%;"> <a href=3D"https://www.linkedin.com/=
comm/profile/view?id=3DAAsAAAAhiHkB2Xl5QqGw01CP-K2o5AvAA-e9my0&amp;midToken=
=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-header-6-profile=
&amp;trkEmail=3Deml-email_m2m_invite_single_01-header-6-profile-null-1b3p5%=
7Einqenmmy%7Eir" style=3D"border-radius:50%;cursor:pointer;color:#008CC9;-w=
ebkit-text-size-adjust:100%;display:inline-block;text-decoration:none;-ms-t=
ext-size-adjust:100%;"><img alt=3D"" border=3D"0" height=3D"36" width=3D"36=
" src=3D"https://media.licdn.com/mpr/mpr/shrinknp_100_100/p/6/005/095/3cc/2=
4a8290.jpg" style=3D"border-radius:50%;outline:none;-ms-interpolation-mode:=
bicubic;color:#FFFFFF;text-decoration:none;"></a></td> <td width=3D"1" styl=
e=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0p=
t;-ms-text-size-adjust:100%;">&nbsp;</td> </tr> </tbody> </table></td> </tr=
> <tr> <td style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-=
table-lspace:0pt;-ms-text-size-adjust:100%;"> <table border=3D"0" cellspaci=
ng=3D"0" cellpadding=3D"0" width=3D"100%" style=3D"-webkit-text-size-adjust=
:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"=
> <tbody> <tr> <td style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:=
0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <table border=3D"0" c=
ellspacing=3D"0" cellpadding=3D"0" width=3D"100%" style=3D"-webkit-text-siz=
e-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjus=
t:100%;"> <tbody> <tr> <td style=3D"padding:24px 24px 36px 24px;-webkit-tex=
t-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-=
adjust:100%;"> <table border=3D"0" cellspacing=3D"0" cellpadding=3D"0" widt=
h=3D"100%" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-=
table-lspace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td align=3D"lef=
t" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-ls=
pace:0pt;-ms-text-size-adjust:100%;"> <p style=3D"margin:0;word-wrap:break-=
word;color:#4C4C4C;word-break:break-word;font-weight:400;-ms-word-break:bre=
ak-all;font-size:16px;line-height:1.5;overflow-wrap:break-word;">Hi Paul, I=
'd like to join your LinkedIn network.</p></td> </tr> <tr> <td align=3D"lef=
t" style=3D"padding:22px 0 16px 0;-webkit-text-size-adjust:100%;mso-table-r=
space:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <table border=
=3D"0" cellspacing=3D"0" cellpadding=3D"0" width=3D"100%" style=3D"-webkit-=
text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-si=
ze-adjust:100%;"> <tbody> <tr> <td valign=3D"top" style=3D"padding:0 15px 0=
 0;-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;=
-ms-text-size-adjust:100%;"><a href=3D"https://www.linkedin.com/comm/profil=
e/view?id=3DAAsAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&amp;authType=3Dname&amp=
;authToken=3DeAsV&amp;invAcpt=3D2197625_I6132985453227360256_500&amp;midTok=
en=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-hero-1-prof%7E=
photo&amp;trkEmail=3Deml-email_m2m_invite_single_01-hero-1-prof%7Ephoto-nul=
l-1b3p5%7Einqenmmy%7Eir" style=3D"cursor:pointer;color:#008CC9;-webkit-text=
-size-adjust:100%;display:inline-block;text-decoration:none;-ms-text-size-a=
djust:100%;"><img src=3D"https://media.licdn.com/mpr/mpr/shrinknp_100_100/A=
AEAAQAAAAAAAALZAAAAJDFhMTQ5YTQ4LWUxNmYtNDhhNy05ZjIyLWI3NTdiNzZkZDFmNw.jpg" =
alt=3D"" height=3D"70" width=3D"70" style=3D"border-radius:50%;outline:none=
;-ms-interpolation-mode:bicubic;color:#FFFFFF;text-decoration:none;"></a></=
td> <td valign=3D"top" width=3D"100%" style=3D"-webkit-text-size-adjust:100=
%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"><a =
href=3D"https://www.linkedin.com/comm/profile/view?id=3DAAsAAAJUVTYBWkKAZwp=
pmyYBjwgm1AI0nKRyTwA&amp;authType=3Dname&amp;authToken=3DeAsV&amp;invAcpt=
=3D2197625_I6132985453227360256_500&amp;midToken=3DAQHQ1w5V4ws4wA&amp;trk=
=3Deml-email_m2m_invite_single_01-hero-2-prof%7Ename&amp;trkEmail=3Deml-ema=
il_m2m_invite_single_01-hero-2-prof%7Ename-null-1b3p5%7Einqenmmy%7Eir" styl=
e=3D"cursor:pointer;color:#008CC9;-webkit-text-size-adjust:100%;display:inl=
ine-block;text-decoration:none;-ms-text-size-adjust:100%;"> <span style=3D"=
word-wrap:break-word;color:#262626;word-break:break-word;font-weight:700;-m=
s-word-break:break-all;font-size:16px;line-height:1.5;overflow-wrap:break-w=
ord;">Michael McAuliffe</span></a> <p style=3D"margin:0;word-wrap:break-wor=
d;color:#737373;word-break:break-word;font-weight:400;-ms-word-break:break-=
all;font-size:14px;line-height:1.429;overflow-wrap:break-word;">Managing Di=
rector</p> <p style=3D"margin:0;color:#737373;font-weight:400;font-size:14p=
x;line-height:1.429;">Charlotte, North Carolina Area</p></td> </tr> </tbody=
> </table></td> </tr> <tr> <td dir=3D"rtl" align=3D"left" style=3D"-webkit-=
text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-si=
ze-adjust:100%;direction:rtl !important;text-align:left !important;"> <!--[=
if mso]><table border=3D"0" cellpadding=3D"0" cellspacing=3D"0" width=3D"au=
to"><tr><td style=3D"padding:12px 0 0 0;"><![endif]--><span style=3D"displa=
y:inline-block;margin-top:12px;"> <table border=3D"0" cellpadding=3D"0" cel=
lspacing=3D"0" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;=
display:inline-block;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <tbo=
dy> <tr> <td align=3D"center" valign=3D"middle" style=3D"-webkit-text-size-=
adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:=
100%;"><a href=3D"https://www.linkedin.com/comm/people/invite-accept?mboxid=
=3DI6132985453227360256_500&amp;sharedKey=3D48j6iM8P&amp;fr=3Dfalse&amp;inv=
itationId=3D6132985418842456064&amp;fe=3Dtrue&amp;midToken=3DAQHQ1w5V4ws4wA=
&amp;trk=3Deml-email_m2m_invite_single_01-hero-0-accept%7Ecta&amp;trkEmail=
=3Deml-email_m2m_invite_single_01-hero-0-accept%7Ecta-null-1b3p5%7Einqenmmy=
%7Eir" target=3D"_blank" style=3D"cursor:pointer;word-wrap:normal;color:#00=
8CC9;word-break:normal;white-space:nowrap;-webkit-text-size-adjust:100%;dis=
play:block;text-decoration:none;-ms-text-size-adjust:100%;overflow-wrap:nor=
mal;"> <table border=3D"0" cellspacing=3D"0" cellpadding=3D"0" width=3D"aut=
o" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-ls=
pace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td bgcolor=3D"#008CC9" =
style=3D"padding:6px 16px;color:#FFFFFF;-webkit-text-size-adjust:100%;font-=
weight:500;font-size:16px;-ms-text-size-adjust:100%;border-color:#008CC9;ba=
ckground-color:#008CC9;border-radius:2px;mso-table-rspace:0pt;mso-table-lsp=
ace:0pt;border-width:1px;border-style:solid;"><a href=3D"https://www.linked=
in.com/comm/people/invite-accept?mboxid=3DI6132985453227360256_500&amp;shar=
edKey=3D48j6iM8P&amp;fr=3Dfalse&amp;invitationId=3D6132985418842456064&amp;=
fe=3Dtrue&amp;midToken=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_sing=
le_01-hero-0-accept%7Ecta&amp;trkEmail=3Deml-email_m2m_invite_single_01-her=
o-0-accept%7Ecta-null-1b3p5%7Einqenmmy%7Eir" target=3D"_blank" style=3D"cur=
sor:pointer;color:#FFFFFF;-webkit-text-size-adjust:100%;display:inline-bloc=
k;text-decoration:none;-ms-text-size-adjust:100%;">Accept</a></td> </tr> </=
tbody> </table></a></td> </tr> </tbody> </table></span> <!--[if mso]></td><=
td style=3D"padding-top:12px;"><![endif]--><span style=3D"display:inline-bl=
ock;margin-top:12px;margin-right:12px;"> <table border=3D"0" cellpadding=3D=
"0" cellspacing=3D"0" style=3D"-webkit-text-size-adjust:100%;mso-table-rspa=
ce:0pt;display:inline-block;mso-table-lspace:0pt;-ms-text-size-adjust:100%;=
"> <tbody> <tr> <td align=3D"center" valign=3D"middle" style=3D"-webkit-tex=
t-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-=
adjust:100%;"><a href=3D"https://www.linkedin.com/comm/profile/view?id=3DAA=
sAAAJUVTYBWkKAZwppmyYBjwgm1AI0nKRyTwA&amp;authType=3Dname&amp;authToken=3De=
AsV&amp;invAcpt=3D2197625_I6132985453227360256_500&amp;midToken=3DAQHQ1w5V4=
ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-hero-3-prof%7Ecta&amp;trkEma=
il=3Deml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy=
%7Eir" target=3D"_blank" style=3D"cursor:pointer;word-wrap:normal;color:#00=
8CC9;word-break:normal;white-space:nowrap;-webkit-text-size-adjust:100%;dis=
play:block;text-decoration:none;-ms-text-size-adjust:100%;overflow-wrap:nor=
mal;"> <table border=3D"0" cellspacing=3D"0" cellpadding=3D"0" width=3D"aut=
o" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-ls=
pace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td style=3D"border-radi=
us:2px;padding:6px 16px;color:#4C4C4C;-webkit-text-size-adjust:100%;mso-tab=
le-rspace:0pt;font-weight:500;mso-table-lspace:0pt;font-size:16px;-ms-text-=
size-adjust:100%;border-color:#737373;border-width:1px;border-style:solid;"=
><a href=3D"https://www.linkedin.com/comm/profile/view?id=3DAAsAAAJUVTYBWkK=
AZwppmyYBjwgm1AI0nKRyTwA&amp;authType=3Dname&amp;authToken=3DeAsV&amp;invAc=
pt=3D2197625_I6132985453227360256_500&amp;midToken=3DAQHQ1w5V4ws4wA&amp;trk=
=3Deml-email_m2m_invite_single_01-hero-3-prof%7Ecta&amp;trkEmail=3Deml-emai=
l_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einqenmmy%7Eir" target=
=3D"_blank" style=3D"cursor:pointer;color:#4C4C4C;-webkit-text-size-adjust:=
100%;display:inline-block;text-decoration:none;-ms-text-size-adjust:100%;">=
View profile</a></td> </tr> </tbody> </table></a></td> </tr> </tbody> </tab=
le></span> <!--[if mso]></td></tr></table><![endif]--></td> </tr> </tbody> =
</table></td> </tr> </tbody> </table></td> </tr> </tbody> </table></td> </t=
r> <tr> <td style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso=
-table-lspace:0pt;-ms-text-size-adjust:100%;"> <table border=3D"0" cellspac=
ing=3D"0" cellpadding=3D"0" width=3D"100%" bgcolor=3D"#EDF0F3" align=3D"cen=
ter" style=3D"background-color:#EDF0F3;padding:0 24px;color:#999999;-webkit=
-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-s=
ize-adjust:100%;text-align:center;"> <tbody> <tr> <td align=3D"center" styl=
e=3D"padding:16px 0 0 0;-webkit-text-size-adjust:100%;mso-table-rspace:0pt;=
mso-table-lspace:0pt;-ms-text-size-adjust:100%;text-align:center;"> <table =
align=3D"center" border=3D"0" cellspacing=3D"0" cellpadding=3D"0" width=3D"=
100%" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table=
-lspace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td valign=3D"middle"=
 align=3D"center" style=3D"padding:0 0 16px 0;-webkit-text-size-adjust:100%=
;mso-table-rspace:0pt;vertical-align:middle;mso-table-lspace:0pt;-ms-text-s=
ize-adjust:100%;text-align:center;"><a href=3D"https://www.linkedin.com/e/v=
2?e=3D1b3p5-inqenmmy-ir&amp;t=3Dlun&amp;midToken=3DAQHQ1w5V4ws4wA&amp;ek=3D=
email_m2m_invite_single_01&amp;li=3D10&amp;m=3Dunsub&amp;ts=3Dunsub&amp;loi=
d=3DAQEYGYigaB9xLgAAAVRy9zzAiKA6TSjt5qtue7m6n7C7x-67Bc2z6DzP-HIHX3HVoujjV4V=
E5dFOCqIvFw&amp;eid=3D1b3p5-inqenmmy-ir" style=3D"cursor:pointer;color:#737=
373;-webkit-text-size-adjust:100%;text-decoration:underline;display:inline-=
block;-ms-text-size-adjust:100%;"> <span style=3D"color:#737373;font-weight=
:400;text-decoration:underline;font-size:12px;line-height:1.333;">Unsubscri=
be</span></a>&nbsp;&nbsp;|&nbsp;&nbsp;<a href=3D"https://www.linkedin.com/e=
/v2?e=3D1b3p5-inqenmmy-ir&amp;a=3DcustomerServiceUrl&amp;midToken=3DAQHQ1w5=
V4ws4wA&amp;ek=3Demail_m2m_invite_single_01&amp;li=3D9&amp;m=3Dfooter&amp;t=
s=3Dhelp&amp;articleId=3D67" style=3D"cursor:pointer;color:#737373;-webkit-=
text-size-adjust:100%;text-decoration:underline;display:inline-block;-ms-te=
xt-size-adjust:100%;"> <span style=3D"color:#737373;font-weight:400;text-de=
coration:underline;font-size:12px;line-height:1.333;">Help</span></a></td> =
</tr> </tbody> </table></td> </tr> <tr> <td style=3D"-webkit-text-size-adju=
st:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%=
;"> <table border=3D"0" cellspacing=3D"0" cellpadding=3D"0" width=3D"100%" =
style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspac=
e:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td align=3D"center" style=
=3D"padding:0 0 12px 0;-webkit-text-size-adjust:100%;mso-table-rspace:0pt;m=
so-table-lspace:0pt;-ms-text-size-adjust:100%;text-align:center;"> <p style=
=3D"margin:0;color:#737373;font-weight:400;font-size:12px;line-height:1.333=
;">You are receiving Invitation emails.</p></td> </tr> <tr> <td align=3D"ce=
nter" style=3D"padding:0 0 12px 0;-webkit-text-size-adjust:100%;mso-table-r=
space:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;text-align:center;=
"> <p style=3D"margin:0;word-wrap:break-word;color:#737373;word-break:break=
-word;font-weight:400;-ms-word-break:break-all;font-size:12px;line-height:1=
.333;overflow-wrap:break-word;">This email was intended for Paul Hammant (S=
enior Director of Engineering at HedgeServ). <a href=3D"https://www.linkedi=
n.com/e/v2?e=3D1b3p5-inqenmmy-ir&amp;a=3DcustomerServiceUrl&amp;midToken=3D=
AQHQ1w5V4ws4wA&amp;ek=3Demail_m2m_invite_single_01&amp;articleId=3D4788" st=
yle=3D"cursor:pointer;color:#737373;-webkit-text-size-adjust:100%;text-deco=
ration:underline;display:inline-block;-ms-text-size-adjust:100%;">Learn why=
 we included this.</a></p></td> </tr> <tr> <td align=3D"center" style=3D"pa=
dding:0 0 8px 0;-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-tabl=
e-lspace:0pt;-ms-text-size-adjust:100%;text-align:center;"><a href=3D"https=
://www.linkedin.com/comm/nhome/?midToken=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-ema=
il_m2m_invite_single_01-footer-8-home&amp;trkEmail=3Deml-email_m2m_invite_s=
ingle_01-footer-8-home-null-1b3p5%7Einqenmmy%7Eir" style=3D"cursor:pointer;=
color:#737373;-webkit-text-size-adjust:100%;text-decoration:underline;displ=
ay:inline-block;-ms-text-size-adjust:100%;"><img alt=3D"LinkedIn" border=3D=
"0" height=3D"14" src=3D"https://static.licdn.com/scds/common/u/images/emai=
l/phoenix/logos/logo_phoenix_footer_gray_197x48_v1.png" width=3D"58" style=
=3D"outline:none;-ms-interpolation-mode:bicubic;color:#FFFFFF;display:block=
;text-decoration:none;"></a></td> </tr> <tr> <td align=3D"center" style=3D"=
padding:0 0 12px 0;-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-t=
able-lspace:0pt;-ms-text-size-adjust:100%;text-align:center;"> <p style=3D"=
margin:0;color:#737373;font-weight:400;font-size:12px;line-height:1.333;">=
=C2=A9 2016 LinkedIn Corporation, 2029 Stierlin Court, Mountain View CA 940=
43. LinkedIn and the LinkedIn logo are registered trademarks of LinkedIn.</=
p></td> </tr> </tbody> </table></td> </tr> </tbody> </table></td> </tr> </t=
body> </table> </center></td> </tr> </tbody> </table> <img src=3D"http://ww=
w.linkedin.com/emimp/1b3p5-inqenmmy-ir.gif" style=3D"outline:none;-ms-inter=
polation-mode:bicubic;color:#FFFFFF;text-decoration:none;width:1px;height:1=
px;"> </body> </html>=

------=_Part_1354067_596425972.1462217686511--"""

FOOBAR = """From: Foo Bar <invitations@linkedin.com>
Message-ID: <311349338.1161874.1462203530637.JavaMail.app@lva1-app3333.prod.linkedin.com>
Subject: Paul, please add me to your LinkedIn network
Content-Type: multipart/alternative;
	boundary="----=_Part_1161867_773496138.1462203530633"
To: Paul Hammant <Paul@Hammant.org>
Date: Mon, 2 May 2016 15:38:50 +0000 (UTC)
MIME-Version: 1.0

------=_Part_1161867_773496138.1462203530633
Content-Type: text/plain;charset=UTF-8
Content-Transfer-Encoding: quoted-printable
Content-ID: text-body

Hi Paul,

I'd like to join your LinkedIn network.

FOO BAR
Vice President

View profile: https://www.linkedin.com/comm/profile/view?id=3DAAsAAAFlvJcBC=
nnIlLvQhDO6ZBU5rdb7fAb_-IU&authType=3Dname&authToken=3D95up&invAcpt=3D21976=
25_I6132926076281774083_500&midToken=3DAQHQ1w5V4ws4wA&trk=3Deml-email_m2m_i=
nvite_single_01-hero-3-prof%7Ecta&trkEmail=3Deml-email_m2m_invite_single_01=
-hero-3-prof%7Ecta-null-1b3p5%7Einq68641%7E1h

Accept: https://www.linkedin.com/comm/people/invite-accept?mboxid=3DI613292=
6076281774083_500&sharedKey=3Dw447gWge&fr=3Dfalse&invitationId=3D6132926046=
288310272&fe=3Dtrue&midToken=3DAQHQ1w5V4ws4wA&trk=3Deml-email_m2m_invite_si=
ngle_01-hero-0-accept%7Ecta&trkEmail=3Deml-email_m2m_invite_single_01-hero-=
0-accept%7Ecta-null-1b3p5%7Einq68641%7E1h

.....................................

Unsubscribe: https://www.linkedin.com/e/v2?e=3D1b3p5-inq68641-1h&t=3Dlun&mi=
dToken=3DAQHQ1w5V4ws4wA&ek=3Demail_m2m_invite_single_01&li=3D10&m=3Dunsub&t=
s=3Dunsub&loid=3DAQFdQYOv_FVJAgAAAVRyHzzTguEadC55UC3CMRW6tuWfby8cpsHi1xOrXC=
RZJ4MzTaYlDlG2VPl5Zx_ohw&eid=3D1b3p5-inq68641-1h

Help: https://www.linkedin.com/e/v2?e=3D1b3p5-inq68641-1h&a=3DcustomerServi=
ceUrl&midToken=3DAQHQ1w5V4ws4wA&ek=3Demail_m2m_invite_single_01&li=3D9&m=3D=
footer&ts=3Dhelp&articleId=3D67


You are receiving Invitation emails.

This email was intended for Paul Hammant (Senior Director of Engineering at=
 HedgeServ).
Learn why we included this: https://www.linkedin.com/e/v2?e=3D1b3p5-inq6864=
1-1h&a=3DcustomerServiceUrl&midToken=3DAQHQ1w5V4ws4wA&ek=3Demail_m2m_invite=
_single_01&articleId=3D4788

=C2=A9 2016 LinkedIn Corporation, 2029 Stierlin Court, Mountain View CA 940=
43. LinkedIn and the LinkedIn logo are registered trademarks of LinkedIn.
------=_Part_1161867_773496138.1462203530633
Content-Type: text/html;charset=UTF-8
Content-Transfer-Encoding: quoted-printable
Content-ID: html-body

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.=
w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns=3D"http://www.w3.=
org/1999/xhtml" lang=3D"en" xml:lang=3D"en"><head>
<meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8"> <=
meta name=3D"HandheldFriendly" content=3D"true"> <meta name=3D"viewport" co=
ntent=3D"width=3Ddevice-width; initial-scale=3D0.666667; maximum-scale=3D0.=
666667; user-scalable=3D0"> <meta name=3D"viewport" content=3D"width=3Ddevi=
ce-width"> <title></title> <!--[if mso]><style type=3D"text/css">body {font=
-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;}.phoenix-email-con=
tainer {width: 512px !important;}</style><![endif]--> <!--[if IE]><style ty=
pe=3D"text/css">.phoenix-email-container {width: 512px !important;}</style>=
<![endif]--> <style type=3D"text/css">@media only screen and (max-width:32e=
m) { .phoenix-email-container { width:100% !important; } } @media only scre=
en and (max-width:20em) {} @media only screen and (max-device-width:30em) {=
} @media screen and (device-width:30em) and (device-height:22.5em), screen =
and (device-width:22.5em) and (device-height:30em), screen and (device-widt=
h:20em) and (device-height:15em) {} @media screen and (-webkit-min-device-p=
ixel-ratio:0) {} @media screen and (max-device-width:25.88em) and (max-devi=
ce-height:48.5em) {} </style> </head> <body style=3D"padding:0;margin:0 aut=
o;-webkit-text-size-adjust:100%;width:100% !important;-ms-text-size-adjust:=
100%;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;"> <div style=
=3D"overflow:hidden;color:transparent;visibility:hidden;mso-hide:all;width:=
0;font-size:0;opacity:0;height:0;"> Hi Paul, I'd like to join your LinkedIn=
 network. </div> <table align=3D"center" border=3D"0" cellspacing=3D"0" cel=
lpadding=3D"0" width=3D"100%" bgcolor=3D"#EDF0F3" style=3D"background-color=
:#EDF0F3;table-layout:fixed;-webkit-text-size-adjust:100%;mso-table-rspace:=
0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td alig=
n=3D"center" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;ms=
o-table-lspace:0pt;-ms-text-size-adjust:100%;"> <center style=3D"width:100%=
;"> <table border=3D"0" class=3D"phoenix-email-container" cellspacing=3D"0"=
 cellpadding=3D"0" width=3D"512" bgcolor=3D"#FFFFFF" style=3D"background-co=
lor:#FFFFFF;margin:0 auto;max-width:512px;-webkit-text-size-adjust:100%;mso=
-table-rspace:0pt;width:inherit;mso-table-lspace:0pt;-ms-text-size-adjust:1=
00%;"> <tbody> <tr> <td bgcolor=3D"#F6F8FA" style=3D"background-color:#F6F8=
FA;padding:12px;-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-tabl=
e-lspace:0pt;-ms-text-size-adjust:100%;border-bottom:1px solid #ECECEC;"> <=
table border=3D"0" cellspacing=3D"0" cellpadding=3D"0" width=3D"100%" style=
=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;width:100% !importan=
t;mso-table-lspace:0pt;-ms-text-size-adjust:100%;min-width:100% !important;=
"> <tbody> <tr> <td align=3D"left" valign=3D"middle" style=3D"-webkit-text-=
size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-ad=
just:100%;"><a href=3D"https://www.linkedin.com/comm/nhome/?midToken=3DAQHQ=
1w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-header-4-home&amp;trkEm=
ail=3Deml-email_m2m_invite_single_01-header-4-home-null-1b3p5%7Einq68641%7E=
1h" style=3D"cursor:pointer;color:#008CC9;-webkit-text-size-adjust:100%;dis=
play:inline-block;text-decoration:none;-ms-text-size-adjust:100%;"> <img al=
t=3D"LinkedIn" border=3D"0" src=3D"https://static.licdn.com/scds/common/u/i=
mages/email/phoenix/logos/logo_phoenix_header_blue_78x66_v1.png" height=3D"=
34" width=3D"40" style=3D"outline:none;-ms-interpolation-mode:bicubic;color=
:#FFFFFF;text-decoration:none;"></a></td> <td valign=3D"middle" width=3D"10=
0%" align=3D"right" style=3D"padding:0 0 0 10px;-webkit-text-size-adjust:10=
0%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"><a=
 href=3D"https://www.linkedin.com/comm/profile/view?id=3DAAsAAAAhiHkB2Xl5Qq=
Gw01CP-K2o5AvAA-e9my0&amp;midToken=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-email_m2m=
_invite_single_01-header-6-profile&amp;trkEmail=3Deml-email_m2m_invite_sing=
le_01-header-6-profile-null-1b3p5%7Einq68641%7E1h" style=3D"cursor:pointer;=
margin:0;color:#008CC9;-webkit-text-size-adjust:100%;display:inline-block;t=
ext-decoration:none;-ms-text-size-adjust:100%;"> <span style=3D"word-wrap:b=
reak-word;color:#4C4C4C;word-break:break-word;font-weight:400;-ms-word-brea=
k:break-all;font-size:14px;line-height:1.429;overflow-wrap:break-word;">Pau=
l Hammant</span></a></td> <td valign=3D"middle" width=3D"40" style=3D"-webk=
it-text-size-adjust:100%;mso-table-rspace:0pt;padding-left:10px;mso-table-l=
space:0pt;-ms-text-size-adjust:100%;"> <a href=3D"https://www.linkedin.com/=
comm/profile/view?id=3DAAsAAAAhiHkB2Xl5QqGw01CP-K2o5AvAA-e9my0&amp;midToken=
=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-header-6-profile=
&amp;trkEmail=3Deml-email_m2m_invite_single_01-header-6-profile-null-1b3p5%=
7Einq68641%7E1h" style=3D"border-radius:50%;cursor:pointer;color:#008CC9;-w=
ebkit-text-size-adjust:100%;display:inline-block;text-decoration:none;-ms-t=
ext-size-adjust:100%;"><img alt=3D"" border=3D"0" height=3D"36" width=3D"36=
" src=3D"https://media.licdn.com/mpr/mpr/shrinknp_100_100/p/6/005/095/3cc/2=
4a8290.jpg" style=3D"border-radius:50%;outline:none;-ms-interpolation-mode:=
bicubic;color:#FFFFFF;text-decoration:none;"></a></td> <td width=3D"1" styl=
e=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0p=
t;-ms-text-size-adjust:100%;">&nbsp;</td> </tr> </tbody> </table></td> </tr=
> <tr> <td style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-=
table-lspace:0pt;-ms-text-size-adjust:100%;"> <table border=3D"0" cellspaci=
ng=3D"0" cellpadding=3D"0" width=3D"100%" style=3D"-webkit-text-size-adjust=
:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"=
> <tbody> <tr> <td style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:=
0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <table border=3D"0" c=
ellspacing=3D"0" cellpadding=3D"0" width=3D"100%" style=3D"-webkit-text-siz=
e-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjus=
t:100%;"> <tbody> <tr> <td style=3D"padding:24px 24px 36px 24px;-webkit-tex=
t-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-=
adjust:100%;"> <table border=3D"0" cellspacing=3D"0" cellpadding=3D"0" widt=
h=3D"100%" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-=
table-lspace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td align=3D"lef=
t" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-ls=
pace:0pt;-ms-text-size-adjust:100%;"> <p style=3D"margin:0;word-wrap:break-=
word;color:#4C4C4C;word-break:break-word;font-weight:400;-ms-word-break:bre=
ak-all;font-size:16px;line-height:1.5;overflow-wrap:break-word;">Hi Paul, I=
'd like to join your LinkedIn network.</p></td> </tr> <tr> <td align=3D"lef=
t" style=3D"padding:22px 0 16px 0;-webkit-text-size-adjust:100%;mso-table-r=
space:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <table border=
=3D"0" cellspacing=3D"0" cellpadding=3D"0" width=3D"100%" style=3D"-webkit-=
text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-si=
ze-adjust:100%;"> <tbody> <tr> <td valign=3D"top" width=3D"100%" style=3D"-=
webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-=
text-size-adjust:100%;"><a href=3D"https://www.linkedin.com/comm/profile/vi=
ew?id=3DAAsAAAFlvJcBCnnIlLvQhDO6ZBU5rdb7fAb_-IU&amp;authType=3Dname&amp;aut=
hToken=3D95up&amp;invAcpt=3D2197625_I6132926076281774083_500&amp;midToken=
=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-hero-2-prof%7Ena=
me&amp;trkEmail=3Deml-email_m2m_invite_single_01-hero-2-prof%7Ename-null-1b=
3p5%7Einq68641%7E1h" style=3D"cursor:pointer;color:#008CC9;-webkit-text-siz=
e-adjust:100%;display:inline-block;text-decoration:none;-ms-text-size-adjus=
t:100%;"> <span style=3D"word-wrap:break-word;color:#262626;word-break:brea=
k-word;font-weight:700;-ms-word-break:break-all;font-size:16px;line-height:=
1.5;overflow-wrap:break-word;">FOO BAR</span></a> <p style=3D"margin:0;wo=
rd-wrap:break-word;color:#737373;word-break:break-word;font-weight:400;-ms-=
word-break:break-all;font-size:14px;line-height:1.429;overflow-wrap:break-w=
ord;">Vice President</p> <p style=3D"margin:0;color:#737373;font-weight:400=
;font-size:14px;line-height:1.429;">Greater New York City Area</p></td> </t=
r> </tbody> </table></td> </tr> <tr> <td dir=3D"rtl" align=3D"left" style=
=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt=
;-ms-text-size-adjust:100%;direction:rtl !important;text-align:left !import=
ant;"> <!--[if mso]><table border=3D"0" cellpadding=3D"0" cellspacing=3D"0"=
 width=3D"auto"><tr><td style=3D"padding:12px 0 0 0;"><![endif]--><span sty=
le=3D"display:inline-block;margin-top:12px;"> <table border=3D"0" cellpaddi=
ng=3D"0" cellspacing=3D"0" style=3D"-webkit-text-size-adjust:100%;mso-table=
-rspace:0pt;display:inline-block;mso-table-lspace:0pt;-ms-text-size-adjust:=
100%;"> <tbody> <tr> <td align=3D"center" valign=3D"middle" style=3D"-webki=
t-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-=
size-adjust:100%;"><a href=3D"https://www.linkedin.com/comm/people/invite-a=
ccept?mboxid=3DI6132926076281774083_500&amp;sharedKey=3Dw447gWge&amp;fr=3Df=
alse&amp;invitationId=3D6132926046288310272&amp;fe=3Dtrue&amp;midToken=3DAQ=
HQ1w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-hero-0-accept%7Ecta&a=
mp;trkEmail=3Deml-email_m2m_invite_single_01-hero-0-accept%7Ecta-null-1b3p5=
%7Einq68641%7E1h" target=3D"_blank" style=3D"cursor:pointer;word-wrap:norma=
l;color:#008CC9;word-break:normal;white-space:nowrap;-webkit-text-size-adju=
st:100%;display:block;text-decoration:none;-ms-text-size-adjust:100%;overfl=
ow-wrap:normal;"> <table border=3D"0" cellspacing=3D"0" cellpadding=3D"0" w=
idth=3D"auto" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;m=
so-table-lspace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td bgcolor=
=3D"#008CC9" style=3D"padding:6px 16px;color:#FFFFFF;-webkit-text-size-adju=
st:100%;font-weight:500;font-size:16px;-ms-text-size-adjust:100%;border-col=
or:#008CC9;background-color:#008CC9;border-radius:2px;mso-table-rspace:0pt;=
mso-table-lspace:0pt;border-width:1px;border-style:solid;"><a href=3D"https=
://www.linkedin.com/comm/people/invite-accept?mboxid=3DI6132926076281774083=
_500&amp;sharedKey=3Dw447gWge&amp;fr=3Dfalse&amp;invitationId=3D61329260462=
88310272&amp;fe=3Dtrue&amp;midToken=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-email_m2=
m_invite_single_01-hero-0-accept%7Ecta&amp;trkEmail=3Deml-email_m2m_invite_=
single_01-hero-0-accept%7Ecta-null-1b3p5%7Einq68641%7E1h" target=3D"_blank"=
 style=3D"cursor:pointer;color:#FFFFFF;-webkit-text-size-adjust:100%;displa=
y:inline-block;text-decoration:none;-ms-text-size-adjust:100%;">Accept</a><=
/td> </tr> </tbody> </table></a></td> </tr> </tbody> </table></span> <!--[i=
f mso]></td><td style=3D"padding-top:12px;"><![endif]--><span style=3D"disp=
lay:inline-block;margin-top:12px;margin-right:12px;"> <table border=3D"0" c=
ellpadding=3D"0" cellspacing=3D"0" style=3D"-webkit-text-size-adjust:100%;m=
so-table-rspace:0pt;display:inline-block;mso-table-lspace:0pt;-ms-text-size=
-adjust:100%;"> <tbody> <tr> <td align=3D"center" valign=3D"middle" style=
=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt=
;-ms-text-size-adjust:100%;"><a href=3D"https://www.linkedin.com/comm/profi=
le/view?id=3DAAsAAAFlvJcBCnnIlLvQhDO6ZBU5rdb7fAb_-IU&amp;authType=3Dname&am=
p;authToken=3D95up&amp;invAcpt=3D2197625_I6132926076281774083_500&amp;midTo=
ken=3DAQHQ1w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-hero-3-prof%7=
Ecta&amp;trkEmail=3Deml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1=
b3p5%7Einq68641%7E1h" target=3D"_blank" style=3D"cursor:pointer;word-wrap:n=
ormal;color:#008CC9;word-break:normal;white-space:nowrap;-webkit-text-size-=
adjust:100%;display:block;text-decoration:none;-ms-text-size-adjust:100%;ov=
erflow-wrap:normal;"> <table border=3D"0" cellspacing=3D"0" cellpadding=3D"=
0" width=3D"auto" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0=
pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td style=
=3D"border-radius:2px;padding:6px 16px;color:#4C4C4C;-webkit-text-size-adju=
st:100%;mso-table-rspace:0pt;font-weight:500;mso-table-lspace:0pt;font-size=
:16px;-ms-text-size-adjust:100%;border-color:#737373;border-width:1px;borde=
r-style:solid;"><a href=3D"https://www.linkedin.com/comm/profile/view?id=3D=
AAsAAAFlvJcBCnnIlLvQhDO6ZBU5rdb7fAb_-IU&amp;authType=3Dname&amp;authToken=
=3D95up&amp;invAcpt=3D2197625_I6132926076281774083_500&amp;midToken=3DAQHQ1=
w5V4ws4wA&amp;trk=3Deml-email_m2m_invite_single_01-hero-3-prof%7Ecta&amp;tr=
kEmail=3Deml-email_m2m_invite_single_01-hero-3-prof%7Ecta-null-1b3p5%7Einq6=
8641%7E1h" target=3D"_blank" style=3D"cursor:pointer;color:#4C4C4C;-webkit-=
text-size-adjust:100%;display:inline-block;text-decoration:none;-ms-text-si=
ze-adjust:100%;">View profile</a></td> </tr> </tbody> </table></a></td> </t=
r> </tbody> </table></span> <!--[if mso]></td></tr></table><![endif]--></td=
> </tr> </tbody> </table></td> </tr> </tbody> </table></td> </tr> </tbody> =
</table></td> </tr> <tr> <td style=3D"-webkit-text-size-adjust:100%;mso-tab=
le-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <table bord=
er=3D"0" cellspacing=3D"0" cellpadding=3D"0" width=3D"100%" bgcolor=3D"#EDF=
0F3" align=3D"center" style=3D"background-color:#EDF0F3;padding:0 24px;colo=
r:#999999;-webkit-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspa=
ce:0pt;-ms-text-size-adjust:100%;text-align:center;"> <tbody> <tr> <td alig=
n=3D"center" style=3D"padding:16px 0 0 0;-webkit-text-size-adjust:100%;mso-=
table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;text-align:=
center;"> <table align=3D"center" border=3D"0" cellspacing=3D"0" cellpaddin=
g=3D"0" width=3D"100%" style=3D"-webkit-text-size-adjust:100%;mso-table-rsp=
ace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td =
valign=3D"middle" align=3D"center" style=3D"padding:0 0 16px 0;-webkit-text=
-size-adjust:100%;mso-table-rspace:0pt;vertical-align:middle;mso-table-lspa=
ce:0pt;-ms-text-size-adjust:100%;text-align:center;"><a href=3D"https://www=
.linkedin.com/e/v2?e=3D1b3p5-inq68641-1h&amp;t=3Dlun&amp;midToken=3DAQHQ1w5=
V4ws4wA&amp;ek=3Demail_m2m_invite_single_01&amp;li=3D10&amp;m=3Dunsub&amp;t=
s=3Dunsub&amp;loid=3DAQFdQYOv_FVJAgAAAVRyHzzTguEadC55UC3CMRW6tuWfby8cpsHi1x=
OrXCRZJ4MzTaYlDlG2VPl5Zx_ohw&amp;eid=3D1b3p5-inq68641-1h" style=3D"cursor:p=
ointer;color:#737373;-webkit-text-size-adjust:100%;text-decoration:underlin=
e;display:inline-block;-ms-text-size-adjust:100%;"> <span style=3D"color:#7=
37373;font-weight:400;text-decoration:underline;font-size:12px;line-height:=
1.333;">Unsubscribe</span></a>&nbsp;&nbsp;|&nbsp;&nbsp;<a href=3D"https://w=
ww.linkedin.com/e/v2?e=3D1b3p5-inq68641-1h&amp;a=3DcustomerServiceUrl&amp;m=
idToken=3DAQHQ1w5V4ws4wA&amp;ek=3Demail_m2m_invite_single_01&amp;li=3D9&amp=
;m=3Dfooter&amp;ts=3Dhelp&amp;articleId=3D67" style=3D"cursor:pointer;color=
:#737373;-webkit-text-size-adjust:100%;text-decoration:underline;display:in=
line-block;-ms-text-size-adjust:100%;"> <span style=3D"color:#737373;font-w=
eight:400;text-decoration:underline;font-size:12px;line-height:1.333;">Help=
</span></a></td> </tr> </tbody> </table></td> </tr> <tr> <td style=3D"-webk=
it-text-size-adjust:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text=
-size-adjust:100%;"> <table border=3D"0" cellspacing=3D"0" cellpadding=3D"0=
" width=3D"100%" style=3D"-webkit-text-size-adjust:100%;mso-table-rspace:0p=
t;mso-table-lspace:0pt;-ms-text-size-adjust:100%;"> <tbody> <tr> <td align=
=3D"center" style=3D"padding:0 0 12px 0;-webkit-text-size-adjust:100%;mso-t=
able-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;text-align:c=
enter;"> <p style=3D"margin:0;color:#737373;font-weight:400;font-size:12px;=
line-height:1.333;">You are receiving Invitation emails.</p></td> </tr> <tr=
> <td align=3D"center" style=3D"padding:0 0 12px 0;-webkit-text-size-adjust=
:100%;mso-table-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;t=
ext-align:center;"> <p style=3D"margin:0;word-wrap:break-word;color:#737373=
;word-break:break-word;font-weight:400;-ms-word-break:break-all;font-size:1=
2px;line-height:1.333;overflow-wrap:break-word;">This email was intended fo=
r Paul Hammant (Senior Director of Engineering at HedgeServ). <a href=3D"ht=
tps://www.linkedin.com/e/v2?e=3D1b3p5-inq68641-1h&amp;a=3DcustomerServiceUr=
l&amp;midToken=3DAQHQ1w5V4ws4wA&amp;ek=3Demail_m2m_invite_single_01&amp;art=
icleId=3D4788" style=3D"cursor:pointer;color:#737373;-webkit-text-size-adju=
st:100%;text-decoration:underline;display:inline-block;-ms-text-size-adjust=
:100%;">Learn why we included this.</a></p></td> </tr> <tr> <td align=3D"ce=
nter" style=3D"padding:0 0 8px 0;-webkit-text-size-adjust:100%;mso-table-rs=
pace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;text-align:center;"=
><a href=3D"https://www.linkedin.com/comm/nhome/?midToken=3DAQHQ1w5V4ws4wA&=
amp;trk=3Deml-email_m2m_invite_single_01-footer-8-home&amp;trkEmail=3Deml-e=
mail_m2m_invite_single_01-footer-8-home-null-1b3p5%7Einq68641%7E1h" style=
=3D"cursor:pointer;color:#737373;-webkit-text-size-adjust:100%;text-decorat=
ion:underline;display:inline-block;-ms-text-size-adjust:100%;"><img alt=3D"=
LinkedIn" border=3D"0" height=3D"14" src=3D"https://static.licdn.com/scds/c=
ommon/u/images/email/phoenix/logos/logo_phoenix_footer_gray_197x48_v1.png" =
width=3D"58" style=3D"outline:none;-ms-interpolation-mode:bicubic;color:#FF=
FFFF;display:block;text-decoration:none;"></a></td> </tr> <tr> <td align=3D=
"center" style=3D"padding:0 0 12px 0;-webkit-text-size-adjust:100%;mso-tabl=
e-rspace:0pt;mso-table-lspace:0pt;-ms-text-size-adjust:100%;text-align:cent=
er;"> <p style=3D"margin:0;color:#737373;font-weight:400;font-size:12px;lin=
e-height:1.333;">=C2=A9 2016 LinkedIn Corporation, 2029 Stierlin Court, Mou=
ntain View CA 94043. LinkedIn and the LinkedIn logo are registered trademar=
ks of LinkedIn.</p></td> </tr> </tbody> </table></td> </tr> </tbody> </tabl=
e></td> </tr> </tbody> </table> </center></td> </tr> </tbody> </table> <img=
 src=3D"http://www.linkedin.com/emimp/1b3p5-inq68641-1h.gif" style=3D"outli=
ne:none;-ms-interpolation-mode:bicubic;color:#FFFFFF;text-decoration:none;w=
idth:1px;height:1px;"> </body> </html>=

------=_Part_1161867_773496138.1462203530633--"""