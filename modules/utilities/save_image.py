import os

import bpy  # type:ignore


def save_image(material: bpy.types.Material):
    nodes = material.node_tree.nodes

    nodes["BaseColor"].image.pack()
    image = nodes["BaseColor"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    print(f"Texture Baker: Save {filename}")

    nodes["RMO"].image.pack()
    image = nodes["RMO"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    print(f"Texture Baker: Save {filename}")

    nodes["Normal"].image.pack()
    image = nodes["Normal"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    print(f"Texture Baker: Save {filename}")
