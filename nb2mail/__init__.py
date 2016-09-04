"""Mail Exporter class"""

# Copyright (c) Jupyter Development Team.
# Copyright (c) Neal Fultz 2016
# Distributed under the terms of the Modified BSD License.

import os

import smtplib
import sys

from traitlets import default, Unicode, Int
from traitlets.config import Config

from nbconvert.exporters.templateexporter import TemplateExporter
from nbconvert.postprocessors.base import PostProcessorBase

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

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

class MailExporter(TemplateExporter):
    """
    Exports to a mail document (.mail)
    """
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
        return 'mail'

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


        msg = MIMEMultipart('alternative')

        msg['Subject'] = resources['metadata']['name']

        msg.attach(MIMEText(output, 'html'))

        if 'attach_data' in resources['metadata']:
            for id, img in resources['metadata']['attach_data'].items():
              img = MIMEImage(img)
              img.add_header('Content-ID', '<%s>' % id)
              msg.attach(img)

        output = msg.as_string()
        return output, resources


class SendMailPostProcessor(PostProcessorBase):
    
    recipient = Unicode(os.getenv("TO"),help="Recipient address").tag(config=True)
    smtp_user = Unicode(os.getenv("GMAIL_USER"),help="SMTP User" ).tag(config=True)
    smtp_pass = Unicode(os.getenv("GMAIL_PASS"),help="SMTP pass" ).tag(config=True)
    smtp_addr = Unicode("smtp.gmail.com", help="SMTP addr" ).tag(config=True)
    smtp_port = Int(587, help="SMTP port" ).tag(config=True)

    def postprocess(self, input):
	" Heavily borrowed from https://www.mkyong.com/python/how-do-send-email-in-python-via-smtplib/ "
	smtpserver = smtplib.SMTP(self.smtp_addr,self.smtp_port)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.login(self.smtp_user, self.smtp_pass)

	with open(input) as f:
	    smtpserver.sendmail(self.smtp_user, self.recipient, f.read())

	smtpserver.close()
