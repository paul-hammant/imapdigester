from digesters.base_digester import BaseDigester


class BaseChargeCardDigester(BaseDigester):

     def matching_rollup_subject(self):
        raise Exception("Should never get here")

     def rewrite_rollup_emails(self, rollup_inbox_proxy, has_previous_message, previously_seen, sender_to_implicate):
        raise Exception("Should never get here")
