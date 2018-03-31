from digesters.confluence.confluence_notification_digester import ConfluenceNotificationDigester
from digesters.fidelity.fidelity_notification_digester import FidelityNotificationDigester
from digesters.github.github_notification_digester import GithubNotificationDigester
from digesters.hipchat.hipchat_notification_digester import HipchatNotificationDigester
from digesters.jira.jira_notification_digester import JiraNotificationDigester
from digesters.linkedin.linkedin_invitation_digester import LinkedinInvitationDigester
from digesters.reddit.reddit_notification_digester import RedditNotificationDigester
from digesters.stackexchange.stack_exchange_notification_digester import StackExchangeNotificationDigester

from metastore import MetaStore
from digesters.charges.charge_card_digester import ChargeCardDigester

# This file - my_digesters_setup_sample.py - is activated despite the 'sample' name, UNLESS
# 'my_digesters_setup.py' is present. You would have made that yourself by copying this source file
# and replacing this notice with "copied from ...". Yes, it is an unconventional way of configuring
# an application (Python versus XML, JSON, YAML, TOML, properties/ini files), but it is what it is.

def add_digesters(digesters):

    # StackExchange site filtered notifications
    # Customize for your filter(s) ...
    digesters.append(StackExchangeNotificationDigester(MetaStore("stack_exchange_1"), "TBD"))

    # Charge (Credit) card spending alerts (and more)
    digesters.append(ChargeCardDigester(MetaStore("charge_cards"))
                      .with_amex()
                      .with_chase()
                      .with_barclaycard()  # non-operational presently
                      .with_bofa()
                      .with_jpmorgan()  # non-operational presently
                      .with_capitalone()  # non-operational presently
                      .with_citi())

    # Regular Github.com notifications (you are watching a repo)
    digesters.append(GithubNotificationDigester(MetaStore("github_notifications")))

    # Github Enterprise installation notifications (you are watching a repo)
    # Note the params for this need customization, or nothing will match .....
    digesters.append(GithubNotificationDigester(MetaStore("ghe_notifications"),
                                            return_path_email="noreply-ghe@yourcompany.com",
                                            from_email="ghe-notifications@yourcompany.com",
                                            site="ghe.yourcompany.com",
                                            known_as="GHE"))

    # Atlassian HipChat (service) notifications
    digesters.append(HipchatNotificationDigester(MetaStore("hipchat_notifications")))

    # Fidelity Investments (investments) Balance notifications
    digesters.append(FidelityNotificationDigester(MetaStore("fidelity_notifications")))

    # Linkedin (service) Invitations
    digesters.append(LinkedinInvitationDigester(MetaStore("linkedin_invitations")))

    # Atlassian Confluence Installation Notifications
    # Customize to the Confluence you're aiming at .....
    digesters.append(ConfluenceNotificationDigester(MetaStore("confluence_notifications"),
                                                    "confluence@apache.org", "Apache"))

    # Customize to the JIRA you're aiming at .....

    # Atlassian's JIRA Installation Notifications
    digesters.append(JiraNotificationDigester(MetaStore("jira_notifications"),
                                                    "jira@atlassian.com", "Atlassian"))
    # Apache's JIRA Notifications
    digesters.append(JiraNotificationDigester(MetaStore("apache_jira_notifications"),
                                              "jira@apache.org", "Apache"))

  # Apache's JIRA Notifications
    digesters.append(RedditNotificationDigester(MetaStore("reddit_notifications"), "paul_h"))
