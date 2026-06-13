# Scribe Frame — Plugin Development Guide

## Overview

Scribe Frame has **four** plugin types. Implement the right base class, register via
`pyproject.toml` entry_points, and your plugin is discovered automatically.

| Plugin type | Base class | entry_points group | Difficulty |
|------------|-----------|-------------------|------------|
| **Formatter** | `BaseFormatter` | `scribe.formatters` | ★☆☆ (20 lines) |
| **Chunker** | `BaseChunker` | `scribe.chunkers` | ★★☆ (50 lines) |
| **Command** | `BaseCommand` | `scribe.commands` | ★★☆ (40 lines) |
| **Provider** | `BaseProvider` | `scribe.providers` | ★★★ (50+ lines) |

All plugins are discovered at runtime — no import, no hardcoding, no config file.

---

## 1. Formatter Plugin

Turns OCR results into a string (JSON, Markdown, CSV, …).

### Template

```python
from scribe_frame import BaseFormatter

class CsvFormatter(BaseFormatter):
    format_id = "csv"                    # unique id
    label = "CSV (comma-separated)"      # shown in GUI dropdown
    file_extension = "csv"
    supported_engines = ["*"]            # or ["general_ocr"]

    def format(self, result) -> str:
        # result is OCRResult or StructureResult
        lines = ["text,confidence"]
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    lines.append(f'"{line.text}",{line.confidence:.2f}')
        return "\n".join(lines)
```

### Register

```toml
# pyproject.toml
[project.entry-points."scribe.formatters"]
csv = "my_package.csv_fmt:CsvFormatter"
```

That's it. `pip install` your package and every Scribe GUI/CLI will offer CSV as an output format.

---

## 2. Chunker Plugin

Splits large images into manageable pieces before OCR.

### Template

```python
from scribe_frame import BaseChunker, ChunkInfo

class GridChunker(BaseChunker):
    name = "grid"

    def chunk(self, image_path: str) -> list[ChunkInfo] | None:
        import cv2, numpy as np
        from pathlib import Path
        import tempfile

        with open(image_path, "rb") as f:
            data = np.frombuffer(f.read(), np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is None:
            return None

        h, w = img.shape[:2]
        if h <= 2000 and w <= 2000:
            return None  # no chunking needed

        # Split into 1000×1000 grid
        chunks = []
        tmp = Path(tempfile.mkdtemp(prefix="grid_"))
        idx = 0
        for y in range(0, h, 1000):
            for x in range(0, w, 1000):
                y2, x2 = min(y + 1000, h), min(x + 1000, w)
                crop = img[y:y2, x:x2]
                path = tmp / f"crop_{idx:04d}.png"
                cv2.imwrite(str(path), crop)
                chunks.append(ChunkInfo(
                    path=str(path), y_offset=y, index=idx,
                    total=((h-1)//1000+1) * ((w-1)//1000+1)
                ))
                idx += 1
        return chunks
```

### Register

```toml
[project.entry-points."scribe.chunkers"]
grid = "my_package.grid_chunker:GridChunker"
```

Return `None` when no chunking is needed. The `ChunkedPredictor` middleware
handles the loop + merge + cleanup automatically.

---

## 3. Command Plugin

Adds a subcommand to `scribe-frame` CLI.

### Template

```python
from scribe_frame import BaseCommand

class ExportCommand(BaseCommand):
    name = "export"
    help = "Export OCR results to a ZIP archive"

    def register(self, parser) -> None:
        parser.add_argument("input", help="Image or directory")
        parser.add_argument("-o", "--output", required=True, help="ZIP path")

    def run(self, args) -> int:
        import zipfile
        print(f"Exporting {args.input} → {args.output}...")
        with zipfile.ZipFile(args.output, "w") as zf:
            zf.write(args.input)
        print("Done.")
        return 0
```

### Register

```toml
[project.entry-points."scribe.commands"]
export = "my_package.commands:ExportCommand"
```

Then:
```bash
$ scribe-frame export my_image.png -o results.zip
```

---

## 4. Provider Plugin

Wraps an OCR engine (PaddleOCR, Tesseract, …) so all Scribe tools can use it.

### Template

```python
from scribe_frame import BaseProvider, ModelSpec, EnginePreset

class MyProvider(BaseProvider):
    name = "my-ocr"

    def list_engine_types(self):
        return ["general_ocr"]

    def list_models(self, engine_type=None):
        return [
            ModelSpec(
                id="my-ocr.fast", name="FastModel",
                provider="my-ocr", engine_type="general_ocr",
                tier="mobile", display_name="Fast Model",
            )
        ]

    def list_presets(self, engine_type=None):
        return [
            EnginePreset(
                id="my_fast", name="My OCR · Fast",
                engine_type="general_ocr",
                recommended_vram_mb=1000,
                model_selections={"det": "fast_det", "rec": "fast_rec"},
            )
        ]

    def check_availability(self):
        try:
            import my_ocr_lib
            return True
        except ImportError:
            return False

    def create_engine(self, engine_type, preset, **config):
        # Return an object with a .predict(path) method (and optionally .close())
        class MyEngine:
            def __init__(self, preset, config):
                self._preset = preset
            def predict(self, image_path):
                # Your OCR logic here
                from scribe.results.base import OCRResult, Page, Block, TextLine, BBox, BlockType
                block = Block(type=BlockType.TEXT, content="recognized text",
                              bbox=BBox(0, 0, 100, 20),
                              lines=[TextLine(text="recognized text", bbox=BBox(0, 0, 100, 20))])
                return OCRResult(pages=[Page(blocks=[block])])
            def close(self):
                pass
        return MyEngine(preset, config)

    def is_model_cached(self, model):
        return True  # or check filesystem

    def download_model(self, model):
        return True  # or trigger download
```

