from django.conf.urls.defaults import *
from savane_user import views


urlpatterns = patterns ('',
                        url('^$',
                            views.index,
                            ),
                        url('^login$',
                            views.sv_login,
                            ),
                        url('^logout$',
                            views.sv_logout,
                            ),
                        url('^conf/$',
                            views.sv_conf,
                            ),
                        url('^conf/identity$',
                            views.sv_identity,
                            ),
                        url('^conf/authentication$',
                            views.sv_authentication,
                            ),
                        url('^conf/mail$',
                            views.sv_mail,
                            ),
                        )
