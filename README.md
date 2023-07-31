# nb2mail - send a jupyter notebook as an email

[![PyPI version](https://badge.fury.io/py/nb2mail.svg)](https://badge.fury.io/py/nb2mail)

This repo contains a `jupyter nbconvert` exporter to convert notebooks to multipart MIME, and a postprocessor to
send it via smtp.

## Installation

    pip install git+https://github.com/Thessal/nb2mail.git

## Usage

`nb2mail` does not do anything by itself. It provides an export format
("mail") and postprocessor ("SendMailPostProcessor"). Please see the nbconvert
documentation and example configuration for more information.

NOTE: BOTH sender and recipient email identities have to be verified to use AWS SES SMTP

## Example

To generate a mail and send it later with another process (eg `sendmail`):

    jupyter nbconvert --execute --to mail notebook.ipynb

### SMTP Example
To convert and send a mail via gmail, you can set the environment
variables and declare a postprocessor with `--post`:

    export FROM=sender@domain.abc TO=receipent@domain.def
    export SMTP_ADDR=email-smtp.region.amazonaws.com SMTP_PORT=587
    export SMTP_USER=aws_ses_smtp_auth SMTP_PASS=`echo $SMTP_HASH | base64 -d` 
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

and then run:

    jupyter nbconvert --config config.py demo.ipynb

### 3rd party email distributor Example
Instead of using SMTP to send emails, one can use 3rd party provider.  
This is an example for using [mailgun](examples/mailgun.ipynb) as a 3rd party provider

## Configuring Mail Headers

In the notebook metadata, you can set mail headers by adding a `nb2mail` block:

    "nb2mail": {
    "attachments": [
        "business_report_attachment.xlsx"
    ],
    "From": "reports@example.com",
    "To": "person1@example.com, person2@example.com",
    "Subject": "Business Report"
    }

You can specify multiple recipients by seperating them with commas.

## Disabling Pilcrows

Since CSS doesn't render the same in email, you may want to disable the pilcrows after each section.

    c.MailExporter.anchor_link_text = '' # disable pilcrow, requires nbconvert >= 5.2

## Refences

  * PyPI - https://pypi.python.org/pypi/nb2mail

## TODO

  * Prerender Math - no js in email
  * Prettier templates
  * Plotly - here is a workaround:

        # py.iplot(fig, filename=‘dcm_ctr_subplots’)
        # The above line is what you normally use to show your plots in the notebook
        # You no longer need that and just need the stuff below

        from IPython.display import Image

        py.image.save_as(fig, filename='yahoo_dcm_ctr_subplots.png')
        Image('yahoo_dcm_ctr_subplots.png')
