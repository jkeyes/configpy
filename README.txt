configpy
==========

configpy allows you to store your config in JSON files. The main features of configpy are:
  * variable look ahead
  * variable look behind
  * expression support

Examples
--------

Simple Configuration

	config_str = """
	{
	    "var_a": "AAAA",
	    "var_b": 10,
	    "var_c": "A longer string",
	    "var_d": 10.04
	}
	"""

	config = Config(config_str)
	assert "AAAA" == config.var_a
	assert type(config.var_a) == types.UnicodeType
	assert 10 == config.var_b
	assert type(config.var_b) == types.IntType
	assert 10 == config.var_b
	assert "A longer string" == config.var_c
	assert 10.04 == config.var_d
	assert type(config.var_d) == types.FloatType

Variable Support (Look Behind)

	config_str = """
	{
	    "first_name": "Howard",
	    "second_name": "Gayle",
	    "full_name": "${first_name} ${second_name}"
	}
	"""

	config = Config(config_str)
	assert "Howard Gayle" == config.full_name

Variable Support (Look Ahead)

    config_str = """
    {
        "first_name": "Hugo",
        "full_name": "${first_name} ${second_name}",
        "second_name": "Sanchez"
    }
    """

    config = Config(config_str)
    assert "Hugo Sanchez" == config.full_name


Expression Support 

    config_str = """
    {
        "a": 10,
        "b": 2,
        "c": "exp(${a} / ${b})",
        "d": "exp(${c} * ${a})",
        "e": "exp(${d} + 50)",
        "f": "exp(${e} - 25)"
    }
    """
    config = Config(config_str)
    assert 10 == config.a
    assert 2 == config.b
    assert 5 == config.c
    assert 50 == config.d
    assert 100 == config.e
    assert 75 == config.f

Unrestricted Expression Support

By default access to globals() is restricted. This prevents potentially 
nasty expressions from being run. For example:

	config_str = """
	{
	    "write_virus": "exp(open('/etc/passwd', 'w').write(\\"# BURNED! \\"))"
	}
	"""
    config = Config(config_str)
	...
	NameError: name 'open' is not defined

If you are confident that the configuration file is trustworthy you can
use unrestricted mode:

    config = Config(config_str, unrestricted=True)
