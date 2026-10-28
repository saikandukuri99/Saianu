"""
Cinematic 3D "money mindset" scene for Blender (4.2+ / 5.x), written with the bpy API.

What it builds
  * procedural gradient world + light volumetric fog
  * glossy reflective floor, gold coin tower, glass cards, glowing idea bulb, neon ring
  * 3-point lighting (warm key, gold rim, cyan fill) + a volumetric spot cone
  * an animated camera: orbit along a Bezier path + dolly + rack-focus depth of field + subtle handheld noise
  * compositor: bloom/glare, chromatic aberration, vignette, film grain, colour grade
  * H.264 output

Run (headless):
    blender -b -P cinematic_money_scene.py -- --engine CYCLES --samples 48 --frames 180 --out ./render/money.mp4
    blender -b -P cinematic_money_scene.py -- --engine EEVEE --samples 64 --still 90 --out ./render/frame.png     # needs a GPU / OpenGL

Run (interactive): open Blender > Scripting > paste this file > Run Script. Use the viewport camera view (numpad 0).

Notes
  * Telugu text: Blender's text object does not do Indic shaping, so conjuncts render wrongly. Render Telugu titles
    to a transparent PNG (any browser/Pillow) and use `add_title_plane()` below, or overlay them in your editor.
  * CYCLES works on CPU only machines; EEVEE needs OpenGL.
"""
import math
import random
import sys

import bpy
import mathutils

# ----------------------------------------------------------------------------- args
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def arg(name, default, cast=str):
    if name in argv:
        return cast(argv[argv.index(name) + 1])
    return default


ENGINE = arg('--engine', 'CYCLES').upper()
SAMPLES = arg('--samples', 48, int)
FRAMES = arg('--frames', 180, int)
STILL = arg('--still', 0, int)          # render only this frame as a PNG if > 0
OUT = arg('--out', '//render/money.mp4')
TITLE_PNG = arg('--title', '')           # optional transparent PNG (e.g. Telugu title) shown as a floating plane
SCALE = arg('--scale', 100, int)
RES_X, RES_Y, FPS = 1920, 1080, 30

random.seed(7)
scene = bpy.context.scene


# ----------------------------------------------------------------------------- helpers
def clean():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.curves, bpy.data.images):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def socket(node, *names):
    """Blender renamed some Principled inputs between versions; return the first that exists."""
    for n in names:
        if n in node.inputs:
            return node.inputs[n]
    raise KeyError(names)


