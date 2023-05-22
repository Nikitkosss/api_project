from api.views import (ClientViewSet, MailingListViewSet, MessageViewSet,
                       StatMailingListAPIView, TotalStatAPIView)
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework import routers

v1_router = routers.DefaultRouter()
v1_router.register('clients', ClientViewSet)
v1_router.register('mailing_list', MailingListViewSet)
v1_router.register('message', MessageViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    path(
       'stats/',
       TotalStatAPIView.as_view(),
       name='stats-total'),
    path('stats/<int:id>',
         StatMailingListAPIView.as_view(),
         name='stats-dist'),
    path('schema/',
         SpectacularAPIView.as_view(),
         name='schema'),
    path('schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('schema/redoc/',
         SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
]
