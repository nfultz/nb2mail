

%.html : %.ipynb
	jupyter nbconvert --execute --config jupyter_nbconvert_config.py --to html --template basic $<

%.mail : %.html
	python html2mail.py $< > $@

%.sent : %.mail
	python sendmail.py $<
	mv $< $@
