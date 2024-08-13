import bpy  # type: ignore

from ..models.bake_object import BakeObject

class TargetMaterial:
    @classmethod
    def delete(cls, bake_objects: list[BakeObject]):
        for bake_object in bake_objects:
            target = bpy.data.objects[bake_object["target"]]
            for material in [s.material for s in target.material_slots]:
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

    @classmethod
    def get_or_create(cls, name: str) -> bpy.types.Material:
        """Bake用のマテリアルを生成する

        Returns:
            bpy.types.Material: Bake用のマテリアル
        """

        mat_name = f"M_{name}"
        tex_name = f"T_{name}"

        # 既にマテリアルが存在する場合はそれを返す
        material = bpy.data.materials.get(mat_name)
        if material is not None:
            return material

        # マテリアルの生成
        material = bpy.data.materials.new(name=mat_name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Principled BSDFノードを取得
        principled = nodes["Principled BSDF"]

        # BaseColorのノードを生成
        bc_node = nodes.new(type="ShaderNodeTexImage")
        bc_node.name = "BaseColor"
        bc_node.location = (-700, 300)
        bc_image = bpy.data.images.new(f"{tex_name}_BC", 8192, 8192)
        bc_image.alpha_mode = "NONE"
        bc_image.pack()
        bc_node.image = bc_image

        # Roughness, Metallic, AmbientOcclusionのノードを生成
        rmo_node = nodes.new(type="ShaderNodeTexImage")
        rmo_node.name = "RMO"
        rmo_node.location = (-700, 0)
        rmo_image = bpy.data.images.new(f"{tex_name}_RMO", 8192, 8192)
        rmo_image.alpha_mode = "NONE"
        rmo_image.colorspace_settings.name = "Non-Color"
        rmo_image.pack()
        rmo_node.image = rmo_image

        rmo_separate = nodes.new(type="ShaderNodeSeparateXYZ")
        rmo_separate.name = "RMO Separate"
        rmo_separate.location = (-400, 100)

        mix = nodes.new(type="ShaderNodeMixRGB")
        mix.name = "BaseColor Mix"
        mix.location = (-200, 300)
        mix.blend_type = "MULTIPLY"
        mix.inputs["Fac"].default_value = 0.8

        n_node = nodes.new(type="ShaderNodeTexImage")
        n_node.name = "Normal"
        n_node.location = (-700, -300)
        n_image = bpy.data.images.new(f"{tex_name}_N", 8192, 8192)
        n_image.alpha_mode = "NONE"
        n_image.colorspace_settings.name = "Non-Color"
        n_image.pack()
        n_node.image = n_image

        normal_map = nodes.new(type="ShaderNodeNormalMap")
        normal_map.name = "Normal Map"
        normal_map.location = (-200, -300)
        normal_map.space = "TANGENT"

        bc_uvmap = nodes.new(type="ShaderNodeUVMap")
        bc_uvmap.name = "BaseColor UVMap"
        bc_uvmap.location = (-900, 200)

        rmo_uvmap = nodes.new(type="ShaderNodeUVMap")
        rmo_uvmap.name = "RMO UVMap"
        rmo_uvmap.location = (-900, -100)

        n_uvmap = nodes.new(type="ShaderNodeUVMap")
        n_uvmap.name = "Normal UVMap"
        n_uvmap.location = (-900, -400)

        # ノードの接続
        links.new(rmo_node.outputs["Color"], rmo_separate.inputs["Vector"])
        links.new(bc_node.outputs["Color"], mix.inputs["Color1"])
        links.new(rmo_separate.outputs["X"], principled.inputs["Roughness"])
        links.new(rmo_separate.outputs["Y"], principled.inputs["Metallic"])
        links.new(rmo_separate.outputs["Z"], mix.inputs["Color2"])
        links.new(mix.outputs["Color"], principled.inputs["Base Color"])

        links.new(n_node.outputs["Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])

        links.new(bc_uvmap.outputs["UV"], bc_node.inputs["Vector"])
        links.new(rmo_uvmap.outputs["UV"], rmo_node.inputs["Vector"])
        links.new(n_uvmap.outputs["UV"], n_node.inputs["Vector"])

        return material
