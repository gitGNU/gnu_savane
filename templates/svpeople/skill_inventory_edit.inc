{% load i18n %}

{{ formset.management_form }}
<table class="box">
  <tr>
    <th>{% trans "Skill" %}</th>
    <th>{% trans "Level" %}</th>
    <th>{% trans "Experience" %}</th>
    <th>{% trans "Delete" %}</th>
  </tr>
  {% for form in formset.forms %}
  <tr class="{% cycle 'boxitemalt' 'boxitem' %}">
    {% for field in form %}
    {% if field.is_hidden %}
    {{ field }}
    {% else %}
    <td>{{ field }}</td>
    {% endif %}
    {% endfor %}
  {% endfor %}
</table>
