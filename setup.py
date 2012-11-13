import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'pyramid_simpleform',
    'pyramid_jinja2',
    'pyramid_fanstatic',
    'js.jquery',
    'js.jqueryui',
    'js.bootstrap',
    'boto',
    ]

setup(name='AWSConsole',
      version='0.0',
      description='AWSConsole',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Nozomu Kaneko',
      author_email='nozom.kaneko@gmail.com',
      url='https://github.com/knzm/awsconsole',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='awsconsole',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = awsconsole:main
      [console_scripts]
      initialize_AWSConsole_db = awsconsole.scripts.initializedb:main
      """,
      )

