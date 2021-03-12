#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division

###############################################################################
# The MIT License (MIT)
#
# Copyright (c) <year> <copyright holders>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###############################################################################
from __future__ import unicode_literals
from __future__ import division

import os
import sys

import time
import random

from io import StringIO

WIN_SIZE = (800, 800)

from panda3d.core import loadPrcFileData
# need to be before the Direct Start Import
loadPrcFileData("", "window-title MMD PMX/PMX Model Viewer")
loadPrcFileData("", "icon-filename viewpmx.ico")
loadPrcFileData("", "win-size %d %d" % WIN_SIZE)
loadPrcFileData("", "window-type none")
loadPrcFileData('', 'text-encoding utf8')
loadPrcFileData('', 'textures-power-2 none')
loadPrcFileData('', 'geom-cache-size 10')
loadPrcFileData('', 'coordinate-system zup-right')
loadPrcFileData('', 'clock-mode limited')
loadPrcFileData('', 'clock-frame-rate 60')
loadPrcFileData('', 'show-frame-rate-meter 1')
# loadPrcFileData('', 'want-pstats 1')

from panda3d.core import ConfigVariableString
from panda3d.core import Shader
from panda3d.core import Filename
from panda3d.core import Material
from panda3d.core import VBase4

from panda3d.bullet import ZUp
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletSoftBodyNode
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletConeShape
from panda3d.bullet import BulletCharacterControllerNode

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBase import WindowControls
from direct.showbase.DirectObject import DirectObject
from direct.directtools.DirectSelection import *
from direct.directtools.DirectGeometry import *
from direct.directtools.DirectGlobals import *


from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.ShowBase import ShowBase

# import direct.directbase.DirectStart

from direct.gui.DirectGui import *

from pandac.PandaModules import *

from utils.DrawPlane import *
from utils.pmx import *
from utils.pmd import *

# Get the location of the 'py' file I'm running:
CWD = os.path.abspath(sys.path[0])

SHOW_LIGHT_POS = True
SHOW_LIGHT_POS = False

SHOW_SHADOW = True
SHOW_SHADOW = False

SHOW_AXIS = True
# SHOW_AXIS = False

lastModel = None

