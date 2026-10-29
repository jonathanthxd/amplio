# TFL Client / Amplio: experimental Ornithe compatibility plan

Upstream: https://github.com/Z1xus/amplio
TFL Client: https://github.com/TFLivesStudio/TFLClientMOD

## Baseline
TFL uses Minecraft 1.8.9, Ornithe Gen2, Java 25, OSL 0.22.2, Legacy LWJGL3 1.4.10, Argentum 1.0.2 and TFL Core. Lucerna is being evaluated separately.

## Important: Pylon is a declared REQUIRED dependency
Amplio's `fabric.mod.json` requires `pylon: "*"`. Our TFL client uses Legacy LWJGL3.
Both provide overlapping legacy-LWJGL compatibility and SDL-window/input functionality.
DO NOT install Pylon together with Legacy LWJGL3 until compatibility is demonstrated.
DO NOT simply remove the metadata requirement and declare the client compatible.
Proposed experiment: keep TFL on Legacy LWJGL3 and inspect/port any required Pylon hooks, then run actual native tests. This is a future code-change decision.

## Source/CI strategy
- The upstream `.github/workflows/build.yml` already builds Linux/Windows native binaries and packages a JAR. Keep it unchanged initially.
- `tfl-ornithe-ci.yml` adds an independent source contract gate and `compileJava`; it intentionally DOES NOT package an incomplete Java-only JAR.
- The native SDK DLSS dependencies have separate licensing terms from Amplio's MIT source.
- Successful native builds do not prove running NVIDIA NGX or OpenGL/Vulkan interoperability on a real GPU.

## Render pipeline risks
- `MixinScaleWorld` temporarily replaces the Minecraft main render target during world rendering.
- `MixinScaleViewport` changes full-window viewports in the world pass.
- `MixinCameraJitter` intercepts camera, hand and cloud projection setup for temporal DLSS.
- TFL `OrnitheColors` uses a post chain; Lucerna also owns shaders, render targets and postprocessing. Render order and correct restore must be established.
- DLSS requires physical NVIDIA hardware, working OpenGL/Vulkan external memory and semaphore extensions, and matching GPU UUIDs.
- FSR1 is spatial; prioritize its native demonstration before DLSS.

## Runtime acceptance (must be performed, not inferred from CI)
- [ ] First certify `Argentum + Legacy LWJGL3 + Amplio` without Lucerna or TFL Core (after dependency resolution)
- [ ] FSR1 OFF/QUALITY/BALANCED/PERFORMANCE, resize, fullscreen, world change, resource reload
- [ ] Add Lucerna and a simple shaderpack, confirm color/depth buffers and UI not upscaled
- [ ] Add TFL Core; test HUD, title video, zoom/freelook, panorama, maps, Paper Doll and color grading
- [ ] NVIDIA GPU only: DLSS Quality, native anti-aliasing, teleport/camera cut/history reset
- [ ] Check mobile hybrid-GPU routing: Vulkan and OpenGL must run on the same physical GPU
- [ ] Profile frame-time p50/p95/p99 and render cost with shaders ON and OFF
- [ ] Report OS, driver, GPU, Java, hashes, video and crash logs

## Shipping policy
No stable binary, automatic merge, bundling of unlicensed third-party natives, or performance claim before native/physical-GPU certification. Keep this integration branch isolated.
