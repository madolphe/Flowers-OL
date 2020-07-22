from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from ..models import Question, Answer
from ..forms import QuestionnaireForm
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
def test(request):
    if request.user.is_superuser:
        participant = request.user.participantprofile
        return render(request, 'test_page.html', locals())
    else:
        return HttpResponseForbidden()
