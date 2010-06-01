"""
Tests for configpy
"""
import os, unittest

from configpy import Config, FileConfig

THIS_DIR = os.path.dirname(__file__)
CFG_PATH = os.path.abspath(os.path.join(THIS_DIR,'test.cfg'))

class ConfigTest(unittest.TestCase):
    """
    TestCase.
    """
        
    def test_base(self):
        """
        Test simple key/value.
        """
        config_json = """
            { "a": "b" }
        """
        config = Config(config_json)
        self.assertEquals(["b"], config.values())
        self.assertEquals(["a"], config.keys())

    def test_simple(self):
        """
        Test string, int and float values.
        """

        config_json = """
        {
            "var_a": "AAAA",
            "var_b": 10,
            "var_c": "A longer string",
            "var_d": 10.04
        }
        """

        config = Config(config_json)
        self.assertEquals("AAAA", config['var_a'])
        self.assertEquals(10, config['var_b'])
        self.assertEquals("A longer string", config['var_c'])
        self.assertEquals(10.04, config['var_d'])

    def test_list(self):
        """
        Test list values.
        """

        config_json = """
        {
            "var_a": ["AAAA", "BBBB"],
            "var_b": ["1", [2, 3]]
        }
        """

        config = Config(config_json)
        self.assertEquals(["AAAA", "BBBB"], config['var_a'])
        self.assertEquals([2, 3], config["var_b"][1])

    def test_dict(self):
        """
        Test dict values.
        """

        config_json = """
        {
            "var_a": {"AAAA": "BBBB"},
            "var_b": ["1", {"2": 3}]
        }
        """

        config = Config(config_json)
        self.assertEquals({"AAAA": "BBBB"}, config['var_a'])
        self.assertEquals({"2": 3}, config["var_b"][1])

    def test_look_behind(self):
        """
        Test look behind variable replacement.
        """

        config_json = """
        {
            "first_name": "Howard",
            "second_name": "Gayle",
            "full_name": "${first_name} ${second_name}"
        }
        """

        config = Config(config_json)
        self.assertEquals("Howard Gayle", config['full_name'])

    def test_look_ahead(self):
        """
        Test look ahead variable replacement.
        """
        
        config_json = """
        {
            "first_name": "Hugo",
            "full_name": "${first_name} ${second_name}",
            "second_name": "Sanchez"
        }
        """

        config = Config(config_json)
        self.assertEquals("Hugo Sanchez", config['full_name'])
        
    def test_list_variable(self):
        """
        Test variable replacement in a list (array) value.
        """

        config_json = """
        {
            "nums": [1,2,3,4],
            "nando": "Nando",
            "names": ["Stevie", "${nando}", "Robbie"]
        }
        """

        config = Config(config_json)
        self.assertEquals([1, 2, 3, 4], config['nums'])
        self.assertEquals(['Stevie', 'Nando', 'Robbie'], config['names'])

    def test_dict_variable(self):
        """
        Test variable replacement in a dict (object) value.
        """

        config_json = """
        {
            "d": { "planet": "${e}" },
            "e": "mars"
        }
        """

        config = Config(config_json)
        self.assertEquals({ "planet": "mars" }, config['d'])

    def test_dict_in_list_variable(self):
        """
        Test replacing a dict variable inside a list value.
        """
        
        config_json = """
        {
            "f": { "title": "The 39 Steps" },
            "g": { "title": "Catch-22" },
            "h": "{{ [ ${f}, ${g} ] }}"
        }
        """

        config = Config(config_json)
        self.assertEquals([ { u'title': u'The 39 Steps' }, { u'title': u'Catch-22'} ], config['h'])

    def test_nested_evals(self):
        """
        Test nested evaluations.
        """
        
        config_json = """ 
        {
            "a": 10,
            "b": 20,
            "c": "{{ {{ ${a} * 5 }} + ${b} }}"
        }
        """
        config = Config(config_json)
        self.assertEquals(10, config['a'])
        self.assertEquals(20, config['b'])
        self.assertEquals(70, config['c'])
 
    def test_python_keywords(self):
        config_json = """
        {
            "class": "MyClassName"
        }
        """

        config = Config(config_json)
        self.assertEquals("MyClassName", config['class'])

    def test_invalid_type_expression(self):
        config_json = """
        {
            "number": 10,
            "string": "My String",
            "invalid": "{{ ${number} / ${string} }}"
        }
        """
        try:
            config = Config(config_json)
            self.fail("SyntaxError not raised.")
        except SyntaxError:
            """Expected error"""

    def test_missing_reference(self):
        config_json = """
        {
            "ping": "${pong}"
        }
        """
        try:
            config = Config(config_json)
            self.fail("KeyError not raised")
        except KeyError:
            """Expected error"""

    def test_self_reference(self):
        config_json = """
        {
            "fubar": "${fubar}"
        }
        """

        try:
            config = Config(config_json)
            self.fail("KeyError not raised")
        except KeyError:
            """Expected error"""

    def test_cyclic_reference(self):
        config_json = """
        {
            "a": "${b}",
            "b": "${a}"
        }
        """
        try:
            config = Config(config_json)
            self.fail("KeyError not raised")
        except KeyError:
            """Expected error"""

    def test_complex_cyclic_reference(self):
        config_json = """
        {
            "a": "${c}",
            "b": {
                "d": {
                    "e": "${a}"
                }
            },
            "c": "${b}"
        }
        """
        try:
            config = Config(config_json)
            self.fail("KeyError not raised")
        except KeyError:
            """Expected error"""

    def test_complex_references(self):
        config_json = """
        {
            "a": "simple",
            "b": "${a} ${c}",
            "c": "${d}",
            "d": "${a} ${e}",
            "e": "as pie"
        }
        """

        config = Config(config_json)

        self.assertEquals("simple", config['a'])
        self.assertEquals("simple simple as pie", config['b'])
        self.assertEquals("simple as pie", config['c'])
        self.assertEquals("simple as pie", config['d'])
        self.assertEquals("as pie", config['e'])

    def test_math(self):
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
        
        config = Config(config_json)
        self.assertEquals(10, config['a'])
        self.assertEquals(2, config['b'])
        self.assertEquals(5, config['c'])
        self.assertEquals(50, config['d'])
        self.assertEquals(100, config['e'])
        self.assertEquals(75, config['f'])
        self.assertEquals("some text = 5", config['g'])

    def test_comments(self):
        config_json = """
        /* We can use single line */
        /* and multi-line
           Javascript like comments */
        {
            "var_a": "AAAA", // or simple single line comments too
            /* we can mix comments everywhere */
            "var_b": "You must escape \/* slashes in name or value strings *\/",
            "var_c": "A longer string \/\/ like this one"
        }
        """

        config = Config(config_json)
        self.assertEquals("AAAA", config['var_a'])
        self.assertEquals("You must escape /* slashes in name or value strings */", config['var_b'])
        self.assertEquals("A longer string // like this one", config['var_c'])

    def test_file(self):
        config = FileConfig(CFG_PATH)

        self.assertEquals("admin", config['db_username'])
        self.assertEquals("password", config['db_password'])
        self.assertEquals("http://localhost", config['host'])

    def test_invalid_open(self):
        config_json = """
        {
            "myfile": "{{ open().read() }}"
        }
        """
        try:
            config = Config(config_json)
        except NameError:
            """Expected error."""

    def test_restricted(self):
        config_json = """
        {
            "myfile": "{{ open('%s').read() }}"
        }
        """ % (CFG_PATH)
        try:
            config = Config(config_json)
            self.fail("NameError not raised")
        except NameError:
            """Expected error"""

    def test_unrestricted(self):
        config_json = """
        {
            "myfile": "{{ open('%s').read() }}"
        }
        """ % (CFG_PATH)
        config = Config(config_json, restricted=False)
        self.assertTrue("db_username" in config['myfile'])
        self.assertTrue("read()" not in config['myfile'])

    def test_compound(self):
        config_json = """
        {
            "person": {
                "name": "John",
                "address": {
                    "town": "Dublin"
                }
            },
            "j": "${person.name}",
            "d": "${person.address.town}",
            "e": [ "a", "b", 2 ],
            "f": "${e.0}",
            "g": "{{ ${e.2} }}",
            "h": "'{{ \\"${person.name}\\" * 2}}'"
        }
        """
        config = Config(config_json, restricted=False)
        self.assertEquals("John", config['j'])
        self.assertEquals("Dublin", config['d'])
        self.assertEquals("a", config['f'])
        self.assertEquals(2, config['g'])
        self.assertEquals("JohnJohn", config['h'])

    def test_attrs(self):
        config_json = """
        {
            "person": {
                "name": "John",
                "address": {
                    "town": "Dublin"
                }
            },
            "j": "${person.name}",
            "d": "${person.address.town}",
            "e": [ "a", "b", 2 ],
            "f": "${e.0}"
        }
        """
        config = Config(config_json)
        self.assertEquals("John", config.j)
        self.assertEquals("Dublin", config.d)
        self.assertEquals("a", config.f)
        self.assertEquals("John", config.person.name)

    def test_dict_attr(self):
        config_json = """
        {
            "keys": "{{ 2 }}"
        }
        """
        config = Config(config_json)
        self.assertNotEquals(2, config.keys)
        self.assertEquals(2, config['keys'])

if __name__ == "__main__":
    unittest.main()
