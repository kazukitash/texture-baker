import os
import re
from typing import TypedDict

import bpy  # type: ignore

bl_info = {
    "name": "Bake BC,RMO,Normal Textures from HiPoly",
    "author": "kazukitash",
    "version": (2, 0),
    "blender": (3, 6, 1),
    "location": "View3D > UI > Bake from HiPoly",
    "description": "Bake BC,RMO,Normal Textures from HiPoly",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}


def get_or_generate_bake_bc_material() -> bpy.types.Material:
    """Bake BC用のマテリアルを生成する

    Returns:
        bpy.types.Material: Bake BC用のマテリアル
    """

    # 既にマテリアルが存在する場合はそれを返す
    bake_bc_material = bpy.data.materials.get("bake_BC")
    if bake_bc_material is not None:
        return bake_bc_material

    # マテリアルの生成
    bake_bc_material = bpy.data.materials.new(name="bake_BC")
    bake_bc_material.use_nodes = True
    nodes = bake_bc_material.node_tree.nodes
    links = bake_bc_material.node_tree.links

    # ノードの追加
    node_principled = nodes["Principled BSDF"]

    bc_node = nodes.new(type="ShaderNodeTexImage")
    bc_node.name = "BaseColor"
    bc_node.location = (-400, 0)

    # ノードの接続
    links.new(bc_node.outputs["Color"], node_principled.inputs["Base Color"])

    return bake_bc_material


def get_or_generate_bake_rmo_material() -> bpy.types.Material:
    """Bake RMO用のマテリアルを生成する

    Returns:
        bpy.types.Material: Bake RMO用のマテリアル
    """

    # 既にマテリアルが存在する場合はそれを返す
    bake_rmo_material = bpy.data.materials.get("bake_RMO")
    if bake_rmo_material is not None:
        return bake_rmo_material

    # マテリアルの生成
    bake_rmo_material = bpy.data.materials.new(name="bake_RMO")
    bake_rmo_material.use_nodes = True
    nodes = bake_rmo_material.node_tree.nodes
    links = bake_rmo_material.node_tree.links

    # ノードの追加
    node_principled = nodes["Principled BSDF"]

    rm_node = nodes.new(type="ShaderNodeTexImage")
    rm_node.name = "RoughnessMetallic"
    rm_node.location = (-600, 0)

    separate_rm = nodes.new(type="ShaderNodeSeparateXYZ")
    separate_rm.location = (-400, 0)

    ao_node = nodes.new(type="ShaderNodeTexImage")
    ao_node.name = "AmbientOcclusion"
    ao_node.location = (-600, 200)

    separate_ao = nodes.new(type="ShaderNodeSeparateXYZ")
    separate_ao.location = (-400, 200)

    combine = nodes.new(type="ShaderNodeCombineXYZ")
    combine.location = (-200, 100)

    # ノードの接続
    links.new(rm_node.outputs["Color"], separate_rm.inputs["Vector"])
    links.new(ao_node.outputs["Color"], separate_ao.inputs["Vector"])
    links.new(separate_rm.outputs["X"], combine.inputs["X"])
    links.new(separate_rm.outputs["Y"], combine.inputs["Y"])
    links.new(separate_ao.outputs["Z"], combine.inputs["Z"])
    links.new(combine.outputs["Vector"], node_principled.inputs["Base Color"])

    return bake_rmo_material


