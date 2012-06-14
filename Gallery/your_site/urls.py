from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'your_site.views.home', name='home'),
    # url(r'^your_site/', include('your_site.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

                       url(r'^$', 'Gallery.views.albumIndex'),
                       url(r'^log_in/$', 'django.contrib.auth.views.login'),
                       url(r'^log_out/$', 'Gallery.views.logOut'),
                       url(r'^update/$', 'Gallery.views.updateDB'),
                       url(r'^accounts/profile/$', 'Gallery.views.redirectHome'),
                       url(r'^(?P<albumName>[\'.\w\ -]+)/(?P<fileName>[\'.\w\ -]+)/addComment$', 'Gallery.views.updateComment'),
                       url(r'^(?P<albumName>[\'.\w\ -]+)/(?P<fileName>[\'.\w\ -]+)/rotate/(?P<angle>\d+)$', 'Gallery.views.rotate'),
                       url(r'^(?P<albumName>[\'.\w\ -]+)/(?P<fileName>[\'.\w\ -]+)$', 'Gallery.views.showPicture'),
                       url(r'^(?P<albumName>[\'.\w\ -]+)/$', 'Gallery.views.pictureIndex'),

)
