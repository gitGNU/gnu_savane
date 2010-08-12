{% load i18n %}

<table class="box">
<tr>
  <th>{% trans "Skill" %}</th>
  <th>{% trans "Level" %}</th>
  <th>{% trans "Experience" %}</th>
</tr>
{% for object in object_list %}
<tr class="{% cycle 'boxitemalt' 'boxitem' %}">
  <td>{{object.skill.label}}</td>
  <td>{{object.skill_level.label}}</td>
  <td>{{object.skill_year.label}}</td>
</tr>
{% empty %}
<tr><td><p class="warn">({% trans "No skill inventory set up" %})</p></td></tr>
{% endfor %}
</table>
