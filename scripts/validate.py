#!/usr/bin/env python3
"""
跳海社区 Skill 数据校验脚本

用法：
    python scripts/validate.py              # 校验所有数据文件
    python scripts/validate.py data/stores  # 校验指定目录
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("需要安装 PyYAML: pip install pyyaml")
    sys.exit(1)

try:
    import jsonschema
except ImportError:
    jsonschema = None
    print("提示: 安装 jsonschema 可启用 schema 校验: pip install jsonschema")

ROOT = Path(__file__).parent.parent
SCHEMA_DIR = ROOT / "data" / "_schema"
DATA_DIR = ROOT / "data"

# 数据目录与 schema 的映射
SCHEMA_MAP = {
    "stores": "store.schema.json",
    "events": "event.schema.json",
    "menus": "menu.schema.json",
    "social-good": "social-good.schema.json",
    "media": "media.schema.json",
}

# 热数据目录（必须有 _meta.last_updated）
HOT_DATA_DIRS = {"menus", "events"}

errors = []
warnings = []
files_checked = 0


def check_yaml_syntax(filepath: Path) -> dict | None:
    """检查 YAML 语法是否正确，返回解析后的数据"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data
    except yaml.YAMLError as e:
        errors.append(f"YAML 语法错误: {filepath}\n  {e}")
        return None


def check_meta(filepath: Path, data: dict, required: bool):
    """检查 _meta 字段"""
    if data is None:
        return

    meta = data.get("_meta")
    if required and meta is None:
        errors.append(f"缺少 _meta 字段（热数据必须有）: {filepath}")
        return

    if meta is not None:
        if "last_updated" not in meta:
            errors.append(f"_meta 缺少 last_updated: {filepath}")


def check_schema(filepath: Path, data: dict, schema_file: str):
    """用 JSON Schema 校验数据"""
    if jsonschema is None or data is None:
        return

    schema_path = SCHEMA_DIR / schema_file
    if not schema_path.exists():
        warnings.append(f"Schema 文件不存在: {schema_path}")
        return

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema 校验失败: {filepath}\n  {e.message}")


def check_required_fields_social_good(filepath: Path, data: dict):
    """社区公益故事的额外字段检查"""
    if data is None:
        return

    stories = data.get("stories", [])
    for i, story in enumerate(stories):
        if not story.get("id"):
            errors.append(f"公益故事缺少 id: {filepath} 第 {i + 1} 条")
        if not story.get("title"):
            errors.append(f"公益故事缺少 title: {filepath} 第 {i + 1} 条")
        if not story.get("category"):
            errors.append(f"公益故事缺少 category: {filepath} 第 {i + 1} 条")

        # 检查 source URL 格式
        for source in story.get("source", []):
            url = source.get("url", "")
            if url and not url.startswith("http"):
                errors.append(f"无效的 source URL: {filepath} 第 {i + 1} 条: {url}")


def validate_directory(target_dir: Path):
    """校验指定目录下的所有 YAML 文件"""
    global files_checked

    for filepath in sorted(target_dir.rglob("*.yaml")):
        # 跳过 schema 目录
        if "_schema" in filepath.parts:
            continue

        files_checked += 1
        data = check_yaml_syntax(filepath)

        if data is None:
            continue

        # 确定数据所属目录
        rel = filepath.relative_to(DATA_DIR)
        top_dir = rel.parts[0] if len(rel.parts) > 1 else None

        # 热数据 _meta 检查
        is_hot = top_dir in HOT_DATA_DIRS
        check_meta(filepath, data, required=is_hot)

        # Schema 校验
        if top_dir in SCHEMA_MAP:
            check_schema(filepath, data, SCHEMA_MAP[top_dir])

        # 社区公益故事额外检查
        if top_dir == "social-good":
            check_required_fields_social_good(filepath, data)


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_DIR

    if not target.exists():
        print(f"目录不存在: {target}")
        sys.exit(1)

    print(f"校验目录: {target}\n")
    validate_directory(target)

    # 输出结果
    if warnings:
        print(f"⚠️  {len(warnings)} 个警告:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print(f"❌ {len(errors)} 个错误:")
        for e in errors:
            print(f"  - {e}")
        print(f"\n共检查 {files_checked} 个文件，发现 {len(errors)} 个错误。")
        sys.exit(1)
    else:
        print(f"✅ 共检查 {files_checked} 个文件，全部通过。")
        sys.exit(0)


if __name__ == "__main__":
    main()
