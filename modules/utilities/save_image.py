import os

import bpy  # type:ignore
from PIL import Image


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
    # Refrection用に画像を反転して保存
    image = Image.open(filename)
    rgb_image = image.convert('RGB')
    r, g, b = rgb_image.split()
    gray_image = r.point(lambda i: 255 - i)
    ref_filename = filename.replace("RMO.tga", "REF.tga")
    gray_image.save(ref_filename)
    print(f"Texture Baker: Save {filename}")

    image = nodes["Normal"].image
    filename = bpy.path.abspath(f"//{image.name.split('.', 1)[0]}.tga")
    if os.path.exists(filename):
        os.remove(filename)
    image.save(filepath=filename)
    image.pack()
    print(f"Texture Baker: Save {filename}")
