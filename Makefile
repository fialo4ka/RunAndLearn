deploy:
	rm -rf temp
	scp -r build/* static.web.cyberfred.eu:/var/www/de.fialo.info/