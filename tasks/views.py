from xxlimited_35 import Null

from tasks.models import Task, ContinueTaskTimer, PauseTaskTimer, TaskTag
from tasks.services.time_utils import get_end_of_month, get_start_of_month, split_time
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
import datetime
import json


def get_total_time_spent(request):

    request_data = json.loads(request.body.decode('utf-8'))

    all_time = 0
    time_past_month = 0
    time_current_month = 0

    current_timezone = timezone.now()
    past_month_and_year = {
        "past_year": current_timezone.year - 1 if current_timezone.month == 1 else current_timezone.year,
        "past_month": 12 if current_timezone.month == 1 else current_timezone.month - 1,
    }

    # if current_timezone.month == 1: past_month_and_year['past_month'] = 12
    # else: past_month_and_year['past_month'] = current_timezone.month - 1

    id_task = request_data.get('id_task')
    if not id_task: return HttpResponse("Ошибка при чтении тела", status=400)

    all_timer = ContinueTaskTimer.objects.filter(started_production__id=id_task).all()

    for el_timer in all_timer:

        pause_task_timer = el_timer.pausetasktimer_set.first()

        if pause_task_timer is None: pause_time = timezone.now()
        else: pause_time = pause_task_timer.pause_time

        continue_time = el_timer.continue_time

        all_time += (pause_time - continue_time).total_seconds()

        # calculate time for "past_month"
        if continue_time.month == past_month_and_year['past_month'] and continue_time.year == past_month_and_year['past_year']:
            if pause_time.month == past_month_and_year['past_month']:
                time_past_month += (pause_time - continue_time).total_seconds()
                continue
            else:
                time_past_month += (get_end_of_month(past_month_and_year['past_year'], past_month_and_year['past_month']) - continue_time).total_seconds()

        if continue_time.month < past_month_and_year['past_month']:
            if pause_time.month == past_month_and_year['past_month']:
                time_past_month += (pause_time - get_start_of_month(
                    past_month_and_year['past_year'],
                    past_month_and_year['past_month'])).total_seconds()
                continue
            if pause_time.year > past_month_and_year['past_year'] or \
            (pause_time.year == past_month_and_year['past_year'] and pause_time.month > past_month_and_year[
                        'past_month']):
                time_past_month += (get_end_of_month(past_month_and_year['past_year'], past_month_and_year['past_month']) - get_start_of_month(past_month_and_year['past_year'],past_month_and_year['past_month'])).total_seconds()
                continue
            if pause_time.month < past_month_and_year['past_month']:
                continue

        # calculate time for "current_month"
        if continue_time.month == current_timezone.month and continue_time.year == current_timezone.year:
            if pause_time.month == current_timezone.month:
                time_current_month += (pause_time - continue_time).total_seconds()
            else:
                time_current_month += (get_end_of_month(continue_time.year, current_timezone.month) - continue_time).total_seconds()
            continue

        if pause_time.month == current_timezone.month and pause_time.year == current_timezone.year:
            start_month = get_start_of_month(current_timezone.year, current_timezone.month)
            if continue_time < start_month:
                time_current_month += (pause_time - start_month).total_seconds()
            else:
                time_current_month += (pause_time - continue_time).total_seconds()
            continue

    # calculated in seconds
    # return HttpResponse(json.dumps({"all_time":all_time, "time_past_month": time_past_month, "time_current_month":time_current_month}), content_type="application/json")
    # calculated in full time

    answer = {
        "all_time": split_time(all_time),
        "time_past_month": split_time(time_past_month),
        "time_current_month": split_time(time_current_month)
    }

    return HttpResponse(json.dumps(answer),content_type="application/json")


def execute_task(request):
    task_id = request.GET.get('task')

    if task_id is None: return HttpResponse("Некоректный запрос", status=400)

    try: current_task = Task.objects.get(id=task_id)
    except Task.DoesNotExist: return HttpResponse("Задача не найдена", status=400)

    # Тег "Выполнена"
    completed_tag = TaskTag.objects.filter(id=2).first()
    if not completed_tag: return HttpResponse("Задача не найдена", status=400)

    if current_task.tags.first() == completed_tag: return HttpResponse("Задача уже Выполнена", status=400)
    else: current_task.tags.set([completed_tag])

    return redirect('admin:tasks_task_changelist')


def add_task(request):
    task_id = request.GET.get('task')
    action = request.GET.get('action')

    if not task_id or not action:
        return HttpResponse("Ошибка: не хватает параметров")

    task = Task.objects.get(id=task_id)

    if action == 'start':
        ContinueTaskTimer.objects.create(
            started_production=task,
            continue_time=datetime.datetime.now()
        )
        # return HttpResponse("Таймер запущен")

    elif action == 'pause':
        active_timers = task.get_started_productions()  # таймеры без пауз
        if active_timers.exists():
            timer = active_timers.first()
            PauseTaskTimer.objects.create(
                related_start_timer=timer,
                pause_time=datetime.datetime.now()
            )
        else:
            return HttpResponse("Нет активного таймера", status=400)

    return redirect('admin:tasks_task_changelist')

