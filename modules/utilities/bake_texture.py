import bpy  # type: ignore

from ..models.ambient_occlusion import AmbientOcclusion
from ..models.target_material import TargetMaterial
from ..models.base_color import BaseColor
from ..models.bake_object import BakeObject
from ..models.normal import Normal
from ..models.rmo import RMO
from .custom_sort import custom_sort
from .get_bake_objects import get_bake_objects
from .get_highpoly_names import get_highpoly_names
from .print_log import print_log
from .save_image import save_image


def init_view():
    # hiとgameコレクションを表示
    for c in bpy.data.collections:
        c.hide_render = True
        c.hide_viewport = True
    bpy.data.collections["hi"].hide_render = False
    bpy.data.collections["hi"].hide_viewport = False
    bpy.data.collections["game"].hide_render = False
    bpy.data.collections["game"].hide_viewport = False


def setup():
    print_log("Set Bake Settings")
    render_engine = bpy.context.scene.render.engine
    if render_engine != "CYCLES":
        bpy.context.scene.render.engine = "CYCLES"

    cycles_preferences = bpy.context.preferences.addons["cycles"].preferences
    if bpy.app.build_platform == b"Windows":
        print_log("Set CUDA")
        cycles_preferences.compute_device_type = "CUDA"
    else:
        print_log("Set METAL")
        cycles_preferences.compute_device_type = "METAL"
    cycles_preferences.refresh_devices()
    cycles_preferences.devices[1].use = True
    print_log(f"Use GPU {cycles_preferences.devices[1].name}")
    bpy.context.scene.cycles.device = "GPU"
    bpy.context.scene.render.bake.use_cage = True
    bpy.context.scene.render.bake.max_ray_distance = 0
    bpy.context.scene.render.bake.use_clear = False
    bpy.context.scene.render.bake.margin = 16
    bpy.context.scene.render.bake.margin_type = "EXTEND"
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_pass_color = True

def cleanup(bake_objects: list[BakeObject]):
    # target materialの初期化（削除）
    TargetMaterial.delete(bake_objects)

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

def bake_texture():
    print_log("Bake Start")

    setup()
    init_view()

    print_log("Select Bake Objects")
    highpoly_names = get_highpoly_names()
    highpoly_names = custom_sort(highpoly_names)
    bake_objects = get_bake_objects(highpoly_names)

    cleanup(bake_objects)

    print_log("Set Bake Materials")
    bake_bc_material = BaseColor.create()
    bake_rmo_material = RMO.create()

    print_log("Baking AmbientOcclusion to HighPoly")
    bpy.context.scene.render.bake.use_selected_to_active = False
    AmbientOcclusion.bake(highpoly_names)
    bpy.context.scene.render.bake.use_selected_to_active = True

    baked_materials = []

    for bake_object in bake_objects:
        print_log(f"target: {bake_object['target']}, source: [{[', '.join(bake_object['sources'])]}]")

    for bake_object in bake_objects:
        # 選択を解除
        for ob in bpy.data.objects:
            ob.select_set(False)

        for bake_source in bake_object["sources"]:
            source = bpy.data.objects[bake_source]
            source.select_set(True)

        target = bpy.data.objects[bake_object["target"]]
        target.select_set(True)

        if len(target.material_slots) > 0:
            material = target.material_slots[0].material
            nodes = material.node_tree.nodes

            bc_node = nodes["BaseColor"]
            bc_node.image.generated_color = (0, 0, 0, 1)

            rmo_node = nodes["RMO"]
            rmo_node.image.generated_color = (0, 0, 0, 1)

            n_node = nodes["Normal"]
            n_node.image.generated_color = (0, 0, 0, 1)

        print_log(f"Baking Base Color of {bake_object['target']}")
        BaseColor.bake(bake_object, target, bake_bc_material, baked_materials)
        print_log(
            f"Baking Roughness, Metallic, AmbientOcclusion of {bake_object['target']}"
        )
        RMO.bake(bake_object, target, bake_rmo_material)
        print_log(f"Baking Normal of {bake_object['target']}")
        Normal.bake(bake_object, target)

        # 選択を解除
        for ob in bpy.data.objects:
            ob.select_set(False)

    bpy.data.materials.remove(bake_bc_material)
    bpy.data.materials.remove(bake_rmo_material)

    print_log("Save Images")
    for baked_material in baked_materials:
        nodes = baked_material.node_tree.nodes
        image = nodes["BaseColor"].image
        print_log(image.file_format)
        print_log(image.filepath)
        print_log(image.filepath_raw)
        print_log(image.filepath_from_user())
        save_image(baked_material)

    print_log("Finish Bake")
