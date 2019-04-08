"""Mail Exporter class"""

# Copyright (c) Jupyter Development Team.
# Copyright (c) Neal Fultz 2016, 2019
# Distributed under the terms of the Modified BSD License.

import os

import json
import mimetypes
import smtplib
import sys

from traitlets import default, Unicode, Int, Dict
from traitlets.config import Config

from nbconvert.exporters.html import HTMLExporter
from nbconvert.postprocessors.base import PostProcessorBase

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.parser import Parser

from base64 import b64decode
import uuid


def basename_attach(path, meta):
    if 'attach_file' not in meta : meta['attach_file'] = {}
    bn = os.path.basename(path)
    meta['attach_file'][bn] = path
    return bn

def data_attach(data,meta):
    if 'attach_data' not in meta : meta['attach_data'] = {}
    id = uuid.uuid4()
    meta['attach_data'][id] = b64decode(data)
    return id

class MailExporter(HTMLExporter):
    """
    Exports to a mail document (.mail)
    """

    headers = Dict(help="Mail Headers", traits={
        'from': Unicode(help="From header"),
        'to': Unicode(help="Comma-separated To header"),
        'cc': Unicode(help="Comma-separated Cc header"),
        'subject': Unicode(help="Subject header")
    }).tag(config=True)

    def __init__(self, config=None, **kw):
        """
        Public constructor

        Parameters
        ----------
        config : config
            User configuration instance.
        """
        super(MailExporter, self).__init__(config=config, **kw)
        self.register_filter('basename_attach', basename_attach)
        self.register_filter('data_attach', data_attach)

    @default('file_extension')
    def _file_extension_default(self):
        return '.mail'

    @default('template_file')
    def _template_file_default(self):
        return 'mail.tpl'

    output_mimetype = 'multipart/mixed'

    @default('raw_mimetypes')
    def _raw_mimetypes_default(self):
        return ['text/markdown', 'text/html', '']

    @property
    def template_path(self):
        """
        We want to inherit from HTML template, and have template under
        `./templates/` so append it to the search path. (see next section)
        """
        return super(MailExporter, self).template_path+[os.path.join(os.path.dirname(__file__), "templates")]


    def from_notebook_node(self, nb, resources=None, **kw):

        output, resources = super(MailExporter, self).from_notebook_node(nb, resources=resources, **kw)

        msg = MIMEMultipart('mixed')

        # Set headers from configuration values (if non-blank)
        for header, val in self.headers.items():
            msg[header] = val

        # Overrides from nb meta
        meta = nb['metadata'].get('nb2mail', {})
        for header in set(meta.keys()) & {'From', 'To', 'Cc', 'Subject'}:
            del msg[header]  # ensure that we are not adding duplicate header
            msg[header] = meta[header]

        # Use notebook name if there's no subject
        if not 'Subject' in msg.keys():
            msg['Subject'] = resources['metadata']['name']

        # Email attachements
        files = meta.get('attachments')
        for fileToSend in files or []:
            ctype, encoding = mimetypes.guess_type(fileToSend)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)
            mode = 'r' + ('b' if maintype != "text" else '')

            constructors = {"text": MIMEText, "image": MIMEImage, "audio": MIMEAudio}

            with open(fileToSend, mode) as fp:
                if maintype in constructors:
                    # Note: we should handle calculating the charset for text
                    attachment = constructors[maintype](fp.read(), _subtype=subtype)
                else:
                    attachment = MIMEBase(maintype, subtype)
                    attachment.set_payload(fp.read())
                    encoders.encode_base64(attachment)

            attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
            msg.attach(attachment)

        msg.attach(MIMEText(output, 'html'))

        if 'attach_data' in resources['metadata']:
            for id, img in resources['metadata']['attach_data'].items():
              img = MIMEImage(img)
              img.add_header('Content-ID', '<%s>' % id)
              msg.attach(img)

        output = msg.as_string()
        return output, resources


class SendMailPostProcessor(PostProcessorBase):

    recipient = Unicode(os.getenv("TO", ''), help="Recipient address").tag(config=True)
    smtp_user = Unicode(os.getenv("GMAIL_USER", ''), help="SMTP User" ).tag(config=True)
    smtp_pass = Unicode(os.getenv("GMAIL_PASS", ''), help="SMTP pass" ).tag(config=True)
    smtp_addr = Unicode("smtp.gmail.com", help="SMTP addr" ).tag(config=True)
    smtp_port = Int(587, help="SMTP port" ).tag(config=True)

    def postprocess(self, input):
        " Heavily borrowed from https://www.mkyong.com/python/how-do-send-email-in-python-via-smtplib/ "
        smtpserver = smtplib.SMTP(self.smtp_addr,self.smtp_port)
        smtpserver.ehlo()
        smtpserver.starttls()

        if self.smtp_user and self.smtp_pass:
            smtpserver.login(self.smtp_user, self.smtp_pass)

        with open(input) as f:
            email = Parser().parse(f)

        if not self.recipient:
            # Set recipients from .mail file
            # Multiple recipients can be comma seperated
            self.recipient = ','.join(filter(None, [email.get('To'), email.get('Cc')]))
        else:
            # Set To header from config
            email['To'] = self.recipient

        smtpserver.sendmail(self.smtp_user, self.recipient.split(','), email.as_string())

        smtpserver.close()
