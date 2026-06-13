# Scribe Frame

**Plugin framework for the Scribe OCR Toolkit.**

`scribe-frame` is the lightweight, zero-hard-dependency foundation that defines
the plugin interfaces and registries.  The full `scribe` application layer
(OCR engines, formatters, GUI, CLI) is built *on top of* this framework.

## Architecture

```
┌─────────────────────────────────────────┐
│  scribe  (application layer)            │
│  engines · formatters · chunkers · GUI  │
├─────────────────────────────────────────┤
│  scribe-frame  (plugin framework)       │  ← this package
│  interfaces · registries · inspector    │
└─────────────────────────────────────────┘
```

Four plugin types, each with an abstract base class and a registry:

| Plugin type | Base class | Registry | entry_points group |
|-------------|-----------|----------|--------------------|
| Provider (OCR backend) | `BaseProvider` | `ProviderRegistry` | `scribe.providers` |
| Formatter (output format) | `BaseFormatter` | `FormatterRegistry` | `scribe.formatters` |
| Chunker (image pre-processor) | `BaseChunker` | `ChunkerRegistry` | `scribe.chunkers` |
| Command (CLI subcommand) | `BaseCommand` | `CommandRegistry` | `scribe.commands` |

📖 **Full plugin development guide:** [docs/PLUGINS.md](docs/PLUGINS.md)

## Quick start

```bash
pip install scribe-frame
```

### Write a Provider plugin

```python
# my_provider.py
from scribe_frame import BaseProvider, ModelSpec, EnginePreset

class MyProvider(BaseProvider):
    name = "my-ocr"

    def list_engine_types(self) -> list[str]:
        return ["general_ocr"]

    def list_models(self, engine_type=None) -> list[ModelSpec]:
        return [ModelSpec(id="my-model", name="MyModel", provider="my-ocr", engine_type="general_ocr")]

    def list_presets(self, engine_type=None) -> list[EnginePreset]:
        return [EnginePreset(id="fast", name="Fast", engine_type="general_ocr", recommended_vram_mb=1000)]

    def check_availability(self) -> bool:
        return True

    def create_engine(self, engine_type, preset, **config):
        ...  # return your engine instance

    def is_model_cached(self, model) -> bool:
        return True

    def download_model(self, model) -> bool:
        return True
```

Then register in `pyproject.toml`:

```toml
[project.entry-points."scribe.providers"]
my-ocr = "my_provider:MyProvider"
```

### Discover plugins at runtime

```python
from scribe_frame import ProviderRegistry, FormatterRegistry, ChunkerRegistry

ProviderRegistry.discover()
for p in ProviderRegistry.list_providers():
    print(p.name, p.list_engine_types())
```

### GUI plugin inspector

```bash
pip install scribe-frame[gui]
scribe-frame-inspect
```

## API reference

### `BaseProvider`

| Method | Description |
|--------|------------|
| `name` | Unique provider identifier |
| `list_engine_types()` | `["general_ocr", "document_parsing", ...]` |
| `list_models(engine_type?)` | Available model specs |
| `list_presets(engine_type?)` | Ready-to-use model combinations |
| `create_engine(engine_type, preset, **config)` | Instantiate an engine |
| `is_model_cached(model)` | Check if model files exist locally |
| `download_model(model)` | Trigger model download |
| `recommend_preset(engine_type, hw?)` | Auto-select based on VRAM |
| `refresh_remote_catalog()` | Re-fetch from server |

### `BaseFormatter`

| Property / Method | Description |
|------------------|------------|
| `format_id` | Unique id (e.g. `"json"`) |
| `label` | Human-readable label |
| `file_extension` | `"json"`, `"md"`, `"txt"` |
| `supported_engines` | `["*"]` or `["general_ocr", ...]` |
| `format(result)` | Convert engine result → string |

### `BaseChunker`

| Property / Method | Description |
|------------------|------------|
| `name` | Unique id (e.g. `"default"`) |
| `chunk(image_path)` | Return `list[ChunkInfo]` or `None` |

### Data classes

- **`ModelSpec`** — model metadata (id, name, role, tier, languages, …)
- **`EnginePreset`** — preset model combination for an engine
- **`HardwareInfo`** — GPU/CPU/RAM info with `recommended_tier` helper
- **`ChunkInfo`** — per-chunk metadata (path, y_offset, index, total)

### `BaseCommand`

| Property / Method | Description |
|------------------|------------|
| `name` | Subcommand name (e.g. `"scan"`) |
| `help` | One-line description |
| `register(parser)` | Add arguments to an argparse subparser |
| `run(args)` | Execute and return exit code |

## CLI

```bash
$ scribe-frame list        # List all installed plugins
$ scribe-frame info        # Framework version + plugin counts
$ scribe-frame scan ...    # Plugin commands appear automatically
$ scribe-frame-inspect     # GUI plugin inspector
```

## License

Apache-2.0 — see [LICENSE](LICENSE).

## Examples

See [`examples/demo.py`](examples/demo.py) for a complete walkthrough:
defining a Provider + Formatter, registering them, creating an engine, and formatting output.

