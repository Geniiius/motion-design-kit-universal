import copy
import datetime
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from universal import config, design_check, diagnostic, logs, modules, onboarding, state
from universal.onboarding import FAILED, OPTIONAL, READY, WARNING

FAKE_KEY = 'sk' + '_abcdefghijklmnop1234'  # put together here: a key-shaped text in a shipped file would stop the packaging, rightly

BASE = {
    'machine': {'os': 'Windows 11', 'family': 'windows', 'arch': 'AMD64', 'bits': 64, 'cpu': 'Processeur', 'cores': 4, 'threads': 8, 'ram_gb': 16.0, 'ram_free_gb': 8.0,
                'gpus': [{'name': 'Carte', 'vram_gb': 4.0}], 'disk_free_gb': 100.0, 'disk_total_gb': 500.0},
    'software': {'python': {'found': True, 'ok': True, 'version': '3.13.2', 'minimum': '3.10', 'for_modules': 'py -3.13', 'modules_need': ['3.12', '3.13'], 'installed': ['3.13']},
                 'node': {'found': True, 'ok': True, 'version': '24.1.0', 'minimum': 22}, 'npm': {'found': True, 'version': '11.0.0'},
                 'ffmpeg': {'found': True, 'ok': True, 'version': '9.0.2', 'minimum': 6}, 'ffprobe': {'found': True},
                 'git': {'found': True, 'version': '2.55.0'}, 'uv': {'found': True, 'version': '0.12.10'},
                 'blender': {'found': True, 'path': 'blender', 'version': '5.2.3', 'on_path': True},
                 'package_manager': {'found': True, 'name': 'winget'}, 'elevenlabs_key': {'found': True}},
    'kit': {'remotion': {'installed': True, 'browser': True, 'version': '4.0.540'}, 'prompt-motion': {'installed': True, 'browser': True, 'version': '1.64.1'},
            'film': {'installed': True, 'browser': True, 'version': '1.64.1'}, 'design-check': {'installed': True},
            'tiers': {t: True for t in ('effects', 'audio', 'music', 'voice', 'transcribe')}, 'packs': {'voice-model': True}, 'whisper_model': True, 'profile': True},
    'conflicts': [],
}
GONE = {'ffmpeg': lambda s: s['software']['ffmpeg'].update(found=False, ok=False, version=None),
        'node': lambda s: s['software']['node'].update(found=False, ok=False, version=None),
        'engine-remotion': lambda s: s['kit']['remotion'].update(installed=False, browser=False, version=None),
        'captions': lambda s: s['kit'].update(whisper_model=False),
        'effects': lambda s: s['kit']['tiers'].update(effects=False),
        'voice-local': lambda s: s['kit']['tiers'].update(voice=False),
        'blender': lambda s: s['software']['blender'].update(found=False, version=None),
        'python-modules': lambda s: (s['software']['python'].update(for_modules=None), s['software']['uv'].update(found=False))}


def seen(*missing, manager='winget'):
    s = copy.deepcopy(BASE)
    for name in missing:
        GONE[name](s)
    s['software']['package_manager'] = {'found': bool(manager), 'name': manager or 'winget'}
    return s


