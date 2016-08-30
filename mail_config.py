# Configuration file for jupyter-nbconvert / nb2email
c = get_config()
c.NbConvertApp.export_format = 'mail.MailExporter'
c.NbConvertApp.postprocessor_class = 'mail.MimePostProcessor'
