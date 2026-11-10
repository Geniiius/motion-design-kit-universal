import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from universal import config, manifest, modules, perfil, workflows
from universal.inventory import inspect
from universal.qc import qc
from universal.router import has, norm, route
from universal.run import NOT_UNDERSTOOD, _edl_from_inputs, run_project
from universal.workflows import captions, chapters, clips, reframe, silence_cut, tools, transcript

ROOT = Path(__file__).resolve().parents[1]
HAS_FF = bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))
HAS_SPEECH = HAS_FF and transcript.missing() is None and (modules.VENV / '.tier-voice').exists() and (ROOT / 'modules/opuscar/core/tts/kokoro-v1.0.onnx').exists()
CAPS = {'tools': {'blender': False, 'three_vrm': False}, 'engines': {k: True for k in ('ffmpeg-edit', 'video-workflow', 'html-deck', 'remotion-2d', 'remotion-3d', 'film-style', 'video-effects')}}


def video(path='clip.mp4', **meta):
    return {'path': path, 'type': 'video', 'role': 'source', 'exists': True, 'metadata': meta, 'rights': {'status': 'unknown'}, 'provenance': {}, 'warnings': [], 'treatment': []}


def logo():
    return {**video('logo.png'), 'type': 'image', 'role': 'logo'}


def engines(p):
    return [e['id'] for e in p['engines']]


def tone_video(path: Path, size='640x360'):
    """7 s: a tone for 1.5 s, silence for 2 s, twice. Nothing but generated signals."""
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', f'testsrc2=s={size}:r=25:d=7', '-f', 'lavfi', '-i',
                    "aevalsrc='0.3*sin(2*PI*440*t)*lt(mod(t,3.5),1.5)':d=7:s=48000", '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(path)], check=True)
    return path


