import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from django.db import models


actual_user = get_user_model()


class TaskTagType(models.Model):
    name = models.TextField()
    # user_message = models.ForeignKey(actual_user, on_delete=models.CASCADE, related_name='user_message')

    def __str__(self):
        return f'{self.name}'


class TaskTag(models.Model):
    name = models.TextField()
    type = models.ForeignKey(TaskTagType, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'

# Create your models here.
class Task(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.TextField()
    description = models.TextField()
    deadline = models.DateTimeField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(actual_user, on_delete=models.CASCADE, related_name='task_creator_user')
    executor = models.ForeignKey(actual_user, on_delete=models.CASCADE, related_name='task_executor_user')
    co_executors = models.ManyToManyField(actual_user, related_name='task_co_executor_user')
    tags = models.ManyToManyField(TaskTag, through='TaskTagRelations')
    # Время начала и завершения работ
    task_start_time = models.DateTimeField(default=timezone.now, verbose_name="Время начала работ")

    def __str__(self):
        return f'({self.id}) {self.title}'

    def get_started_productions(self):
        return self.continuetasktimer_set.annotate(
            pause_count=Count('pausetasktimer')  # было pauseproductiontimer_set
        ).filter(pause_count=0)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

class TaskTagRelations(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    tag = models.ForeignKey(TaskTag, on_delete=models.CASCADE)
    set_time = models.DateTimeField(default=datetime.datetime.now, verbose_name="Время завершения работ")

class ContinueTaskTimer(models.Model):

    started_production = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Начатая работа")
    continue_time = models.DateTimeField(default=timezone.now, verbose_name="Время запуска")

    def __str__(self):
        return 'Cont ' + str(self.continue_time.strftime('%d.%m.%Y %H:%M'))

    class Meta:
        verbose_name = "Начало работ по задаче"
        verbose_name_plural = "Начала работ по Задаче"


class PauseTaskTimer(models.Model):

    pause_time = models.DateTimeField(default=timezone.now, verbose_name="Время остановки")
    related_start_timer = models.ForeignKey(ContinueTaskTimer, on_delete=models.CASCADE, verbose_name="Останавливаемый таймер")

    def __str__(self):
        return 'Pause ' + str(self.pause_time.strftime('%d.%m.%Y %H:%M')) + ' ' + str(self.related_start_timer)

    class Meta:
        verbose_name = "Приостановка работ по задаче"
        verbose_name_plural = "Приостановки работ по задаче"


class TaskFile(models.Model):
    parent = models.ForeignKey(Task, on_delete=models.CASCADE)
    file = models.FileField()


class TaskCommentType(models.Model):
    name = models.TextField()

    def __str__(self):
        return f'{self.name}'


class TaskComment(models.Model):
    parent = models.ForeignKey(Task, on_delete=models.CASCADE)
    commentator = models.ForeignKey(actual_user, on_delete=models.CASCADE, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    type = models.ForeignKey(TaskCommentType, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return f'{self.created_at.strftime("%d.%m.%Y %H:%M")} {self.commentator}'


class TaskCommentFile(models.Model):
    parent = models.ForeignKey(TaskComment, on_delete=models.CASCADE)
    file = models.FileField()

