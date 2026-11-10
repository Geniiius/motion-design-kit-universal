import ast
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from universal import design_check, effects, film_style, modules, perfil, voice_kokoro
from universal.present import infographic
from universal.catalog import load, search
from universal.manifest import validate
from universal.qc import measure_video, qc
from universal.router import has, route

ROOT = Path(__file__).resolve().parents[1]
HAS_FF = bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))
HAS_EFFECTS = modules.python().exists() and (modules.VENV / '.tier-effects').exists()
CAPS = {'tools': {'blender': False, 'three_vrm': False}, 'engines': {k: True for k in ('ffmpeg-edit', 'html-deck', 'remotion-2d', 'remotion-3d', 'film-style', 'video-effects')}}
FX = (ROOT / 'modules/video-effects/scripts/fx.py').read_text(encoding='utf-8')


def video(path='clip.mp4'):
    return {'path': path, 'type': 'video', 'role': 'source', 'exists': True, 'metadata': {}, 'rights': {'status': 'unknown'}, 'provenance': {}, 'warnings': [], 'treatment': []}


def engines(p):
    return [e['id'] for e in p['engines']]


class FilmStyleRouting(unittest.TestCase):
    def go(self, brief, inputs=(), **kw):
        p = route(brief, list(inputs), caps=CAPS, **kw)
        self.assertEqual(validate(p), [])
        return p

    def test_named_style_in_three_languages(self):
        for brief in ('Un film en aquarelle sur la pluie', 'Una película en acuarela sobre la lluvia', 'A watercolor film about the rain'):
            p = self.go(brief)
            self.assertEqual(p['style']['film_style'], 'watercolor', brief)
            self.assertEqual(engines(p), ['film-style'], brief)
            self.assertEqual(p['deliverables'][0]['adapter'], {'engine': 'film-style', 'style': 'watercolor'})

    def test_explicit_style_id(self):
        self.assertEqual(self.go('Un film sur la pluie', style='ukiyoe')['style']['film_style'], 'ukiyoe')

    def test_no_style_named_keeps_the_usual_engines(self):
        for brief, engine in (('Un film promo pour une boulangerie', 'remotion-2d'), ('Une scène 3D cinéma', 'remotion-3d')):
            p = self.go(brief)
            self.assertIsNone(p['style']['film_style'])
            self.assertIn(engine, engines(p))

    def test_restyle_is_never_presented_as_a_film_style(self):
        p = self.go('Transforme cette vidéo en aquarelle', [video()])
        self.assertIn('RESTYLE_FOOTAGE', p['intent'])
        self.assertNotIn('film-style', engines(p))
        self.assertEqual(p['status'], 'blocked')

    def test_interactive_stays_interactive(self):
        p = self.go('Une présentation interactive de services, façon aquarelle')
        self.assertEqual(p['deliverables'][0]['adapter']['engine'], 'html-deck')

    def test_cost_warning_is_stated(self):
        self.assertTrue(any('tokens' in n for n in self.go('Un film en risographie')['notes']))

    def test_every_alias_compiles_and_finds_its_style(self):
        for s in load('style-catalog.json')['styles']:
            if s.get('source') == 'opuscar':
                self.assertTrue(s['alias'], s['id'])
                sample = re.sub(r'[.?()]|\|.*', ' ', s['alias'][0]).replace('  ', ' ').strip()
                has(f' {sample} ', s['alias'])


class EffectsRouting(unittest.TestCase):
    def test_behind_the_head_with_a_video(self):
        for brief in ('Ajoute un mot derrière ma tête', 'Pon una palabra detrás de mi cabeza', 'Put a word behind my head', 'Ajoute un effet orbit', 'Applique spotlight, /effects spotlight'):
            p = route(brief, [video()], caps=CAPS)
            self.assertEqual(validate(p), [])
            self.assertEqual(engines(p), ['video-effects'], brief)
            self.assertEqual(p['deliverables'][0]['adapter'], {'engine': 'video-effects'})
            self.assertTrue(any('Consentement' in a['what'] for a in p['approval_required']))

    def test_not_without_a_video(self):
        self.assertNotIn('video-effects', engines(route('Ajoute un mot derrière ma tête', [], caps=CAPS)))

    def test_plain_edit_is_unchanged(self):
        self.assertEqual(engines(route('Monte ces clips', [video('a.mp4'), video('b.mp4')], caps=CAPS)), ['ffmpeg-edit'])

    def test_ordinary_words_do_not_trigger_it(self):
        for brief in ('Monte la noise du concert', 'Un moody cut de ce clip', 'Coupe le tap dance'):
            self.assertNotIn('video-effects', engines(route(brief, [video()], caps=CAPS)), brief)


