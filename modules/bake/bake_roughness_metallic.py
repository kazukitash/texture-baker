import bpy  # type: ignore

from .bake_object import BakeObject


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
    material = target.material_slots[0].material
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    node = nodes["RMO"]
    node.image.generated_color = (0, 0, 0, 1)
    node.select = True
    nodes.active = node

    link = node.outputs["Color"].links[0]
    links.remove(link)

    bpy.ops.object.bake(type="DIFFUSE")

    node.select = False
    links.new(node.outputs["Color"], nodes["RMO Separate"].inputs["Vector"])

    for bake_source, source_material in zip(bake_object["sources"], source_materials):
        source = bpy.data.objects[bake_source]
        source.material_slots[0].material = source_material
