from django.conf.urls.defaults import *
from savane_user import views


urlpatterns = patterns ('',
                        url('^$',
                            views.index,
                            ),
                        url('^login$',
                            views.sv_login,
                            ),
                        )
