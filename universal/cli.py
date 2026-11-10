"""CLI: python -m universal.cli <start|setup|repair|uninstall|updates|logs|doctor|route|validate|run|workflows|inventory|catalog|qc|contact-sheet|voice|fixtures|plan|render|present|infographic|film|character3d|modules|effects|film-style|transcribe|design-check>"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .engine import plan, read_spec


def show(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description='Motion Design Kit Universal Studio, local d’abord')
    sub = ap.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='diagnostic complet de la machine et du kit, en lecture seule')
    go = sub.add_parser('start', help='point d’entrée unique : premier lancement, reprise, réparation ou kit prêt')
    go.add_argument('--language', choices=['fr', 'es', 'en'], default='fr')
    su = sub.add_parser('setup', help='assistant d’installation : rien ne s’installe sans --approve')
    su.add_argument('action', choices=['detect', 'plan', 'apply', 'decline', 'verify', 'wizard'])
    su.add_argument('ids', nargs='*', help='decline : éléments refusés par l’utilisateur')
    su.add_argument('--approve', action='append', default=[], help='élément accepté par l’utilisateur, par son id (répétable)')
    su.add_argument('--deep', action='store_true', help='verify : relance chaque moteur et fait les vidéos d’essai ; detect : essaie les encodeurs')
    su.add_argument('--language', choices=['fr', 'es', 'en'])
    su.add_argument('--no-questions', action='store_true', help='wizard : ne pose aucune question et n’installe que les --approve')
    rp = sub.add_parser('repair', help='dit ce qui ne fonctionne plus ; ne répare que les --approve')
    rp.add_argument('--approve', action='append', default=[])
    un = sub.add_parser('uninstall', help='liste ce qui peut partir ; ne retire que les --approve, dans le dossier du kit')
    un.add_argument('--approve', action='append', default=[])
    up = sub.add_parser('updates', help='compare les versions fixées avec les dernières publiées ; ne met rien à jour')
    up.add_argument('--offline', action='store_true')
    sub.add_parser('logs', help='derniers événements du journal technique')
    r = sub.add_parser('route', help='brief + fichiers -> project.json validé et fiche de routage')
    r.add_argument('--brief', default='')
    r.add_argument('--input', '-i', action='append', default=[], help='fichier, dossier ou URL (répétable). chemin::role pour imposer un rôle')
    r.add_argument('--name', default='projet')
    r.add_argument('--language', choices=['fr', 'es', 'en'])
    r.add_argument('--format', choices=['16:9', '9:16', '1:1', '4:5'])
    r.add_argument('--duration', type=float)
    r.add_argument('--style')
    r.add_argument('--intent', action='append', help='ce que l’agent a compris : prime sur les mots-clés (répétable)')
    r.add_argument('--effects', action='store_true', help='l’agent a compris : effets autour de la personne filmée')
    r.add_argument('--workflow', action='append', help='l’agent a compris : traitement de la vidéo fournie (répétable), voir « workflows »')
    r.add_argument('--output', '-o', type=Path)
    v = sub.add_parser('validate')
    v.add_argument('project', type=Path)
    u = sub.add_parser('run', help='exécute project.json puis le contrôle qualité')
    u.add_argument('project', type=Path)
    u.add_argument('--profile', choices=['draft', 'review', 'final', '4k'])
    i = sub.add_parser('inventory')
    i.add_argument('paths', nargs='+')
    c = sub.add_parser('catalog', help='cherche dans les styles')
    c.add_argument('query', nargs='*')
    c.add_argument('--category')
    c.add_argument('--presets', action='store_true')
    q = sub.add_parser('qc')
    q.add_argument('--video', required=True, type=Path)
    q.add_argument('--frames', type=Path)
    q.add_argument('--project', type=Path, help='project.json : exceptions déclarées')
    q.add_argument('--subtitles', type=Path)
    q.add_argument('--styleframe', action='append', default=[], help='image@secondes')
    q.add_argument('--registrar', action='store_true', help='avec --project : garde cette entrega dans le profil')
    s = sub.add_parser('contact-sheet')
    s.add_argument('paths', nargs='+', type=Path)
    s.add_argument('--output', '-o', required=True, type=Path)
    t = sub.add_parser('voice', help='voix locale gratuite avec marques de mots et de visèmes')
    t.add_argument('--text', required=True)
    t.add_argument('--language', default='en')
    t.add_argument('--output', '-o', required=True, type=Path)
    t.add_argument('--srt', type=Path)
    t.add_argument('--provider', choices=['local', 'kokoro', 'elevenlabs'], default='local')
    t.add_argument('--voice-id', help='elevenlabs ou kokoro : identifiant de la voix')
    t.add_argument('--approve', action='store_true', help='elevenlabs : autorise cet appel payant')
    sub.add_parser('fixtures', help='médias de test synthétiques, sans droits de tiers')
    wf = sub.add_parser('workflows', help='traitements disponibles pour une vidéo fournie')
    wf.add_argument('--language', choices=['fr', 'es', 'en'], default='fr')
    m = sub.add_parser('modules', help='modules optionnels : environnement local, versions fixées')
    m_sub = m.add_subparsers(dest='action', required=True)
    m_sub.add_parser('status')
    mi = m_sub.add_parser('install')
    mi.add_argument('names', nargs='+', help='effects audio music voice transcribe film voice-model whisper-model hdri instruments-<lib>')
    mi.add_argument('--approve-download', action='store_true', help='autorise le téléchargement des gros fichiers demandés')
    e = sub.add_parser('effects', help='effets autour d’une personne filmée')
    e_sub = e.add_subparsers(dest='action', required=True)
    e_sub.add_parser('list')
    ec = e_sub.add_parser('check')
    ec.add_argument('plan', type=Path)
    for action in ('render', 'still'):
        er = e_sub.add_parser(action)
        er.add_argument('video', type=Path)
        er.add_argument('--plan', required=True, type=Path)
        er.add_argument('--output', '-o', required=True, type=Path)
        er.add_argument('--profile', choices=['draft', 'review', 'final', '4k'], default='draft')
        er.add_argument('--interfaces-marques', action='store_true', help='accepte les effets qui imitent Instagram, iMessage ou iPhone')
        if action == 'still':
            er.add_argument('--at', required=True, help='secondes séparées par des virgules')
    fs = sub.add_parser('film-style', help='films écrits en code dans un style Opuscar')
    fs_sub = fs.add_subparsers(dest='action', required=True)
    fs_sub.add_parser('list')
    fsh = fs_sub.add_parser('show')
    fsh.add_argument('style')
    fn = fs_sub.add_parser('new')
    fn.add_argument('style')
    fn.add_argument('folder', type=Path)
    fn.add_argument('--name', default='Film')
    fn.add_argument('--language', default='fr')
    fn.add_argument('--seconds', type=float, default=12)
    fst = fs_sub.add_parser('still')
    fst.add_argument('folder', type=Path)
    fst.add_argument('times', nargs='+', type=float)
    fst.add_argument('--format', choices=['16:9', '9:16', '1:1', '4:5'], default='16:9')
    fst.add_argument('--profile', choices=['draft', 'review', 'final', '4k'], default='review')
    fst.add_argument('--out', type=Path)
    fr_ = fs_sub.add_parser('render')
    fr_.add_argument('folder', type=Path)
    fr_.add_argument('--output', '-o', required=True, type=Path)
    fr_.add_argument('--format', choices=['16:9', '9:16', '1:1', '4:5'], default='16:9')
    fr_.add_argument('--profile', choices=['draft', 'review', 'final', '4k'], default='draft')
    fr_.add_argument('--fps', type=float, default=24)
    fr_.add_argument('--grain', type=float, default=2)
    fc = fs_sub.add_parser('check')
    fc.add_argument('folder', type=Path)
    fp = fs_sub.add_parser('py', help='lance un script du film dans l’environnement des modules')
    fp.add_argument('script', type=Path)
    fma = fs_sub.add_parser('master')
    fma.add_argument('video', type=Path)
    fma.add_argument('mix', type=Path)
    fma.add_argument('output', type=Path)
    fma.add_argument('--fps', type=float, default=24)
    fma.add_argument('--grain', type=float, default=2)
    fd = fs_sub.add_parser('demo', help='source de la démo du style, au commit audité, à lire seulement')
    fd.add_argument('style')
    fs_sub.add_parser('assets3d', help='textures et modèles Poly Haven (CC0), au commit audité')
    dc = sub.add_parser('design-check', help='contrôle de design d’une page HTML : conseille, ne bloque pas')
    dc.add_argument('page', type=Path)
    tr = sub.add_parser('transcribe', help='minutage des mots, hors ligne')
    tr.add_argument('media', type=Path)
    tr.add_argument('--output', '-o', required=True, type=Path)
    tr.add_argument('--language')
    for cmd in ('plan', 'render', 'present', 'infographic', 'character3d'):
        p = sub.add_parser(cmd)
        p.add_argument('--config', '-c', required=True, type=Path)
        if cmd != 'plan':
            p.add_argument('--output', '-o', required=True, type=Path)
        if cmd == 'render':
            p.add_argument('--profile', choices=['draft', 'review', 'final', '4k'], default='draft')
    f = sub.add_parser('film', help='film linéaire d’une présentation HTML')
    f.add_argument('deck', type=Path)
    f.add_argument('--output', '-o', required=True, type=Path)
    f.add_argument('--stills')
    args = ap.parse_args(argv)
    if args.command == 'doctor':
        from .capabilities import detect
        return show(detect(full=True))
    if args.command == 'start':
        from . import onboarding
        return show(onboarding.start(args.language))
    if args.command == 'setup':
        from . import diagnostic, onboarding
        if args.action == 'detect':
            return show(diagnostic.full(test=args.deep))
        if args.action == 'plan':
            return show(onboarding.plan(language=args.language or 'fr'))
        if args.action == 'apply':
            if not args.approve:
                raise ValueError('Rien ne s’installe sans accord : nommer chaque élément accepté avec --approve.')
            return show(onboarding.apply(args.approve))
        if args.action == 'decline':
            return show(onboarding.decline(args.ids))
        if args.action == 'verify':
            report = onboarding.verify(deep=args.deep)
            show(report)
            if report['verdict'] == 'FAILED':
                raise SystemExit(1)
            return None
        raise SystemExit(onboarding.wizard(args.language, approved=args.approve if args.no_questions else None))
    if args.command == 'repair':
        from . import onboarding
        return show(onboarding.repair(args.approve or None))
    if args.command == 'uninstall':
        from . import onboarding
        return show(onboarding.uninstall(args.approve or None))
    if args.command == 'updates':
        from . import onboarding
        return show(onboarding.updates(online=not args.offline))
    if args.command == 'logs':
        from . import logs
        return show({'dossier': 'logs', 'derniers': logs.tail(20)})
    if args.command == 'route':
        from .inventory import inspect
        from .manifest import save, validate
        from .perfil import context
        from .router import INTENTS, route, summary
        items = [{'path': x.split('::')[0], 'role': x.split('::')[1]} if '::' in x else x for x in args.input]
        unknown = [i for i in args.intent or [] if i not in INTENTS]
        if unknown:
            raise ValueError(f"Intention inconnue : {', '.join(unknown)}. Possibles : {', '.join(INTENTS)}")
        project = route(args.brief, [inspect(x, Path.cwd()) for x in items], name=args.name, language=args.language, style=args.style, fmt=args.format, duration=args.duration,
                        intent=args.intent, force_effects=args.effects, profile=context(args.brief), workflow=args.workflow)
        problems = validate(project)
        if problems:
            raise ValueError('Manifeste invalide : ' + '; '.join(problems[:8]))
        if args.output:
            save(project, args.output)
        print(summary(project))
        for n in project['notes']:
            print('Note:', n)
        for q_ in project['questions']:
            print('Question:', q_['text'], '/'.join(q_['options']))
        return None
    if args.command == 'validate':
        from .manifest import load
        load(args.project)
        return print('OK', args.project)
    if args.command == 'run':
        from .run import run_project
        from .workflows import NeedsInput
        try:
            result = run_project(args.project, args.profile)
        except NeedsInput as waiting:  # not a failure: the kit did its part and waits for a reader's choice
            show({'status': 'needs-input', 'message': str(waiting), 'file': waiting.file})
            raise SystemExit(3)
        show(result)
        if result['status'] not in ('delivered', 'unchanged'):
            raise SystemExit(1)
        return None
    if args.command == 'inventory':
        from .inventory import inspect
        return show([inspect(p, Path.cwd()) for p in args.paths])
    if args.command == 'catalog':
        from .catalog import search
        return show(search(' '.join(args.query), args.category, args.presets))
    if args.command == 'qc':
        from .manifest import load
        from .qc import qc as checker
        project = load(args.project) if args.project else None
        exceptions = project['quality'].get('exceptions', []) if project else []
        frames = [{'path': x.rsplit('@', 1)[0], 'at': float(x.rsplit('@', 1)[1])} for x in args.styleframe]
        result = checker(args.video, args.frames, exceptions=exceptions, subtitles=args.subtitles, styleframes=frames)
        if args.registrar and project:
            from .perfil import remember_delivery
            remember_delivery(project, project['deliverables'][0], {'qc': result})
        show(result)
        if not result['pass']:
            raise SystemExit(1)
        return None
    if args.command == 'contact-sheet':
        from .inventory import contact_sheet
        return print(contact_sheet(args.paths, args.output))
    if args.command == 'voice':
        from .voice import synthesize, to_srt
        if args.provider == 'kokoro':
            from . import voice_kokoro
            marks = voice_kokoro.synthesize(args.text, args.output, args.language, args.voice_id)
        elif args.provider == 'elevenlabs':
            from . import voice_elevenlabs
            if not args.voice_id:
                raise ValueError('--voice-id requis avec elevenlabs')
            marks = voice_elevenlabs.synthesize(args.text, args.output, args.language, args.voice_id, approved=args.approve)
        else:
            marks = synthesize(args.text, args.output, args.language)
        args.output.with_suffix('.json').write_text(json.dumps(marks, ensure_ascii=False, indent=1), encoding='utf-8')
        if args.srt:
            to_srt(marks['words'], args.srt)
        return show({k: marks.get(k) for k in ('voice', 'culture', 'language_match', 'timing', 'duration', 'chars_billed_now')} | {'words': len(marks['words']), 'visemes': len(marks['visemes'])})
    if args.command == 'modules':
        from . import modules
        if args.action == 'status':
            return show(modules.status())
        return show(modules.install(args.names, args.approve_download))
    if args.command == 'effects':
        from . import effects
        if args.action == 'list':
            return show(effects.catalog())
        plan = json.loads(args.plan.read_text(encoding='utf-8'))
        plan = plan.get('effects', plan) if isinstance(plan, dict) else plan
        if args.action == 'check':
            return print(effects.check(plan, Path('out/effects-check.plan.json')))
        base = args.plan.resolve().parent
        return show(effects.render(args.video, plan, args.output, profile=args.profile, stills=getattr(args, 'at', None), brand_ui_ok=args.interfaces_marques, base=base))
    if args.command == 'film-style':
        from . import film_style as fm
        if args.action == 'list':
            return show(fm.styles())
        if args.action == 'show':
            return show(fm.find(args.style))
        if args.action == 'new':
            return print(fm.new(args.style, args.folder, name=args.name, language=args.language, seconds=args.seconds))
        if args.action == 'still':
            return show(fm.stills(args.folder, args.times, fmt=args.format, profile=args.profile, out=args.out))
        if args.action == 'render':
            return show(fm.render(args.folder, args.output, fmt=args.format, profile=args.profile, fps=args.fps, grain=args.grain))
        if args.action == 'check':
            return print(fm.reading_check(args.folder))
        if args.action == 'py':
            return print(fm.run_py(args.script))
        if args.action == 'master':
            return show(fm.master(args.video, args.mix, args.output, fps=args.fps, grain=args.grain))
        if args.action == 'demo':
            return print(fm.demo(args.style))
        return print(fm.assets3d())
    if args.command == 'design-check':
        from .design_check import check
        return show(check(args.page))
    if args.command == 'transcribe':
        from .voice_kokoro import transcribe
        return show({'mots': len(transcribe(args.media, args.output, args.language)), 'fichier': str(args.output)})
    if args.command == 'workflows':
        from .workflows import catalog
        return show(catalog(args.language))
    if args.command == 'fixtures':
        from .fixtures import build
        return show({k: str(v) for k, v in build().items()})
    if args.command == 'film':
        from .run import film
        return print(film(args.deck, args.output, args.stills))
    spec = read_spec(args.config)
    base = args.config.resolve().parent
    if args.command == 'plan':
        from .router import summary
        project = plan(spec, base)
        print(summary(project))
        return show(project)
    if args.command == 'render':
        from .render import render
        return show(render(spec, base, args.output, args.profile))
    if args.command in ('present', 'infographic'):
        from .present import infographic, presentation
        return show((presentation if args.command == 'present' else infographic)(spec, args.output))
    if args.command == 'character3d':
        from .character import build
        return show(build(spec, base, args.output))
    return None


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, RuntimeError, KeyError) as e:
        print('ERREUR:', e, file=sys.stderr)
        sys.exit(2)
