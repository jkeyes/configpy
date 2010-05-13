from setuptools import setup

long_description = """
configpy is a JSON configuration file reader with support 
for variable look-ahead and look-behind, expressions, and 
comments.

Example
-------

::

    config_str = \"\"\"
        /* Some example configuration items */
        {
            "a": 10,
            "b": 2,
            "c": "exp(${a} / ${b})",
            "d": "exp(${c} * ${a})",
            "e": "exp(${d} + 50)",
            "f": "exp(${e} - 25)"
        }
    \"\"\"
    
    config = Config(config_str)
    assert 10 == config.a
    assert 2 == config.b
    assert 5 == config.c
    assert 50 == config.d
    assert 100 == config.e
    assert 75 == config.f

"""

setup(
    name='configpy',
    description='JSON configuration file parser',
    url='http://jkeyes.github.com/configpy/',
    long_description=long_description,
    author='John Keyes',
    author_email='configpy@keyes.ie',
    version='0.3',
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
