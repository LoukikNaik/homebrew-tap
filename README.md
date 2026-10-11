# Loukik Naik's Homebrew tap

## Install PodClipper

Requires an Apple Silicon Mac (M1 or newer) running macOS 14 Sonoma or newer.
Python 3.12 and FFmpeg are installed automatically.

```bash
brew install loukiknaik/tap/podclipper
podclipper init
# Set LLM_API_KEY in .env; optionally set LLM_ENDPOINT and LLM_MODEL.
podclipper "path/to/podcast.mp4"
```

The first video run downloads local transcription and detection models.
No API key is needed to install the package. A key for your chosen LLM host
is needed to select clips and correct captions.

## Upgrade or uninstall

```bash
brew update
brew upgrade podclipper

brew uninstall podclipper
```

Uninstalling the formula does not remove your videos, outputs, or working-directory
configuration/model caches. It also keeps shared dependencies such as FFmpeg.

## Platforms

This first formula supports **macOS 14+ on arm64 only**. Intel Macs and Linux
are not supported by this formula. PodClipper itself is also available from
[PyPI](https://pypi.org/project/podclipper/) for supported Python environments.

This custom tap installs a pinned set of upstream binary Python wheels for the
native ML dependencies. Every download has a SHA-256 checksum; installation is
offline from those downloaded resources inside a private environment. The formula
is not currently suitable for submitting to `homebrew/core`, which has different
source-build requirements. No Homebrew bottles are published yet.

## Updating the formula

The **Update PodClipper** workflow checks PyPI every six hours and updates the
formula when a new stable PodClipper version is available. It can also be run
manually from the Actions tab, optionally with a version such as `0.1.1`.
The tap's own `GITHUB_TOKEN` handles commits; no cross-repository token is needed.
Updates can arrive up to six hours after the corresponding PyPI release.

To regenerate locally, use Python 3.12 on an Apple Silicon Mac:

```bash
python3.12 scripts/update_formula.py --version 0.1.0
```

The generator pins all recursive runtime dependencies and records them in
`locks/macos-arm64-python312.json`. Releasing PodClipper itself is handled in the
[main repository](https://github.com/LoukikNaik/PodClipper/blob/main/docs/RELEASING.md).

## License

AGPL-3.0-only; see [LICENSE](LICENSE). PodClipper uses Ultralytics YOLO under
AGPL. Dependencies and downloaded model assets retain their own licenses.
