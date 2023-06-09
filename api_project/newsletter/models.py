from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator


class Client(models.Model):
    phone_regex = RegexValidator(
        regex=r'^7\d{10}$',
        message="Номер телефона в формате 7XXXXXXXXXX (X - цифра от 0 до 9)")
    phone_number = models.CharField(
        validators=[phone_regex, ], max_length=11, unique=True,
        verbose_name='Номер телефона клиента')
    code = models.CharField(
        max_length=3, verbose_name='Код мобильного оператора')
    tag = models.CharField(max_length=200, verbose_name='Тег')
    timezone = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        verbose_name='Часовой пояс')

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'


class MailingList(models.Model):
    time_start = models.DateTimeField(
        verbose_name='Дата и время запуска рассылки')
    time_end = models.DateTimeField(
        verbose_name='Дата и время окончания рассылки')
    text = models.TextField(
        verbose_name='Текст сообщения для доставки клиенту')
    filter_code = models.CharField(
        null=True, blank=True,
        max_length=3,
        verbose_name='Фильтр: код мобильного оператора')
    filter_tag = models.CharField(
        null=True, blank=True,
        max_length=200, verbose_name='Фильтр: тег')

    def __str__(self):
        return f'{self.pk} {self.time_start} {self.time_end}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Message(models.Model):
    created = models.DateTimeField(
        verbose_name='Отправка')
    status = models.JSONField(null=True, blank=True, verbose_name='Статус')
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='client',
        verbose_name='Клиент')
    distribution = models.ForeignKey(
        MailingList, on_delete=models.CASCADE, related_name='distribution',
        verbose_name='Рассылка')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