### Register

```toml
[project.entry-points."scribe.providers"]
my-ocr = "my_package.provider:MyProvider"
```

### Engine return type

Your `engine.predict(path)` must return an object compatible with formatters:
- **General OCR** → `OCRResult` (from `scribe.results.base`)
- **Document Parsing** → `StructureResult` (from `scribe.results.base`)

For third-party providers without access to `scribe.results`, any object with
`.pages[].blocks[].content` and `.pages[].blocks[].lines[].text` works with
the built-in Raw formatter.

---

## GUI Customization

### Using framework widgets

```python
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTabWidget
from scribe_frame.ui.theme import DARK_STYLE
from scribe_frame.ui.widgets import (
    PrimaryButton, OutlineButton, DropZone, ResultPanel, HardwarePanel,
)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(DARK_STYLE)
        self.setWindowTitle("My OCR Tool")

        tabs = QTabWidget()
        tabs.addTab(self._ocr_tab(), "OCR")
        tabs.addTab(self._settings_tab(), "Settings")
        self.setCentralWidget(tabs)

    def _ocr_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        # Reusable widgets — just drop them in
        drop = DropZone("Drop Image Here")
        drop.file_selected.connect(self._handle_file)
        layout.addWidget(drop)

        run = PrimaryButton("Run OCR")
        run.clicked.connect(self._run_ocr)
        layout.addWidget(run)

        self.result = ResultPanel()
        layout.addWidget(self.result)
        return w
```

### Adding tabs dynamically

```python
from scribe_frame.ui.widgets import TabManager

self._tab_mgr = TabManager(self._tabs)
self._tab_mgr.add_tab(HardwarePanel(), "Hardware")
self._tab_mgr.on_tab_changed(self._on_tab_switch)
```

### Plugin-aware tab building

Plugins can contribute tabs at runtime:

```python
# Detect installed providers
from scribe_frame.provider_registry import ProviderRegistry
ProviderRegistry.discover()
providers = ProviderRegistry.list_providers()

if providers:
    # Show engine selector + presets
    prov = providers[0]
    for engine_type in prov.list_engine_types():
        print(f"Engine available: {engine_type}")
else:
    # Show placeholder
    print("No OCR plugin installed.")
```

### Full example

See [`examples/gui_demo.py`](../examples/gui_demo.py) for a complete,
runnable GUI built entirely on framework widgets (200 lines).

---

## CLI Usage

### Built-in commands

```bash
$ scribe-frame list        # List all installed plugins
$ scribe-frame info        # Framework version + plugin counts
$ scribe-frame --help      # Show all available commands
```

### Plugin commands (when installed)

```bash
$ scribe-frame scan image.png -f json
$ scribe-frame parse document.pdf -f markdown -o output.md
$ scribe-frame batch *.png -o results/
```

Any package that registers a `scribe.commands` entry_point adds its
subcommands automatically.

### GUI

```bash
$ scribe-frame-inspect     # Plugin inspector GUI
$ python examples/gui_demo.py  # Full demo app
```

---

## Packaging & Publishing

### Minimal pyproject.toml for a plugin package

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "scribe-plugin-myocr"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["scribe-frame>=0.1.0"]

[project.entry-points."scribe.providers"]
my-ocr = "scribe_plugin_myocr.provider:MyProvider"

[tool.setuptools.packages.find]
where = ["src"]
```

### Publishing

```bash
pip install build twine
python -m build
twine upload dist/*
```

Users then:
```bash
pip install scribe-plugin-myocr
scribe-frame list          # Your provider appears automatically
```

---

## Data Classes Reference

### ModelSpec

```python
@dataclass
class ModelSpec:
    id: str                  # "paddleocr.text_detection.PP-OCRv6_tiny_det"
    name: str                # "PP-OCRv6_tiny_det"
    provider: str            # "paddleocr"
    engine_type: str         # "general_ocr" | "document_parsing"
    role: str = ""           # "text_detection", "formula_recognition", ...
    display_name: str = ""
    tier: str = "medium"     # "mobile" | "medium" | "server"
    vram_estimate_mb: int = 0
    download_size_mb: int = 0
    description: str = ""
    version: str = ""
    languages: list[str] = ["zh", "en"]
```

### EnginePreset

```python
@dataclass
class EnginePreset:
    id: str                  # "ocr_fast"
    name: str                # "OCR · Fast"
    engine_type: str         # "general_ocr"
    recommended_vram_mb: int # 1500
    model_selections: dict   # {"text_detection": "PP-OCRv6_tiny_det", ...}
    extra_config: dict       # {"precision": "fp16", ...}
```

### HardwareInfo

```python
@dataclass
class HardwareInfo:
    gpu_available: bool = False
    gpu_name: str = ""
    vram_total_mb: int = 0
    # ... plus cpu_cores, ram_total_mb, etc.
    # helpers: .recommended_tier, .supports_fp16
```