def principled(name, color, metallic=0.0, roughness=0.3, coat=0.0, emission=None, emission_strength=0.0,
               transmission=0.0, ior=1.45, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    socket(bsdf, 'Base Color').default_value = (*color, 1)
    socket(bsdf, 'Metallic').default_value = metallic
    socket(bsdf, 'Roughness').default_value = roughness
    socket(bsdf, 'Coat Weight', 'Clearcoat').default_value = coat
    socket(bsdf, 'IOR').default_value = ior
    socket(bsdf, 'Alpha').default_value = alpha
    try:
        socket(bsdf, 'Transmission Weight', 'Transmission').default_value = transmission
    except KeyError:
        pass
    if emission:
        socket(bsdf, 'Emission Color', 'Emission').default_value = (*emission, 1)
        socket(bsdf, 'Emission Strength').default_value = emission_strength
    if alpha < 1:
        m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else m.blend_method
    return m


def bevel(obj, width=0.02, segments=3):
    mod = obj.modifiers.new('Bevel', 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    return mod


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True


def fcurves(idblock):
    """All F-curves of a datablock; works with the layered actions of Blender 5.x and the classic ones before."""
    ad = idblock.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, 'fcurves'):
        return list(act.fcurves)
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                out += list(cb.fcurves)
    return out


def set_ease(obj, interpolation='BEZIER'):
    """Ease in/out (or LINEAR) on every keyframe of a datablock's action."""
    for fc in fcurves(obj):
        for k in fc.keyframe_points:
            k.interpolation = interpolation
            if interpolation == 'BEZIER':
                k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'


def keyframe(obj, frame, **props):
    for path, value in props.items():
        setattr(obj, path, value)
        obj.keyframe_insert(data_path=path, frame=frame)


# ----------------------------------------------------------------------------- scene setup
clean()
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = RES_X, RES_Y, SCALE
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, FRAMES
scene.view_settings.view_transform = 'AgX' if 'AgX' in [v.identifier for v in scene.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
scene.view_settings.look = 'None'

if ENGINE.startswith('EEVEE'):
    ids = [e.identifier for e in scene.render.bl_rna.properties['engine'].enum_items]
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in ids else ('BLENDER_EEVEE' if 'BLENDER_EEVEE' in ids else ids[0])
    if hasattr(scene.eevee, 'taa_render_samples'):
        scene.eevee.taa_render_samples = SAMPLES
    for attr in ('use_raytracing', 'use_gtao'):
        if hasattr(scene.eevee, attr):
            setattr(scene.eevee, attr, True)
else:
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    scene.cycles.device = 'CPU'
    scene.cycles.max_bounces = 6
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False

# ----------------------------------------------------------------------------- world: gradient sky + fog
world = bpy.data.worlds.new('World')
scene.world = world
world.use_nodes = True
wn = world.node_tree.nodes
wl = world.node_tree.links
wn.clear()
tex = wn.new('ShaderNodeTexCoord')
sep = wn.new('ShaderNodeSeparateXYZ')
ramp = wn.new('ShaderNodeValToRGB')
bg = wn.new('ShaderNodeBackground')
out = wn.new('ShaderNodeOutputWorld')
wl.new(tex.outputs['Generated'], sep.inputs['Vector'])
wl.new(sep.outputs['Z'], ramp.inputs['Fac'])
ramp.color_ramp.elements[0].position = 0.35
ramp.color_ramp.elements[0].color = (0.010, 0.012, 0.06, 1)
ramp.color_ramp.elements[1].position = 0.75
ramp.color_ramp.elements[1].color = (0.11, 0.05, 0.32, 1)
mid = ramp.color_ramp.elements.new(0.55)
mid.color = (0.03, 0.02, 0.15, 1)
bg.inputs['Strength'].default_value = 0.55
wl.new(ramp.outputs['Color'], bg.inputs['Color'])
wl.new(bg.outputs['Background'], out.inputs['Surface'])

# a thin volume gives the light cones something to catch
bpy.ops.mesh.primitive_cube_add(size=60, location=(0, 0, 8))
fog = bpy.context.active_object
fog.name = 'FogVolume'
fog.display_type = 'WIRE'
fog.hide_render = False
mfog = bpy.data.materials.new('Fog')
mfog.use_nodes = True
mfog.node_tree.nodes.clear()
vs = mfog.node_tree.nodes.new('ShaderNodeVolumeScatter')
vs.inputs['Density'].default_value = 0.0025
vs.inputs['Anisotropy'].default_value = 0.35
vo = mfog.node_tree.nodes.new('ShaderNodeOutputMaterial')
mfog.node_tree.links.new(vs.outputs['Volume'], vo.inputs['Volume'])
fog.data.materials.append(mfog)

# ----------------------------------------------------------------------------- floor (glossy, reflective)
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = 'Floor'
mf = principled('Floor', (0.02, 0.025, 0.09), metallic=0.0, roughness=0.12, coat=1.0)
floor.data.materials.append(mf)

# grid lines from a checker-free wave/brick trick: emission lines driven by a Brick Texture mortar
nt = mf.node_tree
brick = nt.nodes.new('ShaderNodeTexBrick')
brick.inputs['Scale'].default_value = 3.0
brick.inputs['Mortar Size'].default_value = 0.01
brick.inputs['Brick Width'].default_value = 1.0
brick.inputs['Row Height'].default_value = 1.0
brick.offset = 0
brick.squash = 1.0
brick.inputs['Color1'].default_value = (0, 0, 0, 1)
brick.inputs['Color2'].default_value = (0, 0, 0, 1)
brick.inputs['Mortar'].default_value = (1, 0.78, 0.34, 1)
bsdf = nt.nodes['Principled BSDF']
mul = nt.nodes.new('ShaderNodeMath')
mul.operation = 'MULTIPLY'
mul.inputs[1].default_value = 1.6
nt.links.new(brick.outputs['Fac'], mul.inputs[0])
nt.links.new(mul.outputs['Value'], socket(bsdf, 'Emission Strength'))
nt.links.new(brick.outputs['Color'], socket(bsdf, 'Emission Color', 'Emission'))

# ----------------------------------------------------------------------------- hero props
GOLD = principled('Gold', (1.0, 0.72, 0.18), metallic=1.0, roughness=0.18, coat=0.4)
GOLD_DARK = principled('GoldDark', (0.62, 0.36, 0.05), metallic=1.0, roughness=0.3)
GLASS = principled('Glass', (0.75, 0.82, 1.0), roughness=0.04, transmission=1.0, ior=1.5, coat=1.0)
NEON = principled('Neon', (0.2, 0.9, 1.0), emission=(0.2, 0.9, 1.0), emission_strength=14.0)
BULB = principled('Bulb', (1.0, 0.9, 0.5), roughness=0.05, emission=(1.0, 0.82, 0.3), emission_strength=0.0, coat=1.0)
CORAL = principled('Coral', (1.0, 0.25, 0.3), roughness=0.25, coat=0.8)


def make_coin(location, radius=0.5, tilt=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=radius * 0.16, location=location, rotation=tilt)
    c = bpy.context.active_object
    c.name = 'Coin'
    c.data.materials.append(GOLD)
    bevel(c, radius * 0.04, 3)
    smooth(c)
    # inner dished face
    bpy.ops.mesh.primitive_torus_add(major_radius=radius * 0.78, minor_radius=radius * 0.035, location=location, rotation=tilt,
                                     major_segments=64, minor_segments=12)
    t = bpy.context.active_object
    t.data.materials.append(GOLD_DARK)
    t.parent = c
    t.location = (0, 0, radius * 0.085)
    return c


# coin tower
coins = []
for i in range(14):
    c = make_coin((random.uniform(-.06, .06), random.uniform(-.06, .06), 0.12 + i * 0.085), 0.62, (0, 0, random.uniform(0, 6.28)))
    coins.append(c)
# falling coins (animated)
falling = []
for i in range(10):
    f = make_coin((random.uniform(-3, 3), random.uniform(-2, 2), 7 + random.uniform(0, 4)), 0.38, (random.uniform(0, 3), random.uniform(0, 3), 0))
    falling.append(f)
    start = 1 + i * 8
    keyframe(f, start, location=f.location.copy())
    keyframe(f, start + 40, location=(f.location.x, f.location.y, 0.25 + random.uniform(0, .1)))
    f.rotation_euler = (math.pi / 2 + random.uniform(-.3, .3), 0, random.uniform(0, 6))
    keyframe(f, start, rotation_euler=(random.uniform(0, 6), random.uniform(0, 6), 0))
    keyframe(f, start + 40, rotation_euler=(math.pi / 2 + random.uniform(-.3, .3), 0, random.uniform(0, 6)))
    set_ease(f)

# idea bulb
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.9, location=(-3.2, 0.6, 2.2))
bulb = bpy.context.active_object
bulb.name = 'Bulb'
bulb.data.materials.append(BULB)
smooth(bulb)
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.42, depth=0.7, location=(-3.2, 0.6, 1.05))
base = bpy.context.active_object
base.data.materials.append(principled('BulbBase', (0.6, 0.65, 0.78), metallic=1.0, roughness=0.3))
bulb_light = bpy.data.lights.new('BulbLight', 'POINT')
bulb_light.energy = 0
bulb_light.color = (1.0, 0.8, 0.35)
bulb_light.shadow_soft_size = 0.4
bl = bpy.data.objects.new('BulbLight', bulb_light)
bl.location = bulb.location
bpy.context.collection.objects.link(bl)
bsdf_b = BULB.node_tree.nodes['Principled BSDF']
emit = socket(bsdf_b, 'Emission Strength')
for f, v, e in ((1, 0.0, 0), (60, 0.0, 0), (80, 1.0, 700), (FRAMES, 1.0, 900)):
    emit.default_value = v * 3
    emit.keyframe_insert('default_value', frame=f)
    bulb_light.energy = e
    bulb_light.keyframe_insert('energy', frame=f)