class PureLogic(unittest.TestCase):
    def test_registry_finds_the_treatments_in_their_order(self):
        self.assertEqual(list(workflows.registry()), ['silence-cut', 'clips', 'reframe', 'captions', 'chapters'])
        for mod in workflows.registry().values():
            self.assertEqual(set(mod.TITLE), {'fr', 'es', 'en'}, mod.ID)
            has(' essai ', mod.WORDS)  # every pattern compiles
        self.assertEqual(len(workflows.catalog('es')), 5)

    def test_only_the_inside_of_a_silence_is_cut(self):
        kept = silence_cut.keep_segments([(1.5, 3.5), (5.0, 7.0)], 7.0, .12, .15)
        self.assertEqual(kept, [(0.0, 1.62), (3.38, 5.12)])
        self.assertEqual(silence_cut.keep_segments([(0.0, 1.0)], 4.0, .12, .15), [(0.88, 4.0)])
        self.assertEqual(silence_cut.keep_segments([], 4.0, .12, .15), [(0.0, 4.0)])
        self.assertEqual(silence_cut.keep_segments([(1.0, 1.2)], 4.0, .12, .15), [(0.0, 4.0)], 'a pause shorter than its two breaths stays')
        self.assertEqual(silence_cut.expression([(0.0, 1.62), (3.38, 5.12)]), 'between(t,0.0,1.62)+between(t,3.38,5.12)')
        self.assertEqual(silence_cut.removed_before([(0.0, 1.62), (3.38, 5.12)]), '1.76*gte(T,3.38)')
        self.assertEqual(silence_cut.removed_before([(0.88, 4.0)]), '0.88*gte(T,0.88)', 'a silence at the very start moves everything back')
        self.assertEqual(silence_cut.removed_before([(0.0, 4.0)]), '0')

    def test_a_long_video_does_not_outgrow_what_ffmpeg_accepts(self):
        depth = lambda text: max((text[:i].count('(') - text[:i].count(')') for i in range(len(text))), default=0)
        terms = [f'between(t,{i},{i + .5})' for i in range(1000)]
        whole = tools.balanced_sum(terms)
        self.assertEqual(whole.count('between'), 1000)
        self.assertLess(depth(whole), 16, 'a thousand cuts stay far under the hundred levels FFmpeg accepts')
        self.assertEqual(tools.balanced_sum(['a']), 'a')
        self.assertEqual(tools.balanced_sum(['a', 'b', 'c']), '(a)+(b+c)')
        self.assertEqual(eval(tools.balanced_sum([str(i) for i in range(1, 101)])), 5050)
        hour = reframe.crop_plan([{'t': i * .5, 'x': .2 + .6 * (i % 40) / 40, 'y': .4, 'w': .1} for i in range(7200)], 1920, 1080, 1080, 1920, 3600)
        self.assertEqual(hour['mode'], 'moving')
        self.assertLess(depth(reframe.crop_filter(hour)), 20)

    def test_a_clip_lands_on_word_boundaries(self):
        words = [{'text': 'Bonjour', 'start': 1.0, 'end': 1.5}, {'text': 'à', 'start': 1.6, 'end': 1.7}, {'text': 'tous.', 'start': 1.8, 'end': 2.4}]
        self.assertEqual(clips.snap(1.2, 2.2, words, 10), (0.88, 2.7))
        self.assertEqual(clips.snap(5.0, 8.0, words, 10), (4.88, 8.3), 'no word within reach: the times are kept')
        self.assertEqual(clips.snap(0.0, 9.9, [], 10), (0.0, 10))
        self.assertTrue(clips.check([{'in': 1, 'out': 2}], 60))
        self.assertTrue(clips.check([{'in': 50, 'out': 70}], 60))
        self.assertTrue(clips.check('n\'importe quoi', 60))
        self.assertEqual(clips.check([{'in': 1, 'out': 9}], 60), [])

    def test_chapters_are_checked_and_written_as_a_platform_reads_them(self):
        good = [{'t': 0, 'title': 'Introduction'}, {'t': 95, 'title': 'Le sujet'}, {'t': 3725, 'title': 'Conclusion'}]
        self.assertEqual(chapters.check(good, 4000), [])
        self.assertEqual(chapters.text(good), '00:00 Introduction\n01:35 Le sujet\n1:02:05 Conclusion\n')
        self.assertTrue(chapters.check(good[:2], 4000))
        self.assertTrue(chapters.check([{'t': 5, 'title': 'a'}, {'t': 30, 'title': 'b'}, {'t': 60, 'title': 'c'}], 100))
        self.assertTrue(chapters.check([{'t': 0, 'title': 'a'}, {'t': 4, 'title': 'b'}, {'t': 60, 'title': 'c'}], 100))

    def test_languages_named_in_a_request(self):
        self.assertEqual(captions.languages_in(norm('Sous-titre ma vidéo en anglais et en espagnol')), ['en', 'es'])
        self.assertEqual(captions.languages_in(norm('Subtítulos en alemán y en francés')), ['de', 'fr'])
        self.assertEqual(captions.languages_in(norm('Ajoute des sous-titres')), [])
        self.assertEqual(captions.languages_in(norm('la bibliothèque française de films')), [], 'a word that only starts like a language')

    def test_a_translation_keeps_numbers_and_times(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'a.srt', Path(d) / 'b.srt'
            a.write_text('1\n00:00:01,000 --> 00:00:02,000\nBonjour\n\n2\n00:00:03,000 --> 00:00:04,500\nÀ bientôt\n', encoding='utf-8')
            self.assertEqual(captions.cues(a), [(1.0, 2.0, 'Bonjour'), (3.0, 4.5, 'À bientôt')])
            self.assertEqual(captions.compare(a, b), ['le fichier b.srt manque'])
            b.write_text('1\n00:00:01,000 --> 00:00:02,000\nHello\n\n2\n00:00:03,000 --> 00:00:04,500\nSee you soon\n', encoding='utf-8')
            self.assertEqual(captions.compare(a, b), [])
            b.write_text('1\n00:00:01,000 --> 00:00:02,000\nHello\n', encoding='utf-8')
            self.assertTrue(captions.compare(a, b))
            b.write_text('1\n00:00:01,400 --> 00:00:02,000\nHello\n\n2\n00:00:03,000 --> 00:00:04,500\nSee you soon\n', encoding='utf-8')
            self.assertIn('horaires', captions.compare(a, b)[0])

    def test_a_still_face_gets_a_fixed_frame_and_a_moving_one_is_followed(self):
        still = [{'t': i * .5, 'x': .7 + (.004 if i % 2 else -.004), 'y': .4, 'w': .1} for i in range(20)]
        plan = reframe.crop_plan(still, 1920, 1080, 1080, 1920, 10)
        self.assertEqual((plan['cw'], plan['ch'], plan['axis'], plan['mode']), (608, 1080, 'x', 'fixed'))
        self.assertAlmostEqual(plan['at'], .7 * 1920 - 304, delta=12)
        self.assertEqual(reframe.crop_filter(plan), f"crop=608:1080:{plan['at']}:0,setsar=1")
        walk = [{'t': i * .5, 'x': .2 + .6 * i / 19, 'y': .4, 'w': .1} for i in range(20)]
        moving = reframe.crop_plan(walk, 1920, 1080, 1080, 1920, 10)
        self.assertEqual(moving['mode'], 'moving')
        values = [v for _, v in moving['keys']]
        self.assertLess(values[0], values[-1])
        self.assertTrue(all(0 <= v <= 1920 - 608 for v in values))
        self.assertLess(max(abs(b - a) for a, b in zip(values, values[1:])), 120, 'the frame glides')
        self.assertIn('gte(t,', reframe.crop_filter(moving))
        nobody = reframe.crop_plan([{'t': 0}, {'t': .5}], 1920, 1080, 1080, 1920, 1)
        self.assertEqual((nobody['mode'], nobody['at']), ('fixed', 656), 'no face: the middle')
        tall = reframe.crop_plan([{'t': 0, 'x': .5, 'y': .3, 'w': .2}], 1080, 1920, 1920, 1080, 1)
        self.assertEqual((tall['cw'], tall['ch'], tall['axis']), (1080, 608, 'y'))

    def test_sentences_and_stamps(self):
        words = [{'text': 'Un', 'start': 0, 'end': .2}, {'text': 'deux.', 'start': .3, 'end': .6}, {'text': 'Trois', 'start': 2.0, 'end': 2.3}, {'text': 'quatre', 'start': 3.5, 'end': 3.9}]
        self.assertEqual([s['text'] for s in transcript.sentences(words)], ['Un deux.', 'Trois', 'quatre'])
        self.assertEqual(transcript.stamp(75.25), '01:15.2')
        self.assertEqual(transcript.stamp(3725, tenths=False), '1:02:05')

    def test_settings_have_one_home_and_a_local_change_wins(self):
        self.assertEqual(config.get('workflows.silence.padding_s'), .12)
        self.assertIsNone(config.get('rien.du.tout'))
        self.assertEqual(config._merge({'a': {'b': 1, 'c': 2}}, {'a': {'b': 5}}), {'a': {'b': 5, 'c': 2}})


class Routing(unittest.TestCase):
    def test_a_provided_video_keeps_its_own_shape(self):
        p = route('Ajoute des sous-titres', [video(width=1080, height=1920, duration_s=20)], caps=CAPS)
        d = p['deliverables'][0]
        self.assertEqual((d['format'], d['width'], d['height']), ('source', 1080, 1920))
        self.assertEqual(d['adapter'], {'engine': 'video-workflow', 'steps': ['captions']})
        self.assertEqual(manifest.validate(p), [])
        sideways = route('Ajoute des sous-titres', [video(width=1920, height=1080, rotation=90)], caps=CAPS)['deliverables'][0]
        self.assertEqual((sideways['width'], sideways['height']), (1080, 1920))

    def test_a_named_platform_sets_the_shape_and_the_reframing(self):
        d = route('Ajoute des sous-titres pour TikTok', [video(width=1920, height=1080)], caps=CAPS)['deliverables'][0]
        self.assertEqual(d['format'], '9:16')
        self.assertEqual(d['adapter']['steps'], ['reframe', 'captions'])
        self.assertEqual(route('Une vidéo pour Instagram', [], caps=CAPS)['deliverables'][0]['format'], '9:16')
        self.assertEqual(route('Une vidéo pour le feed Instagram', [], caps=CAPS)['deliverables'][0]['format'], '4:5')
        self.assertEqual(route('Un YouTube Short', [], caps=CAPS)['deliverables'][0]['format'], '9:16')

    def test_several_clips_remain_a_montage(self):
        p = route('Monte ces clips avec des sous-titres pour Reels', [video('a.mp4'), video('b.mp4')], caps=CAPS)
        self.assertEqual(engines(p), ['ffmpeg-edit'])
        self.assertTrue(any('monter d\'abord' in n for n in p['notes']))
        with self.assertRaises(ValueError):
            route('Sous-titres', [video('a.mp4'), video('b.mp4')], caps=CAPS, workflow=['captions'])

    def test_the_agent_names_the_treatment(self):
        p = route('Coupe les moments où je ne dis rien', [video()], caps=CAPS, workflow=['silence-cut'])
        self.assertEqual(p['deliverables'][0]['adapter'], {'engine': 'video-workflow', 'steps': ['silence-cut']})
        self.assertEqual(p['understanding']['source'], 'agent')
        self.assertFalse(route('Coupe les moments où je ne dis rien', [video()], caps=CAPS)['understanding']['certain'])

    def test_languages_reach_the_manifest(self):
        p = route('Sous-titre ma vidéo en anglais et en espagnol', [video()], caps=CAPS)
        self.assertEqual(p['props'], {'workflow': {'captions': {'languages': ['en', 'es']}}})
        self.assertEqual(manifest.validate(p), [])

    def test_a_change_of_form_is_not_a_change_of_look(self):
        p = route("Transforme mon podcast en petits extraits pour TikTok", [video()], caps=CAPS)
        self.assertNotIn('RESTYLE_FOOTAGE', p['intent'])
        self.assertEqual(p['deliverables'][0]['adapter']['steps'], ['clips', 'reframe'])
        for brief in ('Transforme cette vidéo en dessin animé', 'Transforme cette vidéo en aquarelle avec des sous-titres'):
            self.assertIn('RESTYLE_FOOTAGE', route(brief, [video()], caps=CAPS)['intent'], brief)

    def test_fresh_phrases_about_a_provided_video_never_fail_in_silence(self):
        from tests.phrases_naturelles import VIDEO_HOLDOUT, measure
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            report = measure(VIDEO_HOLDOUT, 'test')
        self.assertEqual(report['fausses_sans_le_dire'], 0)


class Delivery(unittest.TestCase):
    def project(self, items, **deliverable):
        return {'timeline': {'edl': []}, 'inputs': items, 'deliverables': [{'kind': 'video', **deliverable}]}

    def test_whole_media_in_order_is_the_default(self):
        edl, how = _edl_from_inputs(self.project([video('a.mp4', duration_s=40), video('b.mp4', duration_s=12), logo()]))
        self.assertEqual([(x['src'], x.get('seconds')) for x in edl], [('a.mp4', None), ('b.mp4', None)])
        self.assertIn('entiers', how)

    def test_only_an_asked_duration_shortens_and_it_says_so(self):
        edl, how = _edl_from_inputs(self.project([video('a.mp4', duration_s=40), video('b.mp4', duration_s=12)], duration_s=20))
        self.assertEqual([x['seconds'] for x in edl], [10.0, 10.0])
        self.assertIn('à vérifier', how)
        whole, _ = _edl_from_inputs(self.project([video('a.mp4', duration_s=8)], duration_s=20))
        self.assertNotIn('seconds', whole[0], 'shorter than asked: nothing to cut')

    def test_only_a_real_shape_becomes_a_habit(self):
        self.assertEqual(perfil.shape_name({'format': 'source', 'width': 1080, 'height': 1920}), '9:16')
        self.assertEqual(perfil.shape_name({'format': '4:5'}), '4:5')
        self.assertIsNone(perfil.shape_name({'format': 'source', 'width': 720, 'height': 576}))
        self.assertIsNone(perfil.shape_name({'format': 'responsive'}))
        saved = perfil.DIR
        with tempfile.TemporaryDirectory() as d:
            perfil.DIR = Path(d)
            try:
                p = route('Ajoute des sous-titres', [video(width=720, height=576)], caps=CAPS)
                for _ in range(2):
                    perfil.remember_delivery(p, p['deliverables'][0], {'qc': {}})
                self.assertIsNone(perfil.habit('format'), 'an odd source shape must not become the default of the next film')
                again = route('Une vidéo sur notre nouveau service', [], caps=CAPS, profile=perfil.context())
                self.assertEqual(again['deliverables'][0]['format'], '16:9')
            finally:
                perfil.DIR = saved

    def test_a_request_that_was_not_understood_is_never_delivered(self):
        p = route('Ça fait pas assez pro, améliore', [video()], caps=CAPS)
        self.assertFalse(p['understanding']['certain'])
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'p.json'
            manifest.save(p, path)
            with self.assertRaises(RuntimeError) as caught:
                run_project(path, 'draft', Path(d) / 'out')
            self.assertEqual(str(caught.exception), NOT_UNDERSTOOD)
            self.assertFalse((Path(d) / 'out').exists() and any((Path(d) / 'out').rglob('*.mp4')))


@unittest.skipUnless(HAS_FF, 'ffmpeg absent')
class RealRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.saved = perfil.DIR
        perfil.DIR = self.dir / 'perfil'
        self.clip = tone_video(self.dir / 'parle.mp4')

    def tearDown(self):
        perfil.DIR = self.saved
        self.tmp.cleanup()

    def go(self, brief, extra=(), change=None, profile='draft', **kw):
        p = route(brief, [inspect(str(self.clip))] + list(extra), name='essai', caps=CAPS, **kw)
        if change:
            change(p)
        path = self.dir / 'essai.json'
        manifest.save(p, path)
        return run_project(path, profile, self.dir / 'out'), self.dir / 'out' / 'essai'

    def test_a_provided_video_is_delivered_whole(self):
        logo_file = self.dir / 'logo.png'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=white:s=200x200', '-frames:v', '1', str(logo_file)], check=True)
        r, out = self.go('Ajoute mon logo à cette vidéo', [inspect({'path': str(logo_file), 'role': 'logo'})])
        self.assertEqual(r['status'], 'delivered')
        self.assertAlmostEqual(tools.info(out / 'essai.mp4')['duration'], 7, delta=.2)
        self.assertTrue(r['results'][0]['logo'])
        self.assertIn('entiers', r['results'][0]['montage'])

    def test_silences_are_removed_and_the_length_is_checked(self):
        r, out = self.go('Enlève les silences de ma vidéo')
        res = r['results'][0]
        self.assertEqual((r['status'], res['steps']), ('delivered', ['silence-cut']))
        self.assertAlmostEqual(tools.info(out / 'essai.mp4')['duration'], 3.36, delta=.25)
        self.assertAlmostEqual(res['outputs'][0]['expected_s'], 3.36, delta=.1)
        self.assertTrue(any('coupes' in n for n in res['notes']))

    def test_a_video_without_silence_is_left_alone(self):
        steady = self.dir / 'continu.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=320x180:r=25:d=3', '-f', 'lavfi', '-i', 'sine=f=440:d=3', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-shortest', str(steady)], check=True)
        self.clip = steady
        r, out = self.go('Enlève les silences')
        self.assertEqual(r['status'], 'unchanged', 'nothing was done: saying "delivered" would be false')
        self.assertTrue(any('aucun silence' in n for n in r['results'][0]['notes']))
        self.assertIn('Rien à changer', r['results'][0]['qc']['note'])
        self.assertEqual(list(out.glob('*.mp4')), [], 'no second copy of a video nothing touched')
        self.assertEqual(manifest.load(self.dir / 'essai.json')['status'], 'unchanged')
        self.assertFalse((perfil.DIR / 'historial.jsonl').exists(), 'and it is not remembered as a delivery')

    def test_sound_and_picture_stay_together_after_a_hundred_cuts(self):
        # The picture is white exactly while the tone sounds: after the cuts, the last flash must still start with the last tone
        long = self.dir / 'cent-coupes.mp4'
        beat = "lt(mod(t,1.2),0.4)"
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', f"testsrc2=s=160x90:r=25:d=130,drawbox=x=0:y=0:w=iw:h=ih:color=white:t=fill:enable='{beat}'", '-f', 'lavfi', '-i',
                        f"aevalsrc='0.3*sin(2*PI*440*t)*{beat}':d=130:s=48000", '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(long)], check=True)
        self.clip = long
        r, out = self.go('Enlève les silences de ma vidéo')
        res, made = r['results'][0], out / 'essai.mp4'
        self.assertEqual(r['status'], 'delivered', res['qc'].get('blocking'))
        self.assertIn('108 coupes', ' '.join(res['notes']), 'more cuts than one FFmpeg expression used to accept')
        self.assertAlmostEqual(tools.info(made)['duration'], res['outputs'][0]['expected_s'], delta=.3)
        seen = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(made), '-vf', 'signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-', '-an', '-f', 'null', '-'],
                              capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
        import re
        frames = [(float(t), float(y) > 200) for t, y in re.findall(r'pts_time:([\d.]+)\s+lavfi\.signalstats\.YAVG=([\d.]+)', seen)]
        flashes = [t for (t, lit), (_, before) in zip(frames[1:], frames) if lit and not before]
        tones = [end for _, end in silence_cut.detect(made, -35.0, .05, tools.info(made)['duration'])]
        self.assertGreater(len(flashes), 100)
        self.assertLess(abs(len(flashes) - len(tones)), 3)
        for flash, tone in zip(flashes[-5:], tones[-5:]):
            self.assertLess(abs(flash - tone), .09, 'two frames at most between the last flashes and their tones')

    def test_a_frame_that_follows_a_face_for_minutes(self):
        plan = reframe.crop_plan([{'t': i * .5, 'x': .15 + .7 * (i % 30) / 30, 'y': .5, 'w': .1} for i in range(600)], 640, 360, 360, 640, 300)
        self.assertEqual((plan['mode'], len(plan['keys']) > 500), ('moving', True))
        out = self.dir / 'suivi-long.mp4'
        tools.ffmpeg(['-i', self.clip] + tools.graph_args(f'[0:v]{reframe.crop_filter(plan)}[v]', self.dir) + ['-map', '[v]', '-an'] + tools.INTERMEDIATE[:8] + [out])
        self.assertAlmostEqual(tools.info(out)['duration'], 7, delta=.2)

    def test_reframing_gives_the_asked_shape_without_stretching(self):
        r, out = self.go('Mets ma vidéo au format TikTok', change=lambda p: p.setdefault('props', {}).update(workflow={'reframe': {'mode': 'center'}}))
        meta = tools.info(out / 'essai.mp4')
        self.assertEqual((meta['width'], meta['height']), (360, 640))
        self.assertAlmostEqual(meta['duration'], 7, delta=.2)
        self.assertTrue(any('centre' in n for n in r['results'][0]['notes']))
        r, out = self.go('Mets ma vidéo au format TikTok', change=lambda p: p.setdefault('props', {}).update(workflow={'reframe': {'mode': 'blur'}}))
        self.assertEqual(tools.info(out / 'essai.mp4')['height'], 640)

    def test_a_followed_face_moves_the_frame(self):
        plan = reframe.crop_plan([{'t': i * .5, 'x': .15 + .7 * i / 13, 'y': .5, 'w': .1} for i in range(14)], 640, 360, 360, 640, 7)
        self.assertEqual(plan['mode'], 'moving')
        out = self.dir / 'suivi.mp4'
        tools.ffmpeg(['-i', self.clip] + tools.graph_args(f'[0:v]{reframe.crop_filter(plan)}[v]', self.dir) + ['-map', '[v]', '-an'] + tools.INTERMEDIATE[:8] + [out])
        meta = tools.info(out)
        self.assertEqual((meta['width'], meta['height']), (plan['cw'], plan['ch']))
        self.assertAlmostEqual(meta['duration'], 7, delta=.2)

    def test_clips_wait_for_a_choice_then_come_out_one_file_each(self):
        with self.assertRaises(RuntimeError):  # no speech to read, or no transcription here: the kit asks, it never picks moments blindly
            self.go('Fais des extraits de cette vidéo')
        pick = lambda p: p.setdefault('props', {}).update(workflow={'clips': [{'in': 0, 'out': 3.2}, {'in': 3.4, 'out': 6.9}]})
        r, out = self.go('Fais des extraits de cette vidéo', change=pick)
        files = [Path(o['output']).name for o in r['results'][0]['outputs']]
        self.assertEqual(files, ['essai-1.mp4', 'essai-2.mp4'])
        self.assertEqual(r['status'], 'delivered')
        self.assertEqual(r['results'][0]['qc']['files'], 2)

    def test_chapters_alone_write_a_text_and_no_new_video(self):
        long = self.dir / 'long.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=320x180:r=10:d=45', '-f', 'lavfi', '-i', 'sine=f=330:d=45', '-c:v', 'libx264', '-preset', 'ultrafast',
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(long)], check=True)
        self.clip = long
        chapters = lambda *rows: lambda p: p.setdefault('props', {}).update(workflow={'chapters': [{'t': t, 'title': title} for t, title in rows]})
        with self.assertRaises(ValueError):
            self.go('Ajoute des chapitres', change=chapters((0, 'Début'), (100, 'Milieu'), (200, 'Fin')))
        with self.assertRaises(ValueError):
            self.go('Ajoute des chapitres', change=chapters((0, 'Début')))
        r, out = self.go('Ajoute des chapitres', change=chapters((0, 'Début'), (15, 'Milieu'), (31, 'Fin')))
        self.assertEqual(r['status'], 'delivered')
        self.assertEqual((out / 'essai.chapitres.txt').read_text(encoding='utf-8'), '00:00 Début\n00:15 Milieu\n00:31 Fin\n')
        self.assertIsNone(r['results'][0]['output'])
        self.assertEqual(list(out.glob('*.mp4')), [], 'chapters are a text: the video is not encoded again')

    def test_a_peak_left_after_encoding_is_brought_down(self):
        from universal import render
        loud = self.dir / 'trop-fort.mp4'
        # A float track above full scale, as an encoder overshoot leaves it: the safety net must bring it under the limit
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=320x180:r=25:d=2', '-f', 'lavfi', '-i', "aevalsrc='1.6*sin(2*PI*440*t)':d=2:s=48000",
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(loud)], check=True)
        self.assertGreater(render.true_peak(loud), -1.0)
        self.assertIn('son baissé', render.limit_peak(loud))
        self.assertLessEqual(render.true_peak(loud), -1.0)
        self.assertIsNone(render.limit_peak(loud), 'nothing to do the second time')
        self.assertAlmostEqual(tools.info(loud)['duration'], 2, delta=.1)

    def test_a_loud_first_sample_does_not_saturate_the_delivery(self):
        # Quiet speech-like sound that starts loud on its very first sample, as a film's music can: it needs gain, and the first AAC frame used to overshoot
        hit = self.dir / 'attaque.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=320x180:r=25:d=6', '-f', 'lavfi', '-i',
                        "aevalsrc='0.55*sin(2*PI*180*t)*lt(t,0.15)+0.06*sin(2*PI*440*t)*lt(mod(t,1),0.6)':d=6:s=48000", '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '256k', '-shortest', str(hit)], check=True)
        self.clip = hit
        r, out = self.go('Mets ma vidéo au format TikTok', change=lambda p: p.setdefault('props', {}).update(workflow={'reframe': {'mode': 'center'}}))
        self.assertEqual(r['status'], 'delivered', r['results'][0]['qc'].get('blocking'))
        self.assertLessEqual(qc(out / 'essai.mp4')['audio']['true_peak'], -1.0)

    def test_the_last_encode_is_measured(self):
        r, out = self.go('Enlève les silences de ma vidéo')
        report = qc(out / 'essai.mp4')
        self.assertEqual(report['pix_fmt'], 'yuv420p')
        self.assertAlmostEqual(report['audio']['lufs'], config.get('render.loudness_lufs'), delta=2.5)
        self.assertLess(report['audio']['true_peak'], -.5)


