import sys
from unittest import TestCase

from mock import Mock, call
from mockextras import stub

from digesters.jira.jira_notification_digester import JiraNotificationDigester
from digesters.digestion_processor import DigestionProcessor


MAIL_HDR = """From: "Atlassian JIRA" <ph@example.com>
Content-Transfer-Encoding: 8bit
Content-Type: multipart/alternative; boundary="---NOTIFICATION_BOUNDARY-5678"
MIME-Version: 1.0
This is a multi-part message in MIME format.
-----NOTIFICATION_BOUNDARY-5678
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: 8bit


"""

NEW_ISSUE = """Date: Thu, 14 Apr 2016 16:45:00 +0000 (UTC)
From: "Paul Hammant (JIRA)" <jira@atlassian.com>
To: ph@example.com
Message-ID: <JIRA.590899.1460652284000.68665.1460652300154@Atlassian.JIRA>
In-Reply-To: <JIRA.590899.1460652284000@Atlassian.JIRA>
References: <JIRA.590899.1460652284000@Atlassian.JIRA> <JIRA.590899.1460652284724@node439>
Subject: [JIRA] (HCPUB-579) Data payload for notification emails.
MIME-Version: 1.0
Content-Type: multipart/related;
	boundary="----=_Part_72151_779492282.1460652300060"
X-JIRA-FingerPrint: 34ed612e0c4ee035f333de85b64c81ec
Auto-Submitted: auto-generated
Precedence: bulk

------=_Part_72151_779492282.1460652300060
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: 7bit

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
        <base href="https://jira.atlassian.com">
        <title>Message Title</title>
    </head>
    <body class="jira" style="color: #333333; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.429">
        <table id="background-table" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #f5f5f5; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt" bgcolor="#f5f5f5">
            <!-- header here -->
            <tbody>
                <tr>
                    <td id="header-pattern-container" style="padding: 0px; border-collapse: collapse; padding: 10px 20px">
                        <table id="header-pattern" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                            <tbody>
                                <tr>
                                    <td id="header-avatar-image-container" valign="top" style="padding: 0px; border-collapse: collapse; vertical-align: top; width: 32px; padding-right: 8px" width="32"> <img id="header-avatar-image" class="image_fix" src="cid:jira-generated-image-avatar-d5256ef3-ad47-4557-bbc8-5ad6b725533d" height="32" width="32" border="0" style="border-radius: 3px; vertical-align: top"> </td>
                                    <td id="header-text-container" valign="middle" style="padding: 0px; border-collapse: collapse; vertical-align: middle; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 1px"> <a class="user-hover" rel="paul230760403" id="email_paul230760403" href="https://jira.atlassian.com/secure/ViewProfile.jspa?name=paul230760403" style="color:#3b73af;; color: #3b73af; text-decoration: none">Paul Hammant</a> <strong>created</strong> an issue </td>
                                </tr>
                            </tbody>
                        </table> </td>
                </tr>
                <tr>
                    <td id="email-content-container" style="padding: 0px; border-collapse: collapse; padding: 0 20px">
                        <table id="email-content-table" cellspacing="0" cellpadding="0" border="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; border-spacing: 0; border-collapse: separate">
                            <tbody>
                                <tr>
                                    <!-- there needs to be content in the cell for it to render in some clients -->
                                    <td class="email-content-rounded-top mobile-expand" style="padding: 0px; border-collapse: collapse; color: #ffffff; padding: 0 15px 0 16px; height: 15px; background-color: #ffffff; border-left: 1px solid #cccccc; border-top: 1px solid #cccccc; border-right: 1px solid #cccccc; border-bottom: 0; border-top-right-radius: 5px; border-top-left-radius: 5px; height: 10px; line-height: 10px; padding: 0 15px 0 16px; mso-line-height-rule: exactly" height="10" bgcolor="#ffffff">&nbsp;</td>
                                </tr>
                                <tr>
                                    <td class="email-content-main mobile-expand " style="padding: 0px; border-collapse: collapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #ffffff" bgcolor="#ffffff">
                                        <table class="page-title-pattern" cellspacing="0" cellpadding="0" border="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                                            <tbody>
                                                <tr>
                                                    <td class="page-title-pattern-first-line " style="padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; padding-top: 10px"> <a href="https://jira.atlassian.com/browse/HCPUB" style="color: #3b73af; text-decoration: none">HipChat</a> / <a href="https://jira.atlassian.com/browse/HCPUB-579" style="color: #3b73af; text-decoration: none"><img src="cid:jira-generated-image-avatar-da8aea7d-75f6-4faf-9221-4b01fb91c863" height="16" width="16" border="0" align="absmiddle" alt="Suggestion" style="vertical-align: text-bottom"></a> <a href="https://jira.atlassian.com/browse/HCPUB-579" style="color: #3b73af; text-decoration: none">HCPUB-579</a> </td>
                                                </tr>
                                                <tr>
                                                    <td style="vertical-align: top;; padding: 0px; border-collapse: collapse; padding-right: 5px; font-size: 20px; line-height: 30px; mso-line-height-rule: exactly" class="page-title-pattern-header-container"> <span class="page-title-pattern-header" style="font-family: Arial, sans-serif; padding: 0; font-size: 20px; line-height: 30px; mso-text-raise: 2px; mso-line-height-rule: exactly; vertical-align: middle"> <a href="https://jira.atlassian.com/browse/HCPUB-579" style="color: #3b73af; text-decoration: none">Data payload for notification emails.</a> </span> </td>
                                                </tr>
                                            </tbody>
                                        </table> </td>
                                </tr>
                                <tr>
                                    <td class="email-content-main mobile-expand  wrapper-special-margin" style="padding: 0px; border-collapse: collapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #ffffff; padding-top: 10px; padding-bottom: 5px" bgcolor="#ffffff">
                                        <table class="keyvalue-table" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                                            <tbody>
                                                <tr>
                                                    <th style="color: #707070; font: normal 14px/20px Arial, sans-serif; text-align: left; vertical-align: top; padding: 2px 0">Issue Type:</th>
                                                    <td class="has-icon" style="padding: 0px; border-collapse: collapse; font: normal 14px/20px Arial, sans-serif; padding: 2px 0 2px 5px; vertical-align: top"> <img src="cid:jira-generated-image-avatar-da8aea7d-75f6-4faf-9221-4b01fb91c863" height="16" width="16" border="0" align="absmiddle" alt="Suggestion" style="vertical-align: text-bottom"> Suggestion </td>
                                                </tr>
                                                <tr>
                                                    <th style="color: #707070; font: normal 14px/20px Arial, sans-serif; text-align: left; vertical-align: top; padding: 2px 0">Assignee:</th>
                                                    <td style="padding: 0px; border-collapse: collapse; font: normal 14px/20px Arial, sans-serif; padding: 2px 0 2px 5px; vertical-align: top"> Unassigned </td>
                                                </tr>
                                                <tr>
                                                    <th style="color: #707070; font: normal 14px/20px Arial, sans-serif; text-align: left; vertical-align: top; padding: 2px 0">Components:</th>
                                                    <td style="padding: 0px; border-collapse: collapse; font: normal 14px/20px Arial, sans-serif; padding: 2px 0 2px 5px; vertical-align: top"> Notifications - email </td>
                                                </tr>
                                                <tr>
                                                    <th style="color: #707070; font: normal 14px/20px Arial, sans-serif; text-align: left; vertical-align: top; padding: 2px 0">Created:</th>
                                                    <td style="padding: 0px; border-collapse: collapse; font: normal 14px/20px Arial, sans-serif; padding: 2px 0 2px 5px; vertical-align: top"> 14/Apr/2016 4:44 PM </td>
                                                </tr>
                                                <tr>
                                                    <th style="color: #707070; font: normal 14px/20px Arial, sans-serif; text-align: left; vertical-align: top; padding: 2px 0">Reporter:</th>
                                                    <td style="padding: 0px; border-collapse: collapse; font: normal 14px/20px Arial, sans-serif; padding: 2px 0 2px 5px; vertical-align: top"> <a class="user-hover" rel="paul230760403" id="email_paul230760403" href="https://jira.atlassian.com/secure/ViewProfile.jspa?name=paul230760403" style="color:#3b73af;; color: #3b73af; text-decoration: none">Paul Hammant</a> </td>
                                                </tr>
                                            </tbody>
                                        </table> </td>
                                </tr>
                                <tr>
                                    <td class="email-content-main mobile-expand  issue-description-container" style="padding: 0px; border-collapse: collapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #ffffff; padding-top: 5px; padding-bottom: 10px" bgcolor="#ffffff">
                                        <table class="text-paragraph-pattern" cellspacing="0" cellpadding="0" border="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 2px">
                                            <tbody>
                                                <tr>
                                                    <td class="text-paragraph-pattern-container mobile-resize-text " style="padding: 0px; border-collapse: collapse; padding: 0 0 10px 0"> <p style="margin-top:0;margin-bottom:10px;; margin: 10px 0 0 0; margin-top: 0">Can you awesome folks add a text/json multipart to the outgoing emails, please ?</p>
                                                        <blockquote style="margin: 10px 0 0 0; border-left: 1px solid #cccccc; color: #707070; margin-left: 19px; padding: 10px 20px">
                                                            <p style="margin-top:0;margin-bottom:10px;; margin: 10px 0 0 0; margin-top: 0"> {<br> "event": "room-mention",<br> "id": "e606affc-c879-4ba5-b6a0-7a085ce46989",<br> "summary": "Paul Hammant just mentioned you in the room AtlassianTotallyRocks",<br> "room": 1484300<br> ...<br> }</p>
                                                        </blockquote> <p style="margin-top:0;margin-bottom:10px;; margin: 10px 0 0 0">Paul Hammant&lt;/a&gt;<br> just mentioned you in the room<br> &lt;a href=3D"https://www.hipchat.com/rooms/show/1484371</p> <p style="margin-top:0;margin-bottom:10px;; margin: 10px 0 0 0">If not a multi-part then somehow encoded in the HTML, so that it can be parsed out without javascript itself. e.g as a base64 string in a display:block section. </p> <p style="margin-top:0;margin-bottom:10px;; margin: 10px 0 0 0">Ref also <a href="https://jira.atlassian.com/browse/JRA-60612" title="Data payload for notification emails." class="issue-link" data-issue-key="JRA-60612" style="color: #3b73af; text-decoration: none">JRA-60612</a></p> </td>
                                                </tr>
                                            </tbody>
                                        </table> </td>
                                </tr>
                                <tr>
                                    <td class="email-content-main mobile-expand " style="padding: 0px; border-collapse: collapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #ffffff" bgcolor="#ffffff">
                                        <table id="actions-pattern" cellspacing="0" cellpadding="0" border="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 1px">
                                            <tbody>
                                                <tr>
                                                    <td id="actions-pattern-container" valign="middle" style="padding: 0px; border-collapse: collapse; padding: 10px 0 10px 24px; vertical-align: middle; padding-left: 0">
                                                        <table align="left" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                                                            <tbody>
                                                                <tr>
                                                                    <td class="actions-pattern-action-icon-container" style="padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 0px; vertical-align: middle"> <a href="https://jira.atlassian.com/browse/HCPUB-579#add-comment" target="_blank" title="Add Comment" style="color: #3b73af; text-decoration: none"> <img class="actions-pattern-action-icon-image" src="cid:jira-generated-image-static-comment-icon-5ae93161-ce0c-42d7-a34a-7ab2532b7c2a" alt="Add Comment" title="Add Comment" height="16" width="16" border="0" style="vertical-align: middle"> </a> </td>
                                                                    <td class="actions-pattern-action-text-container" style="padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 4px; padding-left: 5px"> <a href="https://jira.atlassian.com/browse/HCPUB-579#add-comment" target="_blank" title="Add Comment" style="color: #3b73af; text-decoration: none">Add Comment</a> </td>
                                                                </tr>
                                                            </tbody>
                                                        </table> </td>
                                                </tr>
                                            </tbody>
                                        </table> </td>
                                </tr>
                                <!-- there needs to be content in the cell for it to render in some clients -->
                                <tr>
                                    <td class="email-content-rounded-bottom mobile-expand" style="padding: 0px; border-collapse: collapse; color: #ffffff; padding: 0 15px 0 16px; height: 5px; line-height: 5px; background-color: #ffffff; border-top: 0; border-left: 1px solid #cccccc; border-bottom: 1px solid #cccccc; border-right: 1px solid #cccccc; border-bottom-right-radius: 5px; border-bottom-left-radius: 5px; mso-line-height-rule: exactly" height="5" bgcolor="#ffffff">&nbsp;</td>
                                </tr>
                            </tbody>
                        </table> </td>
                </tr>
                <tr>
                    <td id="footer-pattern" style="padding: 0px; border-collapse: collapse; padding: 12px 20px">
                        <table id="footer-pattern-container" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                            <tbody>
                                <tr>
                                    <td id="footer-pattern-text" class="mobile-resize-text" width="100%" style="padding: 0px; border-collapse: collapse; color: #999999; font-size: 12px; line-height: 18px; font-family: Arial, sans-serif; mso-line-height-rule: exactly; mso-text-raise: 2px"> This message was sent by Atlassian JIRA <span id="footer-build-information">(v7.1.2#71006-<span title="8e7e3091c211bab4b45730515b8b1591e99b0c1c" data-commit-id="8e7e3091c211bab4b45730515b8b1591e99b0c1c}">sha1:8e7e309</span>)</span> </td>
                                    <td id="footer-pattern-logo-desktop-container" valign="top" style="padding: 0px; border-collapse: collapse; padding-left: 20px; vertical-align: top">
                                        <table style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                                            <tbody>
                                                <tr>
                                                    <td id="footer-pattern-logo-desktop-padding" style="padding: 0px; border-collapse: collapse; padding-top: 3px"> <img id="footer-pattern-logo-desktop" src="cid:jira-generated-image-static-footer-desktop-logo-619836fc-78d1-44b8-9fbc-35cd661e2469" alt="Atlassian logo" title="Atlassian logo" width="169" height="36" class="image_fix"> </td>
                                                </tr>
                                            </tbody>
                                        </table> </td>
                                </tr>
                            </tbody>
                        </table> </td>
                </tr>
            </tbody>
        </table>
    </body>
</html>

------=_Part_72151_779492282.1460652300060--"""

