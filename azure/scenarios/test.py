from azure import views
from azure import controls
import gui


class Developmentenvironment(object):
    def __init__(self):
        name = "Development Environment"
        # having such long paths here is so suboptimal..
        models = ["planes/griffin/griffin",]

    def prepare(*args, **kwargs):
        pass

    def begin():
        # how this should look later:
        #AmbientLight(color=(0.6, 0.6, 0.8))
        ambient = AmbientLight("ambient light")
        ambient.setColor(Vec4(0.6, 0.6, 0.8, 1))
        ambient_np = NodePath(ambient)
        ambient_np.reparentTo(render)
        render.setLight(ambient_np)

        sunlight = DirectionalLight("sun")
        sunlight.setColor(Vec4(1.0, 0.9, 0.8, 1))
        sunlight_np = NodePath(sunlight)
        render.setLight(sunlight_np)

        griffin = Aeroplane("griffin", "griffin", True)
        griffin.node.setZ(10)
        # how this should look later:
        #griffin.physics.velocity = Vec3(0, 300, 0)
        griffin.physics.setVelocity(Vec3(0, 300, 0))
        griffin.physics.thrust = 1

        view = views.PlaneCamera(griffin)
        control = controls.PlaneControl(griffin)


        # inline helper functions
#        getSpeed = lambda: round(getattr(griffin.physics, "speed"), 1)
#        getThrust = lambda: round(getattr(griffin.physics, "thrust"), 1)

        # on screen debugging
#        osd = gui.OSDebug(base.a3dTopLeft)
#        osd.add("speed", getSpeed)
#        osd.add("thrust", getThrust)
#        osd = gui.OSDebug(base.a2dBottomRight)
#        osd.add("x", lambda: int(griffin.node.getX()))
#        osd.add("y", lambda: int(griffin.node.getY()))
#        osd.add("z", lambda: int(griffin.node.getZ()))
