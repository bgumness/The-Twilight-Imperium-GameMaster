/* Canonical faction registry for the whole site.
   Every tool refers to a faction by its `id` here. The three original tools each used a
   different naming scheme; `ledger`, `arbiter` and `council` hold the old keys so saved games
   and code can be translated in one place. */
(function (root) {
  const F = [
    // id            name                          set     ledger (full name)            arbiter     council
    ['arborec',   'The Arborec',                 'base', 'Arborec',                    'arborec',  'arborec'],
    ['letnev',    'The Barony of Letnev',        'base', 'Barony of Letnev',           'letnev',   'barony-of-letnev'],
    ['saar',      'The Clan of Saar',            'base', 'Clan of Saar',               'saar',     'clan-of-saar'],
    ['muaat',     'The Embers of Muaat',         'base', 'Embers of Muaat',            'muaat',    'embers-of-muaat'],
    ['hacan',     'The Emirates of Hacan',       'base', 'Emirates of Hacan',          'hacan',    'emirates-of-hacan'],
    ['sol',       'The Federation of Sol',       'base', 'Federation of Sol',          'sol',      'federation-of-sol'],
    ['creuss',    'The Ghosts of Creuss',        'base', 'Ghosts of Creuss',           'creuss',   'ghosts-of-creuss'],
    ['l1z1x',     'The L1Z1X Mindnet',           'base', 'L1Z1X Mindnet',              'l1z1x',    'l1z1x-mindnet'],
    ['mentak',    'The Mentak Coalition',        'base', 'Mentak Coalition',           'mentak',   'mentak-coalition'],
    ['naalu',     'The Naalu Collective',        'base', 'Naalu Collective',           'naalu',    'naalu-collective'],
    ['nekro',     'The Nekro Virus',             'base', 'Nekro Virus',                'nekro',    'nekro-virus'],
    ['sardakk',   'Sardakk N’orr',          'base', "Sardakk N'orr",              'sardakk',  'sardakk-norr'],
    ['jolnar',    'The Universities of Jol-Nar', 'base', 'Universities of Jol-Nar',    'jolnar',   'universities-of-jol-nar'],
    ['winnu',     'The Winnu',                   'base', 'Winnu',                      'winnu',    'winnu'],
    ['xxcha',     'The Xxcha Kingdom',           'base', 'Xxcha Kingdom',              'xxcha',    'xxcha-kingdom'],
    ['yin',       'The Yin Brotherhood',         'base', 'Yin Brotherhood',            'yin',      'yin-brotherhood'],
    ['yssaril',   'The Yssaril Tribes',          'base', 'Yssaril Tribes',             'yssaril',  'yssaril-tribes'],
    ['argent',    'The Argent Flight',           'pok',  'Argent Flight',              'argent',   'argent-flight'],
    ['empyrean',  'The Empyrean',                'pok',  'Empyrean',                   'empyrean', 'empyrean'],
    ['mahact',    'The Mahact Gene-Sorcerers',   'pok',  'Mahact Gene-Sorcerers',      'mahact',   'mahact-gene-sorcerers'],
    ['naazrokha', 'The Naaz-Rokha Alliance',     'pok',  'Naaz-Rokha Alliance',        'naaz',     'naaz-rokha-alliance'],
    ['nomad',     'The Nomad',                   'pok',  'The Nomad',                  'nomad',    'nomad'],
    ['titans',    'The Titans of Ul',            'pok',  'Titans of Ul',               'titans',   'titans-of-ul'],
    ['vuilraith', 'The Vuil’raith Cabal',   'pok',  "Vuil'raith Cabal",           'vuil',     'vuil-raith-cabal'],
    // Codex faction: only the Council Chamber knows it today; no art yet.
    ['keleres',   'The Council Keleres',         'codex', null,                        null,       'council-keleres']
  ];

  const FACTIONS = F.map(([id, name, set, ledger, arbiter, council]) => ({
    id, name, set, legacy: { ledger, arbiter, council },
    art: set === 'codex' ? {} : {
      emblem:   `assets/factions/emblems-px/${id}.webp`,   // the Battle Arbiter's symbols, used site-wide
      portrait: `assets/factions/portraits/${id}.webp`   // © Fantasy Flight Games: show the credit next to it
    }
  }));
  const byId = Object.fromEntries(FACTIONS.map(f => [f.id, f]));
  const fromLegacy = (tool, key) => FACTIONS.find(f => f.legacy[tool] === key) || null;

  /* Same eight player colours all three tools already use. */
  const COLORS = {
    red: '#ff5a52', blue: '#4f8dff', green: '#3fbf6f', yellow: '#f2d14b',
    purple: '#a77bff', black: '#3a4152', orange: '#ff9a3c', pink: '#ff7ac6'
  };

  root.TI4 = Object.assign(root.TI4 || {}, { FACTIONS, faction: id => byId[id] || null, fromLegacy, COLORS });
})(typeof window !== 'undefined' ? window : globalThis);
