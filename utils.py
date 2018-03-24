

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

        multipart = msg.is_multipart()
        content_type_is_html = msg.get_content_type() == "text/html"

        text = ""
        if multipart:
            html = None
            for part in msg.get_payload():
                if part.get_content_charset() is None:
                    # We cannot know the character set, so return decoded "something"
                    text = part.get_payload(decode=True)
                    continue

                charset = part.get_content_charset()

                if part.get_content_type() == 'text/plain' and html_needed == False:
                    text = str(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
                    return text.strip()

                if part.get_content_type() == 'text/html' and html_needed == True:
                    html = str(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
                    return html.strip()
        elif not multipart and content_type_is_html:
            payload = msg.get_payload(decode=True)
            return payload.strip()
        else:
            if html_needed == False:
                chrset = msg.get_content_charset()
                if chrset is not None:
                    return str(msg.get_payload(decode=True), chrset, 'ignore').encode('utf8', 'replace').strip()
                else:
                    return msg.get_payload(decode=True)
            else:
                return None
