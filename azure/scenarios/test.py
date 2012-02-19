class Developmentenvironment(object):
    def __init__(self):
        self.name = "Development Environment"
        # having such long paths here is so suboptimal..
        self.models = ["planes/griffin/griffin",]

    def prepare(*args, **kwargs):
        pass

    def begin(self, managers):
        m = managers

        m.assets.add("AmbientLight", "sky blue", color=(1.6, 1.6, 1.8, 1))
        m.assets.add("DirectionalLight", "sun light", color=(2.0, 1.9, 1.6, 1))
        #m.assets.add("Sky", "bluesky")
        #m.assets.add("Water")

        m.assets.add("Aeroplane", "Griffin", "griffin", True)
        griffin = m.assets.getLast()
        griffin.node.setZ(10)
        griffin.physics.setVelocity(300)
        griffin.physics.setThrust(1)

        m.views.setView("PlaneView", griffin)
        m.controls.addAndActivate("PlaneFlight", griffin, m.views.getView())
        # alternative syntax:
        # pf = m.controls.add("PlaneFlight", griffin)
        # m.controls.activate(pf)
