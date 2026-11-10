import json
import platform
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from universal import fixtures
from universal.catalog import load, search
from universal.datos import decade_rates, facts, read_series
from universal.engine import plan, read_spec
from universal.inventory import inspect
from universal.manifest import save, validate
from universal.present import infographic, presentation
from universal.render import dimensions, edit, render, run
from universal.qc import check_srt, qc, still_windows
from universal.router import route

ROOT = Path(__file__).resolve().parents[1]
DEMOS = ROOT / 'examples/universal'
CSV = ROOT / 'examples/datos/co2_annmean_mlo.csv'
GLB = ROOT / 'examples/modelos/RobotExpressive/RobotExpressive.glb'
HAS_FF = bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))
CAPS = {'tools': {'blender': False, 'three_vrm': False}, 'engines': {k: True for k in ('ffmpeg-edit', 'html-deck', 'remotion-2d', 'remotion-3d')}}


def fake(kind, role='source', name='x', **meta):
    return {'path': f'{name}.bin', 'type': kind, 'role': role, 'exists': True, 'metadata': meta, 'rights': {'status': 'unknown'}, 'provenance': {}, 'treatment': [], 'warnings': []}


def engines(project):
    return [e['id'] for e in project['engines']]


class RoutingTests(unittest.TestCase):
    def go(self, brief, inputs=()):
        p = route(brief, list(inputs), caps=CAPS)
        self.assertEqual(validate(p), [], p['intent'])
        return p

    def test_brief_only(self):
        p = self.go('Vidéo promo de 15 secondes pour une boulangerie')
        self.assertIn('CREATE_FROM_SCRATCH', p['intent'])
        self.assertEqual(p['deliverables'][0]['duration_s'], 15)

    def test_logo_only(self):
        p = self.go('', [fake('image', 'logo')])
        self.assertEqual(p['intent'], ['ANIMATE_LOGO'])
        self.assertEqual(p['deliverables'][0]['adapter']['composition'], 'Logo-Landscape')

    def test_jpeg_named_by_brief_becomes_logo(self):
        self.assertIn('ANIMATE_LOGO', self.go('Anime mon logo', [fake('image')])['intent'])

    def test_photos(self):
        p = self.go('', [fake('image'), fake('image')])
        self.assertEqual(p['intent'], ['ANIMATE_IMAGES'])
        self.assertEqual(p['deliverables'][0]['adapter']['composition'], 'Parallaxe-Landscape')

    def test_clips_use_only_ffmpeg(self):
        p = self.go('Monte ces trois clips', [fake('video'), fake('video'), fake('video')])
        self.assertIn('EDIT_FOOTAGE', p['intent'])
        self.assertEqual(engines(p), ['ffmpeg-edit'], 'pas de chaîne lourde pour une coupe')

    def test_hybrid(self):
        p = self.go('', [fake('video'), fake('image', 'logo'), fake('image'), fake('audio', 'voice')])
        self.assertTrue({'EDIT_FOOTAGE', 'HYBRID_COMPOSITE'} <= set(p['intent']))
        self.assertTrue(any('voix' in a['what'] for a in p['approval_required']))

    def test_restyle_needs_consent_and_provider(self):
        p = self.go('Transforme cette vidéo en caricature', [fake('video')])
        self.assertIn('RESTYLE_FOOTAGE', p['intent'])
        self.assertEqual(p['status'], 'blocked')
        text = ' '.join(a['what'] for a in p['approval_required'])
        self.assertIn('Consentement', text)
        self.assertIn('Fournisseur', text)

    def test_stylized_3d(self):
        p = self.go('Une création 3D stylisée pour présenter un objet')
        self.assertEqual(p['style']['dimension'], '3d')
        self.assertIn('remotion-3d', engines(p))

    def test_realistic_never_promises_blockbuster(self):
        p = self.go('Une scène réaliste façon Hollywood')
        self.assertIn('remotion-3d', engines(p))
        self.assertTrue(any('Blender' in m['need'] for m in p['missing']))
        self.assertTrue(any('Hollywood' in n for n in p['notes']))

    def test_5d_is_a_question_not_a_format(self):
        p = self.go('Je veux une vidéo 5D de ma ville')
        self.assertEqual(p['style']['preset'], 'immersive-5d-inspired')
        self.assertTrue(any("n'est pas un format" in n for n in p['notes']))
        self.assertEqual(p['questions'][0]['id'], 'forme-5d')

    def test_interactive_is_html_not_mp4(self):
        p = self.go('Une présentation interactive de nos services avec de vrais boutons')
        self.assertEqual(p['deliverables'][0]['kind'], 'html')
        self.assertEqual(len(p['deliverables']), 1)
        self.assertTrue(p['deliverables'][0]['interactive'])

    def test_interactive_with_recap_film_gets_two_outputs(self):
        p = self.go('Présentation interactive de services et un film récapitulatif')
        self.assertEqual({d['kind'] for d in p['deliverables']}, {'html', 'video'})

    def test_document_goes_to_explainer(self):
        self.assertIn('DATA_EXPLAINER', self.go('', [fake('data')])['intent'])
        self.assertIn('DATA_EXPLAINER', self.go('', [fake('document')])['intent'])

    def test_model_goes_to_character(self):
        p = self.go('', [fake('3d', readable=True, rigged=True)])
        self.assertEqual(p['deliverables'][0]['adapter']['composition'], 'Personaje-GLB-Landscape')

    def test_existing_project(self):
        self.assertIn('REVISE_EXISTING_PROJECT', self.go('', [fake('project')])['intent'])

    def test_mixed_case_logo_clips_script_model(self):
        p = self.go('Film de marque', [fake('image', 'logo'), *[fake('video')] * 10, fake('document'), fake('3d', readable=True)])
        self.assertTrue({'EDIT_FOOTAGE', 'HYBRID_COMPOSITE', 'DATA_EXPLAINER'} <= set(p['intent']))

    def test_vertical_from_platform_and_three_languages(self):
        self.assertEqual(self.go('Un reel pour TikTok')['deliverables'][0]['format'], '9:16')
        for brief, lang in (('Je veux une vidéo pour mon café', 'fr'), ('Quiero un vídeo para mi café', 'es'), ('I want a video for my cafe', 'en')):
            self.assertEqual(self.go(brief)['request']['language'], lang)

    def test_no_paid_engine_selected_by_default(self):
        for brief in ('Un logo', 'Une infographie', 'Une présentation interactive', 'Un personnage 3D'):
            self.assertNotIn('elevenlabs', engines(self.go(brief)))
            self.assertEqual(self.go(brief)['cost_ceiling']['amount'], 0)


