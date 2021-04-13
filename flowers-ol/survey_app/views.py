from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Question, Answer
from .forms import QuestionnaireForm, ConsentForm
from django.db.models import Count


@login_required
@never_cache
def questionnaire(request):
    """Construct a questionnaire block and render question groups on different pages"""
    participant = request.user.participantprofile
    if 'questions_extra' not in participant.extra_json:
        task_extra = participant.current_task.extra_json
        questions = Question.objects.filter(
            instrument__in = task_extra['instruments']
        )
        for k, v in task_extra.setdefault('exclude', {}).items():
            questions = questions.exclude(**{k: v})
        groups = [i for i in questions.values('instrument', 'group').annotate(size=Count('handle'))]
        order = {k: v for v, k in enumerate(task_extra['instruments'])}
        for d in groups:
            d['order'] = order[d['instrument']]
        groups = sorted(groups, key=lambda d: (d['order'], d['group']))
        grouped_handles = []
        for group in groups:
            grouped_handles.append(
                tuple(questions.filter(
                    instrument__exact = group['instrument'],
                    group__exact = group['group']
                ).values_list('handle', flat=True))
            )
        participant.extra_json['questions_extra'] = {'grouped_handles': grouped_handles}
        participant.extra_json['questions_extra']['ind'] = 0
        participant.save()
    questions_extra = participant.extra_json['questions_extra']
    groups = questions_extra['grouped_handles']
    ind = questions_extra['ind']
    questions = Question.objects.filter(
        handle__in = groups[ind]
    )
    form = QuestionnaireForm(questions, request.POST or None)
    if form.is_valid():
        for q in questions:
            if q.widget != 'custom-header':
                answer = Answer()
                answer.participant = participant
                answer.session = participant.current_session
                answer.question = q
                answer.value = form.cleaned_data[q.handle]
                answer.save()
        participant.extra_json['questions_extra']['ind'] += 1
        participant.save()
        if participant.extra_json['questions_extra']['ind'] == len(groups):
            del participant.extra_json['questions_extra']
            participant.save()
            return redirect(reverse('end_task'))
        return redirect(reverse(questionnaire))
    return render(request, 'tasks/JOLD_Questionnaire/question_block.html', {'CONTEXT': {
        'form': form,
        'current_page': groups.index(groups[ind]) + 1,
        'nb_pages': len(groups)
    }})


@login_required
def consent_page(request):
    user = request.user
    participant = user.participantprofile
    study = participant.study
    greeting = "Salut, {0} !".format(user.username)
    form = ConsentForm(request.POST or None)
    if form.is_valid():
        user.first_name = request.POST['nom']
        user.last_name = request.POST['prenom']
        user.save()
        participant.consent = True
        participant.save()
        participant.populate_session_stack()
        return redirect(reverse(home))
    if request.method == 'POST': person = [request.POST['nom'], request.POST['prenom']]
    return render(request, 'consent_page.html', {'CONTEXT': {
        'greeting': greeting,
        'person': [request.user.first_name.capitalize(), request.user.last_name.upper()],
        'study': study,
        'form': form}})