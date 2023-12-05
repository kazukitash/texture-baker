import bpy  # type: ignore


def generate_highpoly_material(name: str) -> bpy.types.Material:
    """HighPoly用のマテリアルを生成する

    Returns:
        bpy.types.Material: HighPoly用のマテリアル
    """

    mat_name = f"hi_{name}"

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
    bc_image = bpy.data.images.new(f"{mat_name}_BC", 8192, 8192)
    bc_image.alpha_mode = "NONE"
    bc_image.pack()
    bc_node.image = bc_image

    bc_uvmap = nodes.new(type="ShaderNodeUVMap")
    bc_uvmap.name = "BaseColor UVMap"
    bc_uvmap.location = (-900, 200)

    mix = nodes.new(type="ShaderNodeMixRGB")
    mix.name = "BaseColor and AmbientOcclusion Mix"
    mix.location = (-200, 300)
    mix.blend_type = "MULTIPLY"

    # AmbientOcclusionのノードを生成
    ao_node = nodes.new(type="ShaderNodeTexImage")
    ao_node.name = "AmbientOcclusion"
    ao_node.location = (-700, 0)
    ao_image = bpy.data.images.new(f"{mat_name}_AO", 8192, 8192)
    ao_image.alpha_mode = "NONE"
    ao_image.colorspace_settings.name = "Non-Color"
    ao_image.pack()
    ao_node.image = ao_image

    ao_uvmap = nodes.new(type="ShaderNodeUVMap")
    ao_uvmap.name = "AmbientOcclusion UVMap"
    ao_uvmap.location = (-900, -100)

    ao_separate = nodes.new(type="ShaderNodeSeparateXYZ")
    ao_separate.name = "AmbientOcclusion Separate"
    ao_separate.location = (-400, 100)

    # Roughness, Metallicのノードを生成
    rm_node = nodes.new(type="ShaderNodeTexImage")
    rm_node.name = "RoughnessMetallic"
    rm_node.location = (-700, -300)
    rm_image = bpy.data.images.new(f"{mat_name}_RM", 8192, 8192)
    rm_image.alpha_mode = "NONE"
    rm_image.colorspace_settings.name = "Non-Color"
    rm_image.pack()
    rm_node.image = rm_image

    rm_uvmap = nodes.new(type="ShaderNodeUVMap")
    rm_uvmap.name = "RoughnessMetallic UVMap"
    rm_uvmap.location = (-900, -400)

    rm_separate = nodes.new(type="ShaderNodeSeparateXYZ")
    rm_separate.name = "RoughnessMetallic Separate"
    rm_separate.location = (-400, -200)

    # ノードの接続
    # BaseColor
    links.new(ao_node.outputs["Color"], ao_separate.inputs["Vector"])
    links.new(bc_node.outputs["Color"], mix.inputs["Color1"])
    links.new(ao_separate.outputs["Z"], mix.inputs["Color2"])
    links.new(mix.outputs["Color"], principled.inputs["Base Color"])

    # Roughness, Metallic
    links.new(rm_node.outputs["Color"], rm_separate.inputs["Vector"])
    links.new(rm_separate.outputs["X"], principled.inputs["Roughness"])
    links.new(rm_separate.outputs["Y"], principled.inputs["Metallic"])

    # UVMap
    links.new(bc_uvmap.outputs["UV"], bc_node.inputs["Vector"])
    links.new(rm_uvmap.outputs["UV"], rm_node.inputs["Vector"])
    links.new(ao_uvmap.outputs["UV"], ao_node.inputs["Vector"])

    return material