class ManifestTests(unittest.TestCase):
    def test_rejects_bad_projects(self):
        good = route('Un logo', [], caps=CAPS)
        self.assertEqual(validate(good), [])
        for key, bad in (('intent', ['NOPE']), ('intent', []), ('status', 'peut-être'), ('cost_ceiling', {'amount': -1}), ('extra_field', 1), ('name', 'a/b')):
            broken = {**good, key: bad}
            self.assertTrue(validate(broken), key)
        missing = dict(good)
        del missing['request']
        self.assertTrue(validate(missing))

    def test_save_refuses_invalid(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                save({'name': 'x'}, Path(t) / 'p.json')

    def test_examples_route(self):
        for p in DEMOS.glob('*.json'):
            self.assertEqual(validate(plan(read_spec(p), DEMOS)), [], p.name)


class InventoryTests(unittest.TestCase):
    def test_glb_real_header(self):
        m = inspect(str(GLB))
        self.assertEqual(m['type'], '3d')
        self.assertTrue(m['metadata']['rigged'])
        self.assertIn('Wave', m['metadata']['animations'])
        self.assertFalse(m['metadata']['visemes'])
        self.assertTrue(any('bouche' in w for w in m['warnings']))

    def test_csv_ignores_comments(self):
        m = inspect(str(CSV))['metadata']
        self.assertEqual(m['columns'], ['year', 'mean', 'unc'])
        self.assertGreater(m['rows'], 60)

    def test_missing_file_is_reported(self):
        m = inspect('existe-pas.mp4', ROOT)
        self.assertFalse(m['exists'])
        self.assertEqual(route('', [m], caps=CAPS)['intent'], ['CREATE_FROM_SCRATCH'])

    def test_url_is_not_fetched(self):
        self.assertEqual(inspect('https://example.org/a.mp4')['type'], 'url')

    @unittest.skipUnless(HAS_FF, 'FFmpeg requis')
    def test_jpeg_logo_is_not_assumed_vector(self):
        with tempfile.TemporaryDirectory() as t:
            logo = Path(t) / 'logo.jpg'
            run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=red:s=128x128', '-frames:v', 1, logo])
            m = inspect(str(logo))
            self.assertEqual(m['role'], 'logo')
            self.assertFalse(m['metadata']['vector'])
            self.assertTrue(any('sans transparence' in w for w in m['warnings']))


class DataTests(unittest.TestCase):
    def test_figures_come_from_the_file(self):
        series = read_series(CSV)
        f = facts(series)
        self.assertEqual((f['y0'], f['v0']), (series[0]['year'], series[0]['mean']))
        self.assertEqual((f['y1'], f['v1']), (series[-1]['year'], series[-1]['mean']))
        self.assertAlmostEqual(f['diff'], series[-1]['mean'] - series[0]['mean'], places=2)

    def test_decade_rate_recomputed(self):
        series = read_series(CSV)
        by = {r['year']: r['mean'] for r in series}
        first = decade_rates(series)[0]
        self.assertEqual(first['decade'], 1960)
        self.assertAlmostEqual(first['rate'], (by[1969] - by[1959]) / 10, places=2)


class CatalogTests(unittest.TestCase):
    def test_search(self):
        self.assertTrue(any(s['id'] == 'logo-reveal' for s in search('logo')))
        self.assertEqual({s['categorie'] for s in search(category='3d')}, {'3d'})

    def test_hyperframes_blocks_exist_at_pinned_version(self):
        hf = load('hyperframes-0.8.164.json')
        known = set(hf['blocks']) | set(hf['components'])
        for s in load('style-catalog.json')['styles']:
            self.assertLessEqual(set(s['blocs_hyperframes']), known, s['id'])

    def test_required_presets(self):
        art = {x['id'] for x in load('art-directions.json')['directions']}
        self.assertEqual(art, {'cinematic-hollywood', 'stylized-3d', 'cartoon-caricature', 'photorealistic-commercial', 'hybrid-live-action-cgi', 'educational-3d', 'cinematic-logo-reveal', 'animated-photo', 'documentary-premium', 'immersive-5d-inspired'})
        demos = {x['id'] for x in load('demonstrators.json')['demonstrators']}
        self.assertEqual(demos, {'agency-saas-launch', 'premium-service-presentation', 'scientific-explainer', 'animated-infographic', '3d-character-presenter', '3d-product-showcase', 'interactive-services-deck', 'cinematic-hybrid'})

    def test_routed_presets_exist(self):
        art = {x['id'] for x in load('art-directions.json')['directions']}
        from universal.router import ART
        self.assertLessEqual({name for name, _ in ART}, art)


class HTMLTests(unittest.TestCase):
    def test_service_deck_accessible(self):
        with tempfile.TemporaryDirectory() as t:
            file = Path(t) / 'services.html'
            r = presentation(read_spec(DEMOS / 'services.json'), file)
            html = file.read_text(encoding='utf-8')
            self.assertEqual(r['services'], 5)
            self.assertIn('data-open="4"', html)
            self.assertIn('prefers-reduced-motion', html)
            self.assertNotIn('http://', re.sub(r'http://www\.w3\.org\S*', '', html))

    def test_no_invented_price(self):
        with tempfile.TemporaryDirectory() as t:
            file = Path(t) / 's.html'
            presentation({'language': 'en', 'services': [{'title': 'A'}, {'title': 'B', 'price': '100 EUR'}]}, file)
            html = file.read_text(encoding='utf-8')
            self.assertIn('Price on request', html)
            self.assertIn('100 EUR', html)

    def test_infographic(self):
        with tempfile.TemporaryDirectory() as t:
            file = Path(t) / 'info.html'
            r = infographic(read_spec(DEMOS / 'infographic.json'), file)
            self.assertEqual(r['steps'], 4)
            self.assertIn('Source / hypothèse', file.read_text(encoding='utf-8'))

    def test_escaped_input(self):
        with tempfile.TemporaryDirectory() as t:
            file = Path(t) / 'safe.html'
            presentation({'title': '<script>alert(1)</script>', 'services': [{'title': '<img src=x onerror=alert(1)>', 'summary': 'ok'}]}, file)
            h = file.read_text(encoding='utf-8')
            self.assertNotIn('<script>alert(1)</script>', h)
            self.assertIn('&lt;script&gt;', h)

    def test_http_link_only(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'x.html'
            presentation({'services': [{'title': 'Foo', 'url': 'javascript:alert(1)'}]}, p)
            self.assertNotIn('href="javascript:', p.read_text(encoding='utf-8'))


class QualityLogicTests(unittest.TestCase):
    def test_still_windows(self):
        times = [i / 30 for i in range(90)]
        ydif = [2.0] * 30 + [0.0] * 30 + [2.0] * 30
        self.assertEqual(still_windows(times, ydif), [[1.0, 2.0]])

    def test_srt_defects(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / 's.srt'
            f.write_text('1\n00:00:00,000 --> 00:00:02,000\nBonjour\n\n2\n00:00:01,000 --> 00:00:09,000\nSuite\n', encoding='utf-8')
            found = ' '.join(check_srt(f, 5))
            self.assertIn('chevauchement', found)
            self.assertIn('après la fin', found)


@unittest.skipUnless(HAS_FF, 'FFmpeg requis')
class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logo = fixtures.build(full=False)['logo']

    def test_formats(self):
        for x in ('16:9', '9:16', '1:1', '4:5'):
            w, h = dimensions(x, 'draft')
            self.assertEqual((w % 2, h % 2), (0, 0))

    def test_script_to_mp4(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'v.mp4'
            result = render({'brief': 'Bonjour monde', 'duration': 1.5}, ROOT, p, 'draft')
            self.assertGreater(result['bytes'], 1000)
            self.assertTrue(qc(p)['pass'], qc(p))

    def test_logo_to_mp4(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'v.mp4'
            spec = read_spec(DEMOS / 'logo-reveal.json')
            spec['duration'] = 1.5
            self.assertTrue(render(spec, DEMOS, p, 'draft')['logo'])
            self.assertTrue(qc(p)['pass'])

    def clip(self, folder, name='clip.mp4', size='320x180', seconds=.8):
        c = Path(folder) / name
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', f'testsrc2=s={size}:r=25:d={seconds}', '-f', 'lavfi', '-i', f'sine=frequency=440:duration={seconds}', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', c])
        return c

    def test_edit_cut_fade_portrait_and_logo(self):
        with tempfile.TemporaryDirectory() as t:
            a, b = self.clip(t), self.clip(t, 'b.mp4', '180x320')
            out = Path(t) / 'out.mp4'
            r = edit([{'src': str(a), 'seconds': .7}, {'src': str(b), 'seconds': .7, 'transition': 'fade', 'fade_s': .2}, {'src': str(a), 'seconds': .5, 'transition': 'cut'}], ROOT, out, fmt='9:16', logo=self.logo)
            self.assertEqual(r['scenes'], 3)
            self.assertLess(r['width'], r['height'])
            self.assertAlmostEqual(r['duration'], 1.7, delta=.15)
            report = qc(out)
            self.assertTrue(report['pass'], report['blocking'])
            self.assertEqual(report['pix_fmt'], 'yuv420p')

    def test_originals_never_change(self):
        with tempfile.TemporaryDirectory() as t:
            a = self.clip(t)
            before = a.read_bytes()
            edit([{'src': str(a), 'seconds': .5}], ROOT, Path(t) / 'o.mp4')
            self.assertEqual(before, a.read_bytes())

    def test_undeclared_black_blocks_and_declared_passes(self):
        with tempfile.TemporaryDirectory() as t:
            v = Path(t) / 'noir.mp4'
            run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=320x180:r=25:d=1.5', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', v])
            self.assertFalse(qc(v)['pass'])
            self.assertTrue(qc(v, exceptions=[{'type': 'black', 'from': 0, 'to': 2, 'reason': 'silence écrit'}, {'type': 'freeze', 'from': 0, 'to': 2}])['pass'])

    def test_expected_format_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            a = self.clip(t)
            self.assertFalse(qc(a, expect={'width': 1920, 'height': 1080})['pass'])


class ElevenLabsTests(unittest.TestCase):
    ALIGN = {'characters': list('Hola, mi voz'), 'character_start_times_seconds': [i * .1 for i in range(12)], 'character_end_times_seconds': [(i + 1) * .1 for i in range(12)]}

    def test_no_paid_call_without_approval(self):
        from universal import voice_elevenlabs as el
        with tempfile.TemporaryDirectory() as t:
            original, el.CACHE = el.CACHE, Path(t) / 'cache'
            calls = []
            real, el._request = el._request, lambda *a: calls.append(a)
            try:
                with self.assertRaises(el.ApprovalRequired):
                    el.synthesize('Bonjour', Path(t) / 'a.mp3', 'fr', 'voz')
                self.assertEqual(calls, [])
            finally:
                el.CACHE, el._request = original, real

    def test_ceiling_blocks_even_when_approved(self):
        from universal import voice_elevenlabs as el
        with tempfile.TemporaryDirectory() as t:
            original, el.CACHE = el.CACHE, Path(t) / 'cache'
            try:
                with self.assertRaises(el.ApprovalRequired):
                    el.synthesize('x' * 50, Path(t) / 'a.mp3', 'fr', 'voz', approved=True, max_chars=10)
            finally:
                el.CACHE = original

    def test_cache_is_free_and_needs_no_approval(self):
        from universal import voice_elevenlabs as el
        with tempfile.TemporaryDirectory() as t:
            original, el.CACHE = el.CACHE, Path(t) / 'cache'
            try:
                el.CACHE.mkdir()
                k = el.cache_key('Bonjour', 'voz', el.DEFAULT_MODEL, 'fr')
                (el.CACHE / f'{k}.mp3').write_bytes(b'x')
                (el.CACHE / f'{k}.json').write_text('{"words": [], "visemes": [], "chars_billed": 7}', encoding='utf-8')
                self.assertEqual(el.synthesize('Bonjour', Path(t) / 'a.mp3', 'fr', 'voz')['chars_billed_now'], 0)
            finally:
                el.CACHE = original

    def test_words_keep_punctuation_and_real_times(self):
        from universal import voice_elevenlabs as el
        w = el.words_from_alignment(self.ALIGN)
        self.assertEqual([x['text'] for x in w], ['Hola,', 'mi', 'voz'])
        self.assertEqual((w[1]['start'], w[1]['end']), (.6, .8))

    def test_mouth_closes_on_pauses(self):
        from universal import voice_elevenlabs as el
        v = el.visemes_from_alignment({'characters': list('a a'), 'character_start_times_seconds': [0, .1, .5], 'character_end_times_seconds': [.1, .5, .6]})
        self.assertEqual([x['id'] for x in v], [2, 0, 2])

    def test_key_never_leaves_in_marks(self):
        from universal import voice_elevenlabs as el
        marks = el.marks_from_response({'alignment': self.ALIGN}, 'Hola, mi voz', 'voz', 'm', 'es')
        self.assertNotIn('key', ' '.join(marks))
        self.assertEqual(marks['visemes_source'], 'letters')


class NarrationTests(unittest.TestCase):
    def test_each_language_has_seven_sentences_and_computed_figures(self):
        from universal.datos import narration, number
        f = facts(read_series(CSV))
        for lang in ('en', 'fr', 'es'):
            text = narration(f, lang)
            self.assertEqual(len(re.findall(r'[.!?](?:\s|$)', text)), 7, lang)
            for value in (f['y0'], round(f['v0']), f['y1'], round(f['v1']), round(f['diff']), number(f['r0'], lang), number(f['r1'], lang)):
                self.assertIn(str(value), text, lang)


@unittest.skipUnless(platform.system() == 'Windows' and HAS_FF, 'Voix Windows requise')
class VoiceTests(unittest.TestCase):
    def test_marks_match_measured_silences(self):
        from universal.voice import synthesize, to_srt
        with tempfile.TemporaryDirectory() as t:
            wav = Path(t) / 'v.wav'
            m = synthesize('Hello! Watch my mouth: it follows the real sounds.', wav, 'en')
            self.assertEqual(m['words'][0]['text'], 'Hello!')
            log = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(wav), '-af', 'silencedetect=n=-40dB:d=0.12', '-f', 'null', '-'], capture_output=True, text=True).stderr
            ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
            watch = next(w for w in m['words'] if w['text'] == 'Watch')
            self.assertLess(min(abs(watch['start'] - e) for e in ends), .06)
            self.assertLessEqual(max(w['end'] for w in m['words']), m['duration'] + .01)
            self.assertAlmostEqual(sum(v['duration'] for v in m['visemes']), m['duration'], delta=.03)
            self.assertEqual(check_srt(to_srt(m['words'], Path(t) / 'v.srt'), m['duration']), [])


if __name__ == '__main__':
    unittest.main()
