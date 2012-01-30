"""Base class of all control states."""

class ControlBase(object):
    """Specific control state classes should inherit from this."""

    def __init__(self):
        # format for keymap: keymap["action"] = "key1, key2"
        #                 or keymap["action"] = "key"
        self.keymap = {}

        # format for functionmap: functionmap["action"] = function
        self.functionmap = {}

        # the tasks list can contain task functions,
        #     (function1, function2, ...)
        # lists or tuples,
        #     ([function1, name1, sort], [function2, name2, sort], ...)
        # or dicts
        #     ({"taskOrFunc":function, "name":"task name", "sort":10},
        #      {"taskOrFunc":function2, "name":"task name2", "sort":20})
        #
        # in the latter two versions everything except task is optional.
        # in fact if the items aren't callable they're expected to be
        # unpackable
        self.tasks = ()
