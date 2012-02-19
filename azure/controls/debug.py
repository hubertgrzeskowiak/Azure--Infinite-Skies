from direct.task import Task

from controlstate import ControlState

class Debug(ControlState):
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"print_tasks": "f10",
                       "print_scene": "f11",
                       "screenshot": ["f12", "print_screen"],
         #              "toggle_hud": "f9"
                      }
        self.functionmap = {"screenshot": base.screenshot}
        self.tasks = ([self.debugTask, "debugging task"],)
        self.paused = False

    def debugTask(self, task):
        if "print_scene" in self.requested_actions:
            print
            print "render scene graph:"
            print render.ls()
            print "-" * 40
            print "render2d scene graph:"
            print render2d.ls()
            print
        if "print_tasks" in self.requested_actions:
            print base.taskMgr

        self.requested_actions.clear()
        return Task.cont
