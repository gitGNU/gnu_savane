from django.conf.urls.defaults import *
from savane_user import views


urlpatterns = patterns ('',
                        url('^$',
                            views.index,
                            name='test'
                            ),
                        )