class Catalogue(unittest.TestCase):
    def test_counts_and_recipes(self):
        styles = load('style-catalog.json')['styles']
        ours = [s for s in styles if s.get('source') == 'opuscar']
        self.assertEqual(len(ours), 66)
        self.assertEqual(len({s['id'] for s in styles}), len(styles))
        for s in ours:
            self.assertTrue((ROOT / 'modules/opuscar/styles' / s['opuscar'] / 'STYLE.md').exists(), s['id'])
        self.assertTrue(any(s['id'] == 'watercolor' for s in search('acuarela')))

    def test_effects_presets_match_the_code(self):
        data = {x['id']: x for x in load('video-effects.json')['effects']}
        self.assertEqual(set(data), {x['id'] for x in effects.catalog()})
        self.assertEqual(len(data), 51)
        for key in re.findall(r"need\(e, '([a-z_]+)'\)", FX):
            self.assertTrue(any(key in x['obligatoires'] for x in data.values()) or key in ('kpi', 'donut', 'bars'), key)


class EffectsSafety(unittest.TestCase):
    def test_no_author_identity_or_invented_figures(self):
        for word in ('vibha.in', 'Vibha', "'Claude'", 'Edited by', '197K', '672K', '26.9K', '2.4M', 'ChatGPT', 'how did you edit'):
            self.assertNotIn(word, FX.split('"""', 2)[2], word)

    def test_no_code_or_package_is_fetched_or_loaded_at_run_time(self):
        for name in ('fx.py', 'words.py'):
            src = (ROOT / 'modules/video-effects/scripts' / name).read_text(encoding='utf-8')
            calls = {n.func.id for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
            self.assertFalse(calls & {'exec', 'eval'}, name)
            self.assertNotIn("'pip'", src)
            self.assertNotRegex(src, r'urllib|requests\.|socket\.')

    def test_brand_interfaces_need_an_acknowledgement(self):
        plan = [{'fx': 'imessage', 'start': 0, 'end': 1, 'text': 'a'}]
        with self.assertRaises(PermissionError):
            effects.brand_gate(plan, False)
        self.assertEqual(effects.brand_gate(plan, True), ['messages'])
        self.assertEqual(effects.brand_gate([{'fx': 'orbit', 'start': 0, 'end': 1}], False), [])

    def test_tracking_report_is_parsed(self):
        self.assertEqual(effects.tracking('x\nTRACK {"frames": 9, "faces": 3, "silhouettes": 1}\ny')['faces'], 3)
        self.assertIsNone(effects.tracking('rien'))

    def test_font_licences_are_complete(self):
        for f in (ROOT / 'modules/video-effects/fonts').glob('OFL-*.txt'):
            self.assertIn('PERMISSION & CONDITIONS', f.read_text(encoding='utf-8'), f.name)

    @unittest.skipUnless(HAS_EFFECTS, 'module effects absent')
    def test_missing_figure_stops_before_any_video(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError, "'to'"):
                effects.check([{'fx': 'liquid-glass-graph', 'start': 0, 'end': 2, 'text': 'Ventes'}], Path(t) / 'p.json')
            self.assertEqual(effects.check([{'fx': 'liquid-glass-graph', 'start': 0, 'end': 2, 'text': 'Ventes', 'to': '59%'}], Path(t) / 'p.json'), 'OK')


class OpuscarSafety(unittest.TestCase):
    def test_no_political_map_rule(self):
        for f in (ROOT / 'modules/opuscar').rglob('*.md'):
            self.assertNotRegex(f.read_text(encoding='utf-8', errors='replace'), r'Taiwan|Diaoyu|Aksai|Zangnan', f.name)

    def test_no_online_voice_or_auto_update(self):
        lib = ROOT / 'modules/opuscar'
        self.assertFalse((lib / 'core/tts/tts_zh.py').exists())
        self.assertFalse((lib / 'core/render/mux.sh').exists())
        self.assertFalse(list(lib.rglob('setup.sh')))
        for f in lib.rglob('*.py'):
            self.assertNotIn('edge_tts', f.read_text(encoding='utf-8', errors='replace'), f.name)

    def test_node_versions_are_exact(self):
        pkg = json.loads((ROOT / 'modules/opuscar/package.json').read_text(encoding='utf-8'))
        for name, version in pkg['dependencies'].items():
            self.assertRegex(version, r'^\d+\.\d+\.\d+$', name)
        self.assertIn('"integrity"', (ROOT / 'modules/opuscar/package-lock.json').read_text(encoding='utf-8'))


class ModulesInstall(unittest.TestCase):
    def test_locks_are_pinned_hashed_and_portable(self):
        for tier in modules.TIERS:
            text = (modules.LOCKS / f'{tier}.lock').read_text(encoding='utf-8')
            names = re.findall(r'^([A-Za-z0-9_.-]+)==[^ ]+', text, re.M)
            self.assertTrue(names, tier)
            self.assertGreaterEqual(text.count('--hash=sha256:'), len(names), tier)
            self.assertNotRegex(text, r'[A-Za-z]:[/\\]|AppData|/home/|/Users/', tier)

    def test_big_downloads_need_an_approval(self):
        with self.assertRaises(modules.DownloadApprovalRequired) as caught:
            modules.install_pack('instruments-karoryfer', approved=False)
        self.assertIn('Mo', str(caught.exception))
        self.assertIn('github.com', str(caught.exception))
        if not (modules.WHISPER_DIR / 'model.bin').exists():
            with self.assertRaises(modules.DownloadApprovalRequired):
                modules.install_whisper(approved=False)

    def test_every_pack_has_a_checksum(self):
        packs = modules.pack_names()
        self.assertIn('voice-model', packs)
        for p in packs.values():
            self.assertRegex(p['sha256'], r'^[0-9a-f]{64}$')
        self.assertRegex(modules.OPUSCAR_COMMIT, r'^[0-9a-f]{40}$')
        self.assertRegex(modules.WHISPER['revision'], r'^[0-9a-f]{40}$')

    def test_unknown_names_are_refused(self):
        with self.assertRaises(ValueError):
            modules.install_pack('nimporte-quoi')
        with self.assertRaises(ValueError):
            modules.install_tier('nimporte-quoi')


class FilmStyleTools(unittest.TestCase):
    def test_find_and_refuse_to_overwrite(self):
        self.assertEqual(film_style.find('Watercolor Brush')['id'], 'watercolor')
        self.assertEqual(len(film_style.styles()), 66)
        with self.assertRaises(ValueError):
            film_style.find('inconnu')
        with tempfile.TemporaryDirectory() as t:
            folder = film_style.new('risograph', Path(t) / 'film', name='Essai', seconds=4)
            page = (folder / 'index.html').read_text(encoding='utf-8')
            self.assertIn('window.DUR = 4', page)
            self.assertIn('styles/risograph/STYLE.md', page)
            ast.parse((folder / 'mix.py').read_text(encoding='utf-8'))
            with self.assertRaises(FileExistsError):
                film_style.new('risograph', Path(t) / 'film')

    @unittest.skipUnless(HAS_FF, 'ffmpeg absent')
    def test_master_keeps_colours_and_level(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            src, mix, out = t / 'v.mp4', t / 'm.wav', t / 'o.mp4'
            # The same encoding as the film engine: JPEG frames, full range, BT.601
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=0xF0D612:s=320x180:r=24:d=2', '-vf', 'format=yuvj420p', '-colorspace', 'bt470bg', '-color_range', 'pc', '-c:v', 'libx264', '-crf', '12', str(src)], check=True)
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'sine=f=330:d=2:r=48000', '-af', 'volume=0.2', str(mix)], check=True)
            r = film_style.master(src, mix, out, grain=0)
            self.assertTrue(r['audio'])
            info = qc(out)
            self.assertEqual(info['pix_fmt'], 'yuv420p')
            self.assertAlmostEqual(info['audio']['lufs'], -14, delta=1.5)
            self.assertLess(info['audio']['true_peak'], -1)

            def pixel(path):
                raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(path), '-vf', 'crop=8:8:100:80,scale=1:1:flags=area,format=rgb24', '-frames:v', '1', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
                return list(raw[:3])
            for a, b in zip(pixel(src), pixel(out)):
                self.assertLessEqual(abs(a - b), 4, (pixel(src), pixel(out)))

    @unittest.skipUnless(HAS_FF, 'ffmpeg absent')
    def test_master_without_sound_makes_a_silent_track(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            src, out = t / 'v.mp4', t / 'o.mp4'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=red:s=160x90:r=24:d=1', '-c:v', 'libx264', str(src)], check=True)
            r = film_style.master(src, None, out, grain=0)
            self.assertFalse(r['audio'])
            self.assertTrue(r['audio_track'])
            self.assertAlmostEqual(r['duration_s'], 1, delta=.1)


class Voice(unittest.TestCase):
    def test_visemes_follow_the_word_times(self):
        v = voice_kokoro.visemes_from_words([{'text': 'mamá', 'start': .5, 'end': .9}, {'text': '¿sí?', 'start': 1.2, 'end': 1.4}])
        self.assertEqual(v[0], {'id': 0, 'start': 0.0, 'duration': .5})
        self.assertEqual(v[1]['id'], 21)
        self.assertAlmostEqual(v[1]['start'], .5)
        self.assertTrue(any(x['id'] == 0 and x['start'] == .9 for x in v))

    def test_a_number_said_aloud_moves_the_mouth(self):
        v = voice_kokoro.visemes_from_words([{'text': '1959', 'start': 0, 'end': .8}])
        self.assertGreater(len([x for x in v if x['id'] != 0]), 4)

    def test_the_written_text_stays_the_reference(self):
        heard = [{'text': 'Goutter', 'start': 1.0, 'end': 1.4}, {'text': 'la', 'start': 1.4, 'end': 1.5}, {'text': 'différence,', 'start': 1.5, 'end': 2.0},
                 {'text': 'c', 'start': 2.2, 'end': 2.25}, {'text': "'est", 'start': 2.25, 'end': 2.4}, {'text': 'préparer', 'start': 2.4, 'end': 3.0}]
        text = "Goûtez la différence, c'est préparé !"
        words, match = voice_kokoro.align(text, heard)
        self.assertEqual([w['text'] for w in words], ['Goûtez', 'la', 'différence,', "c'est", 'préparé !'])
        self.assertGreater(match, .8)
        self.assertAlmostEqual(words[0]['start'], 1.0, delta=.02)
        self.assertAlmostEqual(words[3]['start'], 2.2, delta=.02)
        for a, b in zip(words, words[1:]):
            self.assertLessEqual(a['end'], b['start'] + .001)

    def test_a_word_not_heard_is_placed_between_its_neighbours(self):
        heard = [{'text': 'en', 'start': 0.0, 'end': .2}, {'text': 'mille', 'start': .3, 'end': .6}, {'text': 'neuf', 'start': .6, 'end': .9}, {'text': 'cent', 'start': .9, 'end': 1.2}, {'text': 'ici', 'start': 1.3, 'end': 1.6}]
        words, _ = voice_kokoro.align('en 1900 ici', heard)
        self.assertEqual([w['text'] for w in words], ['en', '1900', 'ici'])
        self.assertTrue(words[0]['end'] <= words[1]['start'] < words[1]['end'] <= words[2]['start'])

    def test_subtitles_are_even_and_prefer_a_comma(self):
        from universal.qc import check_srt
        from universal.voice import to_srt
        text = 'Bonjour, du pain chaud, chaque matin à deux pas de chez vous. Goûtez la différence.'
        t, words = 0.0, []
        for w in text.split():
            words.append({'text': w, 'start': round(t, 3), 'end': round(t + .06 * len(w) + .05, 3)})
            t += .06 * len(w) + .08
        with tempfile.TemporaryDirectory() as d:
            srt = to_srt(words, Path(d) / 's.srt')
            lines = [x for x in srt.read_text(encoding='utf-8').split('\n') if x and not x[0].isdigit()]
            self.assertEqual(check_srt(srt, t), [])
        self.assertEqual(lines[0], 'Bonjour, du pain chaud,')
        self.assertEqual(lines[-1], 'Goûtez la différence.')
        self.assertLessEqual(max(map(len, lines)), 40)

    def test_a_short_word_stays_readable_without_overlap(self):
        from universal.qc import check_srt
        from universal.voice import to_srt
        words = [{'text': '¡Hola!', 'start': 0.0, 'end': .15}, {'text': 'Soy', 'start': .9, 'end': 1.1}, {'text': 'Nodo.', 'start': 1.1, 'end': 1.4}]
        with tempfile.TemporaryDirectory() as d:
            srt = to_srt(words, Path(d) / 's.srt')
            self.assertEqual(check_srt(srt, 2.0), [])
            self.assertIn('00:00:00,000 --> 00:00:00,353', srt.read_text(encoding='utf-8'))

    def test_each_language_has_a_voice(self):
        self.assertEqual(set(voice_kokoro.VOICES), {'fr', 'es', 'en'})
        with self.assertRaises(ValueError):
            voice_kokoro.synthesize('x', Path('x.wav'), 'de')


class Understanding(unittest.TestCase):
    def test_a_guess_says_it_is_one(self):
        for brief, files in (('Je tiens un salon de coiffure', []), ('Ça fait pas assez pro', [video()]), ('', [video()])):
            seen = route(brief, list(files), caps=CAPS)['understanding']
            self.assertEqual(seen['source'], 'defaut', brief)
            self.assertFalse(seen['certain'])
        self.assertTrue(any('défaut' in n for n in route('Je tiens un salon de coiffure', [], caps=CAPS)['notes']))

    def test_the_agent_decision_wins_over_keywords(self):
        p = route('Je tiens un salon de coiffure', [], caps=CAPS, intent=['CHARACTER_ANIMATION'])
        self.assertEqual(p['understanding']['source'], 'agent')
        self.assertEqual(p['intent'], ['CHARACTER_ANIMATION'])
        self.assertIn('remotion-3d', engines(p))
        self.assertEqual(route('Ça fait pas assez pro', [video()], caps=CAPS, force_effects=True)['deliverables'][0]['adapter'], {'engine': 'video-effects'})
        self.assertEqual(route('Mon village', [], caps=CAPS, style='woodcut')['style']['film_style'], 'woodcut')

    def test_everyday_words_do_not_catch_a_trade(self):
        for brief in ('Pub pour mon entreprise de peinture en bâtiment', 'Vidéo pour ma salle de jeux vidéo'):
            self.assertIsNone(route(brief, [], caps=CAPS)['style']['film_style'], brief)
        self.assertEqual(route('Comme une vieille gravure sur bois', [], caps=CAPS)['style']['film_style'], 'woodcut')

    def test_never_wrong_in_silence_on_unseen_phrases(self):
        from tests.phrases_naturelles import HOLDOUT, measure
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            report = measure(HOLDOUT, 'test')
        self.assertEqual(report['fausses_sans_le_dire'], 0)


class Memory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = perfil.DIR
        perfil.DIR = Path(self.tmp.name) / 'perfil'

    def tearDown(self):
        perfil.DIR = self.saved
        self.tmp.cleanup()

    def project(self, fmt='9:16', problems=()):
        p = route('Un film', [], caps=CAPS, fmt=fmt)
        perfil.remember_delivery(p, p['deliverables'][0], {'qc': {'pass': not problems, 'blocking': [], 'warnings': list(problems), 'duration': 5, 'audio': {'lufs': -14, 'true_peak': -1.5}}})

    def test_a_blank_profile_changes_nothing(self):
        c = perfil.context('Un film')
        self.assertIsNone(c['formato_habitual'])
        self.assertEqual(c['videos_entregados'], 0)
        p = route('Un film sur la mer', [], caps=CAPS, profile=c)
        self.assertEqual(p['deliverables'][0]['format'], '16:9')
        self.assertFalse(any('repris' in n or 'Règle' in n or 'Marque' in n for n in p['notes']))

    def test_the_kit_learns_a_format_from_two_deliveries_and_a_request_still_wins(self):
        self.project()
        self.assertIsNone(perfil.context()['formato_habitual'], 'une seule fois ne fait pas une habitude')
        self.project()
        c = perfil.context()
        self.assertEqual(c['formato_habitual'], '9:16')
        p = route('Un film sur la mer', [], caps=CAPS, profile=c)
        self.assertEqual(p['deliverables'][0]['format'], '9:16')
        self.assertTrue(any('9:16' in n for n in p['notes']))
        self.assertEqual(route('Un film pour YouTube', [], caps=CAPS, profile=c)['deliverables'][0]['format'], '16:9')
        self.assertEqual(route('Un film', [], caps=CAPS, profile=c, fmt='1:1')['deliverables'][0]['format'], '1:1')

    def test_a_defect_seen_twice_is_prevented_whatever_its_numbers(self):
        self.project(problems=['Crête haute -0.9 dBFS (objectif ≤ -1).'])
        self.assertEqual(perfil.recurring_problems(), [])
        self.project(problems=['Crête haute -0.7 dBFS (objectif ≤ -1).'])
        self.assertEqual(len(perfil.recurring_problems()), 1)
        self.assertTrue(any('Crête' in n for n in route('Un film', [], caps=CAPS, profile=perfil.context())['notes']))

    def test_brand_rules_and_language_are_used(self):
        (perfil.DIR / 'marcas').mkdir(parents=True)
        (perfil.DIR / 'marcas/_plantilla.md').write_text('x', encoding='utf-8')
        (perfil.DIR / 'marcas/Lumen.md').write_text('# Lumen', encoding='utf-8')
        (perfil.DIR / 'preferencias.json').write_text('{"idioma_por_defecto": "fr"}', encoding='utf-8')
        (perfil.DIR / 'aprendizajes.md').write_text('## Reglas aprendidas (se aplican siempre)\n- Siempre subtítulos\n\n## Entradas\n- otra cosa\n', encoding='utf-8')
        c = perfil.context('Un film')
        self.assertEqual(c['marca'], 'Lumen')
        self.assertEqual(c['reglas'], ['Siempre subtítulos'])
        p = route('Hola', [], caps=CAPS, profile={**c, 'idioma_por_defecto': 'fr'})
        self.assertTrue(any('Lumen' in n for n in p['notes']))
        self.assertTrue(any('Siempre subtítulos' in n for n in p['notes']))
        self.assertEqual(route('12345', [], caps=CAPS, profile=c)['request']['language'], 'fr')

    def test_a_damaged_history_never_stops_a_video(self):
        perfil.DIR.mkdir(parents=True)
        (perfil.DIR / 'calidad.jsonl').write_text('pas du json\n{"problemas": ["x"]}\n', encoding='utf-8')
        (perfil.DIR / 'preferencias.json').write_text('{cassé', encoding='utf-8')
        self.assertEqual(perfil.preferences(), {})
        self.assertEqual(perfil.recurring_problems(), [])

    def test_a_missing_profile_starts_from_the_blank_template(self):
        self.project()
        self.assertTrue((perfil.DIR / 'mi-estilo.md').exists())
        self.assertTrue((perfil.DIR / 'historial.jsonl').exists())

    @unittest.skipUnless(HAS_FF, 'ffmpeg absent')
    def test_a_real_run_feeds_the_memory(self):
        from universal import fixtures
        from universal.inventory import inspect
        from universal.manifest import save
        from universal.run import run_project
        made = fixtures.build()
        root = Path(self.tmp.name)
        for i in range(2):
            p = route('Monte ces clips pour Reels', [inspect(str(made['clips'][0])), inspect(str(made['clips'][1]))], name=f'essai{i}', caps=CAPS, fmt='9:16')
            path = root / f'p{i}.json'
            save(p, path)
            run_project(path, 'draft', root / 'out')
        self.assertEqual(perfil.context()['formato_habitual'], '9:16')
        self.assertEqual(perfil.context()['videos_entregados'], 2)
        self.assertTrue((perfil.DIR / 'calidad.jsonl').read_text(encoding='utf-8').strip())


class DesignCheck(unittest.TestCase):
    SAMPLE = [{'antipattern': 'side-tab', 'name': 'Side-tab', 'category': 'slop', 'snippet': 'border-left: 4px'}, {'antipattern': 'side-tab', 'name': 'Side-tab', 'category': 'slop', 'snippet': 'border-left: 4px'},
              {'antipattern': 'low-contrast', 'name': 'Low contrast', 'category': 'quality', 'snippet': '3.0:1'}]

    def test_taste_is_kept_apart_and_a_repeat_counts_once(self):
        g = design_check.group(self.SAMPLE)
        self.assertEqual([r['regle'] for r in g['defauts']], ['low-contrast'])
        self.assertEqual(g['gout'][0]['nombre'], 2)

    def test_it_advises_and_never_blocks(self):
        r = design_check.as_report({'ran': True, **design_check.group(self.SAMPLE)})
        self.assertTrue(r['pass'])
        self.assertEqual(r['blocking'], [])
        self.assertEqual(len(r['warnings']), 1)
        self.assertIn('2 fois', r['aesthetic'][0])
        self.assertTrue(design_check.as_report({'ran': False, 'raison': 'x'})['pass'])

    def test_versions_are_exact_and_locked(self):
        pkg = json.loads((design_check.DIR / 'package.json').read_text(encoding='utf-8'))
        self.assertEqual(pkg['dependencies'], {'impeccable': '4.8.0'})
        self.assertIn('"integrity"', (design_check.DIR / 'package-lock.json').read_text(encoding='utf-8'))

    def test_a_binary_that_does_not_match_is_never_run(self):
        with tempfile.TemporaryDirectory() as d:
            saved = design_check.DIR
            design_check.DIR = Path(d)
            try:
                system, arch = design_check._target()
                exe = design_check.binary()
                exe.parent.mkdir(parents=True)
                exe.write_bytes(b'pas le bon programme')
                manifest = Path(d) / 'node_modules/impeccable/skill/scripts/engine-checksums.txt'
                manifest.parent.mkdir(parents=True)
                asset = f"impeccable-{system}-{arch}{'.exe' if system == 'windows' else ''}"
                manifest.write_text(f"0.1.18 {asset} {'0' * 64}\n", encoding='utf-8')
                r = design_check.check(Path(d) / 'page.html')
                self.assertFalse(r['ran'])
                self.assertIn('Empreinte', r['raison'])
            finally:
                design_check.DIR = saved

    @unittest.skipUnless(design_check.binary().exists(), 'module design absent')
    def test_the_kit_pages_no_longer_carry_what_it_found(self):
        spec = json.loads((ROOT / 'examples/universal/infographic.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / 'info.html'
            infographic(spec, page)
            r = design_check.check(page)
        self.assertTrue(r['ran'], r)
        self.assertEqual([x['regle'] for x in r['gout'] + r['defauts']], [])


class QcHonesty(unittest.TestCase):
    @unittest.skipUnless(HAS_FF, 'ffmpeg absent')
    def test_a_relative_path_is_really_measured(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as t:
            src = Path(t) / 'c.mp4'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'testsrc=s=160x90:r=24:d=1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(src)], check=True)
            relative = src.resolve().relative_to(Path.cwd())
            self.assertGreater(len(measure_video(relative)['times']), 10)
            self.assertFalse(any('Analyse' in b for b in qc(relative)['blocking']))


if __name__ == '__main__':
    unittest.main()
