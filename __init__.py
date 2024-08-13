import bpy  # type: ignore

from .modules.models.highpoly import Highpoly
from .modules.utilities.bake_texture import bake_texture
from .modules.utilities.print_log import print_log

bl_info = {
    "name": "Texture Baker",
    "author": "kazukitash",
    "version": (2, 3),
    "blender": (4, 1, 1),
    "location": "View3D > UI > Texture Baker",
    "description": "Bake Normal and AmbientOcclusion Textures from HighPoly",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}


# Define a new operator (action or function)
class BakeTextureOperator(bpy.types.Operator):
    bl_idname = "object.texture_baker_bake_texture"
    bl_label = "Bake"

    def execute(self, context):
        bake_texture()
        self.report({"INFO"}, "Texture Baker: Bake Complete")
        return {"FINISHED"}


class CreateMaterialOperator(bpy.types.Operator):
    bl_idname = "object.texture_baker_create_material"
    bl_label = "Create"

    def execute(self, context):
        print_log("Create Material Start")

        Highpoly.create(context.scene.texture_baker_base_name)
        print_log(f"Create Material. hi_M_{context.scene.texture_baker_base_name}")
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
        layout.prop(context.scene, "texture_baker_base_name")
        layout.operator(CreateMaterialOperator.bl_idname)

        layout.separator()

        layout.label(text="Bake HighPoly to LowPoly", icon="IMAGE")
        layout.operator(BakeTextureOperator.bl_idname)


# Registration
def register():
    bpy.types.Scene.texture_baker_base_name = bpy.props.StringProperty(
        name="Base Name",
        description="Base Name of Material",
        default="Default",
    )
    bpy.utils.register_class(CreateMaterialOperator)
    bpy.utils.register_class(BakeTextureOperator)
    bpy.utils.register_class(TextureBakerPanel)


def unregister():
    del bpy.types.Scene.texture_baker_base_name
    bpy.utils.unregister_class(CreateMaterialOperator)
    bpy.utils.unregister_class(BakeTextureOperator)
    bpy.utils.unregister_class(TextureBakerPanel)


if __name__ == "__main__":
    register()