def get_or_generate_material(name: str) -> bpy.types.Material:
    """Bake用のマテリアルを生成する

    Returns:
        bpy.types.Material: Bake用のマテリアル
    """

    # 既にマテリアルが存在する場合はそれを返す
    material = bpy.data.materials.get(name)
    if material is not None:
        return material

    # マテリアルの生成
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # ノードの追加
    node_principled = nodes["Principled BSDF"]

    bc_node = nodes.new(type="ShaderNodeTexImage")
    bc_node.name = "BaseColor"
    bc_node.location = (-700, 300)
    bc_image = bpy.data.images.new(f"T_{name}_BC", 8192, 8192)
    bc_image.alpha_mode = "NONE"
    bc_node.image = bc_image

    rmo_node = nodes.new(type="ShaderNodeTexImage")
    rmo_node.name = "RMO"
    rmo_node.location = (-700, 0)
    rmo_image = bpy.data.images.new(f"T_{name}_RMO", 8192, 8192)
    rmo_image.alpha_mode = "NONE"
    rmo_image.colorspace_settings.name = "Non-Color"
    rmo_node.image = rmo_image

    separate_rmo = nodes.new(type="ShaderNodeSeparateXYZ")
    separate_rmo.location = (-400, 100)

    mix = nodes.new(type="ShaderNodeMixRGB")
    mix.location = (-200, 300)
    mix.blend_type = "MULTIPLY"

    n_node = nodes.new(type="ShaderNodeTexImage")
    n_node.name = "Normal"
    n_node.location = (-700, -300)
    n_image = bpy.data.images.new(f"T_{name}_N", 8192, 8192)
    n_image.alpha_mode = "NONE"
    n_image.colorspace_settings.name = "Non-Color"
    n_node.image = n_image

    normal_map = nodes.new(type="ShaderNodeNormalMap")
    normal_map.location = (-200, -300)
    normal_map.space = "TANGENT"

    bc_uvmap = nodes.new(type="ShaderNodeUVMap")
    bc_uvmap.location = (-900, 200)

    rmo_uvmap = nodes.new(type="ShaderNodeUVMap")
    rmo_uvmap.location = (-900, -100)

    n_uvmap = nodes.new(type="ShaderNodeUVMap")
    n_uvmap.location = (-900, -400)

    # ノードの接続
    links.new(rmo_node.outputs["Color"], separate_rmo.inputs["Vector"])
    links.new(bc_node.outputs["Color"], mix.inputs["Color1"])
    links.new(separate_rmo.outputs["X"], node_principled.inputs["Roughness"])
    links.new(separate_rmo.outputs["Y"], node_principled.inputs["Metallic"])
    links.new(separate_rmo.outputs["Z"], mix.inputs["Color2"])
    links.new(mix.outputs["Color"], node_principled.inputs["Base Color"])

    links.new(n_node.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], node_principled.inputs["Normal"])

    links.new(bc_uvmap.outputs["UV"], bc_node.inputs["Vector"])
    links.new(rmo_uvmap.outputs["UV"], rmo_node.inputs["Vector"])
    links.new(n_uvmap.outputs["UV"], n_node.inputs["Vector"])

    return material


def get_highpoly_names() -> list[str]:
    """シーン内のハイポリメッシュの名前を取得する
        hi_で始まるオブジェクトを取得する

    Returns:
        list[str]: ハイポリメッシュの名前のリスト
    """

    highpoly_names = []

    for ob in bpy.context.visible_objects:
        if ob.type != "MESH":
            continue

        if ob.name.startswith("hi_"):
            highpoly_names.append(ob.name)

    return highpoly_names


def custom_sort(lst: list[str]) -> list[str]:
    """#が含まれているオブジェクトを後ろにソートする

    Args:
        lst (list[str]): ソート前のリスト

    Returns:
        list[str]: ソート後のリスト
    """

    # リスト内の各要素を#の有無に応じて2つのリストに分割
    with_hash, without_hash = [], []
    for item in lst:
        if "#" in item:
            with_hash.append(item)
        else:
            without_hash.append(item)

    # #を含む要素を後ろにソートして、元のリストに結合
    sorted_list = without_hash + sorted(with_hash)

    return sorted_list


class BakeObject(TypedDict):
    target: str
    sources: list[str]


def get_bake_objects(highpoly_names: list[str]) -> list[BakeObject]:
    """bakeオブジェクトの情報を取得する
        hi_A_Bの場合、AにBakeする
        hi_A#_Bの場合、ACやADなど#を.*にしてregexしたメッシュにBakeする

    Returns:
        list[dict]: bakeオブジェクトの情報のリスト
    """

    bake_objects: list[BakeObject] = []

    for highpoly_name in highpoly_names:
        lowpoly_name = highpoly_name.lstrip("hi_").split("_")[0].replace("#", ".*")

        pattern = re.compile(lowpoly_name)
        match_bakes: list[BakeObject] = list(
            filter(lambda m: pattern.search(m["target"]), bake_objects)
        )
        if len(match_bakes) == 0:
            bake_object: BakeObject = {
                "target": lowpoly_name,
                "sources": [highpoly_name],
            }
            bake_objects.append(bake_object)
        else:
            for bake in match_bakes:
                bake["sources"].append(highpoly_name)

    return bake_objects


