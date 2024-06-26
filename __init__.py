import bpy  # type: ignore

from .modules.models.ambient_occlusion import AmbientOcclusion
from .modules.models.base_color import BaseColor
from .modules.models.highpoly import Highpoly
from .modules.models.normal import Normal
from .modules.models.rmo import RMO
from .modules.utilities.custom_sort import custom_sort
from .modules.utilities.get_bake_objects import get_bake_objects
from .modules.utilities.get_highpoly_names import get_highpoly_names
from .modules.utilities.print_log import print_log
from .modules.utilities.save_image import save_image

bl_info = {
    "name": "Texture Baker",
    "author": "kazukitash",
    "version": (2, 2),
    "blender": (3, 6, 5),
    "location": "View3D > UI > Texture Baker",
    "description": "Bake Textures for BaseColor, Roughness, Metallic, AmbientOcclusion, Normal from HighPoly",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}


# Define a new operator (action or function)
class BakeTextureOperator(bpy.types.Operator):
    bl_idname = "object.texture_baker_bake_texture"
    bl_label = "Bake"

    def execute(self, context):
        print_log("Bake Start")

        print_log("Set Bake Settings")
        render_engine = bpy.context.scene.render.engine
        if render_engine != "CYCLES":
            bpy.context.scene.render.engine = "CYCLES"

        cycles_preferences = bpy.context.preferences.addons["cycles"].preferences
        if bpy.app.build_platform == b"Windows":
            print_log("Set CUDA")
            cycles_preferences.compute_device_type = "CUDA"
        else:
            print_log("Set METAL")
            cycles_preferences.compute_device_type = "METAL"
        cycles_preferences.refresh_devices()
        cycles_preferences.devices[1].use = True
        print_log(f"Use GPU {cycles_preferences.divices[1].name}")
        bpy.context.scene.cycles.device = "GPU"
        bpy.context.scene.render.bake.use_cage = True
        bpy.context.scene.render.bake.use_clear = False
        bpy.context.scene.render.bake.margin = 8
        bpy.context.scene.render.bake.margin_type = "EXTEND"
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True

        print_log("Set Bake Materials")
        bake_bc_material = BaseColor.get_or_create()
        bake_rmo_material = RMO.get_or_create()

        print_log("Select Bake Objects")
        highpoly_names = get_highpoly_names()
        highpoly_names = custom_sort(highpoly_names)
        bake_objects = get_bake_objects(highpoly_names)

        print_log("Baking AmbientOcclusion to HighPoly")
        for c in bpy.data.collections:
            c.hide_render = True
            c.hide_viewport = True
        bpy.data.collections["hi"].hide_render = False
        bpy.data.collections["hi"].hide_viewport = False
        bpy.context.scene.render.bake.use_selected_to_active = False
        AmbientOcclusion.bake(highpoly_names)

        bpy.data.collections["game"].hide_render = False
        bpy.data.collections["game"].hide_viewport = False
        bpy.context.scene.render.bake.use_selected_to_active = True
        baked_materials = []
        for bake_object in bake_objects:
            # 選択を解除
            for ob in bpy.data.objects:
                ob.select_set(False)

            for bake_source in bake_object["sources"]:
                source = bpy.data.objects[bake_source]
                source.select_set(True)

            target = bpy.data.objects[bake_object["target"]]
            target.select_set(True)

            if len(target.material_slots) > 0:
                material = target.material_slots[0].material
                nodes = material.node_tree.nodes

                bc_node = nodes["BaseColor"]
                bc_node.image.generated_color = (0, 0, 0, 1)

                rmo_node = nodes["RMO"]
                rmo_node.image.generated_color = (0, 0, 0, 1)

                n_node = nodes["Normal"]
                n_node.image.generated_color = (0, 0, 0, 1)

            print_log(f"Baking Base Color of {bake_object['target']}")
            BaseColor.bake(bake_object, target, bake_bc_material, baked_materials)
            print_log(
                f"Baking Roughness, Metallic, AmbientOcclusion of {bake_object['target']}"
            )
            RMO.bake(bake_object, target, bake_rmo_material)
            print_log(f"Baking Normal of {bake_object['target']}")
            Normal.bake(bake_object, target)

            # 選択を解除
            for ob in bpy.data.objects:
                ob.select_set(False)

        bpy.data.materials.remove(bake_bc_material)
        bpy.data.materials.remove(bake_rmo_material)

        print_log("Save Images")
        for baked_material in baked_materials:
            save_image(baked_material)

        print_log("Finish Bake")
        self.report({"INFO"}, "Texture Baker: Bake Complete")
        return {"FINISHED"}


class CreateMaterialOperator(bpy.types.Operator):
    bl_idname = "object.texture_baker_create_material"
    bl_label = "Create"

    def execute(self, context):
        print_log("Create Material Start")

        Highpoly.create(context.scene.texture_baker_material_name)
        print_log(f"Create {context.scene.texture_baker_material_name} Material")
        self.report({"INFO"}, "Texture Baker: Material Created")
        return {"FINISHED"}


# Define a new UI panel
class TextureBakerPanel(bpy.types.Panel):
    bl_label = "Texture Baker"
    bl_idname = "OBJECT_PT_texture_baker"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout

        # Add the operator to the panel
        layout.label(text="Create HighPoly Material", icon="MATERIAL")
        layout.prop(context.scene, "texture_baker_material_name")
        layout.operator(CreateMaterialOperator.bl_idname)

        layout.separator()

        layout.label(text="Bake HighPoly to LowPoly", icon="IMAGE")
        layout.operator(BakeTextureOperator.bl_idname)


# Registration
def register():
    bpy.types.Scene.texture_baker_material_name = bpy.props.StringProperty(
        name="Mat. Name",
        description="Material Name",
        default="Default",
    )
    bpy.utils.register_class(CreateMaterialOperator)
    bpy.utils.register_class(BakeTextureOperator)
    bpy.utils.register_class(TextureBakerPanel)


def unregister():
    del bpy.types.Scene.texture_baker_material_name
    bpy.utils.unregister_class(CreateMaterialOperator)
    bpy.utils.unregister_class(BakeTextureOperator)
    bpy.utils.unregister_class(TextureBakerPanel)


if __name__ == "__main__":
    register()
