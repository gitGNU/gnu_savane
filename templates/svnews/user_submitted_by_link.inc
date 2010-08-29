{% load i18n %}

{% if object.submitted_by_id %}
  {% if object.submitted_by %}
  <a href="{% url savane:svmain:user_detail object.submitted_by.username %}"
  >{{object.submitted_by.get_full_name}}
&lt;{{object.submitted_by.username}}&gt;</a>,
  {% else %}
    <strong>{% trans "Invalid user ID" %}</strong>,
  {% endif %}
{% else %}
{% trans "Anonymous" %},
{% endif %}
