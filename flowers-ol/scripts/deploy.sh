#! /bin/bash
# Check if user wants to reset_db: 

python flowers-ol/manage.py makemigrations

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

fixtures=''
function get_fixtures_name (){
  echo $1
  for file in $1; do
    name=${file##*/}
    fixtures+=" ${name}"
  done
}

folders=(flowers-ol/experiment_manager_app/fixtures/*.json flowers-ol/survey_app/fixtures/*.json)

for folder in "${folders[@]}"; do
  get_fixtures_name $folder $fixtures
  done

python flowers-ol/manage.py migrate
python flowers-ol/manage.py loaddata $fixtures
python flowers-ol/manage.py createsuperuser
