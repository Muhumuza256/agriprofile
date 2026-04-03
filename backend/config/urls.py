from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.groups.urls')),
    path('api/', include('apps.farmers.urls')),
    path('api/', include('apps.plots.urls')),
    path('api/', include('apps.scoring.urls')),
    path('api/', include('apps.loans.urls')),
    path('api/', include('apps.parameters.urls')),
    path('api/', include('apps.weather.urls')),
    path('api/', include('apps.calendar.urls')),
    path('api/', include('apps.impact.urls')),
    path('api/', include('apps.analytics.urls')),
    path('api/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
