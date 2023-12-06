import bpy  # type: ignore


class TargetMaterial:
    @classmethod
    def get_or_create(cls, name: str) -> bpy.types.Material:
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

        # Principled BSDFノードを取得
        principled = nodes["Principled BSDF"]

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

        rmo_separate = nodes.new(type="ShaderNodeSeparateXYZ")
        rmo_separate.name = "RMO Separate"
        rmo_separate.location = (-400, 100)

        mix = nodes.new(type="ShaderNodeMixRGB")
        mix.name = "BaseColor Mix"
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
