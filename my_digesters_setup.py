from digesters.confluence.confluence_notification_digester import ConfluenceNotificationDigester
from digesters.githubnotifications.github_notification_digester import GithubNotificationDigester
from digesters.hipchat.hipchat_notification_digester import HipchatNotificationDigester
from digesters.linkedin.linkedin_invitation_digester import LinkedinInvitationDigester
from digesters.stackexchange.stack_exchange_notification_digester import StackExchangeNotificationDigester

from metastore import MetaStore
from digesters.charges.charge_card_digester import ChargeCardDigester

def add_digesters(digesters):

    # StackExchange filtered notifications
    digesters.append(StackExchangeNotificationDigester(MetaStore("stack_exchange_1"), "My SO filters"))

    # Charge (Credit) card spenting alerts (and mmore)
    digesters.append(ChargeCardDigester(MetaStore("charge_cards"))
                      .with_amex()
                      .with_chase()
                      .with_barclaycard()
                      .with_bofa()
                      .with_jpmorgan()
                      .with_capitalone()
                      .with_citi())

    # Regular Github.com notifications (you are watching a repo)
    digesters.append(GithubNotificationDigester(MetaStore("github_notifications")))

    # Github Enterprise notifications (you are watching a repo)
    digesters.append(GithubNotificationDigester(MetaStore("ghe_notifications"),
                                            return_path_email="noreply-ghe@yourcompany.com",
                                            from_email="ghe-notifications@yourcompany.com",
                                            site="ghe.yourcompany.com",
                                            known_as="GHE"))

    # HipChat notifications
    digesters.append(HipchatNotificationDigester(MetaStore("hipchat_notifications")))

    # Linkedin Invitations
    digesters.append(LinkedinInvitationDigester(MetaStore("linkedin_invitations")))

    # Confluence Notifications
    digesters.append(ConfluenceNotificationDigester(MetaStore("confluence_notifications")))
