

%.mail : %.ipynb
	jupyter nbconvert --execute --config jupyter_nbconvert_config.py $<

%.sent : %.mail
	python sendmail.py $<
	mv $< $@
