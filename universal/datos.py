"""Explainer project from a sourced dataset. Every number on screen is computed from the file.

Example dataset: NOAA GML annual mean CO2 at Mauna Loa. The historical notes come from the
comment header of that same file, nothing is added from memory.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

SOURCE_URL = 'https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.csv'
FETCHED = '2026-11-03'

STRINGS = {
    'en': dict(rotulo='NOAA · Mauna Loa, Hawaii', titulo='Carbon dioxide in the air', definicion='Annual mean, in parts per million (ppm) of dry air', curva='Annual mean at Mauna Loa', unidad='ppm', comp='Average rise per year', compu='ppm/yr',
               flujo='How this film got its numbers', pasos=['NOAA file: one mean per year', 'Annual means by decade', 'Year-on-year rise'], crono='What the file itself notes', fuente='Source and limits',
               h1='Data from Scripps Institution (C. David Keeling)', h2='NOAA series continues after April 1974', h3='Volcano: Mauna Loa suspended, Maunakea used until July 2023',
               l1='NOAA Global Monitoring Laboratory, annual means', l3='Downloaded {fetched}. Uncertainty stated in the file: ±{unc} ppm per year', l4='The last year may still be revised by NOAA. No forecast or cause is claimed here.',
               voz=('In {y0}, the air at Mauna Loa held {v0} parts per million of carbon dioxide. By {y1}, the annual mean had reached {v1}. That is {diff} more, in {years} years. '
                    'The pace changed too. In the {d0}s, it rose about {r0} per year. In the {d1}s, about {r1}. This film only reads one public file from NOAA, and shows its limits.')),
    'es': dict(rotulo='NOAA · Mauna Loa, Hawái', titulo='Dióxido de carbono en el aire', definicion='Media anual, en partes por millón (ppm) de aire seco', curva='Media anual en Mauna Loa', unidad='ppm', comp='Subida media por año', compu='ppm/año',
               flujo='De dónde salen las cifras', pasos=['Archivo NOAA: una media por año', 'Medias anuales por década', 'Subida de un año a otro'], crono='Lo que anota el propio archivo', fuente='Fuente y límites',
               h1='Datos de la Scripps Institution (C. David Keeling)', h2='La serie de NOAA continúa tras abril de 1974', h3='Volcán: Mauna Loa suspendido, Maunakea hasta julio de 2023',
               l1='NOAA Global Monitoring Laboratory, medias anuales', l3='Descargado el {fetched}. Incertidumbre indicada en el archivo: ±{unc} ppm por año', l4='NOAA aún puede revisar el último año. Aquí no se afirma ninguna previsión ni causa.',
               voz=('En {y0}, el aire de Mauna Loa contenía {v0} partes por millón de dióxido de carbono. En {y1}, la media anual alcanzó {v1}. Son {diff} más, en {years} años. '
                    'El ritmo también cambió. En los años {d0}, subía unas {r0} por año. En los años {d1}, unas {r1}. Esta película solo lee un archivo público de la NOAA, y muestra sus límites.')),
    'fr': dict(rotulo='NOAA · Mauna Loa, Hawaï', titulo='Le dioxyde de carbone dans l\'air', definicion='Moyenne annuelle, en parties par million (ppm) d\'air sec', curva='Moyenne annuelle à Mauna Loa', unidad='ppm', comp='Hausse moyenne par an', compu='ppm/an',
               flujo='D\'où viennent les chiffres', pasos=['Fichier NOAA : une moyenne par an', 'Moyennes annuelles par décennie', 'Hausse d\'une année à l\'autre'], crono='Ce que note le fichier lui-même', fuente='Source et limites',
               h1='Données de la Scripps Institution (C. David Keeling)', h2='La série NOAA continue après avril 1974', h3='Volcan : Mauna Loa suspendu, Maunakea jusqu\'en juillet 2023',
               l1='NOAA Global Monitoring Laboratory, moyennes annuelles', l3='Téléchargé le {fetched}. Incertitude indiquée dans le fichier : ±{unc} ppm par an', l4='NOAA peut encore réviser la dernière année. Aucune prévision ni cause n\'est affirmée ici.',
               voz=("En {y0}, l'air de Mauna Loa contenait {v0} parties par million de dioxyde de carbone. En {y1}, la moyenne annuelle atteignait {v1}. Soit {diff} de plus, en {years} ans. "
                    "Le rythme a changé aussi. Dans les années {d0}, la hausse était d'environ {r0} par an. Dans les années {d1}, d'environ {r1}. Ce film ne lit qu'un seul fichier public de la NOAA, et il en montre les limites.")),
}


def read_series(path: Path) -> list[dict]:
    lines = [l for l in Path(path).read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    return [{'year': int(r['year']), 'mean': float(r['mean']), 'unc': float(r['unc'])} for r in csv.DictReader(lines)]


def decade_rates(series: list[dict]) -> list[dict]:
    """Mean year-on-year rise for each complete decade in the file."""
    by_year = {r['year']: r['mean'] for r in series}
    out = []
    for d in range(series[0]['year'] // 10 * 10, series[-1]['year'], 10):
        rises = [by_year[y] - by_year[y - 1] for y in range(d, d + 10) if y in by_year and y - 1 in by_year]
        if len(rises) == 10:
            out.append({'decade': d, 'rate': round(sum(rises) / 10, 2)})
    return out


def facts(series: list[dict]) -> dict:
    a, b, rates = series[0], series[-1], decade_rates(series)
    return {'y0': a['year'], 'v0': a['mean'], 'y1': b['year'], 'v1': b['mean'], 'diff': round(b['mean'] - a['mean'], 2), 'years': b['year'] - a['year'],
            'd0': rates[0]['decade'], 'r0': rates[0]['rate'], 'd1': rates[-1]['decade'], 'r1': rates[-1]['rate'], 'unc': b['unc'], 'rates': rates}


def number(value: float, language: str) -> str:
    return str(value) if language == 'en' else str(value).replace('.', ',')


DECADE = {'en': '{d}s', 'fr': 'Années {d}', 'es': 'Años {d}'}


def narration(f: dict, language: str = 'en') -> str:
    return STRINGS[language]['voz'].format(y0=f['y0'], v0=round(f['v0']), y1=f['y1'], v1=round(f['v1']), diff=round(f['diff']), years=f['years'], d0=f['d0'], r0=number(f['r0'], language), d1=f['d1'], r1=number(f['r1'], language))


def _sentence_starts(words: list[dict]) -> list[float]:
    starts = [words[0]['start']]
    for w, nxt in zip(words, words[1:]):
        if w['text'].rstrip().endswith(('.', '!', '?')):
            starts.append(nxt['start'])
    return starts


def build_props(series: list[dict], csv_path: Path, marks: dict | None, language: str = 'en', voice_public: str = '') -> dict:
    f = facts(series)
    s = STRINGS[language]
    words = (marks or {}).get('words', [])
    total_voice = (marks or {}).get('duration', 26.0)
    # Scene changes land on the first word of a sentence; a silent version keeps the same proportions.
    st = _sentence_starts(words) if words else [0, 4, 7, 9.5, 11.5, 15, 19]
    while len(st) < 7:
        st.append(st[-1] + 3)
    source_lines = [s['l1'], SOURCE_URL, s['l3'].format(fetched=FETCHED, unc=number(f['unc'], language)), s['l4']]
    t_flow = st[6]
    t_end = total_voice
    scenes = [
        {'tipo': 'concepto', 'inicio': 0, 'fin': st[0] + 2.6, 'rotulo': s['rotulo'], 'titulo': s['titulo'], 'definicion': s['definicion']},
        {'tipo': 'curva', 'inicio': st[0] + 2.6, 'fin': st[3], 'rotulo': s['curva'], 'unidad': s['unidad'], 'inicioDibujo': st[0] + 3.0, 'finDibujo': st[2] + .2},
        {'tipo': 'comparacion', 'inicio': st[3], 'fin': t_flow, 'rotulo': s['comp'], 'unidad': s['compu'], 'barras': [{'etiqueta': DECADE[language].format(d=r['decade']), 'valor': r['rate']} for r in f['rates']]},
        {'tipo': 'flujo', 'inicio': t_flow, 'fin': t_end + .2, 'rotulo': s['flujo'], 'pasos': s['pasos']},
        {'tipo': 'cronologia', 'inicio': t_end + .2, 'fin': t_end + 4.2, 'rotulo': s['crono'], 'hitos': [{'fecha': '1958', 'texto': s['h1']}, {'fecha': '1974', 'texto': s['h2']}, {'fecha': '2022-2023', 'texto': s['h3']}]},
        {'tipo': 'fuente', 'inicio': t_end + 4.2, 'fin': t_end + 8.4, 'rotulo': s['fuente'], 'lineas': source_lines},
    ]
    return {'duracion': round(t_end + 8.6, 2), 'voz': voice_public, 'words': words, 'coma': language != 'en', 'serie': [{'x': r['year'], 'y': r['mean']} for r in series], 'escenas': scenes,
            '_provenance': {'url': SOURCE_URL, 'fetched': FETCHED, 'sha256': hashlib.sha256(Path(csv_path).read_bytes()).hexdigest(), 'facts': f}}