class Stage(object):
  lights = None
  @staticmethod
  def setAxis(render, update=False):
    def CreateAxis(axisStage):
      grid = ThreeAxisGrid(gridstep=20, subdiv=20, xy=True, yz=False, xz=False, z=False)
      gridnodepath = grid.create()
      grid.showPlane(XY=True)
      grid.showAxis(Z=False)
      gridnodepath.writeBamFile(axisStage)
      return(gridnodepath)

    axisStage = u'./stages/default_axis.bam'
    if not update:
      try:
        gridnodepath = loader.loadModel(axisStage)
        gridnodepath = gridnodepath.getChild(0)
      except:
        gridnodepath = CreateAxis(axisStage)
    else:
      gridnodepath = CreateAxis(axisStage)

    gridnodepath.reparentTo(render)
    pass

  @staticmethod
  def setStudioLight(render):
    lightsStage = u'./stages/default_lights.bam'
    try:
      lights = loader.loadModel(lightsStage)
      lights = lights.getChild(0)
    except:
      lights = NodePath(PandaNode('StageLights'))

      alight = AmbientLight('alight')
      alight.setColor(VBase4(0.33, 0.33, 0.33, 1))
      # alight.setColor(VBase4(0.33, 0.33, 0.33, 0.67))
      alnp = render.attachNewNode(alight)
      alnp.reparentTo(lights)

      dlight_top = PointLight('top dlight')
      dlnp_top = render.attachNewNode(dlight_top)
      dlnp_top.setX(-5)
      dlnp_top.setZ(45)
      dlnp_top.setY(0)
      # dlnp_top.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
      dlnp_top.node().setAttenuation( Vec3( 0.005, 0.005, 0.005 ) )
      dlnp_top.setHpr(0, -180, 0)
      if SHOW_LIGHT_POS:
        dlnp_top.node().showFrustum()
      dlnp_top.reparentTo(lights)

      dlight_back = PointLight('back dlight')
      dlnp_back = render.attachNewNode(dlight_back)
      dlnp_back.setX(0)
      dlnp_back.setZ(25)
      dlnp_back.setY(+55)
      # dlnp_back.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
      dlnp_back.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
      dlnp_back.setHpr(0, -168, 0)
      if SHOW_LIGHT_POS:
        dlnp_back.node().showFrustum()
      dlnp_back.reparentTo(lights)

      dlight_front = PointLight('front dlight')
      dlnp_front = render.attachNewNode(dlight_front)
      dlnp_front.setX(0)
      dlnp_front.setY(-36)
      dlnp_front.setZ(15)
      dlens = dlnp_front.node().getLens()
      dlens.setFilmSize(41, 21)
      # dlens.setNearFar(50, 75)
      dlnp_front.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
      # dlnp_front.node().setAttenuation( Vec3( 0.005, 0.005, 0.005 ) )
      dlnp_front.setHpr(0, -10, 0)
      if SHOW_LIGHT_POS:
        dlnp_front.node().showFrustum()
      dlnp_front.reparentTo(lights)

      dlight_left = Spotlight('left dlight')
      dlnp_left = render.attachNewNode(dlight_left)
      dlnp_left.setX(-46)
      dlnp_left.setY(+36)
      dlnp_left.setZ(27)
      dlens = dlnp_left.node().getLens()
      dlens.setFilmSize(41, 21)
      # dlens.setNearFar(50, 75)
      dlnp_left.node().setAttenuation( Vec3( 0.001, 0.002, 0.001 ) )
      # dlnp_left.node().setAttenuation( Vec3( 0.011, 0.011, 0.011 ) )
      dlnp_left.setHpr(-130, -15, 0)
      if SHOW_LIGHT_POS:
        dlnp_left.node().showFrustum()
      dlnp_left.reparentTo(lights)

      dlight_right = Spotlight('right dlight')
      dlnp_right = render.attachNewNode(dlight_right)
      dlnp_right.setX(+50)
      dlnp_right.setY(+40)
      dlnp_right.setZ(30)
      dlens = dlnp_right.node().getLens()
      dlens.setFilmSize(41, 21)
      # dlens.setNearFar(50, 75)
      dlnp_right.node().setAttenuation( Vec3( 0.001, 0.002, 0.001 ) )
      # dlnp_right.node().setAttenuation( Vec3( 0.011, 0.011, 0.011 ) )
      dlnp_right.setHpr(130, -15, 0)
      if SHOW_LIGHT_POS:
        dlnp_right.node().showFrustum()
      dlnp_right.reparentTo(lights)

      if SHOW_SHADOW:
        lights.setShaderAuto()
        lights.setShadowCaster(True, 512, 512)

      lights.writeBamFile(lightsStage)

    # lights.reparentTo(render)
    Stage.lights = lights
    return(lights)
    pass

  @staticmethod
  def lightAtNode(node=None, lights=None):
    if not lights:
        return
    if not node:
      for light in lights.getChildren():
        render.setLight(light)
    elif isinstance(node, NodePathCollection):
      for np in node:
        for light in lights.getChildren():
          np.setLight(light)
    elif isinstance(node, NodePath):
      for light in lights.getChildren():
        try:
          node.setLight(light)
        except:
          continue
    pass

  @staticmethod
  def setCamera(x=0, y=0, z=0, h=0, p=0, r=0, oobe=False):
    base.camLens.setNearFar(0.1, 550.0)
    base.camLens.setFov(45.0)
    base.camLens.setFocalLength(50)

    # base.trackball.node().setPos(0, 20, -20)
    base.trackball.node().setHpr(h, p, r)
    base.trackball.node().setPos(x, y, -z)

    # base.useDrive()
    if oobe:
      # base.oobe()
      base.oobeCull()
    pass

  @staticmethod
  def resetCamera(model=None):
    WIN_SIZE = (500, 500)
    if model:
      lens = base.camLens

      fov_old = render.getPythonTag('lensFov')
      fov_new = lens.getFov()
      aspect = lens.getAspectRatio()
      scale_x = fov_new.getX() / fov_old.getX()
      scale_y = fov_new.getY() / fov_old.getY()
      # print('Scale : x=%.4f, y=%.4f' % (scale_x, scale_y))

      min_point = LPoint3f()
      max_point = LPoint3f()
      model.calcTightBounds(min_point, max_point)
      node_size = LPoint3f(max_point.x-min_point.x, max_point.y-min_point.y, max_point.z-min_point.z)
      # print(node_size)

      camPosX = 0
      camPosY = 1.6*node_size.z/scale_y
      camPosZ = 0.5*node_size.z #/scale_y

    else:
      camPosX = 0
      camPosY = 100
      camPosZ = 20
    Stage.setCamera(x=camPosX, y=camPosY, z=camPosZ, p=10, oobe=False)
    pass

  pass


