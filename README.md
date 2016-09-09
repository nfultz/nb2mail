#nb2mail - send a jupyter notebook as an email

This repo contains a `jupyter nbconvert` exporter to convert notebooks to multipart MIME, and a postprocessor to 
send it via smtp.

## Installation

    pip install nb2mail

## Usage

`nb2mail` does not do anything by it self, it simply provides an export format ("mail") and postprocessor ("SendMailPostProcessor"). Please see the nbconvert documentation and example configuration for more information.

## Example

To generate a mail to send later with another process (eg `sendmail`):

    jupyter nbconvert --execute --to mail notebook.ipynb

To convert and also send a mail via gmail, you can set some environment variables, and declare a postprocessor with `--post`:

    export TO=example@example.ex GMAIL_USER=user GMAIL_PASS="*****"
    jupyter nbconvert --to mail --post=nb2mail.SendMailPostProcessor notebook.ipynb

Alternatively, you can configure the SMTP settings in a config file `config.py`:

    c = get_config()
    c.NbConvertApp.export_format = 'mail'
    c.Exporter.preprocessors = 'nbconvert.preprocessors.ExecutePreprocessor'
    c.NbConvertApp.postprocessor_class = 'nb2mail.SendMailPostProcessor'
    c.SendMailPostProcessor.recipient = 'example@example.ex'
    c.SendMailPostProcessor.smtp_user = 'user'
    c.SendMailPostProcessor.smtp_pass = '*******'
    c.SendMailPostProcessor.smtp_addr = 'smtp.gmail.com'
    c.SendMailPostProcessor.smtp_port = 587

and then simply run

    jupyter nbconvert --config config.py demo.ipynb  

## Refences

  * PyPI - https://pypi.python.org/pypi/nb2mail

## TODO

  * Prerender Math - no js in email
  * Plotly
  * Configable email headers
