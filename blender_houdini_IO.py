bl_info = {
    "name": "Houdini Bridge",
    "author": "You",
    "version": (1, 1),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Houdini Bridge",
    "description": "Send and receive geometry between Blender and Houdini, with scene sync",
    "category": "3D View",
}


import bpy
import os

def get_geo_base_path():
    possible_path = os.path.expanduser(os.path.join(os.getenv("JOB", ""), "GEO/",))
    if os.path.exists(possible_path):
        return os.path.dirname(possible_path)
    else:
        return None

def get_versioned_path(version_number):
    base = get_geo_base_path()
    if base:
        export_path = os.path.join(base, f"Edit_{str(version_number).zfill(2)}_Return.obj")
        return export_path
    else:
        return None

def get_import_path(version_number):
    base = get_geo_base_path()
    if base:
        import_path = os.path.join(base, f"Edit_{str(version_number).zfill(2)}.obj")
        return import_path
    else:
        return None

class HB_OT_export_to_houdini(bpy.types.Operator):
    bl_idname = "hb.export_to_houdini"
    bl_label = "Export to Houdini"
    bl_description = "Export selected geometry to Houdini as versioned OBJ"

    def execute(self, context):
        version_number = context.scene.version_number
        export_path = get_versioned_path(version_number)

        if export_path:
            os.makedirs(os.path.dirname(export_path), exist_ok=True)

            bpy.ops.export_scene.obj(
                filepath=export_path,
                use_selection=True,
                axis_forward='-Y',
                axis_up='Z',
                use_materials=False,
                use_mesh_modifiers=True
            )
            self.report({'INFO'}, f"Exported to {export_path}")
        else:
            self.report({'ERROR'}, "Could not determine export path")

        return {'FINISHED'}

class HB_OT_refresh_from_houdini(bpy.types.Operator):
    bl_idname = "hb.refresh_from_houdini"
    bl_label = "Refresh From Houdini"
    bl_description = "Import versioned OBJ from Houdini"

    def execute(self, context):
        version_number = context.scene.version_number
        import_path = get_import_path(version_number)

        if import_path and os.path.exists(import_path):
            bpy.ops.import_scene.obj(
                filepath=import_path,
                axis_forward='-Y',
                axis_up='Z',
                use_split_objects=True,
                use_split_groups=True
            )
            self.report({'INFO'}, f"Imported from {import_path}")
        else:
            self.report({'ERROR'}, "OBJ not found")

        return {'FINISHED'}

class HB_PT_panel(bpy.types.Panel):
    bl_label = "Houdini Bridge"
    bl_idname = "HB_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Houdini'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "version_number", text="Version")
        layout.operator("hb.export_to_houdini", icon="EXPORT")
        layout.operator("hb.refresh_from_houdini", icon="IMPORT")

classes = (
    HB_OT_export_to_houdini,
    HB_OT_refresh_from_houdini,
    HB_PT_panel,
)

def register():
    bpy.types.Scene.version_number = bpy.props.IntProperty(name="Version Number", default=1, min=1)
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    del bpy.types.Scene.version_number
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

