# Output a Python dict with tracker fields definition, using a Savane3
# initialized database as source

import MySQLdb
#import MySQLdb.cursors 

db = MySQLdb.connect(unix_socket='/tmp/savane-mini/mysql/sock',
                     user='root',db='savane')
c=db.cursor()

tfields = ['bug_field_id','field_name','display_type','scope','required','special','custom']

defs = {}
field_names = []
complex_defs = {}

def process_field_row(row):
    name = row[1]
    field_names.append(name)
    defs[name] = ''
    if name == 'field_name':
        defs[name] += "    'name' : {\n"
    else:
        defs[name] += "    '"+name+"' : {\n"
    for i,val in enumerate(row):
        if i <= 0 \
                or (complex_defs[name]['display_type'] not in ('TA', 'TF') and tfields[i] == 'display_size'):
            continue
        else:
            defs[name] += "        " \
                + "'"+tfields[i]+"'" \
                + ": "
            if tfields[i] == 'label' or tfields[i] == 'description':
                defs[name] += '_("' + val + '"),'
            elif (name=='priority' or name=='resolution_id' or name=='planned_starting_date' or name=='planned_close_date') \
                    and tfields[i] == 'required':
                # override priority.required so we have a common
                # definition for all trackers
                defs[name] += str(0)+","
            elif (name=='priority' or name=='resolution_id') \
                    and tfields[i] == 'empty_ok':
                # override priority.empty_ok so we have a common
                # definition for all trackers
                defs[name] += str(1)+","
            elif type(val) == long:
                defs[name] += str(val)+","
            else:
                defs[name] += "'"+val+"',"
            defs[name] += "\n"
    defs[name] += "    },\n"

query = "SELECT " + ",".join(tfields) + " FROM bugs_field"
c.execute(query)
for row in c.fetchall():
    name = row[1]
    complex_defs[name] = {}
    for i,val in enumerate(row):
        complex_defs[name][tfields[i]] = val
complex_defs['priority']['required'] = 0
complex_defs['resolution_id']['required'] = 0
c.execute(query)
for row in c.fetchall():
    process_field_row(row)

query = "SELECT " + ",".join(tfields) +" FROM task_field WHERE field_name IN ('planned_starting_date', 'planned_close_date')"
c.execute(query)
for row in c.fetchall():
    name = row[1]
    complex_defs[name] = {}
    for i,val in enumerate(row):
        complex_defs[name][tfields[i]] = val
complex_defs['planned_starting_date']['required'] = 0
complex_defs['planned_close_date']['required'] = 0
c.execute(query)
for row in c.fetchall():
    process_field_row(row)


for name in field_names:
    print defs[name],


# The following is now stored in the DB

# Doc:
#SHOW_ON_ADD_CHOICES = (('0', _('no')),
#                       ('1', _('show to logged in users')),
#                       ('2', _('show to anonymous users')),
#                       ('3', _('show to both logged in and anonymous users')),)

#tfields = ['name','bug_field_id','group_id','use_it','show_on_add',
#           'show_on_add_members','place','custom_label',
#           'custom_description','custom_display_size',
#           'custom_empty_ok','custom_keep_history',
#           'transition_default_auth']
#tfields[6] = 'rank' 
#
#def process_field_usage_row(row):
#    name = row[0]
#    for i,val in enumerate(row):
#        if i <= 2:
#            continue
#        elif tfields[i] == 'custom_label' \
#                or tfields[i] == 'custom_description' \
#                or tfields[i] == 'custom_display_size' \
#                or tfields[i] == 'custom_empty_ok' \
#                or tfields[i] == 'custom_keep_history' \
#                or (complex_defs[name]['required'] == 1 and tfields[i] == 'use_it') \
#                or (complex_defs[name]['display_type'] != 'SB' and tfields[i] == 'transition_default_auth') \
#                :
#            # overlays, duplicates of bugs_field in this context
#            continue
#        elif tfields[i] == 'show_on_add':
#            if val == 0:
#                defs[name] += "        'show_on_add_anonymous': 0,\n"
#                defs[name] += "        'show_on_add_connected': 0,\n"
#            elif val == 1:
#                defs[name] += "        'show_on_add_anonymous': 0,\n"
#                defs[name] += "        'show_on_add_connected': 1,\n"
#            elif val == 2:
#                defs[name] += "        'show_on_add_anonymous': 1,\n"
#                defs[name] += "        'show_on_add_connected': 0,\n"
#            elif val == 3:
#                defs[name] += "        'show_on_add_anonymous': 1,\n"
#                defs[name] += "        'show_on_add_connected': 1,\n"
#        else:
#            defs[name] += "        " \
#                + "'"+tfields[i]+"'" \
#                + ": "
#            if type(val) == long:
#                defs[name] += str(val)+","
#            elif val is None:
#                defs[name] += "None,"
#            else:
#                defs[name] += "'"+val+"',"
#            defs[name] += "\n"
#    defs[name] += "    },\n"
#
#c.execute("""SELECT bugs_field.field_name,bugs_field_usage.*
#  FROM bugs_field_usage JOIN bugs_field USING (bug_field_id) WHERE group_id=100""")
#for row in c.fetchall():
#    process_field_usage_row(row)
#
#c.execute("""SELECT task_field.field_name,task_field_usage.*
#  FROM task_field_usage JOIN task_field USING (bug_field_id) WHERE group_id=100
#  AND field_name IN ('planned_starting_date', 'planned_close_date')""")
#for row in c.fetchall():
#    process_field_usage_row(row)
