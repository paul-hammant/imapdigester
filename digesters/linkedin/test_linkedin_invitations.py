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
              <td><img style="max-width:100px;height:auto" src="https://media.licdn.com/mpr/mpr/shrinknp_100_100/p/4/000/17b/3db/1dbe948.jpg"/></td>
              <td>
                <strong>Steven Footle</strong><br>
                Hi Paul,<br/>
          I\'d like to join your LinkedIn network.<br/>
          Steven Footle<br/>
          Principal Test Architect and Agile Leader - Certified ScrumMaster<br/>
          <br>
                <a href="https://www.linkedin.com/comm/people/invite-accept?mboxid=I6122153999904439999_500&sharedKey=-aWVMgrZ&fr=false&invitationId=6122153757099996400&fe=true&trk=eml-comm_invm-b-accept-newinvite&midToken=AQHQ1w999ws4wA&trkEmail=eml-M2M_Invitation-null-5-null-null-1b3p5%7Eimjp489e%7Ejk">Accept Invitation</a>
                <a href="https://www.linkedin.com/comm/profile/view?id=AAsAAAAIW1gBCVPJFcvlZjm6AtEfNiLTNya_HqA&authType=name&authToken=F40O&invAcpt=2197625_I6122153999904439999_500&midToken=AQHQ1w999ws4wA&trk=eml-M2M_Invitation-hero-1-text%7Eprofile&trkEmail=eml-M2M_Invitation-hero-1-text%7Eprofile-null-1b3p5%7Eimjp489e%999k">View Profile</a>
              </td>
            </tr>          <tr><td colspan="2" style="border-bottom: 1pt solid red; border-top: 1pt solid red;"><center>^ New Invitations Since You Last Checked ^</center></td></tr>          <tr style="background-color: #def;">
              <td><img style="max-width:100px;height:auto" src="https://media.licdn.com/mpr/mpr/shrinknp_100_100/p/4/000/17b/3db/1dbe948.jpg"/></td>
              <td>
                <strong>Steven Blipvert</strong><br>
                Hi Paul,<br/>
          I\'d like to join your LinkedIn network.<br/>
          Steven Blipvert<br/>
          Principal Test Architect and Agile Leader - Certified ScrumMaster<br/>
          <br>
                <a href="https://www.linkedin.com/comm/people/invite-accept?mboxid=I6122153999904439999_500&sharedKey=-aWVMgrZ&fr=false&invitationId=6122153757099996400&fe=true&trk=eml-comm_invm-b-accept-newinvite&midToken=AQHQ1w999ws4wA&trkEmail=eml-M2M_Invitation-null-5-null-null-1b3p5%7Eimjp489e%7Ejk">Accept Invitation</a>
                <a href="https://www.linkedin.com/comm/profile/view?id=AAsAAAAIW1gBCVPJFcvlZjm6AtEfNiLTNya_HqA&authType=name&authToken=F40O&invAcpt=2197625_I6122153999904439999_500&midToken=AQHQ1w999ws4wA&trk=eml-M2M_Invitation-hero-1-text%7Eprofile&trkEmail=eml-M2M_Invitation-hero-1-text%7Eprofile-null-1b3p5%7Eimjp489e%999k">View Profile</a>
              </td>
            </tr>
          </table></body></html>""".replace("\n          ","\n")

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

        expected_message = ("Subject: Linkedin Inv. Digest: 1 new invitation(s)\n" + MAIL_HDR + expected_payload + \
                           "\n\n-----NOTIFICATION_BOUNDARY-5678").replace("\n", "\r\n")

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

        notification_1_content = self.get_li_emailed_invitations()

        notification_2_content = notification_1_content.replace("Footle", "Blipvert").replace("4 Apr 2016", "1 Apr 2016")

        digestion_processor.process_incoming_notification(1234, digesters, notification_1_content, to_delete_from_notification_folder, unmatched_to_move, False)
        digestion_processor.process_incoming_notification(1235, digesters, notification_2_content, to_delete_from_notification_folder, unmatched_to_move, False)

        digester.rewrite_digest_emails(digest_inbox_proxy, has_previous_message=True,
                                       previously_seen=False, sender_to_implicate="ph@example.com")

        self.assertEquals(digest_inbox_proxy.mock_calls, [call.delete_previous_message(), call.append(expected_message)])

        calls = store_writer.mock_calls
        self.assertEquals(calls, [
            call.get_from_binary('linkedin-invitations'),
            call.get_from_binary('most-recently-seen'),
            call.store_as_binary('linkedin-invitations', {
                1459808011: {
                    'spiel': "Hi Paul,\nI'd like to join your LinkedIn network.\nSteven Footle\nPrincipal Test Architect and Agile Leader - Certified ScrumMaster\n",
                    'accept_url': 'https://www.linkedin.com/comm/people/invite-accept?mboxid=I6122153999904439999_500&sharedKey=-aWVMgrZ&fr=false&invitationId=6122153757099996400&fe=true&trk=eml-comm_invm-b-accept-newinvite&midToken=AQHQ1w999ws4wA&trkEmail=eml-M2M_Invitation-null-5-null-null-1b3p5%7Eimjp489e%7Ejk',
                    'who': 'Steven Footle',
                    'img_src': 'https://media.licdn.com/mpr/mpr/shrinknp_100_100/p/4/000/17b/3db/1dbe948.jpg',
                    'profile_url': 'https://www.linkedin.com/comm/profile/view?id=AAsAAAAIW1gBCVPJFcvlZjm6AtEfNiLTNya_HqA&authType=name&authToken=F40O&invAcpt=2197625_I6122153999904439999_500&midToken=AQHQ1w999ws4wA&trk=eml-M2M_Invitation-hero-1-text%7Eprofile&trkEmail=eml-M2M_Invitation-hero-1-text%7Eprofile-null-1b3p5%7Eimjp489e%999k'
                },
                1459548811: {
                    'spiel': "Hi Paul,\nI'd like to join your LinkedIn network.\nSteven Blipvert\nPrincipal Test Architect and Agile Leader - Certified ScrumMaster\n",
                    'accept_url': 'https://www.linkedin.com/comm/people/invite-accept?mboxid=I6122153999904439999_500&sharedKey=-aWVMgrZ&fr=false&invitationId=6122153757099996400&fe=true&trk=eml-comm_invm-b-accept-newinvite&midToken=AQHQ1w999ws4wA&trkEmail=eml-M2M_Invitation-null-5-null-null-1b3p5%7Eimjp489e%7Ejk',
                    'line_here': True,
                    'who': 'Steven Blipvert',
                    'img_src': 'https://media.licdn.com/mpr/mpr/shrinknp_100_100/p/4/000/17b/3db/1dbe948.jpg',
                    'profile_url': 'https://www.linkedin.com/comm/profile/view?id=AAsAAAAIW1gBCVPJFcvlZjm6AtEfNiLTNya_HqA&authType=name&authToken=F40O&invAcpt=2197625_I6122153999904439999_500&midToken=AQHQ1w999ws4wA&trk=eml-M2M_Invitation-hero-1-text%7Eprofile&trkEmail=eml-M2M_Invitation-hero-1-text%7Eprofile-null-1b3p5%7Eimjp489e%999k'
                }
            }),
            call.store_as_binary('most-recently-seen', 1459548811)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(str(to_delete_from_notification_folder), "[1234, 1235]")
        self.assertEquals(len(final_invitations_store.invitations), 2)

    def get_li_emailed_invitations(self):
        with open('../../testdata/linkedin_1.txt', 'r') as myfile:
            notification_1_content = myfile.read().replace('\n', '\r\n')
        return notification_1_content