class Utils(object):
  @staticmethod
  def processVertexData(vdata_src, vdata_dst, morphOn=True, strength=1.0):
    vertex_src = GeomVertexWriter(vdata_src, 'vertex')
    vertex_dst = GeomVertexReader(vdata_dst, 'vertex')
    vindex_dst = GeomVertexReader(vdata_dst, 'vindex')
    # vmorph_dst = GeomVertexReader(vdata_dst, 'v.morph')
    vmorph_dst = GeomVertexReader(vdata_dst, 'vmorph')

    # vertex_src.setColumn('vertex')
    while not vertex_dst.isAtEnd():
      i_dst = vindex_dst.getData1i()
      v_dst = vertex_dst.getData3f()
      m_dst = vmorph_dst.getData3f()
      vertex_src.setRow(i_dst)
      if morphOn:
        vertex_src.setData3f(v_dst.getX()+m_dst.getX()*strength, v_dst.getY()+m_dst.getY()*strength, v_dst.getZ()+m_dst.getZ()*strength)
      else:
        vertex_src.setData3f(v_dst.getX(), v_dst.getY(), v_dst.getZ())
      # print(vertex_src.getWriteRow())
    del vertex_src, vertex_dst, vindex_dst, vmorph_dst

  @staticmethod
  def processGeomNode(geomNode, morphNode, morphOn=True, strength=1.0):
    geom = geomNode.modifyGeom(0)
    morphgeom = morphNode.getGeom(0)
    vdata_src = geom.modifyVertexData()
    vdata_dst = morphgeom.getVertexData()
    result = Utils.processVertexData(vdata_src, vdata_dst, morphOn, strength)
    del vdata_src, vdata_dst, geom, morphgeom
    return(result)

  @staticmethod
  def morphVertex(nodepath, morphnodepath, morphOn=True, strength=1.0):
    morphNode = morphnodepath.node()
    geomNodeCollection = nodepath.findAllMatches('**/Body/+GeomNode')
    idx = 0
    for nodePath in geomNodeCollection:
      log(u'%s' % nodePath.getName())
      geomNode = nodePath.node()
      Utils.processGeomNode(geomNode, morphNode, morphOn, strength)
      # idx += 1
      del geomNode
    del morphNode, geomNodeCollection
    pass

  @staticmethod
  def morphMaterial(nodepath, morphData, morphOn=True, strength=1.0):
    idx = 0
    print(u'-> Morph Material Count : %d' % len(morphData))
    for data in morphData:
      material_index        = data.getPythonTag('materialIndex')
      calc_mode             = data.getPythonTag('calcMode')
      edge_color            = data.getPythonTag('edge_color')
      edge_size             = data.getPythonTag('edge_size')
      texture_factor        = data.getPythonTag('texture_factor')
      sphere_texture_factor = data.getPythonTag('sphere_texture_factor')
      toon_texture_factor   = data.getPythonTag('toon_texture_factor')

      mat = data.getMaterial()
      print(u'--> Target Material Count : %d' % len(morphData))
      print(u'--> Target Material Index : %d' % material_index)

      nps = nodepath.findAllMatches('**/Body/*')
      for np in nps:
        log(u'---> %s, %d, %s' % (np.getName(), np.getPythonTag('material_index'), str(morphOn)), force=True)
        matIndex = np.getPythonTag('material_index')
        if material_index < 0:
          pass
        elif matIndex != material_index:
          continue

        tex_name = u'%s_morph_%04d' % (np.getName(), idx)
        ts_morph = TextureStage(tex_name)

        tsSphereName = u'%s_sphere' % np.getName()
        tsSphere = np.findTextureStage(tsSphereName)
        tsToonName = u'%s_toon' % np.getName()
        tsToon = np.findTextureStage(tsToonName)
        if morphOn:
          np.setMaterial(mat, 1)
          if   calc_mode == 0: # *
            np.setColorScale(texture_factor.r, texture_factor.g, texture_factor.b, texture_factor.a, matIndex)
          elif calc_mode == 1: # +
            np.setColorScale(texture_factor.r, texture_factor.g, texture_factor.b, texture_factor.a, matIndex)
        else:
          np.setColorScaleOff(matIndex)
          np.clearMaterial()
          np.setMaterial(np.getPythonTag('material'), 1)

        if tsSphere:
          if morphOn:
            np.setPythonTag('sphere_combine_mode', (
              tsSphere.getCombineRgbMode(),
              tsSphere.getCombineRgbSource0(),
              tsSphere.getCombineRgbOperand0(),
              tsSphere.getCombineRgbSource1(),
              tsSphere.getCombineRgbOperand1(),
              tsSphere.getCombineRgbSource2(),
              tsSphere.getCombineRgbOperand2(),
              tsSphere.getCombineAlphaMode(),
              tsSphere.getCombineAlphaSource0(),
              tsSphere.getCombineAlphaOperand0(),
              tsSphere.getCombineAlphaSource1(),
              tsSphere.getCombineAlphaOperand1(),
              tsSphere.getCombineAlphaSource2(),
              tsSphere.getCombineAlphaOperand2(),
              tsSphere.getMode()
              ))
            if calc_mode == 0: # *
              color = VBase4(sphere_texture_factor.r*strength/10, sphere_texture_factor.g*strength/10, sphere_texture_factor.b*strength/10, sphere_texture_factor.a*strength/10)
              tsSphere.setColor(color)
              tsSphere.setCombineRgb(TextureStage.CMModulate, TextureStage.CSPrevious, TextureStage.COSrcColor, TextureStage.CSTexture, TextureStage.COSrcColor)
              tsSphere.setCombineAlpha(TextureStage.CMModulate, TextureStage.CSPrevious, TextureStage.COSrcAlpha, TextureStage.CSTexture, TextureStage.COSrcAlpha)
            elif calc_mode == 1: # +
              color = VBase4(-sphere_texture_factor.r*strength, -sphere_texture_factor.g*strength, -sphere_texture_factor.b*strength, -sphere_texture_factor.a*strength)
              tsSphere.setColor(color)
              tsSphere.setCombineRgb(TextureStage.CMSubtract, TextureStage.CSTexture, TextureStage.COSrcColor, TextureStage.CSConstant, TextureStage.COSrcColor)
              tsSphere.setCombineAlpha(TextureStage.CMSubtract, TextureStage.CSTexture, TextureStage.COSrcAlpha, TextureStage.CSConstant, TextureStage.COSrcAlpha)
          else:
            cMode = np.getPythonTag('sphere_combine_mode')
            # tsSphere.setCombineRgb(cMode[0], cMode[1], cMode[2], cMode[3], cMode[4], cMode[5], cMode[6])
            # tsSphere.setCombineAlpha(cMode[7], cMode[8], cMode[9], cMode[10], cMode[11], cMode[12], cMode[13])
            tsSphere.setMode(cMode[14])
          pass
        pass

        if tsToon:
          if morphOn:
            np.setPythonTag('toon_combine_mode', (
              tsToon.getCombineRgbMode(),
              tsToon.getCombineRgbSource0(),
              tsToon.getCombineRgbOperand0(),
              tsToon.getCombineRgbSource1(),
              tsToon.getCombineRgbOperand1(),
              tsToon.getCombineRgbSource2(),
              tsToon.getCombineRgbOperand2(),
              tsToon.getCombineAlphaMode(),
              tsToon.getCombineAlphaSource0(),
              tsToon.getCombineAlphaOperand0(),
              tsToon.getCombineAlphaSource1(),
              tsToon.getCombineAlphaOperand1(),
              tsToon.getCombineAlphaSource2(),
              tsToon.getCombineAlphaOperand2(),
              tsToon.getMode()
              ))
            if calc_mode == 0: # *
              color = VBase4(toon_texture_factor.r*strength/5, toon_texture_factor.g*strength/5, toon_texture_factor.b*strength/5, toon_texture_factor.a*strength/5)
              tsToon.setColor(color)
              tsToon.setCombineRgb(TextureStage.CMModulate, TextureStage.CSTexture, TextureStage.COSrcColor, TextureStage.CSPrevious, TextureStage.COSrcColor)
              tsToon.setCombineAlpha(TextureStage.CMModulate, TextureStage.CSTexture, TextureStage.COSrcAlpha, TextureStage.CSPrevious, TextureStage.COSrcAlpha)
            elif calc_mode == 1: # +
              color = VBase4(toon_texture_factor.r*strength/5, toon_texture_factor.g*strength/5, toon_texture_factor.b*strength/5, toon_texture_factor.a*strength/5)
              tsToon.setColor(color)
              print(color)
              tsToon.setCombineRgb(TextureStage.CMSubtract, TextureStage.CSPrevious, TextureStage.COSrcColor, TextureStage.CSConstant, TextureStage.COSrcColor)
              tsToon.setCombineAlpha(TextureStage.CMSubtract, TextureStage.CSPrevious, TextureStage.COSrcAlpha, TextureStage.CSConstant, TextureStage.COSrcAlpha)
          else:
            cMode = np.getPythonTag('toon_combine_mode')
            print(cMode)
            # tsToon.setCombineRgb(cMode[0], cMode[1], cMode[2], cMode[3], cMode[4], cMode[5], cMode[6])
            # tsToon.setCombineAlpha(cMode[7], cMode[8], cMode[9], cMode[10], cMode[11], cMode[12], cMode[13])
            tsToon.setMode(cMode[14])
          pass
        pass

      idx += 1
    pass

  @staticmethod
  def setExpression(model, expression, morphOn=True, strength=1.0, default=True):
    if strength < 0: strength = 0.0;
    if strength > 1: strength = 1.0;
    strength = 0.95
    morph = model.find('**/Morphs*')
    if len(expression)==0 or expression.lower()=='default':
      for item in morph.getChildren():
        if item.getPythonTag('show'):
          Utils.morphVertex(model, item, morphOn=False, strength=strength)
          item.setPythonTag('show', False)
    else:
      for item in morph.getChildren():
        if len(expression)==0 or expression.lower()=='default':
          Utils.morphVertex(model, item, morphOn=False, strength=strength)
          item.setPythonTag('show', False)
          continue
        if item.getName() == expression:
          log(u'===================\n%s\n===================' % expression, force=True)
          lastExpression = model.getPythonTag('lastExpression')

          morphType = item.getPythonTag('morph_type')
          morphPanel = item.getPythonTag('panel')
          print('Morph Type  : ', morphType)
          # print('Morph Panel : ', morphPanel)
          if morphType == 1:
            if lastExpression and default:
              Utils.morphVertex(model, lastExpression, morphOn=False, strength=strength)
              lastExpression.setPythonTag('show', False)

            state = False if item.getPythonTag('show') else True
            Utils.morphVertex(model, item, morphOn=state, strength=strength)
            item.setPythonTag('show', state)

            model.setPythonTag('lastExpression', item)
            # print(expression, morphOn)
          elif morphType == 8:
            state = False if item.getPythonTag('show') else True
            morphData = item.getPythonTag('morph_data')
            # Utils.morphMaterial(model, morphData, morphOn=state, strength=strength)
            # item.setPythonTag('show', state)
            item.setPythonTag('show', False)
          else:
            log('not vertex/material expression', force=True)
          break
        pass
      pass
    pass

  @staticmethod
  def getExpressionList(model):
    expressions = []
    if model:
      morph = model.find('**/Morphs*')
      if morph:
        for item in morph.getChildren():
          expression_name = item.getName()
          if item.getPythonTag('show'):
            expression_state = True
          else:
            expression_state = False
          expressions.append({'name':expression_name, 'state':expression_state})

    return(expressions)

  @staticmethod
  def snapshot(snapfile='snap_00.png'):
    result = False
    lastModel = render.getPythonTag('lastModel')
    if lastModel:
      GUI = render2d.find('**/aspect2d/*')
      GUI.hide()
      path = lastModel.node().getPythonTag('path')
      fn = os.path.splitext(os.path.basename(path))
      folder = os.path.dirname(path)
      snapfile = os.path.join(folder, u'snap_%s.png' % (fn[0]))
      base.graphicsEngine.renderFrame()
      result = base.screenshot(namePrefix=snapfile, defaultFilename=0, source=None, imageComment=fn[0])
      GUI.show()
    return(result)
    pass

  @staticmethod
  def menuAxisSel(arg):
    if arg in [u'X轴线', u'Y轴线', u'Z轴线', u'XY平面', u'YZ平面', u'XZ平面']:
      if   arg == u'X轴线':
        axis = render.find('**/AXISLINE/X*')
      elif arg == u'Y轴线':
        axis = render.find('**/AXISLINE/Y*')
      elif arg == u'Z轴线':
        axis = render.find('**/AXISLINE/Z*')
      elif arg == u'XY平面':
        axis = render.find('**/PLANEGRID/XY*')
      elif arg == u'YZ平面':
        axis = render.find('**/PLANEGRID/YZ*')
      elif arg == u'XZ平面':
        axis = render.find('**/PLANEGRID/XZ*')

      if axis.isHidden():
        axis.show()
      else:
        axis.hide()
    else:
      pass

  @staticmethod
  def menuMorphSel(arg):
    lastModel = render.getPythonTag('lastModel')
    if lastModel:
      Utils.setExpression(lastModel, arg, default=False)

  @staticmethod
  def setUI(render):
    UI = NodePath('GUI')

    # btnReset = DirectButton(pos=(480,480), text=u'RESET', text_pos=(10,10), frameSize=(460, 460, 80, 80))
    btnSnapshot = DirectButton(text=u'截屏', scale=.05, pos=(-0.935, -10, 0.938), command=Utils.snapshot)
    btnSnapshot.setName('btnSnapShot')
    btnSnapshot.reparentTo(UI)

    btnAxisReset = DirectButton(text=u'复位', scale=.05, pos=(-0.935, -10, 0.852), command=Stage.resetCamera)
    btnAxisReset.setName('btnAxisReset')
    btnAxisReset.reparentTo(UI)

    menuAxisSelect = DirectOptionMenu(text="网格", scale=0.05, pos=(-0.985, -10, -0.980),
      items=[u'Z轴线', u'X轴线', u'Y轴线', u'XY平面', u'YZ平面', u'XZ平面'],
      initialitem=0, highlightColor=(0.65,0.65,0.65,1), command=Utils.menuAxisSel)
    menuAxisSelect.setName('menuAxisSelect')
    menuAxisSelect.reparentTo(UI)

    morphItems = []
    morph = render.find('**/Morphs*')
    if morph:
      for item in morph.getChildren():
        morphItems.append(item.getName())
    if len(morphItems)>0:
      menuMorphs = DirectOptionMenu(text="表情", scale=0.035, pos=(-0.770, -10, -0.980),
        items=morphItems,
        initialitem=0, highlightColor=(0.65,0.65,0.65,1), command=Utils.menuMorphSel)

      menuMorphs.setName('menuMorphSelect')
      menuMorphs.reparentTo(UI)

    UI.reparentTo(aspect2d)
    return(UI)


