// One timeline drives the picture, the score and the sound. At 120 BPM, a beat lasts 0.5 s: every accent lands on one.
export const TIMELINE = { yellow: 4, arrive: 8, pink: 8.5, loaf: 10.5, title: 11.5, end: 14 };
export const EVENTS = [
  { t: .25, type: 'feed' }, { t: 4, type: 'plate' }, { t: 8, type: 'bell' }, { t: 8.5, type: 'plate' }, { t: 10.5, type: 'cut' }, { t: 11.5, type: 'plate' },
];
