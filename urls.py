from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()


import settings

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^$|^upload$', 'image.views.upload'),
    (r'^login/?$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^logout/?$', 'django.contrib.auth.views.logout'),
    
    # list images, list images by user
    (r'^list/?$|^list/(?P<page>\d+)$', 'image.views.list_images'),
    (r'^list/user/?$|^list/user/(?P<user>.+)$', 'image.views.user_images'),
    (r'^i/(?P<id>[A-Za-z0-9]+)$', 'image.views.view_image'),

    # Static pages
    (r'^about/?$', 'django.views.generic.simple.direct_to_template', { 'template':'static_about.html', }),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
    (r'^(?P<path>thumbs/.*\.(?:jpg|png|gif))$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT,}),
    (r'^(?P<path>.*\.(?:jpg|png|gif))$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT,}),
  )
