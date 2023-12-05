import bpy  # type: ignore


def bake_ambient_occlusion(highpoly_names: list[str]):
    targets = [bpy.data.objects[name] for name in highpoly_names]

    # 選択を解除
    for ob in bpy.data.objects:
        ob.select_set(False)

    for target in targets:
        material = target.material_slots[0].material
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        node = nodes["AmbientOcclusion"]
        node.image.generated_color = (0, 0, 0, 1)
        node.select = True
        nodes.active = node

        link = node.outputs["Color"].links[0]
        links.remove(link)

        bpy.context.view_layer.objects.active = target
        target.select = True

    bpy.ops.object.bake(type="AO")

    for target in targets:
        material = target.material_slots[0].material
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        node = nodes["AmbientOcclusion"]
        node.select = False
        links.new(
            node.outputs["Color"], nodes["AmbientOcclusion Separate"].inputs["Vector"]
        )
