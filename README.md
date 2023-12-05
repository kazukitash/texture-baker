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
zip -r texture-baker.zip texture-baker/ -x "*.venv*" -x "*.git*" -x "*.vscode*" -x "*.gitignore*" -x "*poetry.lock*" -x "*pyproject.toml*" -x "*README.md*" -x "*setup.sh*" -x "*.DS_Store*"
```
