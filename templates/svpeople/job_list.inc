{% load i18n %}
<table class="box">
<tr>
  <th>{% trans "Title" %}</th>
  <th>{% trans "Category" %}</th>
  <th>{% trans "Date opened" %}</th>
  <th>{% trans "Project" %}</th>
  <th>{% trans "Type" %}</th>
</tr>
{% for object in object_list %}
<tr class="{% cycle 'boxitemalt' 'boxitem' %}">
  <td>{{object.title}}</td>
  <td>{{object.category.label}}</td>
  <td>{{object.date}}</td>
  <td>{{object.group.svgroupinfo.full_name}}</td>
  <td>{{object.group.svgroupinfo.type.name}}</td>
</tr>
{% endfor %}
</table>
