

%.mail : %.ipynb
	jupyter nbconvert --execute --config mail_config.py $<

%.sent : %.mail
	python sendmail.py $<
	mv $< $@
