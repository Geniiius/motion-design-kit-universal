# Security policy

## Supported versions

| Version | Supported |
|---|---|
| 3.1.x | Yes |
| Earlier | No |

## Reporting a vulnerability

Please do not open a public issue. On this repository, go to **Security → Report a vulnerability** and describe:
- what you found;
- how to reproduce it;
- what it allows someone to do.

This is a small independent project: expect a first answer within about a week.

## What the kit guarantees, and where

| Guarantee | Enforced in | Tested in |
|---|---|---|
| Nothing installs without an approval that names the element | `universal/onboarding.py` (`apply`), `instalar.ps1`, `instalar.sh` | `tests/test_onboarding.py` (Installing, Console), `tests/paquet.ps1` |
| A free option never installs itself in the middle of a task | `universal/modules.py` (`ConsentRequired`), `universal/film_style.py`, `universal/design_check.py` | `tests/test_onboarding.py` (Consent) |
| What already works is not reinstalled | `onboarding.apply` answers `already` | `tests/test_onboarding.py`, `tests/assistant.py` |
| Exact versions | `package-lock.json` files installed with `npm ci`; `modules/requirements/*.lock` installed with `--require-hashes --only-binary :all:`; HyperFrames called at a fixed version | `tests/test_modules.py`, `tests/regression.py` (npm audit) |
| Downloads are checked | The voice model and sample packs against the SHA-256 of the audited manifest; the transcription model at a fixed revision; the design checker binary before each run | `tests/test_modules.py` |
| Big downloads need their own approval | `modules.install_pack`, `modules.install_whisper` | `tests/test_modules.py` |
| Keys are never read or shown | `diagnostic.secret_present` checks presence only; `logs.scrub` masks keys, tokens, user and machine names and the home folder | `tests/test_onboarding.py` (Journal) |
| No paid call without approval | `universal/voice_elevenlabs.py`: explicit approval for each call, cost ceiling, cache | `tests/test_universal.py` |
| Nothing personal is packaged | `.gitignore`; `empaquetar.ps1` refuses keys, personal folders and machine paths | `tests/paquet.ps1` |
| Uninstall stays inside the kit | `onboarding._inside` accepts only the folders the kit generates | `tests/test_onboarding.py` (Leaving) |
| Updates are never applied automatically | `onboarding.updates` only reads public registries | `tests/test_onboarding.py` (Current) |
| A provided video is never altered | Every treatment writes new files; the original is only read | `tests/test_workflows.py` |

## Known risks and limits

- **Commands on your computer.** The kit runs commands through Claude Code. Keep Claude Code's permission prompts on and read them.
- **Computer tools come in their latest version.** Python, Node.js, FFmpeg, Git, uv and Blender are installed through winget or Homebrew in the latest version their publisher ships, and minimum versions are checked afterwards. This path is covered by tests with stand-ins but has not been executed for real yet.
- **HyperFrames dependencies.** HyperFrames is fetched by `npx` at a fixed version, but npm resolves its own dependencies at install time.
- **CDN.** `hyperframes-starter` loads GSAP from a CDN.
- **Unpinned global skills.** The optional installer flag `-ConSkillsTerceros` copies third-party skills into your global `~/.claude/skills` from repositories that are not pinned. It is off by default.
- **Headless browser.** Rendering uses a headless Chromium on local files.
- **Consent of real people.** Face tracking and voice work are done locally, but obtaining the consent of the people filmed or heard is your responsibility.

## Check it yourself

```
python -m unittest discover -s tests -p "test_*.py"
python -m universal.cli updates --offline
```

- Run `npm audit --omit=dev` in `template/` and in `prompt-motion/`.
- Read `modules/requirements/*.lock`: every Python package is listed with its hashes.
