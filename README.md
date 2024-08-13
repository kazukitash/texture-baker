# Template Python

## 概要

python プロジェクトのテンプレート。リンターなどの開発支援ツールを導入する環境を揃えるためのリポジトリ。
以下のコマンドを実行する。

```sh
sh setup.sh
```

## 前提

- python3.1 系が入っていること

## 導入してある開発支援ツール

- ruff
  - flake8（リンター）,black（フォーマッター）,isort（インポーター）の代わり

## ビルド

```sh
sh compile.sh
```

## Blender に pip と pillow を入れる必要がある

```sh
cd ~/Downloads
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
/Applications/Blender.app/Contents/Resources/3.6/python/bin/python3.10 get-pip.py
/Applications/Blender.app/Contents/Resources/3.6/python/bin/python3.10 -m pip install pillow
```
