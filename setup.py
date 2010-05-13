from setuptools import setup

long_description = """
A config file parser with variable replacement, variable look-ahead 
and look-behind support.
"""

setup(
    name='configpy',
    description='Python Configuration File Parser',
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
