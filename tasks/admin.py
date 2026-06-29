from django.contrib import admin
from django.utils.html import format_html

from . import models


class ContinueTaskTimerInline(admin.TabularInline):
    model = models.ContinueTaskTimer
    extra = 1
    fields = ('continue_time', 'show_pauses', 'total_duration')  # новое поле
    readonly_fields = ('show_pauses', 'total_duration')          # оба поля только для чтения

    def show_pauses(self, obj):
        pauses = obj.pausetasktimer_set.all()
        if not pauses:
            return "Нет пауз"
        return ", ".join(str(p) for p in pauses)
    show_pauses.short_description = "Список пауз"

    def total_duration(self, obj):
        from django.utils import timezone

        last_pause = obj.pausetasktimer_set.last()
        end_time = last_pause.pause_time if last_pause else timezone.now()
        duration = end_time - obj.continue_time

        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours} ч {minutes} мин {seconds} с"
        elif minutes > 0:
            return f"{minutes} мин {seconds} с"
        else:
            return f"{seconds} с"

    total_duration.short_description = "Общая длительность"


class TaskCommentInline(admin.TabularInline):
    model = models.TaskComment
    extra = 0
    template = "admin/task_comment_inline.html"


class TaskFileInline(admin.TabularInline):
    model = models.TaskFile
    extra = 0


class TaskInline(admin.TabularInline):
    verbose_name_plural = 'Children tasks'
    model = models.Task
    extra = 0
    show_change_link = True
    # template = "admin/links_inline.html"

class TaskTagRelationsInline(admin.TabularInline):
    # verbose_name_plural = 'Children tasks'
    # model = models.TaskTagRelations
    # extra = 0
    model = models.TaskTagRelations
    extra = 0
    fields = ('tag', 'set_time', 'tag_type')   # добавляем поле
    readonly_fields = ('tag_type',)            # оно только для чтения

    def tag_type(self, obj):
        return obj.tag.type.name if obj.tag else '-'
    tag_type.short_description = 'Тип тега'
    # show_change_link = True

class TaskAdmin(admin.ModelAdmin):
    inlines = [TaskTagRelationsInline, TaskFileInline, TaskCommentInline, TaskInline, ContinueTaskTimerInline]
    filter_horizontal = ['co_executors']

    list_display = [
        'name_task', 'name_tag','timer', 'deadline_display',
        'task_execute_now',
        'task_execute',
    ]

    def deadline_display(self, obj):
        # return obj.deadline.strftime('%d.%m.%Y %H:%M')
        return obj.deadline
        # return f"{obj.deadline.day}.{obj.deadline.month}.{obj.deadline.year} {obj.deadline.hour}:{obj.deadline.minute}"
    deadline_display.short_description = 'Дедлайн'

    def name_task(self, obj):
        return f"Задача - {obj.description}"
    name_task.short_description = 'Задача'

    def name_tag(self, obj):
        all_tags = obj.tags.all()
        data_tag = ''
        for el_tag in all_tags:
            if el_tag.type.name != "Статус":
                data_tag += f"<span style='background: var(--selected-row); margin: 2px; padding: 2px 6px; border-radius: 4px;'><span style='color: var(--link-fg);'>{el_tag.name}</span></span><br><br>"
        return format_html(data_tag)
    name_tag.short_description = 'Теги'

    def task_execute_now(self, obj):
        style_green = ''
        tags_first = obj.tags.first()
        text_element = obj.tags.last()

        for el_tag in obj.tags.all():
            if el_tag.type.name == "Статус":
                if tags_first is not None:
                    text_element = el_tag.name
                    if el_tag.name == "Выполнена": style_green = 'color: #32CD32'
                    break
                else:
                    if text_element is None: text_element = 'Неопределено'
                    break

        if tags_first is not None:
            if tags_first.id == 2: style_green = 'color: #32CD32'
        return format_html(f'<span style="background: var(--selected-row); margin: 2px; padding: 2px 6px; border-radius: 4px;">'
                            f'<span style="color: var(--link-fg);  {style_green}">{text_element}</span>'
                            f'</span>')
    task_execute_now.short_description = 'Статус'


    def timer(self, obj):
        started = obj.get_started_productions()

        gray_span = '<span style="color: gray">▶ Запустить</span>'

        if obj.tags.first() is None: return format_html(gray_span)

        if obj.tags.first().id == 2: return format_html(gray_span,str(obj.id),)

        if len(started) == 0:
            return format_html(
                '<a href="../taskworkend/add/?task={}&action=start">▶ Запустить</a>',
                            str(obj.id),)
        else:
            return format_html(
                    '<a href="../taskworkend/add/?task={}&action=pause">■ Приостановить</a>',
                                str(obj.id),)
    timer.short_description = 'Таймер'

    def task_execute(self, obj):
        tags_first = obj.tags.first()
        color_text = 'style="color: gray"'

        if tags_first is None: return format_html(f'<span {color_text}>Выполнить</span>')

        if tags_first.id == 2:
            return format_html(f'<span {color_text}>'
                               f'Выполнить'
                               f'</span>',
                               str(obj.id),
                               )
        return format_html('<a href="../taskworkend/execute/?'
                           'task={0}'
                           '">'
                           'Выполнить'
                           '</a>',
                           str(obj.id),
                           )
    task_execute.short_description = 'Выполнить задачу'
    # readonly_fields = ['start_time', 'end_time']

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        # <<< ВОТ ЭТОГО У ТЕБЯ НЕ БЫЛО
        for obj in formset.deleted_objects:
            obj.delete()

        for instance in instances:
            if isinstance(instance, models.TaskComment):
                if not instance.commentator_id:
                    instance.commentator = request.user

                if not instance.type_id:
                    default_type, _ = models.TaskCommentType.objects.get_or_create(
                        name='Обычный комментарий'
                    )
                    instance.type = default_type

            instance.save()

        formset.save_m2m()



# Register your models here.
admin.site.register(models.PauseTaskTimer)
admin.site.register(models.TaskTagType)
admin.site.register(models.TaskTag)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.TaskCommentType)
admin.site.register(models.TaskTagRelations)
# admin.site.register(models.TaskComment)
