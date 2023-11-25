install:
	@echo "Adding cron job"
	(crontab -l ; echo "* * * * * cd `pwd` && python3 main.py") | crontab -
	@echo "Cron job added successfully."

uninstall:
	@echo "Removing cron job..."
	(crontab -l | grep -v "cd `pwd` && python3 main.py") | crontab -
	@echo "Cron job removed successfully."
