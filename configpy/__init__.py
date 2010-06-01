"""
Configuration classes to provide access to config files.

FileConfig parses a configuration file.
StringConfig parses a configuration string.
"""
import re

try:
    # json supported since Python 2.6
    import json
except ImportError:
    # older versions of Python (not tested)
    import simplejson as json

# REGULAR EXPRESSION CONSTANTS
VAR_STR = '\$\{(.*?)\}'
RE_HAS_VAR_REF = re.compile('.*%s.*' % VAR_STR)
RE_VAR_REF = re.compile(VAR_STR)
MULTI_LINE_COMMENT = re.compile('/\*.*?\*/', re.DOTALL)
SINGLE_LINE_COMMENT = re.compile('//.*\n')
RE_HAS_EVAL = re.compile('.*\{\{.*\}\}.*')
RE_EVAL = re.compile('(\{\{(.*)\}\})')

class Node(object):
    """
    Represents any value in the configuration.
    """

    def __init__(self, root, parent, key, value):
        """
        Initialize the Node.
        """
        # root of tree (the config object)
        self.root = root
        # the key for this item (dict key or list index)
        self.key = key
        # the value for this item (initially contains unresolved vars)
        self.value = value
        # the parent of this Node (dict or list)
        self.parent = parent
        # the compound key name
        self.abskey = self._abskey()
        self.indent = ""

    def _resolve_var(self, value):
        """
        Resolve the variables in the value.
        """
        # if it's a Node, get it's value
        if isinstance(value, Node):
            value = value.value
        
        # for each variable found in the value
        for match in RE_VAR_REF.finditer(value):
            var = match.group(1)
            if var == self.abskey:
                raise KeyError("self reference")
            var_parts = var.split('.')
            ctx = self.root
            for vpart in var_parts:
                # if the context is a list convert the
                # 'key' to a int
                if isinstance(ctx, list):
                    vpart = int(vpart)
                    
                # get the value
                resolves_to = ctx[vpart]
                
                # change the context
                ctx = resolves_to

            # convert the value to a unicode string to check for more variables
            resolves_to = unicode(resolves_to)
            if self._contains_variable(resolves_to):
                resolves_to = self._resolve_var(resolves_to)
                
            # replace the variable with the resolved value
            value = value.replace('${%s}' % var, resolves_to)
        return value

    def _evalit(self, value):
        """
        Evaluates any eval blocks in the configuration.
        """
        value = unicode(value)
        if RE_HAS_EVAL.match(value):
            for match in RE_EVAL.finditer(value):
                eval_block = match.group(1)
                to_eval = match.group(2).strip()
                value = value.replace(eval_block, \
                                      unicode(self._evalit(to_eval)))
        if value[0] != " " and value[-1] != " ":
            value = eval(unicode(value), \
                         self.root._globals, self.root._locals)
        return value
            
    def _eval(self):
        """
        Evaluate the contents of the Node and return the value.
        """
        # if there is a variable in there resolve it
        if self._contains_variable(self.value):
            self.value = self._resolve_var(self.value)
        # if there is anything to be evaluated do so
        if self._contains_eval():
            self.value = self._evalit(self.value)
        return self.value


    def _contains_variable(self, value=None):
        """
        Returns whether the specified value needs expansion.
        """
        if value is None:
            value = self.value
        if isinstance(value, basestring):
            return RE_HAS_VAR_REF.match(value) is not None
        return False

    def _contains_eval(self, value=None):
        """
        Returns whether the specified value needs expansion.
        """
        if value is None:
            value = self.value
        if isinstance(value, basestring):
            return RE_HAS_EVAL.match(value) is not None
        return False
        
    def _abskey(self):
        """
        Create the abskey (or compound key) for this Node.
        """
        parts = [unicode(self.key)]
        parent = self.parent
        while parent.key is not None:
            parts.append(unicode(parent.key))
            parent = parent.parent
        return ".".join(parts)

    def __unicode__(self):
        """
        Return the unicode for self.value.
        """
        return unicode(self.value)

    def __repr__(self):
        """
        Returns the formal representation of a Node.
        """
        if isinstance(self.value, basestring):
            # strings are wrapped in quotes
            return '"%s"' % unicode(self)
        return unicode(self)

class NodeDict(dict):
    """
    Represents any object (JSON terminology) in the configuration.
    """

    def __init__(self, root, parent, key, *args, **kwargs):
        """
        Initialize the NodeDict.
        """
        # root of tree (the config object)
        self.root = root
        # the key for this item (dict key or list index)
        self.key = key
        # the parent of this Node (dict or list)
        self.parent = parent

        dict.__init__(self, *args, **kwargs)
        self._init_nodes()

    def _init_nodes(self):
        """
        Create Nodes for each value in this object (JSON term).
        """
        for key in self.keys():
            value = self[key]
            if isinstance(value, dict):
                self[key] = NodeDict(self.root, self, key, value)
            elif isinstance(value, list):
                self[key] = NodeList(self.root, self, key, value)
            else:
                self[key] = Node(self.root, self, key, value)

    def _eval(self):
        """
        Set the comupted value for each child Node.
        """
        for key in self.keys():
            value = self[key]
            self[key] = value._eval()
        return self

    def __getattr__(self, attr):
        """
        Attrs unknown to this instance are tried as keys.
        """
        if dict.has_key(self, attr):
            return dict.__getitem__(self, attr)
        raise AttributeError

class NodeList(list):
    """
    Represents any array (JSON terminology) in the configuration.
    """

    def __init__(self, root, parent, key, *args,  **kwargs):
        # root of tree (the config object)
        self.root = root
        # the key for this item (dict key or list index)
        self.key = key
        # the parent of this Node (dict or list)
        self.parent = parent

        list.__init__(self, *args, **kwargs)
        self._init_nodes()

    def _init_nodes(self):
        """
        Create Nodes for each value in this array (JSON term).
        """
        index = 0
        for value in self:
            if isinstance(value, dict):
                self[index] = NodeDict(self.root, self, index, value)
            elif isinstance(value, list):
                self[index] = NodeList(self.root, self, index, value)
            else:
                self[index] = Node(self.root, self, index, value)
            index += 1

    def _eval(self):
        """
        Set the comupted value for each child Node.
        """
        index = 0
        for value in self:
            self[index] = value._eval()
            index += 1
        return self

class Config(NodeDict):
    """
    Represents the JSON configuration object.
    """

    def __init__(self, config_str, restricted=True):
        """
        Initialize the Config.
        """
        
        # how to handle evaluations
        if restricted:
            self._globals = {'__builtins__': None}
        else:
            self._globals = globals()
        self._locals = {}
    
        # strip comments (if any exist)
        config_str = MULTI_LINE_COMMENT.sub('', config_str, re.DOTALL|re.M)
        config_str = SINGLE_LINE_COMMENT.sub('\n', config_str, re.DOTALL|re.M)
        
        # parse JSON
        config_dict = json.loads(config_str)
        
        # save the entries in this dict
        self.update(config_dict)
        
        # initialize the NodeDict
        #                 root, parent, key, value
        NodeDict.__init__(self, self, None, None)
        
        # all the initialisation (tree building) is complete,
        # go compute the values.
        self._eval()

class FileConfig(Config):
    """
    Represents a JSON configuration object stored in a file.
    """
    def __init__(self, filepath, **kwargs):
        config_file = open(filepath)
        config_str = config_file.read()
        config_file.close()
        Config.__init__(self, config_str, **kwargs)
