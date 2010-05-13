# Copyright 2008 John Keyes (johnkeyes@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Configuration classes to provide access to config files.

FileConfig parses a configuration file.
StringConfig parses a configuration string.

The config file format is name value pairs, where the names are
strings and the values are expressions.

Examples:
  first_name = 'John'
  second_name = Keyes
  full_name = ${first_name} ${second_name}
  age = 10
  cost = 99.99
  cost_per_year = ${cost} / ${age}
"""
import logging
import re
import types

try:
    import json
except ImportError:
    import simplejson as json

VAR_STR = '\$\{(.*?)\}'
RE_HAS_VAR_REF = re.compile('.*%s.*' % VAR_STR)
RE_VAR_REF = re.compile(VAR_STR)
MULTI_LINE_COMMENT = re.compile('/\*.*?\*/', re.DOTALL)
SINGLE_LINE_COMMENT = re.compile('//.*\n')

class Config(object):
    
    def __init__(self, config_str, unrestricted=None):
        self.config_str = config_str
        # strip comments (if any exist)
        config_str = MULTI_LINE_COMMENT.sub('', config_str, re.DOTALL|re.M)
        config_str = SINGLE_LINE_COMMENT.sub('\n', config_str, re.DOTALL|re.M)
        
        self.config = json.loads(config_str)
        self._depends = {}
        self._evaluated = []
        if unrestricted:
            self._globals = globals()
        else:
            self._globals = {'__builtins__': None}
        self._locals = {}
        self._check_dependencies()
        # finished parsing lets evaluate each variable
        while len(self.config.keys()) != len(self._evaluated):
            for var_name in self.config.keys():
                self._get_var_value(var_name)        

    def __getattr__(self, key):
        return self.config[key]
        
    def __getitem__(self, key):
        return self.config[key]

    def _check_dependencies(self):
        """
        Make sure the dependency tree is valid
        """
        # build the variable dependency lists
        variable_names = self.config.keys()

        for name in variable_names:
            self._build_dependency_hierarchy(name)

        # now check for cyclical references and unknown variables
        for name in variable_names:
            self._assert_variable_references(name, name)

    def _build_dependency_hierarchy(self, name):
        """
        Creates a dependency hierarchy.
        """
        # every variable gets a dependency list even though
        # it may be empty
        if name not in self._depends:
            self._depends[name] = []

        # only process unevaluated variables
        if not self._is_evaluated(name):
            # get the value which will contain the ${} references
            value = unicode(self.config[name])
            # extract reference names from value
            for match in RE_VAR_REF.finditer(value):
                v_name = match.group(1)
                self._depends[name].append(v_name)

    def _assert_variable_references(self, root_variable, dependency):
        """
        If a cycle is detected in the variable dependencies raise
        a KeyError exception as no mapping for that variable can
        be resolved.  Also raise a KeyError If a variable is 
        referenced but cannot be found.
        """
        depends_on = self._depends[dependency]
        # self reference
        if root_variable in depends_on:
            raise KeyError("A variable cannot refer to itself")

        # check each variable that root_variable depends on
        for var in depends_on:
            if not self._has_variable(var): 
                # no variable could be found for the reference
                raise KeyError("No such variable %s" % var)

            if root_variable in self._depends[var]:
                # found root_variable depends on itself
                raise KeyError("Get a life, not a cyclical reference")

            # check to see if the variable  is also in the 
            # dependencies list
            for next_dependency in self._depends[var]:
                self._assert_variable_references(root_variable, next_dependency)

    def _get_var_value(self, name):
        """
        Returns the actual value of a variable i.e. with 
        variable references replaced by values.
        """
        # evaluate the variable value if required
        if not self._is_evaluated(name): 
            value = self._evaluate_var(name)
        else:
            value = self.config[name]
        return value
        
    def _expand(self, value, ref_name, ref_value):
        if hasattr(value, '__getitem__') and type(value) != types.UnicodeType:
            value = self._evaluate_seq(value, ref_name, ref_value)
        else:
            value = value.replace('${%s}' % ref_name, str(ref_value))

        # if all of the dependencies have been resolved get the correct type
        if not _needs_expansion(value):
            value = self._eval(value)
        return value

    def _evaluate_seq(self, seq, ref_name, ref_value):
        if hasattr(seq, 'items'):
            keys = seq.keys()
            for key in keys:
                if _needs_expansion(key):
                    value = seq[key]
                    del seq[key]
                    seq[self._expand(key, ref_name, ref_value)] = value
            for key in keys:
                value = seq[key]
                if _needs_expansion(value):
                    seq[key] = self._expand(value, ref_name, ref_value)
        else:
            index = 0
            for part in seq:
                if _needs_expansion(part):
                    seq[index] = self._expand(part, ref_name, ref_value)
                index += 1
        return seq
                
    def _eval(self, value):
        if type(value) is types.UnicodeType:
            if "".join(value[0:4]) == "exp(" and value[-1] == ")":
                try:
                    value = eval(value[4:-1], self._globals, self._locals)
                except SyntaxError:
                    # just use the stripped value if there's an error in 
                    # the expression
                    pass
        return value
        
    def _evaluate_var(self, name):
        """
        Evaluate the named variable.
        """
        value = self.config[name]
        # this variable has dependencies which we need to resolve first
        if name in self._depends:
            depends = self._depends[name]
            # for each depends variable replace it's reference with 
            # it's actual value
            for ref_name in depends:
                if ref_name not in self._evaluated:
                    return
                ref_value = self.config[ref_name]
                value = self._expand(value, ref_name, ref_value)

        # if all of the dependencies have been resolved get the correct type
        value = self._eval(value)
        # mark this variable as being evaluated
        self._evaluated.append(name)
        # replace value
        self.config[name] = value
        return value

    def _is_evaluated(self, variable):
        """
        Returns whether the specified variable has been fully evaluated.
        """
        return variable in self._evaluated

    def _has_variable(self, variable):
        """
        Returns whether the specified variable is in this config.
        """
        return variable in self.config

class FileConfig(Config):
    def __init__(self, filepath):
        config_file = open(filepath)
        config_str = config_file.read()
        config_file.close()
        Config.__init__(self, config_str)

def _needs_expansion(value):
    """
    Returns whether the specified value needs expansion.
    """
    value = unicode(value)
    return RE_HAS_VAR_REF.match(value) is not None


