# Token and cost economy

**Principle: Claude decides, local tools do the work.** Claude reads short summaries, never raw media or long logs. The kit stops to ask instead of guessing, so nothing is rendered twice for nothing.

## Measured on version 3.1.0

Run `python tests/tokens.py` to measure again. It writes `docs/preuves/tokens.json`.

The counts are estimates, not tokenizer output:
- **Text:** characters ÷ 3.6, since French and Spanish are a little denser than English.
- **Images:** width × height ÷ 750, the approximation Anthropic publishes for vision.

Claude Code's own instructions and your global skills are not counted: they cost the same with or without the kit.

| What Claude reads | When | Size | ≈ tokens |
|---|---|---|---|
| `CLAUDE.md` and the names and descriptions of the 21 skills | every request | 12,449 characters | 3,460 |
| All skill bodies together | never all at once | 90,624 characters | 25,170 |
| Skills for a provided video: router and treatments | once per task | 14,127 characters | 3,920 |
| Skills for a video created from an idea: router, Remotion, quality review | once per task | 16,264 characters | 4,520 |
| Setup skill, first launch only | once per machine | 6,541 characters | 1,820 |
| `start` answer, kit already installed | every conversation | about 1,200 to 1,500 characters | 330 to 420 |
| `start` answer, first launch | once per machine | 5,142 characters | 1,430 |
| Routing card | every request | 259 characters | 70 |
| (full manifest, which Claude does not need to read) | | 3,225 characters | 900 |
| `run` answer | every render | 1,522 characters | 420 |
| Contact sheet: 10 frames in one 1600×360 image | every check | one image | 770 |
| (the same 10 frames looked at one by one, at 1280×720) | | ten images | 12,290 |
| Transcript as readable sentences | when choosing clips or chapters | 602 characters | 170 |
| (the word-level timings it is made from) | | 3,243 characters | 900 |

## What saves tokens, and why

1. **Deterministic tools instead of reasoning.** Inventory, routing, manifest validation, FFmpeg filter graphs, loudness, silence detection, crop plans and quality metrics are Python code. Claude calls one command and reads its result; it never works out an FFmpeg command line by itself.
2. **Progressive disclosure.**
   - Only the skill descriptions are always in context; a skill's body is read when the task needs it.
   - The setup skill is not read at all once the kit is installed.
   - Its maintenance part (repair, uninstall, updates) lives in a separate file, read only on demand.
3. **Short answers, details in files.**
   - Claude reads the routing card, not the manifest.
   - `run` returns the status, the files and the notes; the full quality report stays in `qc.json` and is opened only when something fails.
4. **Look less, see more.** One contact sheet holds ten frames for about a sixteenth of the image tokens. Film styles are judged on a few stills before the full render.
5. **Stop instead of guess.**
   - A request that was not understood is refused before any render.
   - A treatment that needs a reader's decision writes a file and waits: the transcript to correct, the clips or chapters to choose.
   - A run that changes nothing answers `unchanged` and writes nothing.
6. **Caches.** A transcription is reused as long as the video keeps the same length. ElevenLabs voices are cached, so a line is never generated twice.

## What changed in 3.1.0

| Change | Effect |
|---|---|
| `CLAUDE.md`: when `start` answers `ready`, no setup skill is read | Saves about 2,350 tokens at the start of every conversation once the kit is installed |
| The setup skill split into first launch and maintenance | 8,458 → 6,541 characters at first launch (−23 %) |
| The old entry skill `motion-kit` narrowed to the creation engines, with a description of 622 → 330 characters | The router no longer has a competitor on every video request |

## Cost economy

- **Local by default.** Every engine runs on your computer: a video costs no API fee.
- **Paid only with a yes.** ElevenLabs needs approval for each call, stays under the manifest's cost ceiling (`cost_ceiling`, 0 by default), reports the characters billed, and is cached.
- **Compute.** Renders start as drafts (640 px wide). Review and final come once the draft is right.
- **Hardware encoder.** It is used only for videos longer than five minutes, and only if it produced a file during the machine check.

## Tips for users

- Say "do it directly" to skip the three creative directions when you already know what you want.
- Keep one conversation per project: a new project in a new conversation keeps the context small.
- Ask for a draft first, then the final version.
- Do not ask Claude to watch a whole video frame by frame: the contact sheet and a few chosen frames are enough.

## Limits of these numbers

- **Estimates.** The exact count depends on the tokenizer and on the language of the text.
- **A real conversation costs more.** It also includes your messages, Claude's answers, the images Claude looks at and Claude Code's own instructions.
- **Not measured in practice.** How much a full conversation spends from first message to delivered video has not been measured.
