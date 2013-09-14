import os

template_dir = os.path.dirname(__file__)
def gunicorn_start(context):
    with open('%s/gunicorn_start.template'%(template_dir), 'r') as f:
        return f.read() % context
