import bpy  # type: ignore

from ..materials.get_or_generate_material import get_or_generate_material
from .bake_object import BakeObject


def bake_basecolor(
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
    material = target.material_slots[0].material
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    node = nodes["BaseColor"]
    node.image.generated_color = (0, 0, 0, 1)
    node.select = True
    nodes.active = node

    link = node.outputs["Color"].links[0]
    links.remove(link)

    bpy.ops.object.bake(type="DIFFUSE")
    
    node.select = False
    links.new(node.outputs["Color"], nodes["BaseColor Mix"].inputs["Color1"])

    for bake_source, source_material in zip(bake_object["sources"], source_materials):
        source = bpy.data.objects[bake_source]
        source.material_slots[0].material = source_material
