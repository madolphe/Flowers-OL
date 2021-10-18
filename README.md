# Flowers-OL project

The aim of this project is to propose several tools to organize scientific tele-experimentations. Currently several 
applications (following the django terminology) can be used:
- An experiment manager app:
    - Sign in and login page
    - Schedule tasks according to your experimental design
    - Automaticaly send emails to ask your participant to come back
    - Fit with Prolific guidelines (e.g user redirection after participation)

- A survey app:
    - Add your questionaires in the form of JSON files
    - Use several widgets (e.g likert scale)
    
- A Multi-object tracking task:
    - As describe here: []

*A documentation is still in progress*


## How to install

If you want to run this project localy, you will need python > 3.6. First download this github repo by cloning it:
`git clone https://github.com/madolphe/Flowers-OL.git`. Then, `cd Flowers-OL`.

We would advise you to manage your virtual env with pipenv (you can get it simply with `pip install pipenv`) 
and use the Pipfile located in env/Pipfile:
`pipenv install`

To automaticaly deploy the project, you can use the deployment script:
- `cd flowers-ol`
- `pipenv run python scripts/deploy.py -r`

To deploy the project manually, please follow the guidelines:

- Create a folder 'migrations' in every app
- In all 'migrations' folder add a python file named '\__init\__.py'
- In Flowers-ol/flowers-ol run:
  - `pipenv shell`
  - `python manage.py makemigrations` 
  - `python manage.py migrate` 
  - `python manage.py loaddata experiment_manager_app/fixtures/*` 
  - `python manage.py loaddata survey_app/fixtures/*` 
  - `python manage.py collectstatic -l` 
  - `python manage.py createsuperuser`

## Current problems:
The kidlearn lib needed to run the MOT-app isn't open source anymore. If you are interested in the project and do not
need to use it, you can just:
- In Flowers-ol/flowers-ol/settings.py, delete in the installed application the MOT-app
- Maby other things?
  
## Notes:

When you add new fixtures, be careful if you are using same pks, loadatas won't work!
@TODO : python script to add new fixture (flush a particular table then load datas again)

