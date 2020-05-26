# Multi-object tracking application

The aim of this project is to develop a django app providing a multiple object tracking task. This interface will be leverage in the context of an experiment studying how intelligent tutoring system could be used for attention training.

# Project information

Django and p5.js are used for running the experiment. The web interface would be soon accesible.


# Notes

Before serving the application, it is important to populate the database with some hardcoded data. This data is stored inside interface_app/fixtures as Django fixture files (JSON). To load the fixtures, run `$python manage.py load data <filename>`.
