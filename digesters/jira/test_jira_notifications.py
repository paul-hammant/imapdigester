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

COMMENTED_ISSUE = """Date: Wed, 20 Apr 2016 03:34:00 +0000 (UTC)
From: "Paul Hammant (JIRA)" <jira@atlassian.com>
To: ph@example.com
Message-ID: <JIRA.590897.1460651689000.177651.1461123240081@Atlassian.JIRA>
In-Reply-To: <JIRA.590897.1460651689000@Atlassian.JIRA>
References: <JIRA.590897.1460651689000@Atlassian.JIRA> <JIRA.590897.1460651689064@node438>
Subject: [JIRA] (JRA-60612) Data payload for notification emails.
MIME-Version: 1.0
Content-Type: multipart/related;
	boundary="----=_Part_195733_1307700225.1461123240075"
X-JIRA-FingerPrint: 34ed612e0c4ee035f333de85b64c81ec
Auto-Submitted: auto-generated
Precedence: bulk

------=_Part_195733_1307700225.1461123240075
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
                                    <td id="header-avatar-image-container" valign="top" style="padding: 0px; border-collapse: collapse; vertical-align: top; width: 32px; padding-right: 8px" width="32"> <img id="header-avatar-image" class="image_fix" src="cid:jira-generated-image-avatar-6f8acf53-c1e7-47f7-bb72-8671cff450a7" height="32" width="32" border="0" style="border-radius: 3px; vertical-align: top"> </td>
                                    <td id="header-text-container" valign="middle" style="padding: 0px; border-collapse: collapse; vertical-align: middle; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 1px"> <a class="user-hover" rel="paul230760403" id="email_paul230760403" href="https://jira.atlassian.com/secure/ViewProfile.jspa?name=paul230760403" style="color:#3b73af;; color: #3b73af; text-decoration: none">Paul Hammant</a> <strong>commented</strong> on <a href="https://jira.atlassian.com/browse/JRA-60612" style="color: #3b73af; text-decoration: none"><img src="cid:jira-generated-image-avatar-caffc6ec-733c-42bd-9e31-f88982fe37f2" height="16" width="16" border="0" align="absmiddle" alt="Suggestion"> JRA-60612</a> </td>
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
                                                    <td style="vertical-align: top;; padding: 0px; border-collapse: collapse; padding-right: 5px; font-size: 20px; line-height: 30px; mso-line-height-rule: exactly" class="page-title-pattern-header-container"> <span class="page-title-pattern-header" style="font-family: Arial, sans-serif; padding: 0; font-size: 20px; line-height: 30px; mso-text-raise: 2px; mso-line-height-rule: exactly; vertical-align: middle"> <a href="https://jira.atlassian.com/browse/JRA-60612" style="color: #3b73af; text-decoration: none">Re: Data payload for notification emails.</a> </span> </td>
                                                </tr>
                                            </tbody>
                                        </table> </td>
                                </tr>
                                <tr>
                                    <td id="text-paragraph-pattern-top" class="email-content-main mobile-expand  comment-top-pattern" style="padding: 0px; border-collapse: collapse; border-left: 1px solid #cccccc; border-right: 1px solid #cccccc; border-top: 0; border-bottom: 0; padding: 0 15px 0 16px; background-color: #ffffff; border-bottom: none; padding-bottom: 0" bgcolor="#ffffff">
                                        <table class="text-paragraph-pattern" cellspacing="0" cellpadding="0" border="0" width="100%" style="border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 2px">
                                            <tbody>
                                                <tr>
                                                    <td class="text-paragraph-pattern-container mobile-resize-text " style="padding: 0px; border-collapse: collapse; padding: 0 0 10px 0"> <p style="margin: 10px 0 0 0; margin-top: 0">Great idea, Paul</p> </td>
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
                                                                    <td class="actions-pattern-action-icon-container" style="padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 0px; vertical-align: middle"> <a href="https://jira.atlassian.com/browse/JRA-60612#add-comment" target="_blank" title="Add Comment" style="color: #3b73af; text-decoration: none"> <img class="actions-pattern-action-icon-image" src="cid:jira-generated-image-static-comment-icon-195cfa27-e687-40aa-9e2f-e61b8ff962bf" alt="Add Comment" title="Add Comment" height="16" width="16" border="0" style="vertical-align: middle"> </a> </td>
                                                                    <td class="actions-pattern-action-text-container" style="padding: 0px; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; mso-line-height-rule: exactly; mso-text-raise: 4px; padding-left: 5px"> <a href="https://jira.atlassian.com/browse/JRA-60612#add-comment" target="_blank" title="Add Comment" style="color: #3b73af; text-decoration: none">Add Comment</a> </td>
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
                                                    <td id="footer-pattern-logo-desktop-padding" style="padding: 0px; border-collapse: collapse; padding-top: 3px"> <img id="footer-pattern-logo-desktop" src="cid:jira-generated-image-static-footer-desktop-logo-e79c306c-c2fc-400e-8f10-92a40473583e" alt="Atlassian logo" title="Atlassian logo" width="169" height="36" class="image_fix"> </td>
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

------=_Part_195733_1307700225.1461123240075--"""

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
