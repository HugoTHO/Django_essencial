import django_filters

from django.forms import DateInput
from django.contrib.auth import get_user_model

from .models import Task, Sprint


User = get_user_model()


class NullFilter(django_filters.BooleanFilter):
    """Filtra de acordo com um campo definido como nulo ou não."""

    def filter(self, qs, value):
        if value is not None:
            return qs.filter(**{'%s__isnull' % self.field_name: value})
        return qs


class TaskFilter(django_filters.FilterSet):

    backlog = NullFilter(field_name='sprint', label='Backlog')

    class Meta:
        model = Task
        fields = ('sprint', 'status', 'assigned', 'backlog', )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['assigned'].extra.update(
            {'to_field_name': User.USERNAME_FIELD})


class SprintFilter(django_filters.FilterSet):
    
    end_min = django_filters.DateFilter(field_name='end', lookup_expr='gte',
        widget=DateInput(attrs={'type': 'date'}))
    end_max = django_filters.DateFilter(field_name='end', lookup_expr='lte',
        widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Sprint
        fields = ('end_min', 'end_max', )