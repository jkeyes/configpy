from setuptools import setup

long_description = """
configpy is a JSON configuration file reader with support 
for variable look-ahead and look-behind, expressions, and 
comments.

Example
-------

::

    config_json = \"\"\"
    /* Some example configuration items */
    {
        "a": 10,
        "b": 2,
        "c": "{{ ${a} / ${b} }}",
        "d": "{{ ${c} * ${a} }}",
        "e": "{{ ${d} + 50 }}",
        "f": "{{ ${e} - 25 }}",
        "g": "'some text = {{ ${a} / ${b} }}'"
    }
    \"\"\"

    config = Config(config_json)
    10 == config.a
    2 == config.b
    5 == config.c
    50 == config.d
    100 == config.e
    75 == config.f
    "some text = 5" == config.g
"""

setup(
    name='configpy',
    description='JSON configuration file parser',
    url='http://jkeyes.github.com/configpy/',
    long_description=long_description,
    author='John Keyes',
    author_email='john@keyes.ie',
    version='0.5',
    license="BSD",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=['configpy'],
)