CHANGED_ISSUE = """Date: Thu, 14 Apr 2016 16:51:00 +0000 (UTC)
From: "Paul Hammant (JIRA)" <jira@atlassian.com>
To: ph@example.com
Message-ID: <JIRA.590899.1460652284000.68708.1460652660083@Atlassian.JIRA>
In-Reply-To: <JIRA.590899.1460652284000@Atlassian.JIRA>
References: <JIRA.590899.1460652284000@Atlassian.JIRA> <JIRA.590899.1460652284724@node439>
Subject: [JIRA] (HCPUB-579) Data payload for notification emails.
MIME-Version: 1.0
Content-Type: multipart/related;
	boundary="----=_Part_72190_1168931742.1460652660051"
X-JIRA-FingerPrint: 34ed612e0c4ee035f333de85b64c81ec
Auto-Submitted: auto-generated
Precedence: bulk

------=_Part_72190_1168931742.1460652660051
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org=
/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns=3D"http://www.w3.org/1999/xhtml">
    <head>=20
        <meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Du=
tf-8">=20
        <meta name=3D"viewport" content=3D"width=3Ddevice-width, initial-sc=
ale=3D1.0, maximum-scale=3D1.0">=20
        <base href=3D"https://jira.atlassian.com">=20
        <title>Message Title</title>=20
    </head>=20
    <body class=3D"jira" style=3D"color: #333333; font-family: Arial, sans-=
serif; font-size: 14px; line-height: 1.429">=20
        <table id=3D"background-table" cellpadding=3D"0" cellspacing=3D"0" =
width=3D"100%" style=3D"border-collapse: collapse; mso-table-lspace: 0pt; m=
so-table-rspace: 0pt; background-color: #f5f5f5; border-collapse: collapse;=
 mso-table-lspace: 0pt; mso-table-rspace: 0pt" bgcolor=3D"#f5f5f5">=20
            <!-- header here -->=20
            <tbody>
                <tr>=20
                    <td id=3D"header-pattern-container" style=3D"padding: 0=
px; border-collapse: collapse; padding: 10px 20px">=20
                        <table id=3D"header-pattern" cellspacing=3D"0" cell=
padding=3D"0" border=3D"0" style=3D"border-collapse: collapse; mso-table-ls=
pace: 0pt; mso-table-rspace: 0pt">=20
                            <tbody>
                                <tr>=20
                                    <td id=3D"header-avatar-image-container=
" valign=3D"top" style=3D"padding: 0px; border-collapse: collapse; vertical=
-align: top; width: 32px; padding-right: 8px" width=3D"32"> <img id=3D"head=
er-avatar-image" class=3D"image_fix" src=3D"cid:jira-generated-image-avatar=
-e6e6ec8d-73dd-4980-8128-ec31b7f28af6" height=3D"32" width=3D"32" border=3D=
"0" style=3D"border-radius: 3px; vertical-align: top"> </td>=20
                                    <td id=3D"header-text-container" valign=
=3D"middle" style=3D"padding: 0px; border-collapse: collapse; vertical-alig=
n: middle; font-family: Arial, sans-serif; font-size: 14px; line-height: 20=
px; mso-line-height-rule: exactly; mso-text-raise: 1px"> <a class=3D"user-h=
over" rel=3D"paul230760403" id=3D"email_paul230760403" href=3D"https://jira=
.atlassian.com/secure/ViewProfile.jspa?name=3Dpaul230760403" style=3D"color=
:#3b73af;; color: #3b73af; text-decoration: none">Paul Hammant</a> <strong>=
updated</strong> an issue </td>=20
                                </tr>=20
                            </tbody>
                        </table> </td>=20
                </tr>=20
                <tr>=20
                    <td id=3D"email-content-container" style=3D"padding: 0p=
x; border-collapse: collapse; padding: 0 20px">=20
                        <table id=3D"email-content-table" cellspacing=3D"0"=
 cellpadding=3D"0" border=3D"0" width=3D"100%" style=3D"border-collapse: co=
llapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; border-spacing: 0; bo=
rder-collapse: separate">=20
                            <tbody>
                                <tr>=20
                                    <!-- there needs to be content in the c=
ell for it to render in some clients -->=20
                                    <td class=3D"email-content-rounded-top =
mobile-expand" style=3D"padding: 0px; border-collapse: collapse; color: #ff=
ffff; padding: 0 15px 0 16px; height: 15px; background-color: #ffffff; bord=
er-left: 1px solid #cccccc; border-top: 1px solid #cccccc; border-right: 1p=
x solid #cccccc; border-bottom: 0; border-top-right-radius: 5px; border-top=
-left-radius: 5px; height: 10px; line-height: 10px; padding: 0 15px 0 16px;=
 mso-line-height-rule: exactly" height=3D"10" bgcolor=3D"#ffffff">&nbsp;</t=
d>=20
                                </tr>=20
                                <tr>=20
                                    <td class=3D"email-content-main mobile-=
expand " style=3D"padding: 0px; border-collapse: collapse; border-left: 1px=
 solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bott=
om: 0; padding: 0 15px 0 16px; background-color: #ffffff" bgcolor=3D"#fffff=
f">=20
                                        <table class=3D"page-title-pattern"=
 cellspacing=3D"0" cellpadding=3D"0" border=3D"0" width=3D"100%" style=3D"b=
order-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">=20
                                            <tbody>
                                                <tr>=20
                                                    <td class=3D"page-title=
-pattern-first-line " style=3D"padding: 0px; border-collapse: collapse; fon=
t-family: Arial, sans-serif; font-size: 14px; padding-top: 10px"> <a href=
=3D"https://jira.atlassian.com/browse/HCPUB" style=3D"color: #3b73af; text-=
decoration: none">HipChat</a> / <a href=3D"https://jira.atlassian.com/brows=
e/HCPUB-579" style=3D"color: #3b73af; text-decoration: none"><img src=3D"ci=
d:jira-generated-image-avatar-6833f627-d126-486e-b0c7-1f994f306e9e" height=
=3D"16" width=3D"16" border=3D"0" align=3D"absmiddle" alt=3D"Suggestion" st=
yle=3D"vertical-align: text-bottom"></a> <a href=3D"https://jira.atlassian.=
com/browse/HCPUB-579" style=3D"color: #3b73af; text-decoration: none">HCPUB=
-579</a> </td>=20
                                                </tr>=20
                                                <tr>=20
                                                    <td style=3D"vertical-a=
lign: top;; padding: 0px; border-collapse: collapse; padding-right: 5px; fo=
nt-size: 20px; line-height: 30px; mso-line-height-rule: exactly" class=3D"p=
age-title-pattern-header-container"> <span class=3D"page-title-pattern-head=
er" style=3D"font-family: Arial, sans-serif; padding: 0; font-size: 20px; l=
ine-height: 30px; mso-text-raise: 2px; mso-line-height-rule: exactly; verti=
cal-align: middle"> <a href=3D"https://jira.atlassian.com/browse/HCPUB-579"=
 style=3D"color: #3b73af; text-decoration: none">Data payload for notificat=
ion emails.</a> </span> </td>=20
                                                </tr>=20
                                            </tbody>
                                        </table> </td>=20
                                </tr>=20
                                <tr>=20
                                    <td class=3D"email-content-main mobile-=
expand  wrapper-special-margin" style=3D"padding: 0px; border-collapse: col=
lapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc; bor=
der-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #ff=
ffff; padding-top: 10px; padding-bottom: 5px" bgcolor=3D"#ffffff">=20
                                        <table class=3D"keyvalue-table" sty=
le=3D"border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0=
pt">=20
                                            <tbody>
                                                <tr>=20
                                                    <th style=3D"color: #70=
7070; font: normal 14px/20px Arial, sans-serif; text-align: left; vertical-=
align: top; padding: 2px 0">Change By:</th>=20
                                                    <td style=3D"padding: 0=
px; border-collapse: collapse; font: normal 14px/20px Arial, sans-serif; pa=
dding: 2px 0 2px 5px; vertical-align: top"> <a class=3D"user-hover" rel=3D"=
paul230760403" id=3D"email_paul230760403" href=3D"https://jira.atlassian.co=
m/secure/ViewProfile.jspa?name=3Dpaul230760403" style=3D"color:#3b73af;; co=
lor: #3b73af; text-decoration: none">Paul Hammant</a> </td>=20
                                                </tr>=20
                                            </tbody>
                                        </table> </td>=20
                                </tr>=20
                                <tr>=20
                                    <td class=3D"email-content-main mobile-=
expand  issue-description-container" style=3D"padding: 0px; border-collapse=
: collapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc=
; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color=
: #ffffff; padding-top: 5px; padding-bottom: 10px" bgcolor=3D"#ffffff">=20
                                        <table class=3D"text-paragraph-patt=
ern" cellspacing=3D"0" cellpadding=3D"0" border=3D"0" width=3D"100%" style=
=3D"border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt=
; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-l=
ine-height-rule: exactly; mso-text-raise: 2px">=20
                                            <tbody>
                                                <tr>=20
                                                    <td class=3D"text-parag=
raph-pattern-container mobile-resize-text " style=3D"padding: 0px; border-c=
ollapse: collapse; padding: 0 0 10px 0"> <span class=3D"diffcontext">Can yo=
u awesome folks add a text/json multipart to the outgoing emails, please ?<=
br><br>{quote}<br>&nbsp;&nbsp;&nbsp;&nbsp;\{<br>&nbsp;&nbsp;&nbsp;&nbsp;&nb=
sp;&nbsp;&nbsp;"event": "room-mention",<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&n=
bsp;&nbsp;"id": "e606affc-c879-4ba5-b6a0-7a085ce46989",<br>&nbsp;&nbsp;&nbs=
p;&nbsp;&nbsp;&nbsp;&nbsp;"summary": "Paul Hammant just mentioned you in th=
e room AtlassianTotallyRocks",<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp=
;"room": 1484300<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;...<br>&nbsp;=
&nbsp;&nbsp;&nbsp;\}<br>{quote}<br><br>Paul Hammant&lt;/a&gt;<br>&nbsp;&nbs=
p;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;just mentione=
d you in the room<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;a href=3D3D"ht=
tps://www.hipchat.com/rooms/show/1484371<br><br>If not a multi-part then so=
mehow encoded in the HTML, so that it can be parsed out without javascript =
itself. e.g as a base64 string in a display:block section. <br><br>Ref also=
 JRA-60612</span> <span class=3D"diffaddedchars" style=3D"background-color:=
#ddfade;"><br><br>This issue is mentioned in the [README for ImapDigester|h=
ttps://github.com/paul-hammant/imapdigester]</span> </td>=20
                                                </tr>=20
                                            </tbody>
                                        </table> </td>=20
                                </tr>=20
                                <tr>=20
                                    <td class=3D"email-content-main mobile-=
expand " style=3D"padding: 0px; border-collapse: collapse; border-left: 1px=
 solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bott=
om: 0; padding: 0 15px 0 16px; background-color: #ffffff" bgcolor=3D"#fffff=
f">=20
                                        <table id=3D"actions-pattern" cells=
pacing=3D"0" cellpadding=3D"0" border=3D"0" width=3D"100%" style=3D"border-=
collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-fami=
ly: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-=
rule: exactly; mso-text-raise: 1px">=20
                                            <tbody>
                                                <tr>=20
                                                    <td id=3D"actions-patte=
rn-container" valign=3D"middle" style=3D"padding: 0px; border-collapse: col=
lapse; padding: 10px 0 10px 24px; vertical-align: middle; padding-left: 0">=
=20
                                                        <table align=3D"lef=
t" style=3D"border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rsp=
ace: 0pt">=20
                                                            <tbody>
                                                                <tr>=20
                                                                    <td cla=
ss=3D"actions-pattern-action-icon-container" style=3D"padding: 0px; border-=
collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-h=
eight: 20px; mso-line-height-rule: exactly; mso-text-raise: 0px; vertical-a=
lign: middle"> <a href=3D"https://jira.atlassian.com/browse/HCPUB-579#add-c=
omment" target=3D"_blank" title=3D"Add Comment" style=3D"color: #3b73af; te=
xt-decoration: none"> <img class=3D"actions-pattern-action-icon-image" src=
=3D"cid:jira-generated-image-static-comment-icon-87a482c8-8cf3-44d3-95f2-f1=
75379907b1" alt=3D"Add Comment" title=3D"Add Comment" height=3D"16" width=
=3D"16" border=3D"0" style=3D"vertical-align: middle"> </a> </td>=20
                                                                    <td cla=
ss=3D"actions-pattern-action-text-container" style=3D"padding: 0px; border-=
collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-h=
eight: 20px; mso-line-height-rule: exactly; mso-text-raise: 4px; padding-le=
ft: 5px"> <a href=3D"https://jira.atlassian.com/browse/HCPUB-579#add-commen=
t" target=3D"_blank" title=3D"Add Comment" style=3D"color: #3b73af; text-de=
coration: none">Add Comment</a> </td>=20
                                                                </tr>=20
                                                            </tbody>
                                                        </table> </td>=20
                                                </tr>=20
                                            </tbody>
                                        </table> </td>=20
                                </tr>=20
                                <!-- there needs to be content in the cell =
for it to render in some clients -->=20
                                <tr>=20
                                    <td class=3D"email-content-rounded-bott=
om mobile-expand" style=3D"padding: 0px; border-collapse: collapse; color: =
#ffffff; padding: 0 15px 0 16px; height: 5px; line-height: 5px; background-=
color: #ffffff; border-top: 0; border-left: 1px solid #cccccc; border-botto=
m: 1px solid #cccccc; border-right: 1px solid #cccccc; border-bottom-right-=
radius: 5px; border-bottom-left-radius: 5px; mso-line-height-rule: exactly"=
 height=3D"5" bgcolor=3D"#ffffff">&nbsp;</td>=20
                                </tr>=20
                            </tbody>
                        </table> </td>=20
                </tr>=20
                <tr>=20
                    <td id=3D"footer-pattern" style=3D"padding: 0px; border=
-collapse: collapse; padding: 12px 20px">=20
                        <table id=3D"footer-pattern-container" cellspacing=
=3D"0" cellpadding=3D"0" border=3D"0" style=3D"border-collapse: collapse; m=
so-table-lspace: 0pt; mso-table-rspace: 0pt">=20
                            <tbody>
                                <tr>=20
                                    <td id=3D"footer-pattern-text" class=3D=
"mobile-resize-text" width=3D"100%" style=3D"padding: 0px; border-collapse:=
 collapse; color: #999999; font-size: 12px; line-height: 18px; font-family:=
 Arial, sans-serif; mso-line-height-rule: exactly; mso-text-raise: 2px"> Th=
is message was sent by Atlassian JIRA <span id=3D"footer-build-information"=
>(v7.1.2#71006-<span title=3D"8e7e3091c211bab4b45730515b8b1591e99b0c1c" dat=
a-commit-id=3D"8e7e3091c211bab4b45730515b8b1591e99b0c1c}">sha1:8e7e309</spa=
n>)</span> </td>=20
                                    <td id=3D"footer-pattern-logo-desktop-c=
ontainer" valign=3D"top" style=3D"padding: 0px; border-collapse: collapse; =
padding-left: 20px; vertical-align: top">=20
                                        <table style=3D"border-collapse: co=
llapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">=20
                                            <tbody>
                                                <tr>=20
                                                    <td id=3D"footer-patter=
n-logo-desktop-padding" style=3D"padding: 0px; border-collapse: collapse; p=
adding-top: 3px"> <img id=3D"footer-pattern-logo-desktop" src=3D"cid:jira-g=
enerated-image-static-footer-desktop-logo-86699106-420b-4201-9fbd-4f1a55a49=
97d" alt=3D"Atlassian logo" title=3D"Atlassian logo" width=3D"169" height=
=3D"36" class=3D"image_fix"> </td>=20
                                                </tr>=20
                                            </tbody>
                                        </table> </td>=20
                                </tr>=20
                            </tbody>
                        </table> </td>=20
                </tr>=20
            </tbody>
        </table>  =20
    </body>
</html>

------=_Part_72190_1168931742.1460652660051--"""

