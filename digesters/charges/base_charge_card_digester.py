from digesters.base_digester import BaseDigester


class BaseChargeCardDigester(BaseDigester):

     def matching_digest_subject(self):
        raise Exception("Should never get here")

     def rewrite_digest_emails(self, digest_folder_proxy, has_previous_message, previously_seen, sender_to_implicate):
        raise Exception("Should never get here")
