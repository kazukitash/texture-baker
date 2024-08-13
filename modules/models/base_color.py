import bpy  # type: ignore

from ..models.bake_object import BakeObject
from ..models.target_material import TargetMaterial


class BaseColor:
    @classmethod
    def create(cls) -> bpy.types.Material:
        """Bake BC用のマテリアルを生成する

        Returns:
            bpy.types.Material: Bake BC用のマテリアル
        """

        # 既にマテリアルが存在する場合は削除する
        material = bpy.data.materials.get("bake_BC")
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

    @classmethod
    def bake(
        cls,
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

            target_material_name = source_material.name.replace("hi_M_", "")
            material = bpy.data.materials.get(target_material_name)
            if material is None:
                material = TargetMaterial.get_or_create(target_material_name)
                if material.name not in [m.name for m in baked_materials]:
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
        node.select = True
        nodes.active = node

        link = node.outputs["Color"].links[0]
        links.remove(link)

        cage = bpy.data.objects[f"cage_{target.name}"]
        bpy.context.scene.render.bake.cage_object = cage
        bpy.ops.object.bake(type="DIFFUSE")

        node.select = False
        links.new(node.outputs["Color"], nodes["BaseColor Mix"].inputs["Color1"])

        for bake_source, source_material in zip(
            bake_object["sources"], source_materials
        ):
            source = bpy.data.objects[bake_source]
            source.material_slots[0].material = source_material
