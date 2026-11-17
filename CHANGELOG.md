# Changelog

## 3.2.0 — 2026-11-17

### Added
- **Lyrics of a song, offline:** `transcribe --song` (also `--chanson`) hears a sung voice over music. The song is read several times without the speech filter, in short windows, and the stretches left empty are read again from other starting points. Each word carries the model's confidence and the share of readings that agree; doubtful words are written in brackets with what else was heard, in `<name>.paroles.txt`. The result is a draft to confirm with the person, not a text for the screen.

### Fixed
- **Sung verses no longer disappear without a word.** The ordinary transcription removes what is not speech and took singing for music: on a song, whole verses were missing and nothing said so. It now reports when it found few words for the length and points to `--song`.

  Measured on two real songs that are not in the repository (62 s and 30 s, Spanish): lyric words found went from 34 % to 70 % and from 20 % to 66 %, and no sung line is lost any more. About a third of the words heard are still wrong, and only half of those are flagged: the local model is small.

### Changed
- **The exact test computer no longer appears in the documentation.** The test report, the proofs and the README describe the kind of machine (a Windows 11 laptop with an entry-level NVIDIA card) instead of its processor, graphics cards, memory, disk and Windows build. `tests/rapport.py` now does this by itself for every new proof.
- **Lighter proof images:** the screenshots in `docs/` are compressed without loss (same pixels, about a quarter smaller).

### Removed
- Internal working notes that were of no use to someone using the kit: the starting audit, the master brief and the migration note.

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
