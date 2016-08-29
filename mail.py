"""Mail Exporter class"""

# Copyright (c) Jupyter Development Team.
# Copyright (c) Neal Fultz 2016
# Distributed under the terms of the Modified BSD License.

import os

from traitlets import default
from traitlets.config import Config

from nbconvert.exporters.templateexporter import TemplateExporter
from nbconvert.postprocessors.base import PostProcessorBase

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

_visited = {}
def basename_attach(path):
    bn = os.path.basename(path)
    _visited[bn] = path
    return bn

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
        extra_loaders : list[of Jinja Loaders]
            ordered list of Jinja loader to find templates. Will be tried in order
            before the default FileSystem ones.
        template : str (optional, kw arg)
            Template to use when exporting.
        """
        super(MailExporter, self).__init__(config=config, **kw)
	self.register_filter('basename_attach', basename_attach)

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
    def default_config(self):
        c = Config({
            'ExtractOutputPreprocessor': {'enabled': True},
            'NbConvertBase': {
                'display_data_priority': ['text/html',
                                          'text/markdown',
                                          'image/svg+xml',
                                          'text/latex',
                                          'image/png',
                                          'image/jpeg',
                                          'text/plain'
                                          ]
            },

        })
        c.merge(super(MailExporter, self).default_config)
        return c





class MimePostProcessor(PostProcessorBase):
    def postprocess(self, input):
        msg = MIMEMultipart('alternative')

        msg['Subject'] = input

        with open(input) as f:
          msg.attach(MIMEText(f.read(), 'html'))

        for base, iname in _visited.items():
          with open(iname) as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<%s>' % base)
            msg.attach(img)
          os.remove(iname)

        with open(input, 'w') as f:
            f.write(msg.as_string())

