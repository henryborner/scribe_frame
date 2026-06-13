"""scribe_frame 完整示例 — 演示插件注册、发现、引擎调用、格式化全流程。

运行：  python examples/demo.py
需要：  pip install scribe-frame[gui]
"""

from __future__ import annotations

from scribe_frame import (
    BaseProvider, BaseFormatter, BaseChunker, ChunkInfo,
    ModelSpec, EnginePreset, HardwareInfo,
    ProviderRegistry, FormatterRegistry, ChunkerRegistry,
)


# ═══════════════════════════════════════════════════════════════════════
# 第一步：写一个虚拟 Provider（真正的 Provider 会封装 PaddleOCR / Tesseract）
# ═══════════════════════════════════════════════════════════════════════

class DemoProvider(BaseProvider):
    name = "demo"

    def list_engine_types(self) -> list[str]:
        return ["general_ocr"]

    def list_models(self, engine_type=None) -> list[ModelSpec]:
        return [
            ModelSpec(
                id="demo.fast", name="DemoFast", provider="demo",
                engine_type="general_ocr", tier="mobile", display_name="Demo Fast",
            ),
            ModelSpec(
                id="demo.accurate", name="DemoAccurate", provider="demo",
                engine_type="general_ocr", tier="server", display_name="Demo Accurate",
            ),
        ]

    def list_presets(self, engine_type=None) -> list[EnginePreset]:
        return [
            EnginePreset(
                id="demo_fast", name="Demo · Fast",
                engine_type="general_ocr", recommended_vram_mb=500,
            ),
            EnginePreset(
                id="demo_accurate", name="Demo · Accurate",
                engine_type="general_ocr", recommended_vram_mb=4000,
            ),
        ]

    def check_availability(self) -> bool:
        return True

    def create_engine(self, engine_type, preset, **config):
        # 真实实现会在这里初始化 PaddleOCR / Tesseract pipeline
        class DemoEngine:
            def predict(self, image_path):
                print(f"  [DemoEngine] 假装识别: {image_path}")
                return {"text": "Hello from DemoEngine!", "preset": preset.id}
        return DemoEngine()

    def is_model_cached(self, model) -> bool:
        return True

    def download_model(self, model) -> bool:
        print(f"  [Demo] 模拟下载: {model.name}")
        return True


# ═══════════════════════════════════════════════════════════════════════
# 第二步：写一个虚拟 Formatter
# ═══════════════════════════════════════════════════════════════════════

class DemoFormatter(BaseFormatter):
    format_id = "demo"
    label = "Demo Format"
    file_extension = "txt"
    supported_engines = ["*"]

    def format(self, result) -> str:
        if isinstance(result, dict):
            return f"[{result.get('preset', '?')}] {result.get('text', '')}"
        return str(result)


# ═══════════════════════════════════════════════════════════════════════
# 第三步：注册到框架
# ═══════════════════════════════════════════════════════════════════════

ProviderRegistry.register(DemoProvider())
FormatterRegistry.register(DemoFormatter())

# 真实场景中，第三方包通过 pyproject.toml 的 entry_points 注册：
#
#   [project.entry-points."scribe.providers"]
#   demo = "my_package:DemoProvider"
#
# 用户只需 pip install 即可自动被发现。


# ═══════════════════════════════════════════════════════════════════════
# 第四步：使用框架
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 50)
    print("  Scribe Frame — 完整示例")
    print("=" * 50)

    # ── 发现所有 Provider ──
    print("\n📦 已注册的 Provider:")
    for p in ProviderRegistry.list_providers():
        print(f"  · {p.name}  → 引擎: {p.list_engine_types()}")

    # ── 发现所有 Formatter ──
    print("\n📝 已注册的 Formatter:")
    for f in FormatterRegistry.list_all():
        print(f"  · {f.format_id}  → .{f.file_extension}")

    # ── 发现所有 Chunker ──
    print("\n✂️  已注册的 Chunker:")
    for c in ChunkerRegistry._chunkers.values():
        print(f"  · {c.name}")
    if not ChunkerRegistry._chunkers:
        print("  (无 — chunker 是可选插件)")

    # ── 选一个 Provider，创建引擎 ──
    print("\n🔧 创建引擎...")
    prov = ProviderRegistry.get_provider("demo")  # 精确获取，不影响已安装的其他 Provider
    if prov is None:
        print("  ❌ Demo Provider 未注册！")
        return
    print(f"  使用 Provider: {prov.name}")

    presets = prov.list_presets("general_ocr")
    print(f"  可用 Presets: {[p.id for p in presets]}")

    # 根据硬件自动推荐
    hw = HardwareInfo(gpu_available=True, vram_total_mb=8000)
    best = prov.recommend_preset("general_ocr", hw)
    print(f"  硬件: {hw.vram_total_mb}MB VRAM → 推荐 {best.id}")

    engine = prov.create_engine("general_ocr", best)
    result = engine.predict("example.png")
    print(f"  识别结果: {result}")

    # ── 格式化输出 ──
    print("\n📄 格式化输出:")
    for fmt in FormatterRegistry.list_all():
        try:
            output = fmt.format(result)
            print(f"  [{fmt.format_id}] {output[:80]}")
        except Exception:
            pass  # 不同 formatter 可能要求不同的 result 类型，跳过不兼容的

    # ── 可选：启动 GUI 检查器 ──
    print("\n" + "=" * 50)
    print("  要启动插件检查器 GUI，运行:")
    print("  scribe-frame-inspect")
    print("=" * 50)


if __name__ == "__main__":
    main()
