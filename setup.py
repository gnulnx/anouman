import os
import sys

from distutils.core import setup
from distutils.sysconfig import get_python_lib

from setuptools import find_packages

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Dnginx are
# still present in site-packages. 
overlay_warning = False
if "install" in sys.argv:
    # We have to try also with an explicit prefix of /usr/local in order to
    # catch Debian's custom user site-packages directory.
    for lib_path in get_python_lib(), get_python_lib(prefix="/usr/local"):
        existing_path = os.path.abspath(os.path.join(lib_path, "anouman"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join)
    in a platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


EXCLUDE_FROM_PACKAGES  = []

def is_package(package_name):
    for pkg in EXCLUDE_FROM_PACKAGES:
        if package_name.startswith(pkg):
            return False
    return True


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, package_data = [], {}

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
anouman_dir = 'anouman'

for dirpath, dirnames, filenames in os.walk(anouman_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames and is_package(package_name):
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])


version = "0.0.1"

print find_packages()

setup(
    name='anouman',
    version=version,
    author='John Furr',
    description=('rapidly create and deploy django --> gunicorn --> nginx project'),
    license='BSD',
    #packages=packages,
    include_package_data = True,
    packages=find_packages(),
    package_data=package_data,
    scripts=['anouman/bin/anouman-admin.py'],
    classifiers=[
        'Environment :: Web Environment',
    ],
    install_requires=[
        "Django >= 1.2",
    ],
)

if overlay_warning:
    sys.stderr.write("""

========
Danger Will Robinson!
========

You have just installed Dnginx over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
Dnginx. This is known to cause a variety of problems. You
should manually remove the

%(existing_path)s

directory and re-install Dnginx.

""" % {"existing_path": existing_path})


"""
setup(
-    name='anouman',
-    version='0.1',
+    name='Dnginx',
+    version=version,
     author='John Furr',
-    author_email='john.furr@gmail.com',
-    license='Creative Commons Attribution-Noncommercial-Share Alike license',
-    long_description=open('README.txt').read(),
-    py_modules=['bin/anouman',],
-    scripts=['bin/anouman.py',],
-    packages=find_packages(),
-    install_requires=[
-        "Django >= 1.5.2",
+    description=('rapidly create and deploy django --> gunicorn --> nginx project'),
+    license='BSD',
+    packages=packages,
+    package_data=package_data,
+    scripts=['anouman/bin/anouman.py'],
+    classifiers=[
+        'Development Status :: Beta',
+        'Environment :: Web Environment',
     ],
 )
"""
