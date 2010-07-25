# Batch-decorator for urlpatterns
# http://www.djangosnippets.org/snippets/532/
# Author: miracle2k (Jan 1, 2008)
# 
# I hate legal-speak as much as anybody, but on a site which is geared
# toward sharing code there has to be at least a little bit of it, so
# here goes:
# 
# By creating an account here you agree to three things:
# 
#   1. That you will only post code which you wrote yourself and that
#   you have the legal right to release under these terms.
# 
#   2. That you grant any third party who sees the code you post a
#   royalty-free, non-exclusive license to copy and distribute that
#   code and to make and distribute derivative works based on that
#   code. You may include license terms in snippets you post, if you
#   wish to use a particular license (such as the BSD license or GNU
#   GPL), but that license must permit royalty-free copying,
#   distribution and modification of the code to which it is applied.
# 
#   3. That if you post code of which you are not the author or for
#   which you do not have the legal right to distribute according to
#   these terms, you will indemnify and hold harmless the operators of
#   this site and any third parties who are exposed to liability as a
#   result of your actions.
#
# If you can't legally agree to these terms, or don't want to, you
# cannot create an account here.

from django.core.urlresolvers import RegexURLPattern
from django.conf.urls.defaults import patterns
class DecoratedURLPattern(RegexURLPattern):
    def resolve(self, *args, **kwargs):
        result = RegexURLPattern.resolve(self, *args, **kwargs)
        if result:
            result = list(result)
            result[0] = self._decorate_with(result[0])
        return result
def decorated_patterns(prefix, func, *args):
    result = patterns(prefix, *args)
    if func:
        for p in result:
            if isinstance(p, RegexURLPattern):
                p.__class__ = DecoratedURLPattern
                p._decorate_with = func
    return result
