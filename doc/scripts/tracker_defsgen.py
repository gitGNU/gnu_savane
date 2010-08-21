# Output a Python dict with tracker fields definition, using a Savane3
# initialized database as source

import MySQLdb
#import MySQLdb.cursors 

db = MySQLdb.connect(unix_socket='/tmp/savane-mini/mysql/sock',
                     user='root',db='savane')
c=db.cursor()

tfields = ['bug_field_id','field_name','display_type','display_size',
           'label','description','scope','required','empty_ok','keep_history',
           'special','custom']

defs = {}
field_names = []
c.execute("""SELECT * FROM bugs_field""")
def process_field_row(row):
    name = row[1]
    field_names.append(name)
    defs[name] = ''
    defs[name] += "    '"+name+"' : {\n"
    for i,val in enumerate(row):
        if i <= 0:
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

for row in c.fetchall():
    process_field_row(row)

c.execute("""SELECT * FROM task_field WHERE field_name IN ('planned_starting_date', 'planned_close_date')""")
for row in c.fetchall():
    process_field_row(row)

tfields = ['name','bug_field_id','group_id','use_it','show_on_add',
           'show_on_add_members','place','custom_label',
           'custom_description','custom_display_size',
           'custom_empty_ok','custom_keep_history',
           'transition_default_auth']
c.execute("""SELECT bugs_field.field_name,bugs_field_usage.*
  FROM bugs_field_usage JOIN bugs_field USING (bug_field_id) WHERE group_id=100""")
def process_field_usage_row(row):
    name = row[0]
    for i,val in enumerate(row):
        if i <= 2:
            continue
        elif tfields[i] == 'custom_label' \
                or tfields[i] == 'custom_description' \
                or tfields[i] == 'custom_display_size' \
                or tfields[i] == 'custom_empty_ok' \
                or tfields[i] == 'custom_keep_history' \
                :
            # overlays, duplicates of bugs_field in this context
            continue
        else:
            defs[name] += "        " \
                + "'"+tfields[i]+"'" \
                + ": "
            if type(val) == long:
                defs[name] += str(val)+","
            elif val is None:
                defs[name] += "None,"
            else:
                defs[name] += "'"+val+"',"
            defs[name] += "\n"
    defs[name] += "    },\n"
for row in c.fetchall():
    process_field_usage_row(row)
c.execute("""SELECT task_field.field_name,task_field_usage.*
  FROM task_field_usage JOIN task_field USING (bug_field_id) WHERE group_id=100
  AND field_name IN ('planned_starting_date', 'planned_close_date')""")
for row in c.fetchall():
    process_field_usage_row(row)

for name in field_names:
    print defs[name],
