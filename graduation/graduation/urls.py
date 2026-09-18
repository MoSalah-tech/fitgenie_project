from django.conf import settings
from django.contrib import admin
from django.urls import path, include,re_path
from django.conf.urls.static import static
from .settings.development import de

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user.urls')),  
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [re_path(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}),]
    urlpatterns += [re_path(r'^media/(?P<path>.*)$', static.serve,{'document_root': settings.MEDIA_ROOT}),]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('admin/', admin.site.urls),
        path('', include('user.urls')),  
        # ... your other URL patterns
    ]