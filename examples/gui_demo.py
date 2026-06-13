"""scribe_frame GUI demo — zero mandatory OCR dependency.

Plugins activate automatically when installed:
  pip install any-provider     → OCR Shell shows model list + real OCR
  no plugins                  → shows placeholder

Usage:  python examples/gui_demo.py
Requires: pip install scribe-frame[gui]
"""

from __future__ import annotations

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTabWidget, QLabel, QHBoxLayout, QComboBox, QSplitter,
)
from PyQt6.QtCore import Qt

from scribe_frame.ui.theme import DARK_STYLE
from scribe_frame.ui.widgets import (
    PrimaryButton, OutlineButton,
    DropZone, ResultPanel, HardwarePanel,
)
from scribe_frame.provider_registry import ProviderRegistry
from scribe_frame.formatter_registry import FormatterRegistry
from scribe_frame.interfaces import HardwareInfo, BaseFormatter


# ── Built-in Raw Formatter (always available) ──
class _RawFormatter(BaseFormatter):
    format_id = "raw"
    label = "Raw"
    file_extension = "txt"
    supported_engines = ["*"]

    def format(self, result) -> str:
        if hasattr(result, "all_text"):
            return result.all_text
        return str(result)


FormatterRegistry.register(_RawFormatter())


# ── Optional hardware detection ──
def _detect_hardware() -> dict:
    """Try real detection; fall back to placeholder."""
    try:
        # Works if any provider package is installed
        from scribe.hardware import detect
        hw = detect()
        return {
            "GPU": hw.gpu_name or "N/A",
            "VRAM Total": f"{hw.vram_total_mb} MB ({hw.vram_total_mb / 1024:.1f} GB)",
            "VRAM Free": f"{hw.vram_free_mb} MB",
            "CUDA": hw.cuda_version or "N/A",
            "FP16": "Yes" if hw.supports_fp16 else "No",
            "CPU Cores": str(hw.cpu_cores),
            "RAM": f"{hw.ram_total_mb} MB ({hw.ram_total_mb / 1024:.1f} GB)",
            "Recommended Tier": hw.recommended_tier,
        }
    except Exception:
        return {
            "Status": "No hardware plugin installed",
            "Hint": "Install a provider package to enable detection",
            "Framework": "scribe-frame 0.1.0",
        }


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scribe Frame — UI Demo")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(DARK_STYLE)
        self._input_path: str | None = None

        tabs = QTabWidget()
        tabs.addTab(self._tab_ocr(), "OCR Shell")
        tabs.addTab(self._tab_hardware(), "Hardware")
        tabs.addTab(self._tab_about(), "About")
        self.setCentralWidget(tabs)

    # ── Tab 1: OCR Shell (plugin-aware) ──

    def _tab_ocr(self) -> QWidget:
        w = QWidget()
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── LEFT panel ──
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(8, 8, 8, 8)

        # Drop zone at top
        drop = DropZone("Drop Image Here")
        left_layout.addWidget(drop)

        # ── Plugin status ──
        ProviderRegistry.discover()
        FormatterRegistry.discover()
        providers = ProviderRegistry.list_providers()

        if not providers:
            status = QLabel(
                "No OCR plugin installed.\n"
                "Install any provider package and restart — "
                "models and presets will appear here automatically."
            )
            status.setStyleSheet(
                "color: #f59e0b; background: #1a1a2e; border: 1px solid #333; "
                "border-radius: 8px; padding: 12px; font-size: 13px;"
            )
            status.setWordWrap(True)
            left_layout.addWidget(status)
            engine_combo = preset_combo = None
        else:
            prov = providers[0]
            left_layout.addWidget(QLabel(f"Provider: {prov.name}"))

            left_layout.addWidget(QLabel("Engine"))
            engine_combo = QComboBox()
            for et in prov.list_engine_types():
                engine_combo.addItem(et, et)
            left_layout.addWidget(engine_combo)

            left_layout.addWidget(QLabel("Preset"))
            preset_combo = QComboBox()

            def _update_presets():
                preset_combo.clear()
                et = engine_combo.currentData()
                for p in prov.list_presets(et):
                    preset_combo.addItem(f"{p.name} ({p.recommended_vram_mb} MB)", p)

            _update_presets()
            engine_combo.currentIndexChanged.connect(_update_presets)
            left_layout.addWidget(preset_combo)

        # Format selector
        left_layout.addWidget(QLabel("Output Format"))
        format_combo = QComboBox()

        def _update_formats(*_args):
            format_combo.clear()
            et = engine_combo.currentData() if engine_combo else "general_ocr"
            for f in FormatterRegistry.list_for_engine(et):
                format_combo.addItem(f"{f.label} (.{f.file_extension})", f.format_id)
            if format_combo.count() == 0:
                format_combo.addItem("Raw (.txt)", "raw")

        _update_formats()
        if engine_combo:
            engine_combo.currentIndexChanged.connect(_update_formats)
        left_layout.addWidget(format_combo)

        # Buttons
        btns = QHBoxLayout()

        run = PrimaryButton("Run OCR")
        adv = OutlineButton("Advanced")
        btns.addWidget(run)
        btns.addWidget(adv)
        btns.addStretch()
        left_layout.addLayout(btns)
        left_layout.addStretch()

        # ── RIGHT panel: results ──
        result = ResultPanel()
        result.text = "Drop an image and click Run OCR..."

        # ── Wiring ──
        def _on_file(path):
            self._input_path = path
            result.text = f"Selected: {path}"

        drop.file_selected.connect(_on_file)

        def _on_run():
            if providers and self._input_path and preset_combo:
                try:
                    prov = providers[0]
                    preset = preset_combo.currentData()
                    engine = prov.create_engine(
                        engine_combo.currentData(), preset, device="gpu"
                    )
                    try:
                        raw = engine.predict(self._input_path)
                        fmt = FormatterRegistry.get(format_combo.currentData())
                        if fmt is None:
                            # Fallback to raw
                            result.text = raw.all_text if hasattr(raw, "all_text") else str(raw)
                        else:
                            result.text = fmt.format(raw)
                    finally:
                        engine.close()
                except Exception as e:
                    result.text = f"Recognition failed: {e}"
            else:
                result.text = (
                    "This is simulated output from the Scribe Frame UI Demo.\n\n"
                    "Install an OCR provider plugin to get real results."
                )

        run.clicked.connect(_on_run)

        splitter.addWidget(left)
        splitter.addWidget(result)
        splitter.setSizes([350, 550])

        root = QVBoxLayout(w)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(splitter)
        return w

    # ── Tab 2: Hardware (plugin-aware) ──

    def _tab_hardware(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Hardware Info")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #c0c0ff;")
        layout.addWidget(title)

        hw_panel = HardwarePanel()
        hw_panel.update_info(_detect_hardware())
        layout.addWidget(hw_panel)

        refresh = PrimaryButton("Refresh")
        refresh.clicked.connect(lambda: hw_panel.update_info(_detect_hardware()))
        layout.addWidget(refresh)
        layout.addStretch()

        return w

    # ── Tab 3: About ──

    def _tab_about(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("About Scribe Frame")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #c0c0ff;")
        layout.addWidget(title)

        ProviderRegistry.discover()
        n_providers = len(ProviderRegistry.list_providers())
        FormatterRegistry.discover()
        n_formatters = len(FormatterRegistry.list_all())

        info = QLabel(
            "scribe-frame is the plugin framework for the Scribe OCR Toolkit.\n\n"
            f"Installed Providers: {n_providers}\n"
            f"Installed Formatters: {n_formatters}\n\n"
            "This demo depends only on scribe-frame[gui].\n"
            "No OCR engine is required — plugins activate automatically."
        )
        info.setStyleSheet("color: #aaa; font-size: 14px; padding: 20px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()

        return w


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Scribe Frame UI Demo")
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
