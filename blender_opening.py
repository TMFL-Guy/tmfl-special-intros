import bpy, math, random
from mathutils import Vector
random.seed(7)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.fps=24;scene.frame_end=240
scene.world.color=(.008,.013,.03)
def mat(name,color,metal=0,rough=.8,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m
turf=mat('wet midnight turf',(.012,.028,.035));white=mat('field paint',(.42,.5,.55));stands=mat('dark steel',(.018,.025,.04),.5)
def cube(name,loc,scale,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);return o
cube('field',(0,0,-.12),(70,115,.2),turf)
for x in range(-30,31,10):cube('yard stripe',(x,0,.01),(.13,110,.015),white)
for y in range(-50,51,10):cube('cross stripe',(0,y,.01),(64,.13,.015),white)
for side in [-1,1]:
 for row in range(9):
  cube('stadium seating',((37+row*2)*side,0,1+row*1.2),(2,130,1),stands)
 for y in [-40,40]:
  pole=cube('floodlight tower',((48)*side,y,16),(.7,.7,32),stands)
  panel=cube('light array',(48*side,y,32),(1,13,5),mat('floodlight glass',(.8,.9,1),emit=2))
  for f,value in [(1,1700),(60,1700),(73,120),(79,1700),(142,1700),(154,60),(164,1700),(220,1700)]:
   panel.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=2
  light=bpy.data.lights.new('flickering floodlights','AREA');light.energy=1600;light.shape='RECTANGLE';light.size=12;light.size_y=5
  ob=bpy.data.objects.new('animated floodlight',light);scene.collection.objects.link(ob);ob.location=(side*46,y,29)
  for frame,power in [(1,1800),(75,1800),(80,80),(84,1700),(87,120),(91,1800),(158,1800),(162,100),(169,1800),(240,1800)]:
   light.energy=power;light.keyframe_insert(data_path='energy',frame=frame)
# rolling translucent fog volumes represented by softly shaded layered meshes
mist=mat('moonlit fog',(.16,.22,.31))
for i in range(28):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(random.uniform(-34,34),random.uniform(-52,52),random.uniform(.4,2)))
 o=bpy.context.object;o.name='moving ground fog';o.scale=(random.uniform(5,13),random.uniform(3,8),random.uniform(.2,.6));o.data.materials.append(mist)
 o.hide_render=True # keep scene clean until volumetric assets are added
# camera tracking slowly over field
bpy.ops.object.camera_add(location=(0,-58,7));cam=bpy.context.object
def aim(o,pt):o.rotation_euler=(Vector(pt)-o.location).to_track_quat('-Z','Y').to_euler()
aim(cam,(0,15,1));scene.camera=cam
for frame,y,z in [(1,-58,7),(240,-45,5.8)]:
 cam.location=(0,y,z);aim(cam,(0,15,1));cam.keyframe_insert(data_path='location',frame=frame);cam.keyframe_insert(data_path='rotation_euler',frame=frame)
# cold moon light and lightning pulse
sun=bpy.data.lights.new('moonlight','SUN');sun.energy=.65;sun.color=(.48,.66,1)
o=bpy.data.objects.new('moon',sun);scene.collection.objects.link(o);o.rotation_euler=(.35,-.4,.2)
bolt=bpy.data.lights.new('lightning','AREA');bolt.energy=0;bolt.color=(.55,.72,1);bolt.size=40
o=bpy.data.objects.new('lightning flash',bolt);scene.collection.objects.link(o);o.location=(0,5,35)
for f,v in [(1,0),(217,0),(220,6000),(222,0),(226,9000),(229,0),(240,0)]:bolt.energy=v;bolt.keyframe_insert(data_path='energy',frame=f)
scene.render.image_settings.file_format='FFMPEG';scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.filepath='/tmp/halloween-opening.mp4'
bpy.ops.render.render(animation=True)
