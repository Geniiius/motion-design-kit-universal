# Contributing

Thanks for helping. Many people who use this kit do not code, so the bar is simple: it must never surprise them.

## Ground rules

1. **No personal data or media in the repository.** No real person's face, voice, name or project: demos use generated or CC0 material. `perfil/`, `out/`, `logs/`, `kit-state.json` and `kit.config.local.json` stay out of Git.
2. **Nothing installs, downloads or deletes without an explicit yes** that names the element. A new installable part goes through the setup assistant.
3. **Every dependency is pinned:**
   - npm: lockfiles;
   - Python: hashes, compiled from `modules/requirements/*.in` into `*.lock`;
   - downloaded files: SHA-256.
4. **Local first.** A paid service is optional, asked for on each call, and has a free fallback.
5. **Say what was tested.** PASS is only for what was executed and checked; otherwise use PARTIAL, BLOCKED or NOT TESTED, with the reason.

## Conventions

- `universal/` uses the Python standard library only (3.10 or later). Heavy dependencies live in optional modules under `modules/`.
- Code comments are in English, messages to the user in French, skills in Spanish. Claude answers each user in their own language.
- Keep command outputs short: Claude reads them, and every character costs tokens. Put details in files such as `qc.json` and the proof images.

## Extending the kit

- **A treatment of a provided video:** one file in `universal/workflows/` that declares `ID`, `ORDER`, `TITLE`, `WORDS`, `NEEDS` and `run(ctx, track) -> [Track]`. The registry finds it and the router learns its words. When a reader's decision is needed, raise `NeedsInput` instead of guessing.
- **An installable part:**
  - an entry in `PARTS`, an installer and a check in `universal/onboarding.py`;
  - tests in `tests/test_onboarding.py`.
- **A skill:** `.claude/skills/<name>/SKILL.md`. Keep its description short, because it is loaded in every conversation. Move long reference material into a separate file that the skill reads on demand.

## Tests

| Command | What it does |
|---|---|
| `python -m unittest discover -s tests -p "test_*.py"` | Unit tests: about 4 minutes, FFmpeg needed for the real-run tests |
| `python tests/traitements.py` | Real treatments on a generated talking video |
| `python tests/assistant.py --hors-ligne` | The setup assistant on your machine |
| `python tests/regression.py` | The engines |
| `python tests/tokens.py` | Token measurements |
| `python tests/rapport.py` | Rebuilds `docs/TEST-REPORT.md` and removes your machine's paths from the evidence |
| `powershell -File tests\paquet.ps1 -Termes "words|that|must|not|appear"` | Windows only: the ZIP exactly as a newcomer gets it |

Run `python tests/rapport.py` before committing evidence: it removes the paths of your machine from `docs/preuves`.
