import logging
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, extend_schema_view

from api.serializers import (ClientSerializer, MailingListSerializer,
                             MessageSerializer)
from api.tasks import recipients
from newsletter.models import Client, MailingList, Message


logger = logging.getLogger('main')


@extend_schema_view(
    list=extend_schema(summary='Список всех получателей'),
    create=extend_schema(summary='Создание получателя'),
    retrieve=extend_schema(summary='Детальные данные получателя'),
    update=extend_schema(summary='Создание/изменение получателя'),
    partial_update=extend_schema(summary='Изменение получателя'),
    destroy=extend_schema(summary='Удаление получателя'),)
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def perform_create(self, serializer):
        client = serializer.save()
        logger.info(f'Client:{client.id} created.')

    def perform_update(self, serializer):
        client = serializer.save()
        logger.info(f'Client:{client.id} updated.')

    def perform_destroy(self, serializer):
        logger.info(f'Client:{serializer.id} deleted.')
        serializer.delete()


@extend_schema_view(
    list=extend_schema(summary='Список всех рассылок'),
    create=extend_schema(summary='Создание рассылки'),
    retrieve=extend_schema(summary='Детальные данные по рассылке'),
    update=extend_schema(summary='Создание/изменение рассылки'),
    partial_update=extend_schema(summary='Изменение рассылки'),
    destroy=extend_schema(summary='Удаление рассылки'),)
class MailingListViewSet(viewsets.ModelViewSet):
    queryset = MailingList.objects.all()
    serializer_class = MailingListSerializer

    def perform_create(self, serializer):
        serializer.save()
        return Response(
            {'distribution': 'created'},
            status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        d = serializer.save()
        logger.info(f'DISTRIBUTION:{d.id} updated.')

    def perform_destroy(self, serializer):
        logger.info(f'DISTRIBUTION:{serializer.id} deleted.')
        serializer.delete()


@extend_schema_view(
    list=extend_schema(summary='Список всех сообщений'),)
class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


@extend_schema_view(
    get=extend_schema(summary='Статистика по рассылке'),)
class StatMailingListAPIView(APIView):
    def get(self, request, id):
        try:
            MailingList.objects.all().get(pk=id)
        except ObjectDoesNotExist:
            data = {
                'code': 4,
                'message': f'Distribution {id} Does not exist',
            }
        else:
            data = {
                'distribution': id,
                'recipients': len(recipients(id)),
                'sent': Message.objects.filter(distribution=id).count(),
                'status_0_ok': Message.objects.filter(
                                            distribution=id
                                            ).filter(status__code=0).count(),
                'error_1_network': Message.objects.filter(
                                            distribution=id
                                            ).filter(status__code=1).count(),
                'error_2_expired': Message.objects.filter(
                                            distribution=id
                                            ).filter(status__code=2).count(),
            }
        finally:
            return Response(data)


@extend_schema_view(
    get=extend_schema(summary='Общая статистика'),)
class TotalStatAPIView(APIView):
    def get(self, request):
        data = {
            'distributions': MailingList.objects.all().count(),
            'recipients': Client.objects.all().count(),
            'sent': Message.objects.all().count(),
            'status_0_ok': Message.objects.filter(status__code=0).count(),
            'error_1_network': Message.objects.filter(status__code=1).count(),
            'error_2_expired': Message.objects.filter(status__code=2).count(),
        }
        return Response(data)
