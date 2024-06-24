from datetime import datetime


def print_log(message: str):
    """ログを出力する"""

    time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print(f"[{time}] Texture Baker: {message}")
