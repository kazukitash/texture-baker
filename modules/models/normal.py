import bpy  # type: ignore

from ..models.bake_object import BakeObject


class Normal:
    @classmethod
    def bake(cls, bake_object: BakeObject, target: bpy.types.Object):
        for bake_source in bake_object["sources"]:
            source = bpy.data.objects[bake_source]
            bpy.context.view_layer.objects.active = source

        bpy.context.view_layer.objects.active = target
        material = target.material_slots[0].material
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        node = nodes["Normal"]
        node.select = True
        nodes.active = node

        link = node.outputs["Color"].links[0]
        links.remove(link)

        cage = bpy.data.objects[f"cage_{target.name}"]
        bpy.context.scene.render.bake.cage_object = cage
        bpy.ops.object.bake(type="NORMAL")

        node.select = False
        links.new(node.outputs["Color"], nodes["Normal Map"].inputs["Color"])
