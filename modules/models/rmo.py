import bpy  # type: ignore

from ..models.bake_object import BakeObject


class RMO:
    @classmethod
    def create(cls) -> bpy.types.Material:
        """Bake RMO用のマテリアルを生成する

        Returns:
            bpy.types.Material: Bake RMO用のマテリアル
        """

        # 既にマテリアルが存在する場合は削除する
        material = bpy.data.materials.get("bake_RMO")
        if material is not None:
            # マテリアルが使用中かどうかをチェック
            for obj in bpy.data.objects:
                if material.name in [mat.name if mat is not None else "" for mat in obj.data.materials]:
                    # オブジェクトのマテリアルスロットからマテリアルを取り除く
                    for i in range(len(obj.data.materials)):
                        if obj.data.materials[i] == material:
                            obj.data.materials[i] = None

                    # `None`を削除
                    obj.data.materials.clear()
                    for mat in [m for m in obj.material_slots if m.material is not None]:
                        obj.data.materials.append(mat.material)

            # 使用中のマテリアルを削除
            bpy.data.materials.remove(material)

        # マテリアルの生成
        material = bpy.data.materials.new(name="bake_RMO")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Principled BSDFノードを取得
        principled = nodes["Principled BSDF"]

        # RoughnessMetallicのノードを生成
        rm_node = nodes.new(type="ShaderNodeTexImage")
        rm_node.name = "RoughnessMetallic"
        rm_node.location = (-600, 0)

        rm_separate = nodes.new(type="ShaderNodeSeparateXYZ")
        rm_separate.name = "RoughnessMetallic Separate"
        rm_separate.location = (-400, 0)

        # AmbientOcclusionのノードを生成
        ao_node = nodes.new(type="ShaderNodeTexImage")
        ao_node.name = "AmbientOcclusion"
        ao_node.location = (-600, 200)

        ao_separate = nodes.new(type="ShaderNodeSeparateXYZ")
        ao_separate.name = "AmbientOcclusion Separate"
        ao_separate.location = (-400, 200)

        # RoughnessMetallicとAmbientOcclusionを結合するノードを生成
        combine = nodes.new(type="ShaderNodeCombineXYZ")
        combine.name = "RoughnessMetallic and AmbientOcclusion Combine"
        combine.location = (-200, 100)

        # ノードの接続
        # Roughness, Metallic, AmbientOcclusionのノードを生成
        links.new(rm_node.outputs["Color"], rm_separate.inputs["Vector"])
        links.new(ao_node.outputs["Color"], ao_separate.inputs["Vector"])
        links.new(rm_separate.outputs["X"], combine.inputs["X"])
        links.new(rm_separate.outputs["Y"], combine.inputs["Y"])
        links.new(ao_separate.outputs["Z"], combine.inputs["Z"])
        links.new(combine.outputs["Vector"], principled.inputs["Base Color"])

        return material

    @classmethod
    def bake(
        cls,
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
        node.select = True
        nodes.active = node

        link = node.outputs["Color"].links[0]
        links.remove(link)

        cage = bpy.data.objects[f"cage_{target.name}"]
        bpy.context.scene.render.bake.cage_object = cage
        bpy.ops.object.bake(type="DIFFUSE")

        node.select = False
        links.new(node.outputs["Color"], nodes["RMO Separate"].inputs["Vector"])

        for bake_source, source_material in zip(
            bake_object["sources"], source_materials
        ):
            source = bpy.data.objects[bake_source]
            source.material_slots[0].material = source_material
