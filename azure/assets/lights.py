"""Easy access to proper lighting."""

class Light(object):
    """Genral class for all lights to inherit from."""
    def __init__(self):
        if Light.lights is None:
            assert render
            Light.render.attachNewNode("Lights")

    def destroy():
        self.node.removeNode()


class Ambient(Light):
    id  = 0
    def __init__(self, color=Vec4(0.6, 0.6, 0.8, 1))
        Light.__init__(self)
        self.light = AmbientLight("ambient light " + Ambient.id)
        Ambient.id += 1
        self.light.setColor(color)
        self.node = Light.lights.attachNewNode(self.light)
        render.setLight(self.light)


class Directional(Light):
    id = 0
    def __init__(self, color=Vec4(1,1,1,1), hpr=Vec3(0,0,0)):
        Light.__init__(self)
        self.light = DirectionalLight("directional light " + Directional.id)
        Directional.id += 1
        self.light.setHpr(hpr)
        self.node = Light.lights.attachNewNode(self.light)
        render.setLight(self.light)


class DefaultLights(object):
    def __init__(self):
        self.ambient = Ambient()
        self.sun = DirectionalLight()

