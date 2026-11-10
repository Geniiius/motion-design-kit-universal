# Motion Design Kit Universal Studio

Lire `CLAUDE.md`, puis `docs/ARCHITECTURE.md`, puis `.claude/skills/universal-motion-director/SKILL.md`.
Au premier message, lancer `python -m universal.cli start` et suivre `.claude/skills/kit-onboarding/SKILL.md` : ne rien installer sans accord nommé, ne rien réinstaller de ce qui fonctionne.
Diagnostic : `python -m universal.cli doctor`. Tests : `python -m unittest discover -s tests -p "test_*.py"`.
Ne pas installer de skills globaux. Toute modification d'un média fourni se fait sur une copie.
