#!/usr/bin/env python3
"""TFL Amplio source and JAR contract checks. Not a GPU runtime test."""
import argparse
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def prop(name: str) -> str:
    text = (ROOT / "gradle.properties").read_text()
    match = re.search(r"^" + re.escape(name) + r"=(.+)$", text, re.M)
    assert match, f"Missing {name} in gradle.properties"
    return match.group(1).strip()

def validate(meta: dict) -> None:
    assert meta["id"] == "amplio"
    assert meta["environment"] == "client"
    assert meta["depends"]["minecraft"] == "1.8.9"
    assert meta["depends"]["argentum"].startswith(">=")
    assert "pylon" not in meta["depends"], "Pylon must not be a REQUIRED dependency in TFL branch"
    assert meta.get("suggests", {}).get("legacy-lwjgl3") == "*", "TFL LWJGL3 path not documented as optional"
    assert prop("minecraft_version") == "1.8.9"
    assert prop("feather_build") == "2"
    assert prop("fabric_version") == "0.19.5"
    assert prop("argentum_version").startswith("1.0.2")

def check_source() -> None:
    meta = json.loads((ROOT / "src/main/resources/fabric.mod.json").read_text())
    validate(meta)
    gradle = (ROOT / "build.gradle.kts").read_text()
    assert "JavaLanguageVersion.of(25)" in gradle
    assert "pl.tomgirl:pylon" not in gradle, "Compile path unexpectedly requires Pylon"
    assert "pylon_version" not in (ROOT / "gradle.properties").read_text()
    config = (ROOT / "src/main/java/us/z1x/amplio/AmplioConfig.java").read_text()
    assert "upscaler = UpscalerType.OFF;" in config, "TFL must default to native resolution"
    assert "quality = Quality.QUALITY;" in config
    mixins = json.loads((ROOT / "src/main/resources/amplio.mixins.json").read_text())
    assert meta["mixins"] == ["amplio.mixins.json"]
    assert mixins["required"] is True
    for mixin in ["MixinCameraJitter", "MixinScaleWorld", "MixinScaleViewport", "MixinUpscalingOptions"]:
        assert mixin in mixins["client"], f"Missing graphics mixin: {mixin}"
    for path in [
        "src/main/java/us/z1x/amplio/upscale/Fsr1Upscaler.java",
        "src/main/java/us/z1x/amplio/upscale/DlssUpscaler.java",
        "native/CMakeLists.txt",
        "native/src/amplio.cpp",
        ".github/workflows/build.yml",
    ]:
        assert (ROOT / path).is_file(), f"Required source missing: {path}"
    for java in (ROOT / "src/main/java").rglob("*.java"):
        assert "pl.tomgirl.pylon" not in java.read_text(), f"Pylon API used directly in: {java}"
    print("PASS: Argentum/Ornithe/Java 25; Pylon not required; upscaling defaults OFF")
    print("WARNING: Legacy LWJGL3 render context and GL calls still need GPU testing")

def check_jar() -> None:
    jars = sorted(p for p in (ROOT / "build/libs").glob("*.jar") if not any(x in p.stem for x in ("-sources", "-dev", "-javadoc")))
    assert jars, "No build/libs JAR found"
    for jar in jars:
        with zipfile.ZipFile(jar) as z:
            files = set(z.namelist())
            validate(json.loads(z.read("fabric.mod.json")))
            for path in [
                "us/z1x/amplio/Amplio.class",
                "amplio.mixins.json",
                "natives/windows-x86_64/index",
                "natives/linux-x86_64/index",
            ]:
                assert path in files, f"JAR missing {path}: {jar.name}"
            win = z.read("natives/windows-x86_64/index").decode()
            linux = z.read("natives/linux-x86_64/index").decode()
            assert "amplio.dll" in win and "nvngx_dlss.dll" in win
            assert "libamplio.so" in linux and "libnvidia-ngx-dlss.so" in linux
        print(f"PASS: Windows/Linux native packaging and metadata: {jar.name}")
    print("WARNING: JAR structure cannot certify DLSS / native hardware or EGL/GLFW/SDL interop")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jar", action="store_true")
    args = parser.parse_args()
    check_source()
    if args.jar:
        check_jar()
