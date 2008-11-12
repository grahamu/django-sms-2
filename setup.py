# setup.py borrowed from django-tagging

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Dynamically calculate the version based on tagging.VERSION.
version_tuple = __import__('sms').VERSION
if version_tuple[2] is not None:
    version = "%d.%d_%s" % version_tuple
else:
    version = "%d.%d" % version_tuple[:2]

setup(
    name = 'sms',
    version = version,
    description = 'SMS Helper for Django',
    author = 'Matt Dennewitz',
    author_email = 'mattdennewitz@gmail.com',
    url = 'http://code.google.com/p/django-sms/',
    packages = ['sms'],
    package_data = {},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ]
)