def bake_ambient_occlusion(highpoly_names: list[str]):
    bpy.data.collections["game"].hide_render = True

    targets = [bpy.data.objects[name] for name in highpoly_names]

    # 選択を解除
    for ob in bpy.data.objects:
        ob.select_set(False)

    for target in targets:
        nodes = target.material_slots[0].material.node_tree.nodes
        nodes["AmbientOcclusion"].image.generated_color = (0, 0, 0, 1)
        nodes.active = nodes["AmbientOcclusion"]
        nodes["AmbientOcclusion"].select = True

        bpy.context.view_layer.objects.active = target
        target.select = True

    bpy.ops.object.bake(type="AO")
    nodes["AmbientOcclusion"].select = False

    bpy.data.collections["game"].hide_render = False


def bake_color(
    bake_object: BakeObject,
    target: bpy.types.Object,
    bake_bc_material: bpy.types.Material,
    baked_materials: list[bpy.types.Material],
):
    source_materials = []
    for bake_source in bake_object["sources"]:
        source = bpy.data.objects[bake_source]
        bpy.context.view_layer.objects.active = source
        source_material = source.material_slots[0].material
        source_materials.append(source_material)

        target_material_name = source_material.name.replace("hi_", "")
        material = bpy.data.materials.get(target_material_name)
        if material is None:
            material = get_or_generate_material(target_material_name)
            baked_materials.append(material)
        if len(target.material_slots) == 0:
            target.data.materials.append(material)
        else:
            target.material_slots[0].material = material

        bc_node = bake_bc_material.node_tree.nodes["BaseColor"]
        bc_node.image = source_material.node_tree.nodes["BaseColor"].image
        source.material_slots[0].material = bake_bc_material

    bpy.context.view_layer.objects.active = target
    nodes = target.material_slots[0].material.node_tree.nodes
    nodes["BaseColor"].image.generated_color = (0, 0, 0, 1)
    nodes["BaseColor"].select = True
    nodes.active = nodes["BaseColor"]

    bpy.ops.object.bake(type="DIFFUSE")
    nodes["BaseColor"].select = False

    for bake_source, source_material in zip(bake_object["sources"], source_materials):
        source = bpy.data.objects[bake_source]
        source.material_slots[0].material = source_material


def bake_roughness_metallic(
    bake_object: BakeObject,
    target: bpy.types.Object,
    bake_rmo_material: bpy.types.Material,
):
    source_materials = []
    for bake_source in bake_object["sources"]:
        source = bpy.data.objects[bake_source]
        bpy.context.view_layer.objects.active = source
        source_material = source.material_slots[0].material
        source_materials.append(source_material)

        rm_node = bake_rmo_material.node_tree.nodes["RoughnessMetallic"]
        rm_node.image = source_material.node_tree.nodes["RoughnessMetallic"].image
        ao_node = bake_rmo_material.node_tree.nodes["AmbientOcclusion"]
        ao_node.image = source_material.node_tree.nodes["AmbientOcclusion"].image
        source.material_slots[0].material = bake_rmo_material

    bpy.context.view_layer.objects.active = target
    nodes = target.material_slots[0].material.node_tree.nodes
    nodes["RMO"].image.generated_color = (0, 0, 0, 1)
    nodes["RMO"].select = True
    nodes.active = nodes["RMO"]

    bpy.ops.object.bake(type="DIFFUSE")
    nodes["RMO"].select = False

    for bake_source, source_material in zip(bake_object["sources"], source_materials):
        source = bpy.data.objects[bake_source]
        source.material_slots[0].material = source_material


