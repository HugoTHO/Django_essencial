import requests

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import authentication, permissions, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .forms import TaskFilter, SprintFilter
from .models import Sprint, Task
from .serializers import SprintSerializer, TaskSerializer, UserSerializer

User = get_user_model()

class DefaultMixin(object):
    """
    Configurações default para autenticação, permissões, filtragem e
    paginação da view.
    """
    
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

class UpdateHookMixin(object):
    """
    Classe Mixin para enviar informações sobre atualizações ao 
    servidor de websocket
    """

    def _build_hook_url(self, obj):
        if isinstance(obj, User):
            model = 'user'
        else:
            model = obj.__class__.__name__.lower()
        return '{}://{}/{}/{}'.format(
            'https' if settings.WATERCOOLER_SECURE else 'http',
            settings.WATERCOOLER_SERVER, model, obj.pk)
    
    def _send_hook_request(self, obj, method):
        url = self._build_hook_url(obj)
        try:
            response = requests.request(method, url, timeout=0.5)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            # Host não pôde ser resolvido ou a conexão foi recusada
            pass
        except requests.exceptions.Timeout:
            # Solicitação expirou
            pass
        except requests.exceptions.RequestException:
            # Servidor respondeu com código de status 4XX ou 5XX
            pass

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._send_hook_request(serializer.instance, 'POST')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._send_hook_request(serializer.instance, 'PUT')

    def perform_destroy(self, instance):
        self._send_hook_request(instance, 'DELETE')
        super().perform_destroy(instance)

class SprintViewSet(DefaultMixin, UpdateHookMixin, viewsets.ModelViewSet):
    """Endpoint da API para listar e criar sprints."""

    queryset = Sprint.objects.order_by('end')
    serializer_class = SprintSerializer
    filter_class = SprintFilter
    search_fields = ('name',)
    ordering_fields = ('end', 'name', )

class TaskViewSet(DefaultMixin, UpdateHookMixin, viewsets.ModelViewSet):
    """Endpoint da API para listar e criar tarefas."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_class = TaskFilter
    search_fields = ('name', 'description', )
    ordering_fields = ('name', 'order', 'started', 'due', 'completed', )

class UserViewSet(DefaultMixin, UpdateHookMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint da API para listar usuários."""

    lookup_field = User.USERNAME_FIELD
    lookup_url_kwarg = User.USERNAME_FIELD
    queryset = User.objects.order_by(User.USERNAME_FIELD)
    serializer_class = UserSerializer
    search_fields = (User.USERNAME_FIELD, )