# glass cards (floating, slow rotation)
for i, (x, y, z, ry) in enumerate(((3.4, -0.6, 1.8, 0.35), (4.6, 1.2, 2.7, -0.25), (2.6, 1.6, 1.0, 0.15))):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    card = bpy.context.active_object
    card.scale = (2.2, 0.08, 1.4)
    card.rotation_euler = (0, 0, ry)
    card.data.materials.append(GLASS)
    bevel(card, 0.05, 4)
    keyframe(card, 1, rotation_euler=(0, 0, ry))
    keyframe(card, FRAMES, rotation_euler=(0, 0, ry + 0.6 * (1 if i % 2 else -1)))
    set_ease(card)

# neon ring orbiting the tower
bpy.ops.mesh.primitive_torus_add(major_radius=1.6, minor_radius=0.04, major_segments=128, minor_segments=12, location=(0, 0, 1.1))
ring = bpy.context.active_object
ring.data.materials.append(NEON)
keyframe(ring, 1, rotation_euler=(math.radians(70), 0, 0))
keyframe(ring, FRAMES, rotation_euler=(math.radians(70), math.radians(360), math.radians(90)))
set_ease(ring, 'LINEAR')

# heart ("emotion") built from the classic parametric curve, extruded and bevelled
import bmesh
hm = bpy.data.meshes.new('Heart')
bm = bmesh.new()
ring_pts = []
for i in range(96):
    t = i / 96 * math.tau
    ring_pts.append((16 * math.sin(t) ** 3 / 17, (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17))
verts = [bm.verts.new((x, 0, z)) for x, z in ring_pts]
face = bm.faces.new(verts)
ret = bmesh.ops.extrude_face_region(bm, geom=[face])
bmesh.ops.translate(bm, vec=(0, -0.45, 0), verts=[v for v in ret['geom'] if isinstance(v, bmesh.types.BMVert)])
bm.normal_update()
bm.to_mesh(hm)
bm.free()
heart = bpy.data.objects.new('Heart', hm)
bpy.context.collection.objects.link(heart)
heart.location = (0, -2.6, 1.6)
heart.scale = (0.9, 0.9, 0.9)
heart.data.materials.append(CORAL)
bevel(heart, 0.06, 4)
smooth(heart)
keyframe(heart, 1, scale=(0.9, 0.9, 0.9))
for f in range(1, FRAMES, 30):
    keyframe(heart, f, scale=(0.9, 0.9, 0.9))
    keyframe(heart, f + 12, scale=(1.08, 1.08, 1.08))
    keyframe(heart, f + 24, scale=(0.9, 0.9, 0.9))


def add_title_plane(png_path, location=(0, 3.2, 3.4), width=7.0):
    """Floating, emissive title card from a transparent PNG (render Telugu text to PNG first)."""
    img = bpy.data.images.load(png_path)
    ratio = img.size[1] / max(1, img.size[0])
    bpy.ops.mesh.primitive_plane_add(size=1, location=location, rotation=(math.radians(90), 0, 0))
    p = bpy.context.active_object
    p.scale = (width, width * ratio, 1)
    m = bpy.data.materials.new('Title')
    m.use_nodes = True
    nt_ = m.node_tree
    nt_.nodes.clear()
    tex_ = nt_.nodes.new('ShaderNodeTexImage')
    tex_.image = img
    em = nt_.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 3.0
    tr = nt_.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt_.nodes.new('ShaderNodeMixShader')
    o = nt_.nodes.new('ShaderNodeOutputMaterial')
    nt_.links.new(tex_.outputs['Color'], em.inputs['Color'])
    nt_.links.new(tex_.outputs['Alpha'], mix.inputs['Fac'])
    nt_.links.new(tr.outputs['BSDF'], mix.inputs[1])
    nt_.links.new(em.outputs['Emission'], mix.inputs[2])
    nt_.links.new(mix.outputs['Shader'], o.inputs['Surface'])
    p.data.materials.append(m)
    return p


if TITLE_PNG:
    add_title_plane(TITLE_PNG)

# ----------------------------------------------------------------------------- lights (3-point + volumetric spot)
def area(name, loc, energy, color, size, target=(0, 0, 1.2)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = energy
    d.color = color
    d.size = size
    o = bpy.data.objects.new(name, d)
    o.location = loc
    bpy.context.collection.objects.link(o)
    c = o.constraints.new('TRACK_TO')
    t = bpy.data.objects.new(name + 'T', None)
    t.location = target
    bpy.context.collection.objects.link(t)
    c.target, c.track_axis, c.up_axis = t, 'TRACK_NEGATIVE_Z', 'UP_Y'
    return o


area('Key', (5, -6, 7), 1400, (1.0, 0.93, 0.82), 4.0)
area('RimGold', (-6, 5, 5), 900, (1.0, 0.72, 0.25), 3.0)
area('FillCyan', (-5, -5, 2.5), 450, (0.35, 0.65, 1.0), 5.0)
spot_d = bpy.data.lights.new('Spot', 'SPOT')
spot_d.energy = 9000
spot_d.spot_size = math.radians(38)
spot_d.spot_blend = 0.6
spot_d.color = (1.0, 0.9, 0.7)
spot = bpy.data.objects.new('Spot', spot_d)
spot.location = (0, 0.5, 12)
spot.rotation_euler = (0, 0, 0)
bpy.context.collection.objects.link(spot)

# ----------------------------------------------------------------------------- camera: orbit path + dolly + rack focus + handheld
bpy.ops.curve.primitive_bezier_circle_add(radius=9.5, location=(0, 0, 3.2))
path = bpy.context.active_object
path.name = 'CamPath'
path.data.path_duration = FRAMES
path.data.use_path = True
path.data.eval_time = 0
path.data.keyframe_insert('eval_time', frame=1)
path.data.eval_time = FRAMES * 0.42                    # a 150 degree sweep, not a full lap
path.data.keyframe_insert('eval_time', frame=FRAMES)
set_ease(path.data)

cam_d = bpy.data.cameras.new('Cam')
cam_d.lens = 38
cam_d.sensor_width = 36
cam_d.dof.use_dof = True
cam_d.dof.aperture_fstop = 1.8
cam = bpy.data.objects.new('Cam', cam_d)
bpy.context.collection.objects.link(cam)
scene.camera = cam
follow = cam.constraints.new('FOLLOW_PATH')
follow.target = path
follow.use_curve_follow = False
follow.use_fixed_location = False

aim = bpy.data.objects.new('Aim', None)
aim.location = (0, 0, 1.6)
bpy.context.collection.objects.link(aim)
tt = cam.constraints.new('TRACK_TO')
tt.target, tt.track_axis, tt.up_axis = aim, 'TRACK_NEGATIVE_Z', 'UP_Y'
# the aim point drifts from the coin tower to the bulb, and the focus follows it (rack focus)
for f, loc in ((1, (0, 0, 1.6)), (int(FRAMES * 0.5), (0, 0, 2.0)), (FRAMES, (-3.2, 0.6, 2.2))):
    keyframe(aim, f, location=loc)
set_ease(aim)
cam_d.dof.focus_object = aim
# dolly: focal length creeps from 38 to 52 mm
for f, l in ((1, 26.0), (FRAMES, 40.0)):
    cam_d.lens = l
    cam_d.keyframe_insert('lens', frame=f)
set_ease(cam_d)
# handheld shake: noise modifiers on the camera's own rotation offset (applied via a parent empty)
rig = bpy.data.objects.new('Shake', None)
bpy.context.collection.objects.link(rig)
cam.parent = rig
rig.rotation_mode = 'XYZ'
for idx in range(3):
    rig.keyframe_insert('rotation_euler', index=idx, frame=1)
    fc = [f for f in fcurves(rig) if f.data_path == 'rotation_euler' and f.array_index == idx][0]
    mod = fc.modifiers.new('NOISE')
    mod.scale = 70
    mod.strength = 0.0035
    mod.phase = idx * 13.7

# ----------------------------------------------------------------------------- compositor: bloom, chromatic aberration, vignette, grade
def setp(node, key, value):
    """Set a node option that is a property in some Blender versions and an input socket in others."""
    snake = key.lower().replace(' ', '_')
    if hasattr(node, snake) and not callable(getattr(node, snake)):
        try:
            setattr(node, snake, value)
            return True
        except (AttributeError, TypeError):
            pass
    for name in (key, key.title(), key.capitalize()):
        if name in node.inputs:
            try:
                node.inputs[name].default_value = value
                return True
            except (AttributeError, TypeError):
                return False
    return False


def build_compositor():
    if hasattr(scene, 'compositing_node_group'):                      # Blender 5.x
        ng = bpy.data.node_groups.new('Compositor', 'CompositorNodeTree')
        scene.compositing_node_group = ng
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        nodes, links = ng.nodes, ng.links
        sink = nodes.new('NodeGroupOutput')
        sink_in = sink.inputs['Image']
    else:                                                             # Blender 4.x
        scene.use_nodes = True
        nodes, links = scene.node_tree.nodes, scene.node_tree.links
        nodes.clear()
        sink = nodes.new('CompositorNodeComposite')
        sink_in = sink.inputs['Image']
    rl_ = nodes.new('CompositorNodeRLayers')
    glare = nodes.new('CompositorNodeGlare')
    setp(glare, 'glare_type', 'FOG_GLOW'); setp(glare, 'type', 'Fog Glow'); setp(glare, 'quality', 'HIGH'); setp(glare, 'threshold', 1.0)
    setp(glare, 'mix', -0.4); setp(glare, 'strength', 0.55)
    lens = nodes.new('CompositorNodeLensdist')
    setp(lens, 'use_fit', False); setp(lens, 'Dispersion', 0.01)
    grade = nodes.new('CompositorNodeColorBalance')
    setp(grade, 'correction_method', 'LIFT_GAMMA_GAIN')
    setp(grade, 'lift', (0.97, 0.98, 1.04, 1)); setp(grade, 'gain', (1.05, 1.02, 0.97, 1))
    ell = nodes.new('CompositorNodeEllipseMask')
    setp(ell, 'width', 0.92); setp(ell, 'height', 0.92)
    blur = nodes.new('CompositorNodeBlur')
    setp(blur, 'size_x', 140); setp(blur, 'size_y', 140); setp(blur, 'use_relative', False); setp(blur, 'Size', (140, 140))
    vmix = nodes.new('CompositorNodeMixRGB') if hasattr(bpy.types, 'CompositorNodeMixRGB') else None
    links.new(rl_.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], lens.inputs['Image'])
    links.new(lens.outputs['Image'], grade.inputs['Image'])
    if vmix:
        vmix.blend_type = 'MULTIPLY'
        vmix.inputs[0].default_value = 0.5
        links.new(ell.outputs['Mask'], blur.inputs['Image'])
        links.new(grade.outputs['Image'], vmix.inputs[1])
        links.new(blur.outputs['Image'], vmix.inputs[2])
        links.new(vmix.outputs['Image'], sink_in)
    else:
        links.new(grade.outputs['Image'], sink_in)


if hasattr(scene.render, 'compositor_device'):
    scene.render.compositor_device = 'CPU'            # no OpenGL needed for compositing
try:
    build_compositor()
except Exception as exc:   # the compositor API changes between releases; the render still works without it
    print('compositor setup skipped:', exc)

# ----------------------------------------------------------------------------- output
scene.render.image_settings.file_format = 'PNG' if STILL else 'FFMPEG'
if not STILL:
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.filepath = OUT

if '--no-render' in argv:
    print('scene built (no render)')
elif STILL:
    scene.frame_set(STILL)
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
