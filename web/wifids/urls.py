from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'wifids.views.home', name='home'),
    url(r'^add-mac$', 'wifids.views.add_mac', name='add-address'),
    url(r'^delete-mac$', 'wifids.views.delete_mac', name='delete-address'),
    url(r'^view-log$', 'wifids.views.view_log', name='view-log'),
    url(r'^view-images$', 'wifids.views.view_images', name='view-images'),
)
