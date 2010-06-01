configpy
==========

configpy allows you to store your config in JSON files. The main features of configpy are:
  * variable look ahead
  * variable look behind
  * expression support

Examples
--------

Simple Configuration

	config_json = """
	{
	    "var_a": "AAAA",
	    "var_b": 10,
	    "var_c": "A longer string",
	    "var_d": 10.04
	}
	"""

	config = Config(config_json)
	"AAAA" == config['var_a']
	10 == config['var_b']
	"A longer string" == config['var_c']
	10.04 == config['var_d']

Variable Support (Look Behind)

	config_json = """
	{
	    "first_name": "Howard",
	    "second_name": "Gayle",
	    "full_name": "${first_name} ${second_name}"
	}
	"""

	config = Config(config_json)
	"Howard Gayle" == config['full_name']

Variable Support (Look Ahead)

	config_json = """
	{
	    "first_name": "Hugo",
	    "full_name": "${first_name} ${second_name}",
	    "second_name": "Sanchez"
	}
	"""

	config = Config(config_json)
	"Hugo Sanchez" == config['full_name']

Expression Support 

	config_json = """
	{
	    "a": 10,
	    "b": 2,
	    "c": "{{ ${a} / ${b} }}",
	    "d": "{{ ${c} * ${a} }}",
	    "e": "{{ ${d} + 50 }}",
	    "f": "{{ ${e} - 25 }}",
	    "g": "'some text = {{ ${a} / ${b} }}'"
	}
	"""

	# note the text at the start of g makes it a text value

	config = Config(config_json)
	10 == config['a']
	2 == config['b']
	5 == config['c']
	50 == config['d']
	100 == config['e']
	75 == config['f']
	"some text = 5" == config['g']

Restricted Expression Support

By default access to globals() is restricted. This prevents potentially 
nasty expressions from being run. For example:

	config_json = """
	{
	    "write_virus": "open('/etc/passwd', 'w').write(\\"# BURNED! \\")"
	}
	"""
    config = Config(config_str)
	...
	NameError: name 'open' is not defined

If you are confident that the configuration file is trustworthy you can
use unrestricted mode:

    config = Config(config_str, unrestricted=True)
