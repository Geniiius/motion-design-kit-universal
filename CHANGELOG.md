# Changelog

## 3.1.0 — 2026-11-10

### Added
- **Setup assistant with a single way in.** It looks at the machine without changing anything, then proposes a table and installs only the elements you approve. It runs every engine, makes two test videos and reports READY, WARNING, FAILED or OPTIONAL. It also resumes an interrupted install, repairs, uninstalls inside the kit, and compares pinned versions with the latest ones without updating anything.
- **Treatments of a provided video:**
  - silence removal;
  - short clips;
  - reframing to another shape;
  - captions and translations;
  - chapters.

  One file per treatment, and a single final encode. The kit stops and asks when a reader's decision is needed.
- **Exact machine diagnostic:**
  - system and architecture;
  - processor and memory;
  - graphics cards and their memory;
  - free disk space;
  - versions of every tool;
  - conflicts;
  - hardware encoders, tested for real.
- **Central settings, install state and logs:** `kit.config.json`, `kit.config.local.json`, `kit-state.json` and `logs/`. Logs are written without keys or personal data.
- **Blender detection:** Blender is found outside the PATH, and the mascot script works with Blender 5.
- **Documentation:**
  - beginner guides in French (`LISEZ-MOI.md`) and Spanish (`LEEME.md`);
  - an English README;
  - a starter message in three languages;
  - `SECURITY.md`, `CONTRIBUTING.md` and `docs/TOKEN-ECONOMY.md`;
  - real-run evidence for the treatments and the assistant.

### Changed
- **Nothing installs silently any more.** Optional modules, engines and the design checker ask first.
- **A provided video is kept whole and in its own shape.** A request that was not understood is not executed, and a run that changes nothing answers `unchanged`.
- **New installers.** `instalar.ps1` and `instalar.sh` now launch the assistant; Python is installed only after a yes.
- **Fewer tokens per conversation.** Once the kit is installed, the setup skill is no longer loaded. Its maintenance part is read only when needed, and the old entry skill no longer competes with the router.

### Fixed
- A provided video was cut to 3.5 seconds and reported as delivered.
- Silence removal failed beyond about a hundred cuts, and sound drifted away from the picture after many cuts. Fixed and tested on a 20-minute video with 343 cuts.
- The Blender script failed on Blender 5.
- Proof files could carry paths of the machine that produced them into the package.

## 3.0 — 2026-11-03

First Universal Studio version. It was not published.

- **Core:** router, file inventory, validated manifest and quality check.
- **Creation:** Remotion compositions in 2D and 3D, and an interactive presentation.
- **Memory:** the kit learns the user's habits.
- **Modules:**
  - Opuscar film styles (66 styles);
  - video effects around a person;
  - local Kokoro voice and transcription;
  - design check;
  - ElevenLabs, as an option.
