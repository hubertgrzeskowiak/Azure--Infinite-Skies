class Developmentenvironment(object):
    def __init__(self):
        name = "Development Environment"
        # having such long paths here is so suboptimal..
        models = ["planes/griffin/griffin",]

    def prepare(*args, **kwargs):
        pass

    def begin(self, managers):
        m = managers

        m.assets.add("AmbientLight", color=(1.6, 1.6, 1.8, 1))
        m.assets.add("DirectionalLight", color=(2.0, 1.9, 1.6, 1))
        m.assets.add("Sky", "bluesky")
        m.assets.add("Water")

        m.assets.add("Aeroplane", "griffin", name="Griffin")
        griffin = m.assets.getLast()
        griffin.node.setZ(10)
        griffin.physics.setVelocity(0, 300, 0)
        griffin.physics.setThrust(1)

        m.views.activate("PlaneFlight", griffin)
        m.controls.activate("PlaneFlight", griffin, m.views.getLast())
        # alternative syntax:
        #pf = m.controls.add("PlaneFlight", griffin)
        #m.controls.activate(pf)


        # inline helper functions
        getSpeed = lambda: round(griffin.physics.speed(), 1)
        getThrust = lambda: round(getattr(griffin.physics, "thrust"), 1)

        # on screen debugging
        osd = debug.OSDebug(base.a2dTopLeft)
        osd.add("speed", getSpeed)
        osd.add("thrust", getThrust)
        osd = debug.OSDebug(base.a2dBottomRight)
        osd.add("x", lambda: int(griffin.node.getX()))
        osd.add("y", lambda: int(griffin.node.getY()))
        osd.add("z", lambda: int(griffin.node.getZ()))
