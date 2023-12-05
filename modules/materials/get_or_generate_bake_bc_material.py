import bpy  # type: ignore


def get_or_generate_bake_bc_material() -> bpy.types.Material:
    """Bake BC用のマテリアルを生成する

    Returns:
        bpy.types.Material: Bake BC用のマテリアル
    """

    # 既にマテリアルが存在する場合はそれを返す
    material = bpy.data.materials.get("bake_BC")
    if material is not None:
        return material

    # マテリアルの生成
    material = bpy.data.materials.new(name="bake_BC")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Principled BSDFノードを取得
    principled = nodes["Principled BSDF"]

    # BaseColorのノードを生成
    bc_node = nodes.new(type="ShaderNodeTexImage")
    bc_node.name = "BaseColor"
    bc_node.location = (-400, 0)

    # ノードの接続
    links.new(bc_node.outputs["Color"], principled.inputs["Base Color"])

    return material
