# Template Python

## 概要

pythonプロジェクトのテンプレート。リンターなどの開発支援ツールを導入する環境を揃えるためのリポジトリ。
以下のコマンドを実行する。

```
sh setup.sh
```

## 前提

- python3.1系が入っていること

## 導入してある開発支援ツール

- ruff
  - flake8（リンター）,black（フォーマッター),isort（インポーター）の代わり

```bash
rm texture-baker.zip && zip -r texture-baker.zip texture-baker/ -x "*.venv*" -x "*.git*" -x "*.vscode*" -x "*.gitignore*" -x "*poetry.lock*" -x "*pyproject.toml*" -x "*README.md*" -x "*setup.sh*" -x "*.DS_Store*"
```

## Blenderにpipとpillowを入れる必要がある。

```
cd ~/Downloads
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
/Applications/Blender.app/Contents/Resources/3.6/python/bin/python3.10 get-pip.py
/Applications/Blender.app/Contents/Resources/3.6/python/bin/python3.10 -m pip install pillow
```