COMMENTED_ISSUE = """Received: from CO2PR20MB0105.namprd20.prod.outlook.com (10.161.81.17) by
 CY1PR20MB0111.namprd20.prod.outlook.com (10.162.41.143) with Microsoft SMTP
 Server (TLS) id 15.1.466.19 via Mailbox Transport; Sun, 24 Apr 2016 21:36:15
 +0000
Received: from BY1PR20CA0008.namprd20.prod.outlook.com (10.162.140.18) by
 CO2PR20MB0105.namprd20.prod.outlook.com (10.161.81.17) with Microsoft SMTP
 Server (TLS) id 15.1.466.19; Sun, 24 Apr 2016 21:36:14 +0000
Received: from SN1NAM02FT052.eop-nam02.prod.protection.outlook.com
 (2a01:111:f400:7e44::209) by BY1PR20CA0008.outlook.office365.com
 (2a01:111:e400:51a4::18) with Microsoft SMTP Server (TLS) id 15.1.477.8 via
 Frontend Transport; Sun, 24 Apr 2016 21:36:14 +0000
Received: from COL004-MC2F30.hotmail.com (10.152.72.59) by
 SN1NAM02FT052.mail.protection.outlook.com (10.152.72.146) with Microsoft SMTP
 Server (TLS) id 15.1.477.4 via Frontend Transport; Sun, 24 Apr 2016 21:36:14
 +0000
Received: from mail.apache.org ([140.211.11.3]) by COL004-MC2F30.hotmail.com with Microsoft SMTPSVC(7.5.7601.23143);
	 Sun, 24 Apr 2016 14:36:13 -0700
Received: (qmail 57808 invoked by uid 99); 24 Apr 2016 21:36:13 -0000
Received: from arcas.apache.org (HELO arcas) (140.211.11.28)
    by apache.org (qpsmtpd/0.29) with ESMTP; Sun, 24 Apr 2016 21:36:13 +0000
Received: from arcas.apache.org (localhost [127.0.0.1])
	by arcas (Postfix) with ESMTP id F11062C044E
	for <paul_h555@outlook.com>; Sun, 24 Apr 2016 21:36:12 +0000 (UTC)
Date: Sun, 24 Apr 2016 21:36:12 +0000
From: "Kfir Lev-Ari (JIRA)" <jira@apache.org>
To: <paul_h555@outlook.com>
Message-ID: <JIRA.12737480.1409240469000.19772.1461533772879@Atlassian.JIRA>
In-Reply-To: <JIRA.12737480.1409240469000@Atlassian.JIRA>
References: <JIRA.12737480.1409240469000@Atlassian.JIRA> <JIRA.12737480.1409240469316@arcas>
Subject: [jira] [Commented] (ZOOKEEPER-2024) Major throughput improvement
 with mixed workloads
Content-Type: multipart/related;
	boundary="----=_Part_2511_1798417668.1461533772838"
X-JIRA-FingerPrint: 30527f35849b9dde25b450d4833f0394
Return-Path: jira@apache.org
X-OriginalArrivalTime: 24 Apr 2016 21:36:13.0478 (UTC) FILETIME=[5332B460:01D19E71]
X-MS-Exchange-Organization-Network-Message-Id: 9836dd70-b0d6-4fd0-2415-08d36c887650
X-EOPAttributedMessage: 0
X-EOPTenantAttributedMessage: 84df9e7f-e9f6-40af-b435-aaaaaaaaaaaa:0
X-MS-Exchange-Organization-MessageDirectionality: Incoming
CMM-sender-ip: 140.211.11.3
CMM-sending-ip: 140.211.11.3
CMM-Authentication-Results: hotmail.com; spf=none (sender IP is 140.211.11.3)
 smtp.mailfrom=jira@apache.org; dkim=none header.d=apache.org; x-hmca=none
 header.id=jira@apache.org
CMM-X-SID-PRA: jira@apache.org
CMM-X-AUTH-Result: NONE
CMM-X-SID-Result: NONE
CMM-X-Message-Status: n:n
CMM-X-Message-Delivery: Vj0xLjE7dXM9MDtsPTE7YT0xO0Q9MTtHRD0xO1NDTD0w
CMM-X-Message-Info: NhFq/7gR1vRMTq/Ey2ZlMeezFH9jGl6tcMZYzGIU5YbQaLpLv1mFSS/pXdM/fhWpeXqdL6KOFU6I9T083q7eofANIYH5ouJIpO9lCz7z3x8sbzaOhxTKYV1CqP174DfAKVikXzlG1wnpkR8bWnLuM4cYmSj3KzwbsUCopK8e8TyBxDe1d5UBqUKwlddXNAjSUWFYYr1DPSJWmGphCwMFqlwU58CjhxoXK2Pj+QIlXnNUuJv7U7ygxQ==
X-MS-Exchange-Organization-PCL: 2
X-Forefront-Antispam-Report: EFV:NLI;SFV:NSPM;SFS:(98900003);DIR:INB;SFP:;SCL:1;SRVR:CO2PR20MB0105;H:COL004-MC2F30.hotmail.com;FPR:;SPF:None;MLV:ovrnspm;LANG:en;
X-MS-Office365-Filtering-Correlation-Id: 9836dd70-b0d6-4fd0-2415-08d36c887650
X-Microsoft-Exchange-Diagnostics: 1;CO2PR20MB0105;2:HqYMPEXjd4mR38wFLClTZT0smKQAl24Qn30WBgfd3ATLRwm0GoDD02T/1Nepb6p2YnLYuJ6KU9h5RlCBti/nQxDsyVcJZP+vCcaDNk2q9U2huh2qQhl6pcH7ZLU29fWhXU3acFYhdji8KkjJNNNx9LnbwIxGdACn+pgFVgjw+oKm/2Gub5b9ctsAPKo3wxodLDf4mmSYCPyhnJ3CmNvozQ==;3:pv/MPBttuPz/eKvQ3Iz8Vm6lSYqC8UH+fvAmAsF4qC2IBjPeYdgzH028U+v6WYfGr6LzazDanx8WWTn9QfGaN5N1la2OnHm3AZAplY1RG1GKxvN6tcLoslnXc6kUecZvy8OpivEd594XcQcggSSp4VMx7dFlWq6lzEtwqjRHsvU=;25:/oG1SutJBBV/5pUsaFwMNtzrw6X0k+Y3v4Me1JvYdFv1P2S3i+Vm1lCaMoDNXIqAPgESmwkJIk05Vp4txkst+5gzcz/3RQ6484QcenegO1dfE2fJcFU0gAHVnUG5dnbC76frmLc+ntiQi7OQODgn/f5tKkHDJV9jvbWrb6aSbadVP6fbgHni1jfVnNldfqBHFjC932GC6zs0JD7r+EYfkLDvhscTgaVmqKfRUWtQ+8yNFxBveQObcAUr2itMgf7m5NJVfpA5IqucrcGvtNB1j5O3zkca2FHbGW7TamJqQT1O5etEl0m0ugMCAtHRusyxuOXORTxu0GxnzilSyViV4gNmpVqf5jwnQrvS+55wFm8=
X-Microsoft-Antispam: BCL:0;PCL:0;RULEID:(8291501002);SRVR:CO2PR20MB0105;
X-MS-Exchange-Organization-AVStamp-Service: 1.0
X-Exchange-Antispam-Report-CFA-Test: BCL:0;PCL:0;RULEID:(102415293)(102615271)(82015046);SRVR:CO2PR20MB0105;BCL:0;PCL:0;RULEID:;SRVR:CO2PR20MB0105;
X-Microsoft-Exchange-Diagnostics: 1;CO2PR20MB0105;4:QRWeKB+kJC0tgwpsd7bZrBf97/0HQtX8PssDb6/HfDr18OZ8DHLdGQqnbNa3udMqna/dz9HEqSPZ/eO/BgVaZVRUw3c0PbHzCc1pYROM49QJ27CAtWUAS+hvF+dEvCFxO+0NISbvs1QVMsRqZBKHExPmRqQT+tFrXYeKsTelhk4wAVs1aUc/UVDlpVQ62zsdeX2QiHnJjeMeaWlVuiRHZuZVvdjsi3c5uT3yGOBK9vepTPZ623gxP8MFtR18xq7/TzeAlI/Td9zrRnIeLclIDwxx2pMQsWs2z46bNfbdCIgo3Bueatm+ha0JdMCViy7D;23:Isi9DGn4h9i1Lm3zZwTB802LCvK1iiY2HhpYf9VTup4hIwtA73nQ0aFQaqanUgZmemMh70G0e42THNbO6wddUTq4IEJiATVdvMRWy2v7haTOSAt7JzNuItdFf5a4tDjAEmGRlDD/tvgQPNFKnuE2NDknupyu8QzClwEW9OiH9wnBcNQco0rPIdKaiVpy5wkp;5:+7R71eoSqojhntWk3KiHYoJWqysMJRpmzKzs7K6ZetSqySs+7J8aSRlqw+bvqgOdgQ8Ltib1G+IwislEnhUYno47pDON6Wvvch/88pJ1f6xHF0GZKg+y2scrIxigQbRXLUdVbm52QL8mqARrQfnLkLDa2YwbaylDyuPmmeqgYndQDL8sRVEedRD0tAuqEx49;24:CPLkbK36dYIiwfhW7VklIY/rYpLSbzgDpdCIqOmQpZU2oz9+iBBS+L4VklXNIn+5EcMVEICrr89MIE8WrkydZR3RftgLlB5WaecZWNZj6gM=
X-MS-Exchange-Organization-SCL: 1
SpamDiagnosticOutput: 1:23
SpamDiagnosticMetadata: NSPM
X-Microsoft-Exchange-Diagnostics: 1;CO2PR20MB0105;7:srdxkGyJcLPYRQzo2p6OMhmX5kv0nbe+2NaLp51xqShYIZRiegOP0ybuKDwvKIdLhhG0Q0N25ZTtH0c4HnOoz53OcE8rD1SJs5cA7oXf74NsdlqqJ8BZxKc4exAktj5YUXTe/ReZNAXXh2ABNwK4NHhnXXqA7RUq5BNmexpTmLDrkYNAJYYUtsRMwWhJbdH5k42otanJZXOhXIepWMC8LOQnz3PXHgw+3dblaAhVcd4=
X-MS-Exchange-CrossTenant-OriginalArrivalTime: 24 Apr 2016 21:36:14.0999
 (UTC)
X-MS-Exchange-CrossTenant-Id: 84df9e7f-e9f6-40af-b435-aaaaaaaaaaaa
X-MS-Exchange-CrossTenant-FromEntityHeader: Internet
X-MS-Exchange-Transport-CrossTenantHeadersStamped: CO2PR20MB0105
X-MS-Exchange-Organization-AuthSource: SN1NAM02FT052.eop-nam02.prod.protection.outlook.com
X-MS-Exchange-Organization-AuthAs: Anonymous
X-MS-Exchange-Transport-EndToEndLatency: 00:00:01.4648304
MIME-Version: 1.0

------=_Part_2511_1798417668.1461533772838
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: 7bit

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0"> <base href="https://issues.apache.org/jira">
        <title>Message Title</title>
    </head>
    <body class="jira" style="color: #333; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.429">
        <table id="background-table" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #f5f5f5; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
            <!-- header here -->
            <tr>
                <td id="header-pattern-container" style="padding: 0px; border-collapse: collapse; padding: 10px 20px">
                    <table id="header-pattern" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                        <tr>
                            <td id="header-avatar-image-container" valign="top" style="padding: 0px; border-collapse: collapse; vertical-align: top; width: 32px; padding-right: 8px"> <img id="header-avatar-image" class="image_fix" src="cid:jira-generated-image-avatar-kfirlevari-dbd33342-b3bc-4269-b05e-c9266c21d61f" height="32" width="32" border="0" style="border-radius: 3px; vertical-align: top">
                            </td>
                            <td id="header-text-container" valign="middle" style="padding: 0px; border-collapse: collapse; vertical-align: middle; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 1px"> <a class="user-hover" rel="kfirlevari" id="email_kfirlevari" href="https://issues.apache.org/jira/secure/ViewProfile.jspa?name=kfirlevari" style="color:#3b73af;; color: #3b73af; text-decoration: none">Kfir Lev-Ari</a> <strong>commented</strong> on <a href="https://issues.apache.org/jira/browse/ZOOKEEPER-2024" style="color: #3b73af; text-decoration: none"><img src="cid:jira-generated-image-static-improvement-ca3e91bc-5b72-4890-88ce-b0f93ceaab37" height="16" width="16" border="0" align="absmiddle" alt="Improvement"> ZOOKEEPER-2024</a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td id="email-content-container" style="padding: 0px; border-collapse: collapse; padding: 0 20px">
                    <table id="email-content-table" cellspacing="0" cellpadding="0" border="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; border-spacing: 0; border-collapse: separate">
                        <tr>
                            <!-- there needs to be content in the cell for it to render in some clients -->
                            <td class="email-content-rounded-top mobile-expand" style="padding: 0px; border-collapse: collapse; color: #fff; padding: 0 15px 0 16px; height: 15px; background-color: #fff; border-left: 1px solid #ccc; border-top: 1px solid #ccc; border-right: 1px solid #ccc; border-bottom: 0; border-top-right-radius: 5px; border-top-left-radius: 5px; height: 10px; line-height: 10px; padding: 0 15px 0 16px; mso-line-height-rule: exactly">
                                &nbsp;
                            </td>
                        </tr>
                        <tr>
                            <td class="email-content-main mobile-expand " style="padding: 0px; border-collapse: collapse; border-left: 1px solid #ccc; border-right: 1px solid #ccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #fff">
                                <table class="page-title-pattern" cellspacing="0" cellpadding="0" border="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                                    <tr>
                                        <td style="vertical-align: top;; padding: 0px; border-collapse: collapse; padding-right: 5px; font-size: 20px; line-height: 30px; mso-line-height-rule: exactly" class="page-title-pattern-header-container"> <span class="page-title-pattern-header" style="font-family: Arial, sans-serif; padding: 0; font-size: 20px; line-height: 30px; mso-text-raise: 2px; mso-line-height-rule: exactly; vertical-align: middle"> <a href="https://issues.apache.org/jira/browse/ZOOKEEPER-2024" style="color: #3b73af; text-decoration: none">Re: Major throughput improvement with mixed workloads</a> </span>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td id="text-paragraph-pattern-top" class="email-content-main mobile-expand  comment-top-pattern" style="padding: 0px; border-collapse: collapse; border-left: 1px solid #ccc; border-right: 1px solid #ccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #fff; border-bottom: none; padding-bottom: 0">
                                <table class="text-paragraph-pattern" cellspacing="0" cellpadding="0" border="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 2px">
                                    <tr>
                                        <td class="text-paragraph-pattern-container mobile-resize-text " style="padding: 0px; border-collapse: collapse; padding: 0 0 10px 0">
                                            <p style="margin: 10px 0 0 0">Hi all,<br> Please let me know if there is anything else that is missing in order for this patch to be submitted.<br> Thanks <img class="emoticon" src="https://issues.apache.org/jira/images/icons/emoticons/wink.gif" height="16" width="16" align="absmiddle" alt="" border="0"></p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td class="email-content-main mobile-expand " style="padding: 0px; border-collapse: collapse; border-left: 1px solid #ccc; border-right: 1px solid #ccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #fff">
                                <table id="actions-pattern" cellspacing="0" cellpadding="0" border="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 1px">
                                    <tr>
                                        <td id="actions-pattern-container" valign="middle" style="padding: 0px; border-collapse: collapse; padding: 10px 0 10px 24px; vertical-align: middle; padding-left: 0">
                                            <table align="left" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                                                <tr>
                                                    <td class="actions-pattern-action-icon-container" style="padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 0px; vertical-align: middle"> <a href="https://issues.apache.org/jira/browse/ZOOKEEPER-2024#add-comment" target="_blank" title="Add Comment" style="color: #3b73af; text-decoration: none"> <img class="actions-pattern-action-icon-image" src="cid:jira-generated-image-static-comment-icon-80047bd6-22d2-4d43-a140-ffacc6341881" alt="Add Comment" title="Add Comment" height="16" width="16" border="0" style="vertical-align: middle"> </a>
                                                    </td>
                                                    <td class="actions-pattern-action-text-container" style="padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 4px; padding-left: 5px"> <a href="https://issues.apache.org/jira/browse/ZOOKEEPER-2024#add-comment" target="_blank" title="Add Comment" style="color: #3b73af; text-decoration: none">Add Comment</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <!-- there needs to be content in the cell for it to render in some clients -->
                        <tr>
                            <td class="email-content-rounded-bottom mobile-expand" style="padding: 0px; border-collapse: collapse; color: #fff; padding: 0 15px 0 16px; height: 5px; line-height: 5px; background-color: #fff; border-top: 0; border-left: 1px solid #ccc; border-bottom: 1px solid #ccc; border-right: 1px solid #ccc; border-bottom-right-radius: 5px; border-bottom-left-radius: 5px; mso-line-height-rule: exactly">
                                &nbsp;
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td id="footer-pattern" style="padding: 0px; border-collapse: collapse; padding: 12px 20px">
                    <table id="footer-pattern-container" cellspacing="0" cellpadding="0" border="0" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                        <tr>
                            <td id="footer-pattern-text" class="mobile-resize-text" width="100%" style="padding: 0px; border-collapse: collapse; color: #999; font-size: 12px; line-height: 18px; font-family: Arial, sans-serif; mso-line-height-rule: exactly; mso-text-raise: 2px">
                                 This message was sent by Atlassian JIRA <span id="footer-build-information">(v6.3.4#6332-<span title="51bc225ef474afe3128b2f66878477f322397b16" data-commit-id="51bc225ef474afe3128b2f66878477f322397b16}">sha1:51bc225</span>)</span>
                            </td>
                            <td id="footer-pattern-logo-desktop-container" valign="top" style="padding: 0px; border-collapse: collapse; padding-left: 20px; vertical-align: top">
                                <table style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt">
                                    <tr>
                                        <td id="footer-pattern-logo-desktop-padding" style="padding: 0px; border-collapse: collapse; padding-top: 3px"> <img id="footer-pattern-logo-desktop" src="cid:jira-generated-image-static-footer-desktop-logo-3d990929-6fae-4044-b7fa-b28027808dde" alt="Atlassian logo" title="Atlassian logo" width="169" height="36" class="image_fix">
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
------=_Part_2511_1798417668.1461533772838
Content-Type: image/png
Content-Transfer-Encoding: base64
Content-Disposition: inline
Content-ID: <jira-generated-image-static-improvement-ca3e91bc-5b72-4890-88ce-b0f93ceaab37>

iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAADAFBMVEX///+1tbWzs7OwsLD////7
+/v5+fny9PfZ2dnW1tbT09PPz8+2ws6ruMaJnK+Li4tziqGBgYFogZl7e3teeJNycnJwcHBKZ4UA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAADv+1LMAAAAEHRSTlMAIiIi3e7u7u7u7u7u7u7uwTEa7gAAABt0RVh0amlyYS1z
eXN0ZW0taW1hZ2UtdHlwZQBpY29uuio5RQAAAIFJREFUeNpdj9sOAiEMRIcul4BR//8jfdAYkK4s
AlLXbEPS9nQyE4BDKaiLq7LxoypcKa+TWLfdCZZZFJwsdGttDL6DWwEI6PeYhqQOMGoT3wkWK0B/
95MpL/I7cCan8qcIPsXuvCtmSHdsQL+jOC79GSuZpMOaFej8iwQ/y/H3+ABAMif3I4dQAwAAAABJ
RU5ErkJggg==

------=_Part_2511_1798417668.1461533772838
Content-Type: image/png
Content-Transfer-Encoding: base64
Content-Disposition: inline
Content-ID: <jira-generated-image-static-comment-icon-80047bd6-22d2-4d43-a140-ffacc6341881>

iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAADAFBMVEX///+1tbWzs7OysrKrq6um
pqalpaWdnZ2ZmZn///+VlZWPj4/7+/vu7u7p6enn5+fl5eXk5OTh4eHW1tbT09PMzMzJycm6urq5
ubm1tbWzs7OysrKrq6upqamlpaWKioqFhYWRkZGKioqHh4eDg4OAgIB/f398fHx6enp4eHh2dnZ0
dHRycnJwcHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAIFWMjAAAAIXRSTlMAIiIzZoiZu8zd3d3u7u7u7u7u7u7u7u7u7u7u7u7u7u6n
leogAAAAG3RFWHRqaXJhLXN5c3RlbS1pbWFnZS10eXBlAGljb266KjlFAAAAo0lEQVR42l2P2wrC
MAyG09Pa1SqKzIk3QwTf/3G8UByKyK4EcV0POqzDaTUQwv+R/EkA/gKFJGyuQrFH/+iAWJnGOCCp
THcmALms6ne7ykpNeFHpft75xZWsL/XX0bMppj7eUXNseQykI7eZu3+0GpfYuVz1ephriwAnxdkD
QVwIsTVAoTUswZNBuPRkw6X01cqzZtMbdWB0aFqIANqb349ZLJ5XFjQIuveaPQAAAABJRU5ErkJg
gg==

------=_Part_2511_1798417668.1461533772838
Content-Type: image/png
Content-Transfer-Encoding: base64
Content-Disposition: inline
Content-ID: <jira-generated-image-avatar-kfirlevari-dbd33342-b3bc-4269-b05e-c9266c21d61f>

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
ynN+6O6Nseif/RLmXWLrvHgAAAAASUVORK5CYII=

------=_Part_2511_1798417668.1461533772838
Content-Type: image/png
Content-Transfer-Encoding: base64
Content-Disposition: inline
Content-ID: <jira-generated-image-static-footer-desktop-logo-3d990929-6fae-4044-b7fa-b28027808dde>

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
nvfbckn7YgAAAABJRU5ErkJggg==

------=_Part_2511_1798417668.1461533772838--"""

