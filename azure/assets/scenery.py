"""This module manages everthing about non-interactive environment."""

from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject

from azure.errors import *


class Scenery(object):
    """Standard scenery class."""

    _scenery_count = 0

    def __init__(self, name, model_to_load=None, pos=VBase3(0,0,0),
            scale=VBase3(1,1,1)):
        """Arguments are model to load, position (default is parent's origin)
        and scale (default is 1).
        """

        if not hasattr(Scenery, "_scenery"):
            assert render
            Scenery._scenery = render.attachNewNode("scenery")

        self._id = Scenery._scenery_count
        Scenery._scenery_count += 1

        new_node_name = "Scenery" + str(Scenery._scenery_count)
        self._dummy_node = Scenery._scenery.attachNewNode(new_node_name)
        del new_node_name
        self.name = name

        if model_to_load == 0:
            pass
        elif model_to_load:
            try:
                self.loadSceneryModel(model_to_load)
            except (ResourceHandleError, ResourceLoadError), e:
                handleError(e)
        else:
            try:
                self.loadSceneryModel(name)
            except (ResourceHandleError, ResourceLoadError), e:
                handleError(e)

        self.node.setPos(pos)
        self.node.setScale(scale)

    def loadSceneryModel(self, model, force=False):
        """Loads a model for the scenery object. Force if there's already one
        loaded.
        """
        if hasattr(self, "scenery_model"):
            if force:
                self.scenery_model = loader.loadModel(model)
                if self.scenery_model != None:
                    self.scenery_model.reparentTo(self.node)
                else:
                    raise ResourceLoadError(model, "no such model")
            else:
                raise ResourceHandleError(model,
                    "scenery object already has a model. force to change")
        else:
            self.scenery_model = loader.loadModel(model)
            if self.scenery_model != None:
                self.scenery_model.reparentTo(self.node)
            else:
                raise ResourceLoadError(model, 'no such model')

    def id(self):
        """Every scenery object has its own unique ID."""
        return self._id

    @property
    def node(self):
        """Returns a container class, which you should use instead of
        dummy_mode or the model itself.
        """
        return self._dummy_node


#class Sky2(NodePath):
#    def __init__(self, *args):
#        self = loader.loadModel("textured_sky")
#        self.setScale(10000)
#        self.setBin('background', 0)
#        self.setDepthTest(False)
#        self.setDepthWrite(False)
#        self.setLightOff()
#        self.setCompass()
#        self.reparentTo(camera)

class Sky(NodePath, DirectObject):
    """Skies are implemented in form of a cube with 6 square textures. See
    assets/skyboxes/README.txt for more details.
    """
    def __init__(self, resource):
        """Arguments:
        resource -- name of a directory in assets/skyboxes that contains 6
        images.
        """
        NodePath.__init__(self, "sky")
        DirectObject.__init__(self)

        tex = None
        for ext in ("png", "jpg", "tga"):
            f = "skyboxes/%s/0.%s" % (resource, ext)
            if vfs.resolveFilename(f, getModelPath().getValue()):
                tex = loader.loadCubeMap("skyboxes/%s/#.%s" % (resource, ext))
                if tex is not None:
                    break
        if tex is None:
            raise ResourceLoadError("assets/skyboxes/%s" % resource,
                                 "maybe wrong names or different extensions?")
        #self.attachNewNode(loader.loadModel("misc/invcube"))
        loader.loadModel("misc/invcube").reparentTo(self)
        # probably the same as the line above
        #self.attachNewNode(loader.loadModelNode("misc/invcuvbe"))
        self.clearTexture()
        self.clearMaterial()
        self.setScale(10000)
        self.setTwoSided(True)
        self.setBin('background', 0)
        self.setDepthTest(False)
        self.setDepthWrite(False)
        self.setLightOff()
        self.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.setTexProjector(TextureStage.getDefault(), render, self);
        self.setTexture(tex, 1)
        self.flattenLight()
        #self.setCompass()  # not needed with world-space-UVs
        self.reparentTo(render)
        self.addTask(self.update, "sky repositioning", sort=10,
                     taskChain="world")

    def update(self, task):
        self.setPos(camera.getPos(render))
        return task.cont

    def destroy(self):
        self.removeAllTasks()
        self.removeNode()


