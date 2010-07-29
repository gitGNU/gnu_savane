from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',)

urlpatterns += patterns('',
  # Home/presentation pages
  (r'', include('savane.svmain.urls', namespace='svmain')),
  # User account
  (r'^my/', include('savane.my.urls', namespace='my')),
)
