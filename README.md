# Multi-object tracking application

The aim of this project is to develop a django app providing a multiple object tracking task. This interface will be leverage in the context of an experiment studying how intelligent tutoring system could be used for attention training.

# Project information

Django and p5.js are used for running the experiment. The web interface would be soon accesible.


## Notes

1. Before serving the application, it is important to populate the database with some hand-coded data. This data is stored inside interface_app/fixtures as Django fixture files (JSON). To load the fixtures, run `$python manage.py loaddata <filename>`.

2. The database must conform to the models as defined in `interface_app/models.py`. To make sure this is satisfied, you can hard-reset the database entirely and remove all migration files, including the 0001_initial.py one. Then, using `django-extensions` (included in the `Pipfile` and setup in `settings.py`), run `python manage.py reset_db` to hard-reset the database, . After performing the hard-reset, create a new initial migration and run the server. You will need to repeat the step in the previous note to re-populate the refreshed DB with hand-coded data.
