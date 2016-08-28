#!/usr/bin/env python

import sys
import re
from os.path import basename



from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage



def main():
    msg = MIMEMultipart('alternative')

    fname = sys.argv[1]
    msg['Subject'] = fname

    with open(fname) as f:
      html = f.read()

    images = [ match for match in re.finditer('(?<=<img src=")[^"]+', html) ]

    for i in range(len(images)-1, -1, -1):
      match = images[i]
      iname = match.group()
      base = basename(iname)
      images[i] = (base, iname)
      html = html[:match.start()] + "cid:" + base + html[match.end():]

    msg.attach(MIMEText(html, 'html'))

    for base, iname in images:
      with open(iname) as f:
        img = MIMEImage(f.read())
      img.add_header('Content-ID', '<%s>' % base)
      msg.attach(img)

    print msg.as_string()


if __name__ == '__main__':
        main()

