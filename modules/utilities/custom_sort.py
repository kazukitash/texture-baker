def custom_sort(lst: list[str]) -> list[str]:
    """#が含まれているオブジェクトを後ろにソートする

    Args:
        lst (list[str]): ソート前のリスト

    Returns:
        list[str]: ソート後のリスト
    """

    # リスト内の各要素を#の有無に応じて2つのリストに分割
    with_hash, without_hash = [], []
    for item in lst:
        if "#" in item:
            with_hash.append(item)
        else:
            without_hash.append(item)

    # #を含む要素を後ろにソートして、元のリストに結合
    sorted_list = without_hash + sorted(with_hash)

    return sorted_list
