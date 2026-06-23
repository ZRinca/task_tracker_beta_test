from xxlimited_35 import Null

from tasks.models import Task, ContinueTaskTimer, PauseTaskTimer, TaskTag
from django.http.response import HttpResponse
from django.shortcuts import redirect
import datetime


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

