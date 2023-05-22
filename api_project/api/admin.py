from django.contrib import admin

import newsletter.models as n_models

admin.site.site_header = 'Рассылки'
admin.site.site_title = 'Рассылки'


@admin.register(n_models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'tag',)


@admin.register(n_models.MailingList)
class MailingListAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'time_start',
        'time_end',
        'filter_code',
        'filter_tag',
        )


@admin.register(n_models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('created', 'client', 'distribution',)
