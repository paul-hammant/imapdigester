

class Utils(object):
    # From https://gist.github.com/miohtama/5389146
    @staticmethod
    def get_decoded_email_body(msg, html_needed):
        """ Decode email body.
        Detect character set if the header is not set.
        We try to get text/plain, but if there is not one then fallback to text/html.
        :param html_needed: html if True, or plain if False, or None perhaps
        :param message_body: Raw 7-bit message body input e.g. from imaplib. Double encoded in quoted-printable and latin-1
        :return: Message body as unicode string
        """

        text = ""
        if msg.is_multipart():
            html = None
            for part in msg.get_payload():
                if part.get_content_charset() is None:
                    # We cannot know the character set, so return decoded "something"
                    text = part.get_payload(decode=True)
                    continue

                charset = part.get_content_charset()

                if part.get_content_type() == 'text/plain' and html_needed == False:
                    text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
                    return text.strip()

                if part.get_content_type() == 'text/html' and html_needed == True:
                    html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
                    return html.strip()

        else:
            if html_needed == False:
                text = unicode(msg.get_payload(decode=True), msg.get_content_charset(), 'ignore') \
                    .encode('utf8', 'replace')
                return text.strip()
            else:
                return None
