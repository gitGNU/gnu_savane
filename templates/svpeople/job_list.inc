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
  <td><a href="{% url savane:svpeople:job_detail object.pk %}">{{object.title}}</a></td>
  <td>{{object.category.label}}</td>
  <td>{{object.date}}</td>
  <td><a href="{% url savane:svmain:group_detail object.group.pk %}">{{object.group.svgroupinfo.full_name}}</a></td>
  <td>{{object.group.svgroupinfo.type.name}}</td>
</tr>
{% endfor %}
</table>
