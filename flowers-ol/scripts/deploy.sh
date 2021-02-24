#! /bin/bash
# Check if user wants to reset_db: 

pipenv run python flowers-ol/manage.py makemigrations

if [ ! -z $1 ]; then
	if [ $1 = "reset_db" ]; then
		read -p "You really want to delete db (y/n)? " -n 1 -r
		echo    # (optional) move to a new line
		if [[ ! $REPLY =~ ^[Yy]$ ]]; then
			echo 'Reset db aborted'
		else
			pipenv run python flowers-ol/manage.py reset_db
		fi
	fi
fi

# To load datas, either manualy or load all fixtures in fixtures folder:
#pipenv run python manage.py loaddata JOLDSessions JOLDTasks MOTSessions MOTTasks Questions Questions_mot Studies

folder=flowers-ol/interface_app/fixtures/*.json
fixtures=''
for file in $folder; do
  echo $file
	fixtures="$fixtures ${file:34}"
done
echo "$fixtures"

pipenv run python flowers-ol/manage.py migrate
pipenv run python flowers-ol/manage.py loaddata $fixtures
pipenv run python flowers-ol/manage.py createsuperuser

