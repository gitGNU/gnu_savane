# http://www.djangosnippets.org/snippets/766/
# http://www.djangosnippets.org/snippets/1033/
# Author: simon (May 21, 2008)
# Author: crucialfelix (September 7, 2008)
# Copyright (C) 2009  Sylvain Beucler
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

import time
from django.dispatch import dispatcher
from django.core.signals import request_started
from django.test.signals import template_rendered
from django.conf import settings
from django.db import connection
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

TEMPLATE = """
<div id="debug" style="clear:both;">
<a href="#debugbox"
    onclick="this.style.display = 'none';
        document.getElementById('debugbox').style.display = 'block';
        return false;"
    style="font-size: small; color: red; text-decoration: none; display: block; margin: 12px;"
>+</a>

<div style="display: none;clear: both; border: 1px solid red; padding: 12px; margin: 12px; overflow: scroll" id="debugbox">

<p>Server-time taken: {{ server_time|floatformat:"5" }} seconds</p>
<p>View: <strong>{{view}}</strong></p>
<p>Templates used:</p>
{% if templates %}
<ol>
    {% for template in templates %}
        <li><strong>{{ template.0 }}</strong> loaded from <samp>{{ template.1 }}</samp></li>
    {% endfor %}
</ol>
{% else %}
    None
{% endif %}
<p>Template path:</p>
{% if template_dirs %}
    <ol>
    {% for template in template_dirs %}
        <li>{{ template }}</li>
    {% endfor %}
    </ol>
{% else %}
    None
{% endif %}
<p>SQL executed:</p>
{% if sql %}
<ol>
{% for query in sql %}
    <li><pre>{{ query.sql|linebreaksbr }}</pre><p>took {{ query.time|floatformat:"3" }} seconds</p></li>
{% endfor %}
</ol>
<p>Total SQL time: {{ sql_total }}</p>
{% else %}
    None
{% endif %}
</div>
</div>
</body>
"""

# Monkeypatch instrumented test renderer from django.test.utils - we could use
# django.test.utils.setup_test_environment for this but that would also set up
# e-mail interception, which we don't want
from django.test.utils import instrumented_test_render
from django.template import Template, Context
if Template.render != instrumented_test_render:
    Template.original_render = Template.render
    Template.render = instrumented_test_render
# MONSTER monkey-patch
old_template_init = Template.__init__
def new_template_init(self, template_string, origin=None, name='<Unknown Template>'):
    old_template_init(self, template_string, origin, name)
    self.origin = origin
Template.__init__ = new_template_init

class DebugFooter:
    def process_request(self, request):
        self.time_started = time.time()
        self.templates_used = []
        self.contexts_used = []
        self.sql_offset_start = len(connection.queries)
        template_rendered.connect(self._storeRenderedTemplates)

    def process_response(self, request, response):
        # Only include debug info for text/html pages not accessed via Ajax
        if 'text/html' not in response['Content-Type']:
            return response
        if request.is_ajax():
            return response
        if not settings.DEBUG:
            return response
        if response.status_code != 200:
            return response

        templates = [
            (t.name, t.origin and t.origin.name or 'No origin')
            for t in self.templates_used
        ]

        sql_queries = connection.queries[self.sql_offset_start:]
        # Reformat sql queries a bit
        sql_total = 0.0
        for query in sql_queries:
            query['sql'] = reformat_sql(query['sql'])
            sql_total += float(query['time'])

        from django.core.urlresolvers import resolve
        view_func, args, kwargs = resolve(request.META['PATH_INFO'])

        if hasattr(view_func,'view_func'):
            # it the view_func has a view_func then its a decorator
            co = view_func.view_func.func_code
        else:
            co = view_func.func_code
            
        view =  '%s.%s' % (view_func.__module__, view_func.__name__)
        debug_content = Template(TEMPLATE).render(Context({
            'server_time': time.time() - self.time_started,
            'templates': templates,
            'sql': sql_queries,
            'sql_total': sql_total,
            'template_dirs': settings.TEMPLATE_DIRS,
            'view': view
        }))

        content = response.content
        response.content = force_unicode(content).replace('</body>', debug_content)

        return response

    def _storeRenderedTemplates(self, **kwargs):
        #signal=signal, sender=sender, template=template, context=context):
        template = kwargs.get('template')
        if(template):
            self.templates_used.append(template)
        context = kwargs.get('context')
        if(context):
            self.contexts_used.append(context)

def reformat_sql(sql):
    sql = sql.replace('`,`', '`, `')
    sql = sql.replace('` FROM `', '` \n  FROM `')
    sql = sql.replace('` WHERE ', '` \n  WHERE ')
    sql = sql.replace(' ORDER BY ', ' \n  ORDER BY ')
    return sql
