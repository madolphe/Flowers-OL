from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from manager_app.models import ParticipantProfile, Study
from survey_app.models import Answer, Question
from .models import CognitiveTask, CognitiveResult
from django.conf import settings
import os
from .views import cog_results_exists_in_db


# Create your tests here.
# Instantiate client and user:
class TestConnexion(TestCase):

    def get_fixtures():
        apps = settings.USER_APPS
        apps.remove('survey_app')

        fixtures = []
        for app in apps:
            if os.path.isdir(f'flowers-ol/{app}/fixtures/'):
                for f in os.listdir(f'flowers-ol/{app}/fixtures'):
                    fixtures.append(f)
        return fixtures

    fixtures = get_fixtures()

    def setUp(self):
        self.c = Client()
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        user.save()

        study = Study.objects.get(name='v0_ubx')
        participant_profile = ParticipantProfile(user=user, study=study)
        participant_profile.save()
        participant_profile.populate_session_stack()

        question = Question.objects.get(handle='prof-mot-1')
        ans = Answer(participant=participant_profile, question=question)
        ans.save()

    def test_co(self):
        self.c.login(username='john', password='johnpassword')
        response = self.c.get('/home')
        # response = self.c.get('/cognitive_assessment_home')
        self.assertEqual(response.status_code, 302)

    def test_cog_results_exists_in_db(self):
        # Log and add tasks
        self.c.login(username='john', password='johnpassword')
        response = self.c.get('/cognitive_assessment_home')
        participant = ParticipantProfile.objects.get(user=response.wsgi_request.user.id)
        task_stack = participant.extra_json['cognitive_tests_task_stack']
        for i in range(4):
            cog_task = CognitiveTask.objects.get(name=task_stack[i])
            self.assertEqual(cog_results_exists_in_db(cog_task, participant), False)
            cog_res = CognitiveResult(participant=participant, cognitive_task=cog_task, status='PRE_TEST', idx=int(i))
            cog_res.save()
            self.assertEqual(cog_results_exists_in_db(cog_task, participant), True)
        self.assertEqual(cog_results_exists_in_db(CognitiveTask.objects.get(name=task_stack[0]), participant), True)

    def test_break(self):
        self.c.login(username='john', password='johnpassword')
        response = self.c.get('/cognitive_assessment_home')
        participant = ParticipantProfile.objects.get(user=response.wsgi_request.user.id)
        task_stack = participant.extra_json['cognitive_tests_task_stack']
        self.assertEqual(response.status_code, 200)
        for i in range(3):
            # SIMULATION OF EXITING TASK + RETRIEVE PARTICIPANT FROM RESPONSE OF EXIT VIEW
            response = self.c.post('/exit_view_cognitive_task', {'task_id': i})
            participant = ParticipantProfile.objects.get(user=response.wsgi_request.user.id)
            # CHECK THAT COGNITIVE RESULT HAS BEEN STORED:
            cognitive_results = CognitiveResult.objects.get(participant=participant, cognitive_task__name=task_stack[i])
            self.assertEqual(cognitive_results.results['task_id'], str(i))
            # SEE THAT RESPONSE STATUS IS 200:
            response = self.c.get('/cognitive_assessment_home')
            self.assertEqual(response.status_code, 200)

        # REQUESTING TWICE THE EXIT VIEW --> CODE STATUS IS 302 (REVERSE)
        response = self.c.post('/exit_view_cognitive_task', {'task_id': 4})
        response = self.c.get('/cognitive_assessment_home')
        participant = ParticipantProfile.objects.get(user=response.wsgi_request.user.id)

        # ASKING A SECOND TIME WITH SAME TASK --> CODE STATUS SHOULD STAY 302 (FOR THAT WE NEED TO USE IDX -1,
        # TO PROPOSE LAST TASK)
        participant.extra_json['cognitive_tests_current_task_idx'] -= 1
        participant.save()
        response = self.c.post('/exit_view_cognitive_task', {'task_id': 4})
        participant = ParticipantProfile.objects.get(user=response.wsgi_request.user.id)
        self.assertEqual(response.status_code, 302)

    def test_end(self):
        pass