@unittest.skipUnless(HAS_SPEECH, 'voix locale et transcription absentes')
class RealSpeech(unittest.TestCase):
    def test_captions_stop_for_a_reading_then_burn_and_translate(self):
        from universal import voice_kokoro
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            saved, perfil.DIR = perfil.DIR, d / 'perfil'
            try:
                voice_kokoro.synthesize('Bonjour à tous. Ceci est un essai de sous-titres.', d / 'voix.wav', 'fr')
                clip = d / 'parle.mp4'
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=640x360:r=25:d=20', '-i', str(d / 'voix.wav'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                                '-c:a', 'aac', '-shortest', str(clip)], check=True)
                p = route('Sous-titre ma vidéo en anglais', [inspect(str(clip))], name='st', caps=CAPS)
                path = d / 'st.json'
                manifest.save(p, path)
                with self.assertRaises(workflows.NeedsInput) as first:
                    run_project(path, 'draft', d / 'out')
                source = Path(first.exception.file)
                self.assertEqual(source.name, 'st.fr.srt')
                rows = captions.cues(source)
                self.assertTrue(rows)
                p = manifest.load(path)
                p['props']['workflow']['captions']['reviewed'] = True
                manifest.save(p, path)
                with self.assertRaises(workflows.NeedsInput) as second:
                    run_project(path, 'draft', d / 'out')
                self.assertEqual(Path(second.exception.file).name, 'st.en.srt')
                stamp = lambda s: f'{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
                Path(second.exception.file).write_text('\n'.join(f'{i}\n{stamp(a)} --> {stamp(b)}\nLine {i}\n' for i, (a, b, _) in enumerate(rows, 1)), encoding='utf-8')
                r = run_project(path, 'draft', d / 'out')
                self.assertEqual(r['status'], 'delivered')
                self.assertTrue((d / 'out/st/st.mp4').exists())
            finally:
                perfil.DIR = saved


if __name__ == '__main__':
    unittest.main()
