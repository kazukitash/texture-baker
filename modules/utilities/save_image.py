import os

import bpy  # type:ignore


def save_image(material: bpy.types.Material):
    nodes = material.node_tree.nodes

    image = nodes["BaseColor"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    image.pack()
    print(f"Texture Baker: Save {filename}")

    image = nodes["RMO"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    image.pack()
    print(f"Texture Baker: Save {filename}")

    image = nodes["Normal"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    image.pack()
    print(f"Texture Baker: Save {filename}")
