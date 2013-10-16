#!/bin/bash

# Export your projects settings module
export DJANGO_SETTINGS_MODULE={{DJANGO_SETTINGS_MODULE}}

# Make sure your project is at the beginning of PYTHONPATH
export PYTHONPATH={{DJANGODIR}}:$PYTHONPATH

{# If using a unix socket then create the run directory #}
{% if SOCKFILE %}
# Make sure the directory for teh sockfile is created
RUNDIR=$(dirname {{SOCKFILE}})
test -d $RUNDIR || mkdir -p $RUNDIR
{% endif %}

# Start gunicorn
exec {{GUNICORN}} {{DJANGO_WSGI_MODULE}}:application \
  --bind={{BIND}} \
  --name {{NAME}} \
  --workers {{NUM_WORKERS}} \
  --user={{USER}} \
  --log-level=debug  \
  --error-logfile {{ERROR_LOG}} \
  --access-logfile {{ACCESS_LOG}} \
  {% if DAEMON %} --daemon \{% endif %}

echo "gunicorn start for site: {{NAME}}"
