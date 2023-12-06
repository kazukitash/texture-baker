import re

from ..models.bake_object import BakeObject


def get_bake_objects(highpoly_names: list[str]) -> list[BakeObject]:
    """bakeオブジェクトの情報を取得する
        hi_A_Bの場合、AにBakeする
        hi_A#_Bの場合、ACやADなど#を.*にしてregexしたメッシュにBakeする

    Returns:
        list[dict]: bakeオブジェクトの情報のリスト
    """

    bake_objects: list[BakeObject] = []

    for highpoly_name in highpoly_names:
        lowpoly_name = highpoly_name.lstrip("hi_").split("_")[0].replace("#", ".*")

        pattern = re.compile(lowpoly_name)
        match_bakes: list[BakeObject] = list(
            filter(lambda m: pattern.search(m["target"]), bake_objects)
        )
        if len(match_bakes) == 0:
            bake_object: BakeObject = {
                "target": lowpoly_name,
                "sources": [highpoly_name],
            }
            bake_objects.append(bake_object)
        else:
            for bake in match_bakes:
                bake["sources"].append(highpoly_name)

    return bake_objects
