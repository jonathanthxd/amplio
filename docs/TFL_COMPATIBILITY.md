# TFL Client / Amplio: experimental Ornithe compatibility plan

Upstream: https://github.com/Z1xus/amplio
TFL Client: https://github.com/TFLivesStudio/TFLClientMOD
Companion: https://github.com/jonathanthxd/lucerna/pull/1

## Tested compile-time baseline
Minecraft 1.8.9, Feather Gen2 mappings build 2, Java 25, Fabric Loader 0.19.5 at build time, and Argentum 1.0.2.
TFL runtime baseline: Ornithe Gen2, Fabric Loader 0.20.1, OSL 0.22.2, Legacy LWJGL3 1.4.10, Argentum 1.0.2, TFL Core 0.4.0-depth.1.

## Pylon removal: source-level adaptation, not proof of a working renderer
Upstream Amplio requires Pylon at runtime. TFL uses Legacy LWJGL3. The fork makes Pylon optional (metadata "suggests") and removes the unused Pylon compile-only dependency. A review of all 18 Java source files found no direct pl.tomgirl.pylon Java API calls.

This allows Fabric Loader to resolve the TFL mod stack WITHOUT installing Pylon. It does not validate OpenGL context/extension compatibility, custom framebuffers, or any shaderpack interactions. Do not add Pylon alongside Legacy LWJGL3 in a test profile.

## Startup defaults
New amplio.properties will have upscaler=OFF (native world resolution), with QUALITY selected as the default preset if the user opts into FSR1/DLSS. Existing configuration files are not overwritten by these Java defaults. For baseline testing, explicitly check the existing properties file or reset it after backing it up.

FSR1 is spatial upscaling and likely offers little benefit in CPU-bound, shaderless 1.8.9 PvP. On the AMD A10 system, only FSR1 should be tested. NVIDIA DLSS requires an RTX GPU and a compatible OpenGL/Vulkan interop path.

## CI strategy
- tfl-ornithe-ci.yml validates the source metadata, checks no Pylon imports, asserts OFF defaults and compiles Java with JDK 25.
- build.yml builds native libraries on Linux/Windows, packages a full JAR and checks packaged metadata plus platform-specific native indexes.
- GitHub Actions is not a replacement for a physical graphics device with valid drivers; successful CI is not runtime certification.
- NVIDIA DLSS SDK distribution and third-party license terms must be checked before any public redistribution.

## Rendering and integration risks
- MixinScaleWorld swaps Minecraft's main framebuffer around GameRenderer.renderWorld. Lucerna intercepts world shaders/postprocessing.
- MixinScaleViewport changes viewport dimensions during the world pass.
- MixinCameraJitter modifies camera/hand/cloud projections for temporal DLSS. TFL zoom, freelook, panorama, FOV and teleports need history reset validation.
- OrnitheColors uses a PostChain on Minecraft's render target. Disable native TFL grading while testing Lucerna + Amplio until the postprocess composition order is established.
- Mixed desktop/iGPU laptop setups require Vulkan and OpenGL to operate on the same RTX device for DLSS.

## Hardware acceptance matrix
- [ ] Clean Argentum + Legacy LWJGL3 1.4.10 + Amplio without TFL Core and Lucerna; set OFF, world load, resize, fullscreen and exit
- [ ] FSR1 QUALITY, BALANCED, PERFORMANCE; compare frames, graphics artifacts and GUI sharpness
- [ ] Repeat with Lucerna shaderpack OFF, then simple shaderpack ON, including weather/sky/hand/particles and switching dimensions
- [ ] Add TFL Core; test main menu, HUD, Paper Doll, zoom, freelook, overlays, minimap, world map, colors and transitions
- [ ] NVIDIA RTX machine: verify DLSS QUALITY, temporal history/camera cuts, GL/Vulkan external memory and semaphores, matching UUID
- [ ] Record OS, GPU, driver, mods and hashes, screenshots, crash log and benchmark p50/p95/p99 frametimes

Do not ship as a stable release or merge automatically until these runtime tests pass. Keep the implementation on a dedicated experimental branch.
