"""
urls

Created by: Martin Sicho
On: 02-12-19, 17:18
"""

from django.urls import path, include
from rest_framework import routers

import commons.views
from qsar.models import QSARModel
from . import views

router = routers.DefaultRouter()
router.register(r'models', views.QSARModelViewSet, basename='model')
router.register(r'models/<int:pk>/performance', views.ModelPerformanceViewSet, basename='performance')
router.register(r'algorithms', views.AlgorithmViewSet, basename='algorithm')
router.register(r'metrics', views.MetricsViewSet, basename='metric')


routes = [
    path('models/<int:pk>/tasks/all/', commons.views.ModelTasksView.as_view(model_class=QSARModel))
    , path('models/<int:pk>/tasks/started/', commons.views.ModelTasksView.as_view(started_only=True, model_class=QSARModel))
]

urlpatterns = [
    path('', include(routes)),
    path('', include(router.urls)),
]
