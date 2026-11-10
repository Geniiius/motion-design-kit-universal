"""Procedural 3D mascot (Blender 4+): demo rig, idle, gestures, illustrative mouth loop.
Run: blender -b --python mascot_blender.py -- --output /tmp/mascot.mp4 --duration 5
Voice-over needs external muxing. Loop is NOT phoneme/viseme lip sync.
"""
import argparse
import math
import sys
try:
    import bpy
    from mathutils import Vector
except ImportError as exc:
    raise SystemExit('Ce script fonctionne uniquement dans Blender (bpy requis).') from exc

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
p.add_argument('--duration', type=float, default=6)
a = p.parse_args(argv)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.fps = 25
scene.frame_end = int(a.duration * 25)
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
settings = scene.render.image_settings
if hasattr(settings, 'media_type'):  # Blender 5: a video is chosen by its media type first
    settings.media_type = 'VIDEO'
settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = a.output
scene.world.color = (0.07, 0.08, 0.16)
background = scene.world.node_tree.nodes.get('Background') if getattr(scene.world, 'node_tree', None) else None
if background:  # with nodes, the sky colour lives in the Background node: without this it stays grey
    background.inputs[0].default_value = (0.07, 0.08, 0.16, 1)


def mat(name, col, metallic=0, roughness=.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*col, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*col, 1)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return m

purple = mat('Branded purple',(.28,.16,.75),.18)
lavender = mat('Face',(.69,.57,.98),.06)
white = mat('Eye white',(.96,.95,.98))
black = mat('Pupil',(.045,.05,.09))
blue = mat('Backdrop',(.028,.044,.099))
groundmat = mat('Floor',(.075,.1,.16))


def blob(name, location, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj

body=blob('Torso',(0,0,1.2),(.65,.39,.82),purple)
head=blob('Head',(0,-.07,2.33),(.83,.73,.72),lavender)
left=blob('Left arm',(-.8,0,1.33),(.26,.27,.62),lavender)
right=blob('Right arm',(.8,0,1.33),(.26,.27,.62),lavender)
blob('Eye L',(-.29,-.70,2.54),(.18,.085,.17),white)
blob('Eye R',(.29,-.70,2.54),(.18,.085,.17),white)
blob('Pupil L',(-.29,-.778,2.54),(.085,.038,.095),black)
blob('Pupil R',(.29,-.778,2.54),(.085,.038,.095),black)
mouth=blob('Mouth (illustrative)',(0,-.777,2.15),(.20,.04,.04),black)
blob('Foot L',(-.3,-.08,.38),(.26,.4,.18),purple)
blob('Foot R',(.3,-.08,.38),(.26,.4,.18),purple)

bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,.01))
bpy.context.object.data.materials.append(groundmat)

for frame in range(1,scene.frame_end+1,5):
    t=frame/25
    body.location.z=1.2+.035*math.sin(t*2.6)
    body.keyframe_insert(data_path='location',frame=frame)
    head.rotation_euler[2]=.09*math.sin(t*1.7)
    head.keyframe_insert(data_path='rotation_euler',frame=frame)
    left.rotation_euler[1]=.13*math.sin(t*3)
    right.rotation_euler[1]=-.34+.24*math.sin(t*2.8)
    left.keyframe_insert(data_path='rotation_euler',frame=frame)
    right.keyframe_insert(data_path='rotation_euler',frame=frame)
    mouth.scale.z=.04 + (.10 if math.sin(t*13)>0 else .025)
    mouth.keyframe_insert(data_path='scale',frame=frame)


def point(obj,where):
    obj.rotation_euler=(Vector(where)-obj.location).to_track_quat('-Z','Y').to_euler()

bpy.ops.object.camera_add(location=(0,-7.3,3.4))
scene.camera=bpy.context.object
point(scene.camera,(0,0,1.7))
scene.camera.data.type='PERSP'
scene.camera.data.lens=36
for name,where,power,size in [('Key',(-3,-4,6),850,4),('Fill',(3,-3,4),450,3),('Rim',(1,2,5),650,3)]:
    bpy.ops.object.light_add(type='AREA',location=where)
    obj=bpy.context.object
    obj.name=name
    obj.data.energy=power
    obj.data.shape='DISK'
    obj.data.size=size
    point(obj,(0,0,1.7))
try:scene.render.engine='BLENDER_EEVEE_NEXT'
except (TypeError,ValueError):scene.render.engine='BLENDER_EEVEE'
scene.view_settings.view_transform='Standard'
bpy.ops.render.render(animation=True)
