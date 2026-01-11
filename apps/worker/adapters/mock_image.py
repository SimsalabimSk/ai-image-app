from __future__ import annotations

import io
import random
from dataclasses import dataclass
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class MockImageResult:
    mime_type: str
    bytes: bytes
    width: int
    height: int


def _parse_resolution(resolution: str) -> Tuple[int, int]:
    # e.g., "1024x1024"
    parts = resolution.lower().split("x")
    if len(parts) != 2:
        raise ValueError("Invalid resolution format")
    return int(parts[0]), int(parts[1])


def generate_deterministic_png(
    *,
    intent_text: str,
    resolution: str,
    seed: Optional[int],
) -> MockImageResult:
    """Deterministic placeholder PNG.

    Determinism:
    - If seed is provided, output is stable for same (seed, resolution).
    - If seed is None, we still derive a stable seed from intent_text.
    """
    width, height = _parse_resolution(resolution)

    if seed is None:
        seed = abs(hash(intent_text)) % (2**31 - 1)

    rng = random.Random(seed)

    # Create a simple noise-like pattern + stamped seed
    img = Image.new("RGB", (width, height))
    px = img.load()

    # Sparse deterministic pattern for speed (not full noise for 1024^2)
    step = max(4, min(width, height) // 128)
    for y in range(0, height, step):
        for x in range(0, width, step):
            r = rng.randrange(0, 256)
            g = rng.randrange(0, 256)
            b = rng.randrange(0, 256)
            # Fill a small block
            for yy in range(y, min(y + step, height)):
                for xx in range(x, min(x + step, width)):
                    px[xx, yy] = (r, g, b)

    draw = ImageDraw.Draw(img)
    text = f"MOCK • seed={seed} • {width}x{height}"
    # Default font is OK for placeholder
    draw.rectangle([(0, 0), (width, 40)], fill=(0, 0, 0))
    draw.text((10, 10), text, fill=(255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return MockImageResult(
        mime_type="image/png",
        bytes=buf.getvalue(),
        width=width,
        height=height,
    )
