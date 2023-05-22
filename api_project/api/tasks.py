import datetime
import requests
import logging

from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail

from django.conf import settings
from api_project.celery import app
from newsletter.models import Message, Client, MailingList


logger = logging.getLogger('main')


@app.task
def send_one_notify(distribution_id: int, client_id: int):
    distribution = MailingList.objects.get(pk=distribution_id)
    client = Client.objects.get(pk=client_id)
    now = timezone.now()
    message = Message(created=now, client=client, distribution=distribution,)
    message.save()

    if now > distribution.time_end:
        res = {'code': 2, 'message': 'Message expired'}
        logger.warning(f'MESSAGE:{message.pk} DISTRIBUTION:{distribution.pk} CLIENT:{client.pk} expired.')
    else:
        s_head = {      # заголовок запроса
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(settings.TOKEN), }
        s_data = {      # тело запроса
            'id': message.pk,
            'phone': int(client.phone_number),
            'text': distribution.text, }
        try:
            # Запрос
            res = requests.post(
                f'https://probe.fbrq.cloud/v1/send/{message.pk}',
                json=s_data, headers=s_head).json()
            logger.info(f'MESSAGE:{message.pk} DISTRIBUTION:{distribution.pk} CLIENT:{client.pk} delivered successfully.')
        except:
            # Ошибка сети
            res = {'code': 1, 'message': 'Network error'}
            logger.error(f'MESSAGE:{message.pk} DISTRIBUTION:{distribution.pk} CLIENT:{client.pk} not delivered. Network error.')
        finally:
            pass

    message.status = res
    message.save()  # Сохраняем результат выполнения запроса


def recipients(distribution_id: int):
    dist = MailingList.objects.get(pk=distribution_id)

    q = Q()
    if dist.filter_code:
        q = q & Q(code=dist.filter_code)
    if dist.filter_tag:
        q = q & Q(tag=dist.filter_tag)
    return Client.objects.filter(q)


@app.task
def make_distribution(distribution_id: int):
    clients = recipients(distribution_id)

    for client in clients:
        send_one_notify.delay(distribution_id, client.pk)


@app.task
def send_daily_stats():
    yesterday = timezone.now() - datetime.timedelta(days=1)
    dist_count = MailingList.objects.filter(
        time_start__year=yesterday.year,
        time_start__month=yesterday.month,
        time_start__day=yesterday.day
    )
    mess_count = Message.objects.filter(
        created__year=yesterday.year,
        created__month=yesterday.month,
        created__day=yesterday.day
    )

    # Отправляем письмо
    return send_mail(
        f'Daily Stats {yesterday.date()}',
        f'Distributions: {dist_count} Messages: {mess_count}',
        settings.SERVER_EMAIL,
        [settings.SERVER_EMAIL, ],
        fail_silently=False,
    )
