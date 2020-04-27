"""genui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.account.views import ConfirmEmailView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

# from . import views
from genui.commons.views import TaskProgressView

schema_view = get_schema_view(
   openapi.Info(
      title="GenUI API",
      default_version='v0',
      description="API to interact with the GenUI backend server.",
      # terms_of_service="https://www.google.com/policies/terms/",
      # contact=openapi.Contact(email="contact@something.local"),
      # license=openapi.License(name="BSD License"), # FIXME: needs to be changed
   ),
   public=False,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('allauth.urls')),
    path(f'api/{settings.REST_FRAMEWORK["URLS_ROOT"]}', include('rest_framework.urls')),
    path('api/accounts/', include('rest_auth.urls')),
    re_path(r'^api/accounts/registration/account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(),
    name='account_confirm_email'),
    path('api/accounts/registration/', include('rest_auth.registration.urls')),
    re_path(r'^api/celery-progress/(?P<task_id>[\w-]+)/$', TaskProgressView.as_view()),
    path('api/projects/', include('genui.projects.urls')),
    path('api/compounds/', include('genui.compounds.urls')),
    path('api/qsar/', include('genui.qsar.urls')),
    path('api/generators/', include('genui.generators.urls')),
    path('api/maps/', include('genui.maps.urls')),
    re_path(r'^api/schema/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^api/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^api/(swagger/)?$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += [
#     # if it is not a direct request to backend, serve the frontend app
#     path('', views.FrontendAppView.as_view()),
#     re_path(r'^(?:.*)/?$', views.FrontendAppView.as_view())
# ]