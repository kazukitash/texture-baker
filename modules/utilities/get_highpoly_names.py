import bpy  # type: ignore


def get_highpoly_names() -> list[str]:
    """シーン内のハイポリメッシュの名前を取得する
        hi_で始まるオブジェクトを取得する

    Returns:
        list[str]: ハイポリメッシュの名前のリスト
    """

    highpoly_names = []

    for ob in bpy.context.visible_objects:
        if ob.type != "MESH":
            continue

        if ob.name.startswith("hi_"):
            highpoly_names.append(ob.name)

    return highpoly_names