class Water(NodePath, DirectObject):
    def __init__(self, size=10000, resolution=1024):
        """Arguments:
        size -- Edge length of the water square.
        resolution -- Texture size of the rendered reflection buffer.
        """
        # Uncomment to see the output of the refclection buffer.
        #base.bufferViewer.toggleEnable()

        NodePath.__init__(self, "water")
        DirectObject.__init__(self)
        self.cm = CardMaker("water surface")
        self.cm.setFrame(-0.5*size, 0.5*size, -0.5*size, 0.5*size)
        self.cm.setHasUvs(True)
        self.attachNewNode(self.cm.generate())
        self.reparentTo(render)
        self.setP(self, -90)
        self.flattenLight()
        self.hide(BitMask32.bit(1))
        #self.setTwoSided(True)
        self.setShaderOff()

        # size of one texture tile in meters
        self.tex_size = 100.0

        diffuse = loader.loadTexture("textures/water.diffuse.png")
        diffuse.setWrapU(Texture.WMRepeat)
        diffuse.setWrapV(Texture.WMRepeat)
        diffuse.setMinfilter(Texture.FTLinearMipmapLinear)
        diffuse.setMagfilter(Texture.FTLinearMipmapLinear)
        diffuse_stage = TextureStage("diffuse")
        diffuse_stage.setSort(2)
        self.setTexture(diffuse_stage, diffuse)
        self.setTexScale(diffuse_stage, size/self.tex_size, size/self.tex_size)
        self.diffuse_stage = diffuse_stage


        # Reflection camera renders to 'buffer' which is projected onto the
        # water surface.
        buffer = base.win.makeTextureBuffer("water reflection",
                                            resolution, resolution)
        buffer.setClearColor(Vec4(0, 0, 0, 1))
        
        self.refl_cam = base.makeCamera(buffer)
        self.refl_cam.reparentTo(render)
        self.refl_cam.node().setCameraMask(BitMask32.bit(1))
        self.refl_cam.node().getLens().setFov(base.camLens.getFov())
        self.refl_cam.node().getLens().setNearFar(1,100000)
        
        plane = PlaneNode("water culling plane",
                          Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        cfa = CullFaceAttrib.makeReverse()
        cpa = ClipPlaneAttrib.make(PlaneNode.CEVisible, plane)
        rs = RenderState.make(cfa, cpa)
        self.refl_cam.node().setInitialState(rs)
        
        reflection = buffer.getTexture()
        reflection.setMinfilter(Texture.FTLinear)
        reflection.setMagfilter(Texture.FTLinear)
        refl_stage = TextureStage("reflection")
        refl_stage.setSort(1)
        self.refl_stage = refl_stage
        self.projectTexture(refl_stage, reflection, base.cam)
        self.setTexture(refl_stage, reflection)

        # Blend between diffuse and reflection.
        diffuse_stage.setColor(VBase4(1, 1, 1, 0.2))  # opacity of 20%
        diffuse_stage.setCombineRgb(TextureStage.CMInterpolate,
                TextureStage.CSTexture, TextureStage.COSrcColor,
                TextureStage.CSPrevious, TextureStage.COSrcColor,
                TextureStage.CSConstant, TextureStage.COSrcAlpha)

        self.addTask(self.update,
                     name="water update",
                     sort=1,
                     taskChain="world")

    def update(self, task):
        """Updates position of the reflection camera and the water plane."""
        mc = base.cam.getMat(render)
        #mf = Plane(Vec3(0, 0, 1), Point3(0, 0, 0)).getReflectionMat()
        mf = Mat4(1, 0, 0, 0,
                  0, 1, 0, 0,
                  0, 0, -1, 0,
                  0, 0, 0, 1)
        self.refl_cam.setMat(mc * mf)
        
        self.setX(camera.getX(render))
        self.setY(camera.getY(render))
        self.setTexOffset(self.diffuse_stage,
                          self.getX()/self.tex_size,
                          self.getY()/self.tex_size)

        return task.cont

    def destroy(self):
        self.removeAllTasks()
        self.removeNode()
        self.refl_cam.removeNode()
