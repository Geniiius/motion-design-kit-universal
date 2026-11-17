"""A sung voice over music: how the readings of the model are cleaned, compared and completed.

The rules are tested on written readings, with no model. One real run checks the whole path on a generated voice over
a generated tone: it proves that the pieces fit, not that singing is understood (no free sung fixture exists)."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from universal import modules, song
from universal.workflows import transcript

ROOT = Path(__file__).resolve().parents[1]
HAS_FF = bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))
HAS_SPEECH = HAS_FF and transcript.missing() is None and (modules.VENV / '.tier-voice').exists() and (ROOT / 'modules/opuscar/core/tts/kokoro-v1.0.onnx').exists()


def w(text, start, end=None, p=.9):
    return {'w': text, 's': start, 'e': start + .3 if end is None else end, 'p': p}


def said(words):
    return [x['w'] for x in words]


def line(text, start=0.0, step=.4, p=.9):
    return [w(t, round(start + i * step, 2), p=p) for i, t in enumerate(text.split())]


def passes(*readings, start=0.0, end=12.5):
    return {'duration': end, 'language': 'es', 'passes': [{'variant': f'v{i}', 'hint': False, 'start': start, 'end': end, 'words': r} for i, r in enumerate(readings)]}


class Clean(unittest.TestCase):
    def test_signs_that_are_not_words_are_dropped(self):
        self.assertEqual(said(song.clean([w('¡¡¡¡¡¡', 0), w('♪', 1), w('hola', 2)])), ['hola'])

    def test_a_word_split_at_the_apostrophe_is_one_word_again(self):
        got = song.clean([w('c', 0, .2), w("'est", .2, .5, p=.6), w('ici', .6), w('-même', .9)])
        self.assertEqual(said(got), ["c'est", 'ici-même'])
        self.assertEqual((got[0]['s'], got[0]['e'], got[0]['p']), (0, .5, .6))

    def test_words_piled_on_one_instant_are_dropped(self):
        got = song.clean([w('oh', 5, 5.3), w('oh', 5.3, 5.3), w('oh', 5.3, 5.3), w('oh', 5.31, 5.31), w('sol', 6)])
        self.assertEqual(said(got), ['oh', 'oh', 'sol'])

    def test_a_word_sung_a_few_times_in_a_row_stays(self):
        got = song.clean(line('ven ven ven la luna'))
        self.assertEqual(said(got), ['ven', 'ven', 'ven', 'la', 'luna'])
        self.assertFalse(any('x' in x for x in got))

    def test_a_looping_word_is_kept_once_and_says_how_often_it_came_back(self):
        got = song.clean(line('sol ' + 'no, ' * 9 + 'mar'))
        self.assertEqual(said(got), ['sol', 'no,', 'mar'])
        self.assertEqual(got[1]['x'], 9)

    def test_a_looping_phrase_is_kept_once_and_a_phrase_sung_twice_stays(self):
        got = song.clean(line('quien va a venir ' * 4 + 'hoy'))
        self.assertEqual(said(got), ['quien', 'va', 'a', 'venir', 'hoy'])
        self.assertEqual(got[3]['x'], 4)
        self.assertEqual(len(song.clean(line('quien va a venir ' * 2))), 8)


class Choose(unittest.TestCase):
    def test_the_reading_the_others_agree_with_wins_over_a_long_invented_one(self):
        invented = line('la ciudad duerme bajo un cielo de papel y nadie sabe por que cantamos', p=.97)
        got = song.choose([line('uno dos tres cuatro'), invented, line('uno dos tres cuarto'), line('uno dos tres cuatro')])
        self.assertEqual(said(got), ['uno', 'dos', 'tres', 'cuatro'])
        self.assertEqual([x['votes'] for x in got], [.75, .75, .75, .5])

    def test_a_single_reading_is_kept_as_it_is(self):
        got = song.choose([[], line('uno dos'), []])
        self.assertEqual((said(got), got[0]['votes']), (['uno', 'dos'], 1.0))
        self.assertEqual(song.choose([[], []]), [])

    def test_a_word_the_readings_disagree_on_is_flagged_with_what_else_was_heard(self):
        words = song.merge(passes(line('el combate sigue'), line('el compadre sigue'), line('el compas sigue'), line('el combate sigue')))
        self.assertEqual([x['text'] for x in words], ['el', 'combate', 'sigue'])
        self.assertNotIn('doubt', words[0])
        self.assertEqual((words[1]['doubt'], sorted(words[1]['alt'])), (True, ['compadre', 'compas']))

    def test_a_word_the_model_is_unsure_of_is_flagged_even_when_all_agree(self):
        words = song.merge(passes([w('uno', 0), w('nombre', .4, p=.3)], [w('uno', 0), w('nombre', .4, p=.3)]))
        self.assertEqual([bool(x.get('doubt')) for x in words], [False, True])

    def test_readings_that_time_a_line_start_half_a_second_apart_still_agree(self):
        got = song.choose([line('paso firme', 14.3), line('paso firme', 15.1), line('paso firme', 14.9)])
        self.assertEqual(got[0]['votes'], 1.0)


class Stitch(unittest.TestCase):
    def test_a_word_seen_from_both_sides_of_a_seam_is_kept_once(self):
        first = [w('uno', 9.0), w('dos', 11.6), w('tres', 12.1)]
        second = [w('dos', 11.7), w('tres', 12.0), w('cuatro', 13.0)]
        got = song.stitch([(0.0, 12.5, first), (11.0, 23.5, second)])
        self.assertEqual(said(got), ['uno', 'dos', 'tres', 'cuatro'])

    def test_a_word_repeated_inside_one_window_is_sung_twice(self):
        self.assertEqual(said(song.stitch([(0.0, 12.5, [w('ven', 5.3), w('ven', 5.6)])])), ['ven', 'ven'])


class Holes(unittest.TestCase):
    def test_empty_stretches_include_the_edges_of_the_song(self):
        words = [{'text': 'a', 'start': 4.0, 'end': 4.5}, {'text': 'b', 'start': 5.0, 'end': 6.0}, {'text': 'c', 'start': 12.0, 'end': 12.4}]
        self.assertEqual(song.holes(words, 20.0), [(0.0, 4.0), (6.0, 12.0), (12.4, 20.0)])
        self.assertEqual(song.holes(words[:2], 7.0), [(0.0, 4.0)])
        self.assertEqual(song.holes([], 2.0), [])

    def test_second_readings_start_at_several_points_and_stay_inside_the_song(self):
        got = song.tries((2.2, 11.8), 30.0)
        self.assertEqual((len(got), got[0][0], got[-1][0]), (5, 1.9, 9.3))
        self.assertTrue(all(abs(b - a - song.WINDOW) < .011 for a, b in got))
        self.assertEqual(song.tries((0.0, 3.5), 4.0), [(0.0, 4.0)])
        self.assertLessEqual(len(song.tries((10.0, 90.0), 120.0)), song.TRIES)

    def test_a_skipped_verse_is_filled_from_the_starting_point_whose_readings_agree(self):
        loop = [line('no, ' * 12, 3.0, .2)] * 3 + [line('la la la la la la la', 3.0)]
        verse = [line('ven a jugar esta noche', 4.6), line('ven a jugar esta noche', 4.7), line('ven a cantar esta noche', 4.6)]
        got = song.fill((2.2, 11.8), [[song.clean(r) for r in loop], verse])
        self.assertEqual([x['text'] for x in got], ['ven', 'a', 'jugar', 'esta', 'noche'])

    def test_an_instrumental_break_stays_empty(self):
        invented = [line('gracias por ver el video', 36.0), line('suscribete al canal', 36.5), line('no, ' * 10, 36.0, .3), []]
        self.assertEqual(song.fill((35.0, 41.8), [[song.clean(r) for r in invented], [[], []]]), [])

    def test_a_filled_verse_does_not_repeat_the_word_at_its_edge(self):
        words = [{'text': 'hola', 'start': 2.0, 'end': 2.2}, {'text': 'jugar', 'start': 11.8, 'end': 12.2}]
        more = [{'text': 'ven', 'start': 5.0, 'end': 5.3}, {'text': 'jugar', 'start': 11.7, 'end': 12.0}]
        self.assertEqual([x['text'] for x in song._add(words, more)], ['hola', 'ven', 'jugar'])


class Text(unittest.TestCase):
    def test_doubtful_words_come_in_brackets_with_what_else_was_heard(self):
        words = [{'text': 'Paso', 'start': 15.0, 'end': 15.6}, {'text': 'firme,', 'start': 15.7, 'end': 16.2},
                 {'text': 'compadre', 'start': 72.5, 'end': 73.1, 'doubt': True, 'alt': ['combate']},
                 {'text': 'no,', 'start': 80.0, 'end': 80.2, 'doubt': True, 'repeat': 9}]
        text = song.as_text(words)
        self.assertIn('0:15.0  Paso firme,', text)
        self.assertIn('1:12.5  [compadre|combate]', text)
        self.assertIn('1:20.0  [no,] (répété ×9 ?)', text)
        self.assertIn('faire confirmer', text)

    def test_a_long_run_of_words_is_cut_into_sung_lines(self):
        words = [{'text': t, 'start': i * .4, 'end': i * .4 + .4} for i, t in enumerate('Paso firme, no hay descanso Listo y con mente fría, fuerza en las venas'.split())]
        self.assertEqual([' '.join(x['text'] for x in row) for row in song.lines(words)], ['Paso firme, no hay descanso', 'Listo y con mente fría,', 'fuerza en las venas'])

    def test_few_words_for_a_long_sound_suggest_the_song_mode(self):
        words = [{'text': 'a', 'start': 12.0, 'end': 20.0}]
        self.assertIn('--song', song.sparse(words, 60.0))
        self.assertIsNone(song.sparse(words, 15.0))
        self.assertIsNone(song.sparse([{'text': 'a', 'start': 0.0, 'end': 30.0}], 60.0))

    def test_the_command_has_the_song_option_under_both_names(self):
        r = subprocess.run([sys.executable, '-m', 'universal.cli', 'transcribe', '--help'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertIn('--song, --chanson', r.stdout)


@unittest.skipUnless(HAS_SPEECH, 'voix locale et transcription absentes')
class RealRun(unittest.TestCase):
    def test_a_voice_over_a_tone_is_heard_and_written_as_lyrics(self):
        from universal import voice_kokoro
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            voice_kokoro.synthesize('Bonjour à tous. Nous jouons ce soir, et la nuit sera longue.', d / 'voix.wav', 'fr')
            mix = d / 'morceau.wav'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'sine=frequency=220:duration=12', '-i', str(d / 'voix.wav'),
                            '-filter_complex', '[0:a]volume=0.08[t];[1:a]adelay=4000:all=1[v];[t][v]amix=inputs=2:duration=first:normalize=0[o]', '-map', '[o]', str(mix)], check=True)
            heard = voice_kokoro.transcribe_full(mix, d / 'mots.json', 'fr', song=True)
            words = json.loads((d / 'mots.json').read_text(encoding='utf-8'))
            self.assertEqual(words, heard['words'])
            keys = {song._key(x['text']) for x in words}
            self.assertTrue({'bonjour', 'nuit', 'longue'} <= keys, keys)
            self.assertTrue(all({'text', 'start', 'end', 'p', 'votes'} <= set(x) for x in words))
            self.assertGreater(min(x['start'] for x in words), 3.5)  # the voice starts after four seconds of tone
            self.assertIn('Brouillon', Path(heard['text']).read_text(encoding='utf-8'))
            self.assertEqual(heard['language'], 'fr')


if __name__ == '__main__':
    unittest.main()
