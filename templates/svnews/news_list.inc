{% load i18n %}
{% load svmarkup %}

{% for object in object_list %}
<div class="{% cycle 'boxitem' 'boxitemalt' as rowcolor %}">
  <a href="{% url savane:svnews:news_detail object.pk %}"><strong>{{object.summary}}</strong></a><br />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <span class="smaller"><em>
    {% trans "posted by" %}
    {% include 'svnews/user_submitted_by_link.inc' %}
    {{object.date}} -
    {% blocktrans count object.comment_set.count as count %}{{count}} comment{% plural %}{{count}} comments{% endblocktrans %}
  </em></span>
  <br />
  {{object.get_details_short|safe}}
</div>
{% endfor %}
