"""Base class of all control states."""
# TODO: declare private attributes and outsource some functions
class ControlState(DirectObject):
    """Specific control state classes should inherit from this."""
    conf_parser = SafeConfigParser()
    f = Filename(EE.expandString("$MAIN_DIR/etc/keybindings.ini"))
    conf_parser.read(f.toOsSpecific())

    @classmethod
    def reloadKeybindings(cls, filenames="etc/keybindings.ini"):
        """Read the keybindings file again. Existing instances won't update
        until you call loadKeybindings() on them."""
        cls.conf_parser.read(filenames)

    def __init__(self):
        self.name = self.__class__.__name__
        self.paused = False
        self.active = False

    def __repr__(self):
        t = "ControlState: " + self.name
        if self.paused: t += " (paused)"
        if not self.active: t += " (inactive)"
        t += "\nlistens to the following events:\n" + self.getAllAccepting()
        t += "\nkeymap:\n" + self.keymap
        t += "\nfunctionmap:\n" + self.functionmap
        t += "\nrequested actions:\n" + self.requested_actions
        t += "\n"
        return t

    def __str__(self):
        return self.name

    def loadKeybindings(self):
        """Overrides the hardcoded keymap with those found in the keybindings
        file (or owerwrites previously loaded ones). Only defined actions are
        overwritten - no extra actions are added from the keybindings file.
        """
        try:
            keys_from_file = ControlState.conf_parser.items(self.name)
            for a in self.keymap:
                for action, key in keys_from_file:
                    if a == action:
                        for k in map(str.strip, key.split(',')):
                            self.keymap[a] = k
        except NoSectionError:
            notify.warning("".join("Keybindings for section {0} not found. ",
                                  "Using built-in bindings").format(self.name))

    def activate(self):
        if self.active is True:
            return False
        notify.info("Activating %s" % self.name)

        def assignKey(key, action):
            self.accept(key, self.requested_actions.add, [action])
            self.accept(key+"-up", self.requested_actions.discard, [action])
            if action in self.functionmap:
                self.accept(key, self.functionmap[action])

        for action, key in self.keymap.items():
            if isinstance(key, basestring):
                assignKey(key, action)
            elif isinstance(key, list):
                for k in key:
                    assignKey(k, action)

        self.loadKeybindings()

        for task in self.tasks:
            if callable(task):
                self.addTask(task, task.__name__, taskChain="world")
            else:
                self.addTask(*task, taskChain="world")

        self.active = True
        ControlState.active_states.append(self)

    def deactivate(self):
        if self.active is False:
            return False
        notify.info("Deactivating %s" % self.name)
        self.ignoreAll()
        self.requested_actions.clear()
        #for task in self.tasks:
        #    self.removeTask(task)
        #self.removeAllTasks()
        self.active = False
        ControlState.active_states.remove(self)
