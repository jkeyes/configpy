import types

from configpy import Config, FileConfig

def test_no_variables():
    config = Config("{}")

def test_simple_variable():
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

def test_look_behind_replace():
    config_str = """
    {
        "first_name": "Howard",
        "second_name": "Gayle",
        "full_name": "${first_name} ${second_name}"
    }
    """

    config = Config(config_str)
    assert "Howard Gayle" == config.full_name

def test_look_ahead_replace():
    config_str = """
    {
        "first_name": "Hugo",
        "full_name": "${first_name} ${second_name}",
        "second_name": "Sanchez"
    }
    """

    config = Config(config_str)
    assert "Hugo Sanchez" == config.full_name

def test_list_variable():
    config_str = """
    {
        "nums": [1,2,3,4],
        "nando": "Nando",
        "names": ["Stevie", "${nando}", "Robbie"]
    }
    """

    config = Config(config_str)
    assert type(config.nums) == types.ListType
    assert [1,2,3,4] == config.nums
    assert type(config.names) == types.ListType
    assert ['Stevie', 'Nando', 'Robbie']  == config.names

def test_dict_variable():
    config_str = """
    {
        "d": { "planet": "${e}" },
        "e": "mars"
    }
    """

    config = Config(config_str)
    assert type(config.d) == types.DictType
    assert { "planet": "mars" } == config.d

def test_dict_in_list_variable():
    config_str = """
    {
        "f": { "title": "The 39 Steps" },
        "g": { "title": "Catch-22" },
        "h": "exp([ ${f}, ${g} ])"
    }
    """

    config = Config(config_str)
    assert type(config.h) == types.ListType
    assert config.h == [ { u'title': u'The 39 Steps' }, { u'title': u'Catch-22'} ]
    assert type(config.h[0]) == types.DictType

def test_eval_safety():
    config_str = """
    {
        "filename": "exp(len('/tmp/ssc.txt'))"
    }
    """
    try:
        config = Config(config_str)
    except NameError:
        """Expected error"""
    config = Config(config_str, unrestricted=True)


def test_eval_maths():
    config_str = """ 
    {
        "a": 10,
        "b": 20,
        "c": "exp(${a} + ${b})"
    }
    """
    config = Config(config_str)
    assert 10 == config.a
    assert type(config.a) == types.IntType
    assert 20 == config.b
    assert 30 == config.c

def test_python_keywords():
    config_str = """
    {
        "class": "MyClassName"
    }
    """

    config = Config(config_str)
    assert "MyClassName" == config['class']

def test_invalid_type_expression():
    config_str = """
    {
        "number": 10,
        "string": "My String",
        "invalid": "exp(${number} / ${string})"
    }
    """

    config = Config(config_str)

def test_missing_reference():
    config_str = """
    {
        "ping": "${pong}"
    }
    """
    try:
        config = Config(config_str)
    except KeyError:
        """Expected error"""

def test_self_reference():
    config_str = """
    {
        "fubar": "${fubar}"
    }
    """

    try:
        config = Config(config_str)
    except KeyError:
        """Expected error"""

def test_cyclic_reference():
    config_str = """
    {
        "a": "${b}",
        "b": "${a}"
    }
    """
    try:
        config = Config(config_str)
    except KeyError:
        """Expected error"""

def test_complex_cyclic_reference():
    config_str = """
    {
        "a": "${c}",
        "b": "${a}",
        "c": "${b}"
    }
    """
    try:
        config = Config(config_str)
    except KeyError:
        """Expected error"""

def test_complex_references():
    config_str = """
    {
        "a": "simple",
        "b": "${a} ${c}",
        "c": "${d}",
        "d": "${a} ${e}",
        "e": "as pie"
    }
    """

    config = Config(config_str)

    assert "simple" == config.a
    assert "simple simple as pie" == config.b
    assert "simple as pie" == config.c
    assert "simple as pie" == config.d
    assert "as pie" == config.e

def test_math():
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

def test_file():
    import os
    dirname = os.path.dirname(__file__)
    config = FileConfig(os.path.join(dirname,'test.cfg'))

    assert "admin" == config.db_username
    assert "password" == config.db_password


if __name__ == "__main__":
    import sys
    import traceback

    tests = [a for a in dir() if a[0:4] == 'test']
    attrs = locals()
    for test in tests:
        print test.ljust(30, '.'),
        try:
            attrs[test]()
            print "OK"
        except AssertionError, e:
            print "ERROR"
            traceback.print_exc(file=sys.stdout)
            print
        except Exception, exp:
            print "FAIL"
            traceback.print_exc(file=sys.stdout)
            print