def bake_normal(bake_object: BakeObject, target: bpy.types.Object):
    for bake_source in bake_object["sources"]:
        source = bpy.data.objects[bake_source]
        bpy.context.view_layer.objects.active = source

    bpy.context.view_layer.objects.active = target
    nodes = target.material_slots[0].material.node_tree.nodes
    nodes["Normal"].image.generated_color = (0, 0, 0, 1)
    nodes["Normal"].select = True
    nodes.active = nodes["Normal"]

    bpy.ops.object.bake(type="NORMAL")
    nodes["Normal"].select = False


def save_image(material: bpy.types.Material):
    nodes = material.node_tree.nodes

    image = nodes["BaseColor"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    image.pack()

    image = nodes["RMO"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    image.pack()

    image = nodes["Normal"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    image.pack()


# Define a new operator (action or function)
class BakeAllOperator(bpy.types.Operator):
    bl_idname = "object.bake_all"
    bl_label = "Bake"

    def execute(self, context):
        self.report({"INFO"}, "Bake Start")

        render_engine = bpy.context.scene.render.engine
        if render_engine != "CYCLES":
            bpy.context.scene.render.engine = "CYCLES"

        cycles_preferences = bpy.context.preferences.addons["cycles"].preferences
        if bpy.app.build_platform == b"Windows":
            cycles_preferences.compute_device_type = "CUDA"
            cycles_preferences.refresh_devices()
            cycles_preferences.devices["NVIDIA GeForce RTX 4090"].use = True
        else:
            cycles_preferences.compute_device_type = "METAL"
            cycles_preferences.refresh_devices()
            cycles_preferences.devices["Apple M2 Max (GPU - 38 cores)"].use = True
        bpy.context.scene.cycles.device = "GPU"
        bpy.context.scene.render.bake.use_selected_to_active = False
        bpy.context.scene.render.bake.use_cage = True
        bpy.context.scene.render.bake.use_clear = False
        bpy.context.scene.render.bake.margin = 8
        bpy.context.scene.render.bake.margin_type = "EXTEND"
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True

        bake_bc_material = get_or_generate_bake_bc_material()
        bake_rmo_material = get_or_generate_bake_rmo_material()
        highpoly_names = get_highpoly_names()
        highpoly_names = custom_sort(highpoly_names)
        bake_objects = get_bake_objects(highpoly_names)

        # AmbientOcclusionのBake
        self.report({"INFO"}, "Baking AmbientOcclusion")
        bake_ambient_occlusion(highpoly_names)

        baked_materials = []

        bpy.context.scene.render.bake.use_selected_to_active = True
        for bake_object in bake_objects:
            # 選択を解除
            for ob in bpy.data.objects:
                ob.select_set(False)

            for bake_source in bake_object["sources"]:
                source = bpy.data.objects[bake_source]
                source.select_set(True)

            target = bpy.data.objects[bake_object["target"]]
            target.select_set(True)

            self.report({"INFO"}, f"Baking {bake_object['target']} Base Color")
            bake_color(bake_object, target, bake_bc_material, baked_materials)
            self.report(
                {"INFO"},
                f"Baking {bake_object['target']} Roughness, Metallic, AmbientOcclusion",
            )
            bake_roughness_metallic(bake_object, target, bake_rmo_material)
            self.report({"INFO"}, f"Baking {bake_object['target']} Normal")
            bake_normal(bake_object, target)

            # 選択を解除
            for ob in bpy.data.objects:
                ob.select_set(False)

        bpy.data.materials.remove(bake_bc_material)
        bpy.data.materials.remove(bake_rmo_material)

        for baked_material in baked_materials:
            save_image(baked_material)

        self.report({"INFO"}, "Bake End")
        return {"FINISHED"}


# Define a new UI panel
class BakeAllPanel(bpy.types.Panel):
    bl_label = "Bake All"
    bl_idname = "OBJECT_PT_bake_all"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout

        # Add the operator to the panel
        layout.operator("object.bake_all")


# Registration
def register():
    bpy.utils.register_class(BakeAllOperator)
    bpy.utils.register_class(BakeAllPanel)


def unregister():
    bpy.utils.unregister_class(BakeAllOperator)
    bpy.utils.unregister_class(BakeAllPanel)


if __name__ == "__main__":
    register()
