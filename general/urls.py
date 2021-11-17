from django.conf.urls import url, include
from rest_framework import routers
from .views import AlarmViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'send', AlarmViewSet, basename='alarm')

urlpatterns = [
    url(r'^', include(router.urls)),
]

