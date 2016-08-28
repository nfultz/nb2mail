#!/usr/bin/env python

import smtplib
import os
import sys

# Heavily borrowed from https://www.mkyong.com/python/how-do-send-email-in-python-via-smtplib/
def main():
    to = os.getenv("TO")
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pwd = os.getenv("GMAIL_PASS")
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.login(gmail_user, gmail_pwd)

    with open(sys.argv[1]) as f:
        smtpserver.sendmail(gmail_user, to, f.read())

    smtpserver.close()

if __name__ == '__main__':
    main()
