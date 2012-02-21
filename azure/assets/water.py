from panda3d.core import CardMaker
from panda3d.core import NodePath
from panda3d.core import BitMask32
from panda3d.core import Vec4, Vec3
from panda3d.core import Point3
from panda3d.core import VBase4
from panda3d.core import Mat4
from panda3d.core import PlaneNode, Plane
from panda3d.core import Texture, TextureStage
from panda3d.core import CullFaceAttrib, ClipPlaneAttrib
from panda3d.core import RenderState

from assetbase import AssetBase
from azure.loaderglobal import loader

class Water(AssetBase):
    def __init__(self, name, size=10000, resolution=1024):
        """Arguments:
        size -- Edge length of the water square.
        resolution -- Texture size of the rendered reflection buffer.
        """
        # Uncomment to see the output of the refclection buffer.
        base.bufferViewer.toggleEnable()
        
        AssetBase.__init__(self)   
        self.name = name 

        self.cm = CardMaker("water surface")
        self.cm.setFrame(-0.5*size, 0.5*size, -0.5*size, 0.5*size)
        self.cm.setHasUvs(True)
        self.node = NodePath(self.cm.generate())

        self.node.setP(self.node, -90)
        self.node.flattenLight()
        self.node.hide(BitMask32.bit(1))
        #self.node.setTwoSided(True)
        self.node.setShaderOff()

        # size of one texture tile in meters
        self.tex_size = 100.0

        diffuse = loader.loadTexture("textures/water.diffuse.png")
        diffuse.setWrapU(Texture.WMRepeat)
        diffuse.setWrapV(Texture.WMRepeat)
        diffuse.setMinfilter(Texture.FTLinearMipmapLinear)
        diffuse.setMagfilter(Texture.FTLinearMipmapLinear)
        self.diffuse_stage = TextureStage("diffuse")
        self.diffuse_stage.setSort(2)
        self.node.setTexture(self.diffuse_stage, diffuse)
        self.node.setTexScale(self.diffuse_stage, size/self.tex_size, size/self.tex_size)


        # Reflection camera renders to 'buffer' which is projected onto the
        # water surface.
        buffer = base.win.makeTextureBuffer("water reflection",
                                            resolution, resolution)
        buffer.setClearColor(Vec4(0, 0, 0, 1))
        
        self.refl_cam = base.makeCamera(buffer)
        self.refl_cam.reparentTo(self.node)
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
        self.refl_stage = TextureStage("reflection")
        self.refl_stage.setSort(1)
        self.node.projectTexture(self.refl_stage, reflection, base.cam)
        self.node.setTexture(self.refl_stage, reflection)

        # Blend between diffuse and reflection.
        self.diffuse_stage.setColor(VBase4(1, 1, 1, 0.2))  # opacity of 20%
        self.diffuse_stage.setCombineRgb(TextureStage.CMInterpolate,
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
        
        self.node.setX(camera.getX(render))
        self.node.setY(camera.getY(render))
        self.node.setTexOffset(self.diffuse_stage,
                          self.node.getX()/self.tex_size,
                          self.node.getY()/self.tex_size)

        return task.cont

    def destroy(self):
        self.removeAllTasks()
        self.node.removeNode()
        self.refl_cam.removeNode()
