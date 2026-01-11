from __future__ import annotations


def temp_asset_key(*, project_id: str, run_id: str, asset_id: str, ext: str = "png") -> str:
    return f"temp/{project_id}/{run_id}/{asset_id}.{ext}"
