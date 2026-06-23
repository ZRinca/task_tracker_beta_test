from django.contrib import admin

# Register your models here.
from django.contrib.admin.options import *
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.translation import gettext as _
from django.contrib.admin import site


site.site_title = 'TaskTracker'
site.site_header = 'Task tracker'
site.index_title = 'MAIN'


RelatedFieldWidgetWrapper.template_name = 'admin/custom_related_widget_wrapper.html'


class ForeignFieldWidget(widgets.ForeignKeyRawIdWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context['widget']['type'] = 'hidden'

        return context


def formfield_for_foreignkey(self, db_field, request, **kwargs):
    """
    Get a form Field for a ForeignKey.
    """
    db = kwargs.get("using")

    if "widget" not in kwargs:
        if db_field.name in self.get_autocomplete_fields(request):
            kwargs["widget"] = AutocompleteSelect(
                db_field, self.admin_site, using=db
            )
        elif db_field.name in self.raw_id_fields:
            kwargs["widget"] = widgets.ForeignKeyRawIdWidget(
                db_field.remote_field, self.admin_site, using=db
            )
        elif db_field.name in self.radio_fields:
            kwargs["widget"] = widgets.AdminRadioSelect(
                attrs={
                    "class": get_ul_class(self.radio_fields[db_field.name]),
                }
            )
            kwargs["empty_label"] = (
                kwargs.get("empty_label", _("None")) if db_field.blank else None
            )
        elif db_field.name not in getattr(self, 'std_foreign_fields', []):
            kwargs["widget"] = ForeignFieldWidget(
                db_field.remote_field, self.admin_site, using=db
            )

    if "queryset" not in kwargs:
        queryset = self.get_field_queryset(db, db_field, request)
        if queryset is not None:
            kwargs["queryset"] = queryset

    return db_field.formfield(**kwargs)


BaseModelAdmin.formfield_for_foreignkey = formfield_for_foreignkey
