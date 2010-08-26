import os

template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'views'))
static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

db_connect_url = 'sqlite://'
db_connect_args = {}

# We're using multipart in strict mode (to fetch instead of ignoring them silently).
# Disk and memory limits are set to low values (in kB here) as we want to check the
# behaviour under restriced resources. Note that memfile_limit should be well below
# mem_limit, as otherwise the available memory might be exhausted by in files stored
# in memory.
multipart_strict = True
multipart_memfile_limit = 1
multipart_mem_limit = 10
multipart_disk_limit = 100

try:
    from secrets import *
except ImportError:
    print('no secrets found, fall back to an in-memory sqlite database')
