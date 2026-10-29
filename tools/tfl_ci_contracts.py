#!/usr/bin/env python3
"""TFL Amplio static integration gate. No native/GPU runtime certification."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
def prop(name: str) -> str:
    source = (ROOT / "gradle.properties").read_text()
    found = re.search(r"^" + re.escape(name) + r"=(.+)$", source, re.M)
    assert found, f"Missing {name} in gradle.properties"
    return found.group(1).strip()

meta = json.loads((ROOT / "src/main/resources/fabric.mod.json").read_text())
mixins = json.loads((ROOT / "src/main/resources/amplio.mixins.json").read_text())
gradle = (ROOT / "build.gradle.kts").read_text()
assert meta["id"] == "amplio"
assert meta["environment"] == "client"
assert meta["depends"]["minecraft"] == "1.8.9"
assert meta["depends"]["argentum"].startswith(">=")
assert prop("minecraft_version") == "1.8.9"
assert prop("feather_build") == "2"
assert prop("fabric_version") == "0.19.5"
assert prop("argentum_version").startswith("1.0.2")
assert "JavaLanguageVersion.of(25)" in gradle
assert meta["mixins"] == ["amplio.mixins.json"]
assert mixins["required"] is True
for mixin in ["MixinCameraJitter", "MixinScaleWorld", "MixinScaleViewport", "MixinUpscalingOptions"]:
    assert mixin in mixins["client"], f"Missing expected graphics mixin {mixin}"
for path in [
    "src/main/java/us/z1x/amplio/upscale/Fsr1Upscaler.java",
    "src/main/java/us/z1x/amplio/upscale/DlssUpscaler.java",
    "native/CMakeLists.txt",
    "native/src/amplio.cpp",
    ".github/workflows/build.yml",
]:
    assert (ROOT / path).is_file(), f"Required source missing: {path}"
assert "pylon" in meta["depends"], "Review the runtime dependency contract before changing Pylon"
print("PASS: Amplio/Argentum/Java 25 source and dependency metadata")
print("BLOCKED FOR TFL: Pylon runtime requirement conflicts with unverified Legacy LWJGL3 coexistence")
print("RUNTIME NOT CERTIFIED: DLSS Vulkan/OpenGL interop, FSR, shaderpack rendering, framebuffer state")
