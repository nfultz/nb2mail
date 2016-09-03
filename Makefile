
%.mail : %.ipynb
	jupyter nbconvert --execute --config mail_config.py $<