class MmdViewerApp(ShowBase):
  wp = None
  modelidx = 0
  appConfig = dict()

  def __init__(self):
    self.loadConfig()

    self.base = ShowBase.__init__(self, fStartDirect=False, windowType=None)

    base.openMainWindow(type='onscreen')

    self.setupGL()

    self.setupWorld()

    pass

  def OnResize(self, event=None):
    if self.wp:
      w, h = self.frame.panda.GetSize()
      self.wp.setSize(w, h)
      base.win.requestProperties(self.wp)
      base.messenger.send(base.win.getWindowEvent(), [base.win])
    pass

  def OnClose(self, event=None):
    self.onDestroy(event)
    try:
      self.saveConfig()
      base
    except NameError:
      self.saveConfig()
      sys.exit()
    base.userExit()
    pass

  def OnCloseWindow(self, event=None):
    self.saveConfig()
    pass

  def loadConfig(self):
    fn = os.path.splitext(__file__)
    fn = os.path.join(CWD, fn[0]+'.config')
    print('--> Reading config from %s ...' % fn)
    if os.path.isfile(fn):
      with codecs.open(fn, 'r', encoding='utf8') as f:
        try:
          self.appConfig = json.load(f, encoding='utf8')
        except:
          pass

    if not 'recent' in self.appConfig:
      self.appConfig['recent'] = []

    if not 'hana2eng' in self.appConfig:
      self.appConfig['hana2eng'] = loadJ2ETable(u'和英変換.txt')
      # print(self.appConfig['hana2eng'])
    pass

  def saveConfig(self):
    fn = os.path.splitext(__file__)
    fn = os.path.join(CWD, fn[0]+'.config')
    print('--> Writing config to %s ...' % fn)

    self.appConfig['lastModel'] = self.appConfig['lastModel'].replace('\\', '/')
    self.appConfig['recent'] = self.appConfig['recent'][:10]
    for idx in range(len(self.appConfig['recent'])):
      self.appConfig['recent'][idx] = self.appConfig['recent'][idx].replace('\\', '/')

    with codecs.open(fn, 'w', encoding='utf8') as f:
      json.dump(self.appConfig, f, indent=2, encoding='utf8', ensure_ascii=False)

    pass

  def setupGL(self):
    FPS = 60
    self.globalClock = ClockObject.getGlobalClock()
    self.globalClock.setMode(ClockObject.MLimited)
    self.globalClock.setFrameRate(FPS)
    globalClock.setFrameTime(globalClock.getRealTime())

    base.setSleep(.01)
    # base.setFrameRateMeter(True)

    base.camLens.setNearFar(0.1, 550.0)
    base.camLens.setFov(45.0)
    base.camLens.setFocalLength(50)

    Stage.setAxis(render)

    self.lights = Stage.setStudioLight(render)
    Stage.lightAtNode(lights=Stage.lights)

    Stage.resetCamera()

    render.setAntialias(AntialiasAttrib.MAuto)

    fov = base.camLens.getFov()
    render.setPythonTag('lensFov', LVecBase2f(fov.getX(), fov.getY()))

    #
    # setup object picker
    #
    # Create a traverser that Panda3D will automatically use every frame.
    base.cTrav = CollisionTraverser()
    # base.cTrav.showCollisions(render)
    # Create a handler for the events.
    self.collHandler = CollisionHandlerQueue()

    self.pickerNode = CollisionNode('mouseRay')
    self.pickerNP = camera.attachNewNode(self.pickerNode)
    self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
    self.pickerRay = CollisionRay()
    self.pickerNode.addSolid(self.pickerRay)
    self.cTrav.addCollider(self.pickerNP, self.collHandler)
    self.lastPickedObj = None

    #
    # input accept
    self.do = DirectObject()
    self.do.accept('f1', self.toggleDebug)
    self.do.accept('f2', self.toggleModel)
    self.do.accept('f3', base.toggleWireframe)
    self.do.accept('f4', base.toggleTexture)
    self.do.accept('f5', self.toggleBone)

    self.accept('mouse1', self.OnMouseLeftClick)
    print('click event')

  def setupWorld(self):
    # Task
    taskMgr.add(self.updateWorld, 'updateWorld')

    # World
    self.worldNP = render.attachNewNode('World')

    self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
    # self.debugNP.show()
    self.debugNP.node().showWireframe(True)
    self.debugNP.node().showConstraints(False)
    self.debugNP.node().showBoundingBoxes(False)
    self.debugNP.node().showNormals(False)

    self.world = BulletWorld()
    self.world.setGravity(Vec3(0, 0, -9.81))
    self.world.setDebugNode(self.debugNP.node())

    # Ground (static)
    shape = BulletPlaneShape(Vec3(0, 0, 1), 1)

    self.groundNP = self.worldNP.attachNewNode(BulletRigidBodyNode('Ground'))
    self.groundNP.node().addShape(shape)
    self.groundNP.setPos(0, 0, -1)
    self.groundNP.setCollideMask(BitMask32.allOn())

    self.world.attachRigidBody(self.groundNP.node())

    self.FirstUpdateWorld = False
    self.UpdateCount = 0
    # self.worldNP.flattenStrong()
    print('World Setup')
    # render.ls()
    pass

  def toggleDebug(self):
    if self.debugNP.isHidden():
      self.debugNP.show()
      print('--> Bullet Debug On')
    else:
      self.debugNP.hide()
      print('--> Bullet Debug Off')
      print(self.UpdateCount)

  def updateWorld(self, task):
    dt = globalClock.getDt()

    # self.processInput(dt)
    self.world.doPhysics(dt)
    if not self.FirstUpdateWorld or self.UpdateCount<100:
      # self.world.doPhysics(dt, 1, 3.0/180.0)
      self.FirstUpdateWorld = True
      self.UpdateCount += 1

    return task.cont

  def toggleModel(self):
    lastModel = render.getPythonTag('lastModel')
    if lastModel:
      if lastModel.isHidden():
        lastModel.show()
      else:
        lastModel.hide()
    pass

  def toggleBone(self):
    print('nonbone')
    lastModel = render.getPythonTag('lastModel')
    if lastModel:
      bones = lastModel.findAllMatches('**/Bones')
      for bone in bones:
        if bone.isHidden():
          bone.show()
        else:
          bone.hide()
    pass

  def OnMouseLeftClick(self):
    if not base.mouseWatcherNode.hasMouse():
      return
    if self.lastPickedObj:
      self.lastPickedObj.clearRenderMode()

    mpos = base.mouseWatcherNode.getMouse()
    self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())

    base.cTrav.traverse(render)
    # Assume for simplicity's sake that myHandler is a CollisionHandlerQueue.
    print(self.collHandler.getNumEntries())
    if self.collHandler.getNumEntries() > 0:
      # for entry in self.collHandler.getEntries():
      #   log(str(entry.getInto()), force=True)

      # This is so we get the closest object.
      self.collHandler.sortEntries()
      pickedObj = self.collHandler.getEntry(0).getIntoNodePath()
      pickedObj = pickedObj.findNetPythonTag('pickableObjTag')
      if not pickedObj.isEmpty():
        # pickedObj.showTightBounds()
        pickedObj.setRenderModeWireframe()
        self.lastPickedObj = pickedObj
        # handlePickedObject(pickedObj)
        log('Selected: %s' % pickedObj.getName(), force=True)
    pass

  def loadModel(self, modelname=None):
    p3dnode = None
    if modelname == None:
      modelname = 'panda'

    lastModel = render.getPythonTag('lastModel')
    if lastModel:
      node = lastModel.find('**/+ModelRoot')
      if node:
        loader.unloadModel(node)
      else:
        loader.unloadModel(lastModel)
      lastModel.removeNode()
      render.setPythonTag('lastModel', None)
      for rigid in self.world.getRigidBodies():
        self.world.remove(rigid)
      for cs in self.world.getConstraints():
        self.world.remove(cs)


    modelname = os.path.relpath(modelname, CWD).replace('\\', '/')
    ext = os.path.splitext(modelname)[1].lower()
    if ext in ['.pmx']:
      p3dnode = loadPmxModel(modelname)
    elif ext in ['.pmd']:
      p3dnode = loadPmdModel(modelname)
    else:
      p3dnode = loader.loadModel(Filename.fromOsSpecific(modelname))

    if p3dnode:
      p3dnode.reparentTo(render)
      # Stage.lightAtNode(p3dnode, lights=Stage.lights)
      Stage.resetCamera(model=p3dnode)
      render.setPythonTag('lastModel', p3dnode)

      # p3dnode.hide()

      #
      # Bullet Test
      #
      bulletBody = p3dnode.find('**/Bullet')
      if bulletBody:
        for np in bulletBody.getChildren():
          node = np.node()
          if isinstance(node, BulletRigidBodyNode):
            self.worldNP.attachNewNode(node)
            self.world.attachRigidBody(node)
        for cs in bulletBody.getPythonTag('Joints'):
          self.world.attachConstraint(cs)

      # p3dnode.writeBamFile('lastModel.bam')
      # print(p3dnode.hasMaterial())
      # p3dnode.setMaterialOff()
      # print(p3dnode.hasMaterial())

      #
      # Update config setting
      #
      self.appConfig['lastModel'] = modelname
      count = len(self.appConfig['recent'])
      if modelname in self.appConfig['recent']:
        self.appConfig['recent'].remove(modelname)
      self.appConfig['recent'].insert(0, modelname)

      # base.wireframeOn()
      # base.textureOff()
    return(p3dnode)
    pass

  def OnOpenFileTest(self, event):
    # p3dnode = self.loadModel('models/meiko/meiko.pmx')
    modellist = [u'./models/meiko/meiko.pmx', u'panda', u'./models/apimiku/Miku long hair.pmx']
    # modellist = [u'./models/meiko.pmx']
    # p3dnode = self.loadModel(modellist[self.modelidx % 3])
    p3dnode = self.loadModel(modellist[0])
    self.modelidx += 1

    # p3dnode = self.loadModel('panda')

    # print(type(p3dnode))
    # print(p3dnode.ls())

  def OnOpenFile(self, event):
    lastFolder = CWD
    lastModel = render.getPythonTag('lastModel')
    if lastModel:
      try:
        lastFolder = os.path.dirname(lastModel.getPythonTag('path'))
      except:
        pass
    elif 'lastModel' in self.appConfig['lastModel']:
      lastFolder = os.path.dirname(self.appConfig['lastModel'])
    else:
      lastFolder = CWD

    # print(lastFolder)
    wildcard = "MMD PMX Model (*.pmx)|*.pmx|"    \
               "MMD PMD Model (*.pmd)|*.pmd|"    \
               "MMD VMD Model (*.vmd)|*.vmd|"    \
               "Panda3D Egg file (*.egg)|*.egg|" \
               "Panda3D bam file (*.bam)|*.bam|" \
               "All Supported files (*.pmx;*.pmd;*.egg;*.bam*)|*.pmx;*.pmd;*.egg;*.bam|" \
               "All files (*.*)|*.*"

    dlgOpen = wx.FileDialog(
            self.frame, message=_("Choose a file"),
            defaultDir=lastFolder,
            defaultFile="",
            wildcard=wildcard,
            # style=wx.OPEN | wx.CHANGE_DIR
            style=wx.OPEN | wx.FILE_MUST_EXIST
            )

    if dlgOpen.ShowModal() == wx.ID_OK:
      modelFile = dlgOpen.GetPath()
      self.loadModel(modelFile)
    pass

  def OnResetCamera(self, event):
    model = render.getPythonTag('lastModel')
    Stage.resetCamera(model=model)

  def OnSnapshot(self, event):
    lastModel = render.getPythonTag('lastModel')
    if lastModel:
      path = lastModel.node().getPythonTag('path')
      if path:
        fn = os.path.splitext(os.path.basename(path))
        folder = os.path.dirname(path)
        snapfile = os.path.join(folder, u'snap_%s.png' % (fn[0]))
      else:
        snapfile = os.path.join(CWD, 'snap_%s.png' % lastModel.getName())
    else:
      snapfile = os.path.join(CWD, 'snap.png')
    snapfile = Filename.fromOsSpecific(snapfile)
    # print(Filename.makeTrueCase(snapfile))
    Filename.makeCanonical(snapfile)
    axis = render.find('**/threeaxisgrid*')
    axis.hide()
    base.graphicsEngine.renderFrame()
    source = base.camera.getChild(0).node().getDisplayRegion(0)
    result = base.screenshot(namePrefix=snapfile, defaultFilename=0, source=None, imageComment='')
    axis.show()
    base.graphicsEngine.renderFrame()
    pass

  def GetAxisById(self, id):
    axis = None
    if   id in [20000, -31991]:
      axis = render.find('**/AXISLINE/X*')
    elif id in [20001, -31990]:
      axis = render.find('**/AXISLINE/Y*')
    elif id in [20002, -31989]:
      axis = render.find('**/AXISLINE/Z*')
    elif id in [20004, -31988]:
      axis = render.find('**/PLANEGRID/XY*')
    elif id in [20005, -31987]:
      axis = render.find('**/PLANEGRID/YZ*')
    elif id in [20006, -31986]:
      axis = render.find('**/PLANEGRID/XZ*')
    elif id in [20008, -31985]:
      axis = render.findAllMatches('**/**/PLANEGRID/*/SUBDIV')
      # axis = render.find('**/**/PLANEGRID/*/SUBDIV')
    return(axis)

  def RefreshMenuState(self, menu):
    #
    # update Axis Grid Plane menu
    #
    idlist_plane = [20000, 20001, 20002, 20003, 20004, 20005, 20006, 20007, 20008,
                    -31991, -31990, -31989, -31988, -31987, -31986, -31985]
    for mId in idlist_plane:
      axis = self.GetAxisById(mId)
      if axis and isinstance(menu, wx.Menu):
        for item in menu.GetMenuItems():
          if item.GetId() == mId and item.IsCheckable():
            if isinstance(axis, NodePathCollection):
              checked  = item.IsChecked()
              for ax in axis:
                checked = not ax.isHidden()
                break
              item.Check(checked)
            else:
              item.Check(not axis.isHidden())
            break
          pass
        pass
      pass
    pass

    #
    # Update expressions menu
    #
    idlist_expression = [30000, 31000]
    model = render.getPythonTag('lastModel')
    if model:
      expressionList = Utils.getExpressionList(model)
      for item in menu.GetMenuItems():
        text = item.GetText()
        for expression in expressionList:
          if text == expression['name']:
            item.Check(expression['state'])
            break
        pass
      pass
    pass

    #
    # Update Recent Files menu
    #
    idlist_expression = [21000, 21100]
    if self.menuRecentFiles:
      for item in self.menuRecentFiles.GetMenuItems():
        self.menuRecentFiles.Delete(item.GetId())
        item.Destroy()
    if self.frame.menuMRU:
      for item in self.frame.menuMRU.GetMenuItems():
        self.frame.menuMRU.Delete(item.GetId())
        item.Destroy()
    idx = 1
    for recent in self.appConfig['recent']:
      text = os.path.basename(recent)
      help = recent
      mItem = self.menuRecentFiles.Append(ID_RECENTFILES+idx, text, help)
      mruItem = self.frame.menuMRU.Append(ID_RECENTFILES+idx, text, help)
      self.frame.Bind(wx.EVT_MENU, self.OnRecentFilesItemSelected, id=mItem.GetId())
      self.frame.Bind(wx.EVT_MENU, self.OnRecentFilesItemSelected, id=mruItem.GetId())
      idx += 1

    pass

  def OnMenuPopup(self, event):
    menu = event.GetEventObject()
    self.RefreshMenuState(menu)

  def OnPlanePopupItemSelected(self, event):
    arg = event.GetId()
    menu = event.GetEventObject()
    if isinstance(menu, wx.Menu):
      axis = self.GetAxisById(arg)
      if axis:
        if isinstance(axis, NodePathCollection):
          if menu.IsChecked(arg):
            for ax in axis:
              ax.show()
          else:
            for ax in axis:
              ax.hide()
        else:
          if axis.isHidden():
            axis.show()
          else:
            axis.hide()

        self.RefreshMenuState(menu)
      else:
        pass
      pass
    pass

  def OnRecentFilesItemSelected(self, event):
    menu = event.GetEventObject()
    if isinstance(menu, wx.Menu):
      for item in menu.GetMenuItems():
        if item.GetId() == event.GetId():
          modelname = item.GetText()
          modelpath = item.GetHelp()
          p3dnode = self.loadModel(modelpath)
          break
    else:
      self.OnOpenFile(event)
      # print('button clicked')
      # p3dnode = self.loadModel('panda')
    pass

  def OnExpressionSeleced(self, event):
    menu = event.GetEventObject()
    if isinstance(menu, wx.Menu):
      for item in menu.GetMenuItems():
        if item.GetId() == event.GetId():
          Utils.setExpression(render.getPythonTag('lastModel'), item.GetText(), default=False)
          break
    else:
      Utils.setExpression(render.getPythonTag('lastModel'), 'default', default=False)
    pass

  pass