class NotificationsStore(object):

    def __init__(self, cls=object):
        self._cls = cls
        self.notifications = None

    def __eq__(self, other):
        self.notifications = other
        return True

    def __ne__(self, other):
        return False

    def __repr__(self):
        return "NotificationsStore(..)"


class TestJiraNotifications(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestJiraNotifications, self).__init__(methodName)
        reload(sys)
        sys.setdefaultencoding('utf8')

    def test_two_related_notifications_can_be_rolled_up(self):

        expected_payload = """<html><body><span>You have previously read notifications up to: Apr 09 2016 02:37 AM</span>
<table>
  <tr style="background-color: #acf;">
    <th>Notifications</th>
  </tr>
          <tr style="">
    <td>
        <table>
            <tr>
                <td>What:</td><td>Paul Hammant commented on  JRA-60612</td>
            </tr>
            <tr>
                <td>Project:</td><td>unknown</td>
            </tr>
            <tr>
                <td>Issue:</td><td><a href="https://jira.atlassian.com/browse/JRA-60612">JRA-60612</a></td>
            </tr>
            <tr>
                <td>Comment:</td>
                <td>
                    Great idea, Paul
                </td>
            </tr>
        </table>
    </td>
  </tr>          <tr style="background-color: #def;">
    <td>
        <table>
            <tr>
                <td>What:</td><td>Paul Hammant updated an issue</td>
            </tr>
            <tr>
                <td>Project:</td><td>HipChat</td>
            </tr>
            <tr>
                <td>Issue:</td><td><a href="https://jira.atlassian.com/browse/HCPUB-579">HCPUB-579</a></td>
            </tr>
            <tr>
                <td>Fields:</td>
                <td>
                    <table>
                    <tr><td>Change By</td><td>Paul Hammant</td></tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td>Comment:</td>
                <td>
                    Can you awesome folks add a text/json multipart to the...
                </td>
            </tr>
        </table>
    </td>
  </tr>          <tr><td colspan="2" style="border-bottom: 1pt solid red; border-top: 1pt solid red;"><center>^ New Notifications Since You Last Checked ^</center></td></tr>          <tr style="">
    <td>
        <table>
            <tr>
                <td>What:</td><td>Paul Hammant created an issue</td>
            </tr>
            <tr>
                <td>Project:</td><td>HipChat</td>
            </tr>
            <tr>
                <td>Issue:</td><td><a href="https://jira.atlassian.com/browse/HCPUB-579">HCPUB-579</a></td>
            </tr>
            <tr>
                <td>Fields:</td>
                <td>
                    <table>
                    <tr><td>Issue Type</td><td>Suggestion</td></tr>
                    <tr><td>Assignee</td><td>Unassigned</td></tr>
                    <tr><td>Components</td><td>Notifications - email</td></tr>
                    <tr><td>Created</td><td>14/Apr/2016 4</td></tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td>Comment:</td>
                <td>
                    Can you awesome folks add a text/json multipart to the...
                </td>
            </tr>
        </table>
    </td>
  </tr>
</table></body></html>"""

        notification_store = {}

        final_notifications_store = NotificationsStore()

        store_writer = Mock()
        store_writer.get_from_binary.side_effect = stub(
            (call('jira-notifications'), notification_store),
            (call('most-recently-seen'), 1460183824)
        )
        store_writer.store_as_binary.side_effect = stub(
            (call('jira-notifications', final_notifications_store), True),
            (call('most-recently-seen', 1460183824), True)
        )

        expected_message = ("Subject: Atlassian JIRA Notif. Digest: 1 new notification(s)\n"
                            + MAIL_HDR + expected_payload + "\n\n-----NOTIFICATION_BOUNDARY-5678")

        digest_inbox_proxy = Mock()
        digest_inbox_proxy.delete_previous_message.side_effect = stub((call(), True))
        digest_inbox_proxy.append.side_effect = stub((call(expected_message), True))

        digesters = []
        digester = JiraNotificationDigester(store_writer, "jira@atlassian.com", "Atlassian")  ## What we are testing
        digester.notification_boundary_rand = "-5678"  # no random number for the email's notification boundary
        digesters.append(digester)

        digestion_processor = DigestionProcessor(None, None, digesters, False, "ph@example.com", False, "INBOX")

        unmatched_to_move = []
        to_delete_from_notification_folder = []

        digestion_processor.process_incoming_notification(1234, digesters, NEW_ISSUE, to_delete_from_notification_folder, unmatched_to_move, False)
        digestion_processor.process_incoming_notification(1235, digesters, CHANGED_ISSUE, to_delete_from_notification_folder, unmatched_to_move, False)
        digestion_processor.process_incoming_notification(1236, digesters, COMMENTED_ISSUE, to_delete_from_notification_folder, unmatched_to_move, False)

        digester.rewrite_digest_emails(digest_inbox_proxy, has_previous_message=True,
                                       previously_seen=False, sender_to_implicate="ph@example.com")

        self.assertEquals(digest_inbox_proxy.mock_calls, [call.delete_previous_message(), call.append(expected_message)])

        calls = store_writer.mock_calls
        self.assertEquals(calls, [
            call.get_from_binary('jira-notifications'),
            call.get_from_binary('most-recently-seen'),
            call.store_as_binary('jira-notifications', {
                1461123240: {u'comment': u'Great idea, Paul',
                             u'project_name': u'unknown',
                             u'who': u'Paul Hammant',
                             u'kvtable': [],
                             u'issue_id': u'JRA-60612',
                             u'event': u'Paul Hammant commented on  JRA-60612',
                             u'issue_url': u'https://jira.atlassian.com/browse/JRA-60612'},
                1460652660: {u'comment': u'Can you awesome folks add a text/json multipart to the...',
                             u'project_name': u'HipChat',
                             u'who': u'Paul Hammant',
                             u'kvtable': [{u'k': u'Change By', u'v': u'Paul Hammant'}],
                             u'issue_id': u'HCPUB-579',
                             u'event': u'Paul Hammant updated an issue',
                             u'issue_url': u'https://jira.atlassian.com/browse/HCPUB-579'},
                1460652300: {u'comment': u'Can you awesome folks add a text/json multipart to the...',
                             u'project_name': u'HipChat',
                             u'line_here': True,
                             u'who': u'Paul Hammant',
                             u'kvtable': [{u'k': u'Issue Type', u'v': u'Suggestion'},
                                          {u'k': u'Assignee', u'v': u'Unassigned'},
                                          {u'k': u'Components', u'v': u'Notifications - email'},
                                          {u'k': u'Created', u'v': u'14/Apr/2016 4'}],
                             u'issue_id': u'HCPUB-579',
                             u'event': u'Paul Hammant created an issue',
                             u'issue_url': u'https://jira.atlassian.com/browse/HCPUB-579'}}),
            call.store_as_binary('most-recently-seen', 1460183824)])
        self.assertEquals(len(unmatched_to_move), 0)
        self.assertEquals(str(to_delete_from_notification_folder), "[1234, 1235, 1236]")
        self.assertEquals(len(final_notifications_store.notifications), 3)
