from digesters.confluence.confluence_notification_digester import ConfluenceNotificationDigester
from digesters.githubnotifications.github_notification_digester import GithubNotificationDigester
from digesters.hipchat.hipchat_notification_digester import HipchatNotificationDigester
from digesters.linkedin.linkedin_invitation_digester import LinkedinInvitationDigester
from digesters.stackexchange.stack_exchange_notification_digester import StackExchangeNotificationDigester

from metastore import MetaStore
from digesters.charges.charge_card_digester import ChargeCardDigester

def add_digesters(digesters):
    digesters.append(StackExchangeNotificationDigester(MetaStore("stack_exchange_1"), "My SO filters"))
    digesters.append(ChargeCardDigester(MetaStore("charge_cards"))
                      .with_amex()
                      .with_chase()
                      .with_barclaycard()
                      .with_bofa()
                      .with_jpmorgan()
                      .with_capitalone()
                      .with_citi())
    digesters.append(GithubNotificationDigester(MetaStore("github_notifications")))
    digesters.append(HipchatNotificationDigester(MetaStore("hipchat_notifications")))
    digesters.append(LinkedinInvitationDigester(MetaStore("linkedin_invitations")))
    digesters.append(ConfluenceNotificationDigester(MetaStore("confluence_notifications")))