class Isolated(unittest.TestCase):
    """Every test writes its state and its log in a temporary folder: the real installation is never touched."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.patches = [mock.patch.object(state, 'FILE', self.dir / 'kit-state.json'), mock.patch.object(logs, 'DIR', self.dir / 'logs'),
                        mock.patch.object(onboarding, 'npx_cached', lambda name, version: True), mock.patch.object(onboarding, 'ensure_profile', lambda: 'profil conservé'),
                        mock.patch.object(onboarding, 'refresh_path', lambda: None)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def world(self, *missing, manager='winget'):
        """A machine whose missing parts appear once their installer has run."""
        box = {'missing': set(missing), 'calls': [], 'commands': []}

        def look(machine=None):
            return seen(*box['missing'], manager=manager)

        def installer(pid):
            def install(run_):
                box['calls'].append(pid)
                box['missing'].discard(pid)
            return install

        def runner(cmd, **kw):
            box['commands'].append(cmd)
            for pid, part in onboarding.BY_ID.items():
                if cmd[:2] == ['winget', 'install'] and part.get('packages', {}).get('winget') in cmd or cmd[:2] == ['brew', 'install'] and cmd[2:] == part.get('packages', {}).get('brew', '').split():
                    box['missing'].discard(pid)
            return ''
        box.update(look=look, installers={pid: installer(pid) for pid in onboarding.INSTALLERS}, runner=runner)
        return box

    def apply(self, box, approved, **kw):
        with mock.patch.object(onboarding, 'check', lambda pid, deep: (READY, 'essai réussi')):
            return {r['id']: r for r in onboarding.apply(approved, installers=box['installers'], runner=box['runner'], look=box['look'], **kw)['results']}


class Proposal(Isolated):
    def test_what_is_already_there_is_said_and_left_alone(self):
        p = onboarding.plan(seen())
        self.assertTrue(all(r['state'] == 'present' and 'rien à faire' in r['action'] for r in p['rows']))
        self.assertEqual(p['to_approve'], {'required': [], 'recommended': [], 'optional': []})
        self.assertNotIn('python-modules', [r['id'] for r in p['rows']], 'a technical dependency that is satisfied is not shown')
        self.assertEqual(p['required_mb'], 0)

    def test_missing_parts_are_proposed_with_reason_size_and_level(self):
        p = onboarding.plan(seen('ffmpeg', 'node', 'engine-remotion', 'captions', 'blender'))
        rows = {r['id']: r for r in p['rows']}
        self.assertEqual(p['to_approve'], {'required': ['ffmpeg', 'node', 'engine-remotion'], 'recommended': ['captions'], 'optional': ['blender']})
        self.assertEqual((rows['ffmpeg']['how'], rows['ffmpeg']['licence'], rows['ffmpeg']['size_mb']), ('winget', 'GPL', 200))
        self.assertIn('hors du dossier du kit', rows['ffmpeg']['outside'])
        self.assertEqual((rows['engine-remotion']['how'], rows['engine-remotion']['needs']), ('kit', ['node']))
        self.assertIn('accord', rows['captions']['action'])
        self.assertEqual(p['required_mb'], 200 + 90 + 1200)
        self.assertTrue(all(r['why'] for r in p['rows']))

    def test_every_part_speaks_three_languages(self):
        for part in onboarding.PARTS:
            for key in ('title', 'why'):
                self.assertEqual(set(part[key]), {'fr', 'es', 'en'}, part['id'])
        self.assertEqual(onboarding.plan(seen(), 'es')['rows'][3]['title'], 'Motor de creación')
        self.assertEqual({len(w) for w in onboarding.WORDS.values()}, {len(onboarding.WORDS['fr'])})

    def test_linux_gets_a_line_to_type_never_a_password_prompt(self):
        part = onboarding.BY_ID['ffmpeg']
        self.assertEqual(onboarding.system_command(part, {'found': True, 'name': 'apt-get'}), (None, 'sudo apt-get install -y ffmpeg'))
        row = {r['id']: r for r in onboarding.plan(seen('ffmpeg', manager='apt-get'))['rows']}['ffmpeg']
        self.assertEqual(row['how'], 'manual')
        self.assertIn('à faire à la main', row['action'])
        self.assertEqual(onboarding.plan(seen('ffmpeg', manager='apt-get'))['to_approve']['required'], [])

    def test_each_system_has_its_own_way(self):
        ffmpeg, blender, node = (onboarding.BY_ID[x] for x in ('ffmpeg', 'blender', 'node'))
        command, manual = onboarding.system_command(ffmpeg, {'found': True, 'name': 'winget'})
        self.assertEqual(command[:5], ['winget', 'install', '--id', 'Gyan.FFmpeg', '-e'])
        self.assertIsNone(manual)
        self.assertEqual(onboarding.system_command(blender, {'found': True, 'name': 'brew'}), (['brew', 'install', '--cask', 'blender'], None))
        self.assertIn('nodejs.org', onboarding.system_command(node, {'found': False, 'name': 'winget'})[1])
        self.assertIn('nodejs.org', onboarding.system_command(node, {'found': True, 'name': 'apt-get'})[1], 'a distribution\'s Node is often too old: the official site is given')

    def test_a_version_that_is_too_old_is_not_called_missing(self):
        s = seen()
        s['software']['node'].update(ok=False, version='18.2.0')
        row = {r['id']: r for r in onboarding.plan(s)['rows']}['node']
        self.assertEqual((row['state'], row['version']), ('outdated', '18.2.0'))

    def test_the_hidden_dependency_shows_up_when_it_is_missing(self):
        rows = {r['id']: r for r in onboarding.plan(seen('python-modules', 'captions'))['rows']}
        self.assertEqual(rows['captions']['needs'], ['python-modules'])
        self.assertIn('python-modules', rows)

    def test_advice_follows_the_machine(self):
        weak = {**BASE['machine'], 'ram_gb': 4.0, 'gpus': [], 'threads': 4, 'disk_free_gb': 5.0}
        self.assertEqual(len(onboarding.advice(weak)), 4)
        self.assertEqual(onboarding.advice(BASE['machine']), [])
        self.assertIn('h264_qsv', onboarding.advice(BASE['machine'], {'h264_qsv': True, 'h264_nvenc': False})[0])
        self.assertIn('16,0 Go', onboarding.summary(BASE['machine'])['memoire'])


class Installing(Isolated):
    def test_nothing_is_installed_without_a_name(self):
        box = self.world('engine-remotion', 'captions')
        self.assertEqual(self.apply(box, []), {})
        self.assertEqual((box['calls'], box['commands']), ([], []))
        from universal.cli import main
        with self.assertRaises(ValueError):
            main(['setup', 'apply'])

    def test_only_the_approved_parts_are_installed(self):
        box = self.world('engine-remotion', 'captions', 'effects')
        done = self.apply(box, ['captions'])
        self.assertEqual(box['calls'], ['captions'])
        self.assertEqual(done['captions']['result'], 'installed')
        st = state.load()
        self.assertTrue(st['consent']['captions']['approved'])
        self.assertEqual(st['steps']['captions']['status'], 'done')
        self.assertEqual([(x['id'], x['kind']) for x in st['installed_by_kit']], [('captions', 'kit')])

    def test_a_part_that_works_is_never_reinstalled(self):
        box = self.world()
        done = self.apply(box, ['ffmpeg', 'engine-remotion'])
        self.assertEqual([d['result'] for d in done.values()], ['already', 'already'])
        self.assertIn('rien n\'a été refait', done['ffmpeg']['detail'])
        self.assertEqual((box['calls'], box['commands'], state.load()['installed_by_kit']), ([], [], []))

    def test_a_part_waits_for_what_it_needs_and_order_does_not_matter(self):
        box = self.world('node', 'engine-remotion')
        self.assertEqual(self.apply(box, ['engine-remotion'])['engine-remotion']['result'], 'blocked')
        done = self.apply(box, ['engine-remotion', 'node'])
        self.assertEqual([done[k]['result'] for k in ('node', 'engine-remotion')], ['installed', 'installed'])

    def test_a_system_tool_goes_through_the_manager_once_approved(self):
        box = self.world('ffmpeg')
        done = self.apply(box, ['ffmpeg'])
        self.assertEqual(box['commands'], [['winget', 'install', '--id', 'Gyan.FFmpeg', '-e', '--silent', '--accept-source-agreements', '--accept-package-agreements']])
        self.assertEqual(done['ffmpeg']['result'], 'installed')
        self.assertEqual(state.load()['installed_by_kit'][0]['kind'], 'system')

    def test_what_needs_a_password_is_handed_to_the_person(self):
        box = self.world('ffmpeg', manager='apt-get')
        done = self.apply(box, ['ffmpeg'])
        self.assertEqual((done['ffmpeg']['result'], done['ffmpeg']['detail']), ('manual', 'sudo apt-get install -y ffmpeg'))
        self.assertEqual(box['commands'], [])

    def test_a_failure_is_recorded_and_the_next_launch_resumes(self):
        box = self.world('captions')

        def broken(run_):
            raise RuntimeError('réseau coupé')
        box['installers']['captions'] = broken
        done = self.apply(box, ['captions'])
        self.assertEqual((done['captions']['result'], done['captions']['status']), ('failed', FAILED))
        self.assertIn('réseau coupé', done['captions']['detail'])
        self.assertEqual(state.load()['installed_by_kit'], [])
        with mock.patch.object(onboarding, 'snapshot', box['look']):
            again = onboarding.start()
        self.assertEqual((again['phase'], again['failed']), ('resume', ['captions']))

    def test_an_install_that_leaves_nothing_behind_is_a_failure(self):
        box = self.world('captions')
        box['installers']['captions'] = lambda run_: None
        self.assertIn('introuvable', self.apply(box, ['captions'])['captions']['detail'])

    def test_an_interrupted_install_is_seen_at_the_next_launch(self):
        onboarding._record('engine-remotion', 'running')
        with mock.patch.object(onboarding, 'snapshot', lambda machine=None: seen('engine-remotion')):
            again = onboarding.start()
        self.assertEqual((again['phase'], again['interrupted']), ('resume', ['engine-remotion']))

    def test_a_repair_really_reinstalls(self):
        box = self.world()
        with mock.patch.object(modules, 'VENV', self.dir):
            (self.dir / '.tier-effects').write_text('fini', encoding='utf-8')
            done = self.apply(box, ['effects', 'ffmpeg'], force=True)
            self.assertFalse((self.dir / '.tier-effects').exists(), 'the marker of the finished install is cleared first')
        self.assertEqual(box['calls'], ['effects'])
        self.assertEqual(done['ffmpeg']['result'], 'already', 'a tool of the computer is never reinstalled by a repair')

    def test_a_refusal_is_remembered(self):
        self.assertEqual(onboarding.decline(['engine-remotion', 'inconnu']), {'declined': ['engine-remotion']})
        self.assertTrue(state.load()['consent']['engine-remotion']['declined'])


class Checking(Isolated):
    def verify(self, world, deep=False, checks=None, test=None):
        checks = checks or {}
        with mock.patch.object(onboarding, 'snapshot', lambda machine=None: world), mock.patch.object(onboarding, 'check', lambda pid, d: checks.get(pid, (READY, 'vérifié'))), \
                mock.patch.object(onboarding, 'end_to_end', lambda creation=True: test or {'montage': {'status': READY, 'detail': 'ok'}, 'creation': {'status': READY, 'detail': 'ok'}}), \
                mock.patch.object(diagnostic, 'test_encoders', lambda: {'h264_qsv': True}):
            report = onboarding.verify(deep=deep)
        return report, {r['id']: r for r in report['rows']}

    def test_four_states_and_one_verdict(self):
        report, rows = self.verify(seen('engine-remotion', 'captions', 'blender'))
        self.assertEqual((rows['engine-remotion']['status'], rows['captions']['status'], rows['blender']['status'], rows['ffmpeg']['status']), (FAILED, OPTIONAL, OPTIONAL, READY))
        self.assertIn('recommandé', rows['captions']['detail'])
        self.assertEqual(report['verdict'], FAILED)
        self.assertEqual(sum(report['counts'].values()), len(report['rows']))

    def test_a_refused_part_is_a_limit_not_a_failure(self):
        onboarding.decline(['engine-remotion'])
        report, rows = self.verify(seen('engine-remotion'), deep=True)
        self.assertEqual(rows['engine-remotion']['status'], WARNING)
        self.assertIn('à ta demande', rows['engine-remotion']['detail'])
        self.assertEqual(report['verdict'], WARNING)
        self.assertTrue(state.load()['configured'], 'a choice the person made does not keep the kit unconfigured')

    def test_only_the_full_check_can_say_ready(self):
        report, _ = self.verify(seen())
        self.assertEqual(report['verdict'], READY)
        self.assertIn('Seule la vérification complète', report['note'])
        self.assertFalse(state.load()['configured'])
        self.assertFalse((logs.DIR / 'dernier-rapport.md').exists())
        report, rows = self.verify(seen(), deep=True)
        st = state.load()
        self.assertTrue(st['configured'])
        self.assertEqual((st['verdict'], st['encoders']), (READY, {'h264_qsv': True}))
        self.assertIn('essai-creation', rows)
        self.assertIn('| FFmpeg | READY |', (logs.DIR / 'dernier-rapport.md').read_text(encoding='utf-8'))

    def test_a_failed_test_video_fails_the_engine_behind_it(self):
        bad = {'montage': {'status': READY, 'detail': 'ok'}, 'creation': {'status': FAILED, 'detail': 'rendu impossible'}}
        report, rows = self.verify(seen(), deep=True, test=bad)
        self.assertEqual((rows['essai-creation']['status'], rows['engine-remotion']['status'], rows['ffmpeg']['status']), (FAILED, FAILED, READY))
        self.assertEqual(report['verdict'], FAILED)
        self.assertFalse(state.load()['configured'])

    def test_a_broken_option_warns_without_blocking(self):
        report, rows = self.verify(seen(), deep=True, checks={'effects': (FAILED, 'import impossible')})
        self.assertEqual((rows['effects']['status'], report['verdict']), (FAILED, WARNING))
        self.assertTrue(state.load()['configured'])

    def test_a_machine_problem_is_part_of_the_report(self):
        world = seen()
        world['conflicts'] = [{'level': WARNING, 'what': 'Il reste 5 Go.', 'effect': 'Juste.'}, {'level': FAILED, 'what': 'Node trop ancien.', 'effect': 'Création impossible.'}]
        report, rows = self.verify(world)
        self.assertEqual((rows['machine-1']['status'], rows['machine-2']['status'], report['verdict']), (WARNING, FAILED, FAILED))

    def test_a_check_that_crashes_is_a_failed_check(self):
        def crash(deep):
            raise OSError('disque débranché')
        with mock.patch.dict(onboarding.CHECKS, {'ffmpeg': crash}):
            self.assertEqual(onboarding.check('ffmpeg', False), (FAILED, 'OSError : disque débranché'))

    def test_the_launch_is_instant_when_ready_and_notices_what_went_away(self):
        self.verify(seen(), deep=True)
        with mock.patch.dict(onboarding.QUICK, {k: (lambda: True) for k in onboarding.QUICK}), mock.patch.object(onboarding, 'snapshot', side_effect=AssertionError('no detection when ready')):
            ready = onboarding.start()
        self.assertEqual(ready['phase'], 'ready')
        self.assertIn('Ne rien réinstaller', ready['next'])
        self.assertEqual(ready['features']['sur_demande'], [])
        with mock.patch.dict(onboarding.QUICK, {**{k: (lambda: True) for k in onboarding.QUICK}, 'engine-remotion': lambda: False}):
            lost = onboarding.start()
        self.assertEqual((lost['phase'], lost['lost']), ('repair', ['Moteur de création']))

    def test_what_is_not_installed_is_offered_not_hidden(self):
        f = onboarding.features({'python', 'ffmpeg'})
        self.assertEqual(len(f['pret']), 3)
        wanted = {x['quoi'][:11]: x for x in f['sur_demande']}
        self.assertEqual(wanted['Sous-titres']['demande'], ['Sous-titres automatiques'])
        self.assertEqual(wanted['Sous-titres']['taille'], '345 Mo')

    def test_repair_says_what_is_broken_and_touches_nothing(self):
        with mock.patch.object(onboarding, 'snapshot', lambda machine=None: seen('engine-remotion')), mock.patch.object(onboarding, 'check', lambda pid, d: (READY, '')), \
                mock.patch.object(onboarding, 'apply', side_effect=AssertionError('no repair without approval')):
            found = onboarding.repair()
        self.assertEqual([(f['id'], f['by_hand']) for f in found['fixes']], [('engine-remotion', False)])
        self.assertIn('accord', found['next'])


class Leaving(Isolated):
    def setUp(self):
        super().setUp()
        self.kit = self.dir / 'kit'
        for rel in ('template/node_modules/remotion', 'modules/.venv/Lib', 'perfil/marcas', 'out/film'):
            (self.kit / rel).mkdir(parents=True)
        for rel, size in (('template/node_modules/remotion/a.js', 3_000_000), ('modules/.venv/Lib/b.py', 2_000_000), ('perfil/mi-estilo.md', 10), ('out/film/film.mp4', 10), ('kit.config.local.json', 2)):
            (self.kit / rel).write_bytes(b'x' * size)
        self.extra = [mock.patch.object(onboarding, 'ROOT', self.kit), mock.patch.object(onboarding, 'npx_cached', lambda n, v: False),
                      mock.patch.object(diagnostic, 'browsers_cache', lambda: self.dir / 'absent'), mock.patch.object(diagnostic, 'secret_present', lambda name: False)]
        for p in self.extra:
            p.start()

    def tearDown(self):
        for p in self.extra:
            p.stop()
        super().tearDown()

    def test_the_list_shows_sizes_and_changes_nothing(self):
        found = onboarding.uninstall()
        self.assertEqual([(g['id'], g['size_mb']) for g in found['removable']], [('engine-remotion', 3), ('options', 2)])
        self.assertEqual([k['where'] for k in found['kept']], ['perfil', 'out', 'kit.config.local.json'])
        self.assertTrue((self.kit / 'template/node_modules/remotion/a.js').exists())

    def test_only_the_named_groups_go_and_personal_folders_stay(self):
        done = onboarding.uninstall(['engine-remotion', 'perfil', 'out'])
        self.assertEqual([(r['id'], r['freed_mb']) for r in done['removed']], [('engine-remotion', 3)])
        self.assertEqual(done['refused'], ['perfil', 'out'], 'the profile and the videos are not something the kit removes')
        self.assertFalse((self.kit / 'template/node_modules').exists())
        for rel in ('modules/.venv/Lib/b.py', 'perfil/mi-estilo.md', 'out/film/film.mp4', 'kit.config.local.json'):
            self.assertTrue((self.kit / rel).exists(), rel)
        self.assertFalse(state.load()['configured'])

    def test_a_path_that_is_not_the_kits_own_is_refused(self):
        for rel in ('perfil', 'out', '../ailleurs', 'template', ''):
            with self.assertRaises(ValueError):
                onboarding._inside(rel)

    def test_what_lives_outside_the_kit_is_listed_not_removed(self):
        st = state.load()
        st['installed_by_kit'] = [{'id': 'ffmpeg', 'kind': 'system', 'at': '2026-11-10T08:00:00', 'how': 'winget'}, {'id': 'captions', 'kind': 'kit', 'at': '2026-11-10T08:00:00', 'how': 'kit'}]
        state.save(st)
        outside = onboarding.uninstall()['outside_the_kit']
        self.assertEqual(len(outside), 1)
        self.assertIn('FFmpeg, installé par le kit le 2026-11-10', outside[0]['what'])


class Current(Isolated):
    def test_the_size_of_a_change_is_named(self):
        cases = {('4.0.540', '4.0.542'): 'corrective', ('1.64.1', '1.65.0'): 'mineure', ('1.9.0', '2.0.0'): 'majeure', ('0.8.164', '0.9.28'): 'majeure',
                 ('0.8.164', '0.8.170'): 'corrective', ('1.2.1', '1.2.1'): 'à jour', ('5.0.0.93', '5.0.0.93'): 'à jour', ('2.0.0', '1.9.0'): 'à jour', ('1.0.0', None): 'inconnu'}
        for (have, latest), name in cases.items():
            self.assertEqual(onboarding.change(have, latest), name, (have, latest))

    def test_offline_asks_nobody_and_updates_nothing(self):
        with mock.patch.object(onboarding, '_get', side_effect=AssertionError('no request offline')):
            found = onboarding.updates(online=False)
        self.assertFalse(found['online'])
        self.assertTrue(found['dependencies'])
        self.assertEqual({d['change'] for d in found['dependencies']}, {'inconnu'})
        self.assertIn('Rien n\'est mis à jour', found['note'])
        self.assertEqual(found['kit']['version'], config.get('kit.version'))

    def test_online_only_reads(self):
        answers = {'registry.npmjs.org/remotion/latest': {'version': '9.9.9'}}
        with mock.patch.object(onboarding, '_get', lambda url: next((v for k, v in answers.items() if k in url), None)):
            found = onboarding.updates()
        rows = {d['name']: d for d in found['dependencies']}
        self.assertEqual((rows['remotion']['latest'], rows['remotion']['change']), ('9.9.9', 'majeure'))
        self.assertEqual(rows['playwright']['change'], 'inconnu')
        self.assertEqual(diagnostic.lock_version('template', 'remotion'), rows['remotion']['pinned'], 'the lockfile is untouched')


class Journal(Isolated):
    def test_no_secret_no_name_no_home_folder(self):
        home = str(Path.home())
        with mock.patch.dict(os.environ, {'FAUX_API_KEY': 'valeur-tres-secrete-123', 'USERNAME': 'martine'}):
            line = logs.scrub(f'{home}\\Videos\\kit {FAKE_KEY} token=abc12345 valeur-tres-secrete-123 C:/Users/martine/x Authorization: Bearer abcdef123456 martinet')
        for secret in (FAKE_KEY, 'abc12345', 'valeur-tres-secrete-123', 'abcdef123456', home):
            self.assertNotIn(secret, line)
        self.assertIn('~', line)
        self.assertIn('C:/Users/[privé]/x', line)
        self.assertIn('martinet', line, 'a word that only contains the name is left alone')
        self.assertIn('token=[masqué]', line)

    def test_a_line_is_written_scrubbed_and_old_files_go(self):
        logs.DIR.mkdir()
        old = logs.DIR / f'kit-{datetime.date.today() - datetime.timedelta(days=90):%Y-%m-%d}.jsonl'
        old.write_text('{}\n', encoding='utf-8')
        logs.write('essai', command='winget install', key=FAKE_KEY, where=Path.home() / 'kit', nested={'a': ['password=hunter22']})
        self.assertFalse(old.exists())
        row = logs.tail()[-1]
        self.assertEqual((row['event'], row['command'], row['key']), ('essai', 'winget install', logs.MASK))
        self.assertEqual(row['nested'], {'a': ['password=' + logs.MASK]})
        self.assertTrue(row['where'].startswith('~'))

    def test_a_log_that_cannot_be_written_stops_nothing(self):
        with mock.patch.object(logs, 'DIR', self.dir / 'kit-state.json' / 'impossible'):
            (self.dir / 'kit-state.json').write_text('{}', encoding='utf-8')
            logs.write('essai')


class Memory(Isolated):
    def test_a_kit_copied_to_another_machine_starts_over(self):
        state.save({**state.blank(), 'configured': True})
        self.assertTrue(state.load()['configured'])
        data = json.loads(state.FILE.read_text(encoding='utf-8'))
        state.FILE.write_text(json.dumps({**data, 'machine': 'une-autre-machine'}), encoding='utf-8')
        fresh = state.load()
        self.assertFalse(fresh['configured'])
        self.assertIn('autre machine', fresh['note'])
        state.FILE.write_text('{pas du json', encoding='utf-8')
        self.assertIn('illisible', state.load()['note'])
        self.assertNotIn(os.environ.get('USERNAME') or 'aucun-nom', json.dumps(state.blank()))

    def test_a_local_setting_wins_and_the_shipped_file_stays(self):
        shipped = config.DEFAULTS.read_text(encoding='utf-8')
        with mock.patch.object(config, 'LOCAL', self.dir / 'kit.config.local.json'):
            self.assertEqual(config.get('consent.free_modules'), 'ask')
            config.set_local('consent.free_modules', 'auto')
            self.assertEqual(config.get('consent.free_modules'), 'auto')
            (self.dir / 'kit.config.local.json').write_text('{cassé', encoding='utf-8')
            self.assertEqual(config.get('consent.free_modules'), 'ask', 'a broken local file falls back to the defaults')
        self.assertEqual(config.DEFAULTS.read_text(encoding='utf-8'), shipped)


class Consent(Isolated):
    def test_a_missing_option_asks_instead_of_installing_itself(self):
        with mock.patch.object(modules, 'VENV', self.dir / 'venv'), mock.patch.object(modules, 'install_tier', side_effect=AssertionError('no silent install')):
            with self.assertRaises(modules.ConsentRequired) as asked:
                modules.run_python(['-c', 'pass'], tier='transcribe')
        self.assertIn('setup apply --approve captions', str(asked.exception))
        self.assertIn('gratuite', str(asked.exception))

    def test_the_person_can_choose_to_let_free_parts_install(self):
        calls = []
        with mock.patch.object(config, 'LOCAL', self.dir / 'kit.config.local.json'), mock.patch.object(modules, 'VENV', self.dir / 'venv'), \
                mock.patch.object(modules, 'install_tier', calls.append):
            config.set_local('consent.free_modules', 'auto')
            with self.assertRaises(RuntimeError):
                modules.run_python(['-c', 'pass'], tier='voice')
        self.assertEqual(calls, ['voice'])

    def test_the_design_adviser_is_offered_not_installed(self):
        with mock.patch.object(design_check, 'DIR', self.dir / 'design'), mock.patch.object(design_check, 'install', side_effect=AssertionError('no silent install')):
            result = design_check.check(self.dir / 'page.html')
        self.assertFalse(result['ran'])
        self.assertIn('proposer', result['raison'])
        self.assertTrue(design_check.as_report(result)['pass'], 'an adviser that did not run never blocks a delivery')


class Console(Isolated):
    def run_wizard(self, world, answers=None, approved=None, verdict=READY):
        said, asked, applied = [], [], []
        replies = iter(answers or [])

        def ask(question):
            asked.append(question)
            try:
                return next(replies)
            except StopIteration:
                raise EOFError from None

        def fake_apply(ids, **kw):
            applied.append(list(ids))
            return {'results': [{'id': i, 'result': 'installed', 'detail': 'essai réussi'} for i in ids]}
        with mock.patch.object(onboarding, 'snapshot', lambda machine=None: world), mock.patch.object(onboarding, 'apply', fake_apply), \
                mock.patch.object(onboarding, 'verify', lambda deep=True: {'verdict': verdict, 'rows': [{'status': verdict, 'title': 'FFmpeg', 'detail': 'essai'}]}):
            code = onboarding.wizard('fr', ask=ask, say=said.append, approved=approved)
        return code, '\n'.join(str(s) for s in said), asked, applied

    def test_each_missing_part_is_asked_and_only_a_yes_installs(self):
        code, said, asked, applied = self.run_wizard(seen('ffmpeg', 'captions', 'effects'), ['o', 'non', ''])
        self.assertEqual(len(asked), 3)
        self.assertIn('licence (GPL)', asked[0])
        self.assertIn('345 Mo', asked[1])
        self.assertEqual(applied, [['ffmpeg']])
        self.assertEqual(code, 0)
        self.assertIn('Ta machine', said)
        self.assertNotIn('declined', state.load()['consent'].get('ffmpeg', {}))

    def test_a_refused_required_part_is_remembered_and_nothing_is_forced(self):
        code, said, asked, applied = self.run_wizard(seen('engine-remotion'), ['n'], verdict=WARNING)
        self.assertEqual((applied, code), ([], 0))
        self.assertTrue(state.load()['consent']['engine-remotion']['declined'])

    def test_no_one_to_answer_means_nothing_is_installed(self):
        code, said, asked, applied = self.run_wizard(seen('ffmpeg', 'captions'), [], verdict=FAILED)
        self.assertEqual((applied, code), ([], 1))
        self.assertIn('rien ne sera installé', said)

    def test_parts_approved_beforehand_are_the_only_ones_installed_and_no_question_is_asked(self):
        code, said, asked, applied = self.run_wizard(seen('engine-remotion', 'captions', 'effects'), ['o', 'o', 'o'], approved=['captions'])
        self.assertEqual((asked, applied), ([], [['captions']]))

    def test_everything_there_means_no_question_at_all(self):
        code, said, asked, applied = self.run_wizard(seen())
        self.assertEqual((asked, applied, code), ([], [], 0))
        self.assertIn('Rien à installer', said)


class RealMachine(unittest.TestCase):
    """Read-only probes of the computer the tests run on."""

    def test_versions_are_read_not_guessed(self):
        self.assertEqual(diagnostic.numbers('ffmpeg version 9.0.2-full_build-www.gyan.dev'), (9, 0, 2))
        self.assertEqual(diagnostic.numbers('v24.14.1'), (24, 14, 1))
        self.assertEqual(diagnostic.numbers('rien'), ())
        self.assertEqual(diagnostic.dotted((5, 2, 3)), '5.2.3')
        self.assertIsNone(diagnostic.dotted(()))

    def test_memory_processor_and_disk_are_measured(self):
        memory, processor = diagnostic.memory(), diagnostic.cpu()
        self.assertGreater(memory['ram_gb'], 0.5)
        self.assertGreaterEqual(processor['threads'], 1)
        self.assertTrue(processor['cpu'])
        seen_python = diagnostic.pythons()
        self.assertTrue(seen_python['ok'])
        self.assertFalse(diagnostic.secret_present('UNE_CLE_QUI_N_EXISTE_PAS_42'))

    def test_what_does_not_fit_together_is_said(self):
        m = dict(BASE['machine'])
        s = copy.deepcopy(BASE['software'])
        self.assertEqual([c for c in diagnostic.conflicts(m, s) if 'Plusieurs' not in c['what'] and 'chemin' not in c['what'] and 'synchronisé' not in c['what']], [])
        s['node'].update(ok=False, version='18.0.0')
        s['ffmpeg'].update(ok=None, version=None)
        s['python'].update(for_modules=None)
        s['uv']['found'] = False
        found = diagnostic.conflicts({**m, 'disk_free_gb': 1.0, 'ram_gb': 4.0, 'bits': 32}, s)
        said = ' '.join(c['what'] for c in found)
        for word in ('32 bits', 'Node 18.0.0', 'non reconnue', 'Aucun Python 3.12 ou 3.13', 'Il reste 1.0 Go', '4.0 Go de mémoire'):
            self.assertIn(word, said)
        self.assertEqual({c['level'] for c in found if 'Node' in c['what'] or '32 bits' in c['what'] or 'Il reste' in c['what']}, {FAILED})
        with mock.patch.object(diagnostic, 'ROOT', Path('C:/Users/x/OneDrive/Vidéos/kit')):
            cloud = ' '.join(c['what'] for c in diagnostic.conflicts(m, copy.deepcopy(BASE['software'])))
        self.assertIn('synchronisé', cloud)
        self.assertIn('accents', cloud)

    def test_blender_is_found_where_its_installer_puts_it(self):
        from universal import capabilities
        with tempfile.TemporaryDirectory() as d, mock.patch.object(capabilities.shutil, 'which', lambda name: None), mock.patch.object(capabilities.platform, 'system', lambda: 'Windows'), \
                mock.patch.dict(os.environ, {'ProgramFiles': d, 'ProgramW6432': d, 'ProgramFiles(x86)': d}):
            self.assertIsNone(capabilities.find_blender())
            for version in ('Blender 4.2', 'Blender 5.2', 'Blender 5.10'):
                (Path(d) / 'Blender Foundation' / version).mkdir(parents=True)
                (Path(d) / 'Blender Foundation' / version / 'blender.exe').write_bytes(b'')
            self.assertEqual(Path(capabilities.find_blender()).parent.name, 'Blender 5.10', 'the newest one, by number and not by spelling')

    def test_a_node_project_is_installed_only_at_the_locked_version(self):
        self.assertIsNone(diagnostic.lock_version('template', 'un-paquet-absent'))
        self.assertRegex(diagnostic.lock_version('template', 'remotion'), r'^\d+\.\d+\.\d+$')
        with mock.patch.object(diagnostic, '_pkg', lambda project, package: '0.0.1'):
            self.assertFalse(diagnostic.node_project('template', 'remotion')['installed'])


if __name__ == '__main__':
    unittest.main()
