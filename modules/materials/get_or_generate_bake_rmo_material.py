import bpy  # type: ignore


def get_or_generate_bake_rmo_material() -> bpy.types.Material:
    """Bake RMO用のマテリアルを生成する

    Returns:
        bpy.types.Material: Bake RMO用のマテリアル
    """

    # 既にマテリアルが存在する場合はそれを返す
    material = bpy.data.materials.get("bake_RMO")
    if material is not None:
        return material

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