def myWink(value, model, delay):
  if value >= delay:
    setExpression(model, u'まばたき',  morphOn=True)
    base.graphicsEngine.renderFrame()
    Wait(.5)
    setExpression(model, u'びっくり',  morphOn=True)
    base.graphicsEngine.renderFrame()
  # Wait(delay)
  return(True)

if __name__ == '__main__':
  app = MmdViewerApp()

  # mmdFile = u'./models/apimiku/Miku long hair.pmx'
  # mmdFile = u'./models/cupidmiku/Cupid Miku.pmx'
  # mmdFile = u'./models/meiko/meiko.pmx'
  mmdFile = "models/MEIKO.pmx"

  if len(sys.argv) > 1:
    if len(sys.argv[1]) > 0:
      mmdFile = sys.argv[1]

  app.loadModel(mmdFile)

  # Shader.load(Shader.SLGLSL, './shader_v.sha', './shader_f.sha' )
  # render.setShader(Shader.load("inkGen.sha"))
  # render.setShaderAuto()

  filters = CommonFilters(base.win, base.cam)
  # v1.8.1 supported
  # filters.setAmbientOcclusion()
  # filters.setBloom()
  # filters.setBlurSharpen(0.3)
  # filters.setCartoonInk()
  # filters.setHalfPixelShift()
  # filters.setInverted()
  # filters.setViewGlow()
  # filters.setVolumetricLighting()


  Utils.setUI(render)

  # render.setAntialias(AntialiasAttrib.MMultisample, 8)
  render.setAntialias(AntialiasAttrib.MAuto)

  app.run()
