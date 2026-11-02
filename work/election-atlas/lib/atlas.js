/* Shared by the four atlas pages: optional data, the "not available yet" state,
   and portraits. */

/* A data file that may legitimately be missing. Never throws:
     { ok: true, doc }            the file, parsed
     { ok: false, reason: 'absent' } the server answered 404
     { ok: false, reason: 'error' }  a network failure, another status, or bad JSON */
export async function fetchOptional(url) {
  let r;
  try { r = await fetch(url); } catch { return { ok: false, reason: 'error' }; }
  if (r.status === 404) return { ok: false, reason: 'absent' };
  if (!r.ok) return { ok: false, reason: 'error' };
  try { return { ok: true, doc: await r.json() }; } catch { return { ok: false, reason: 'error' }; }
}

/* data/availability.json says which optional files exist, so a page never has to
   probe for one. If the index itself cannot be read, every optional file reads
   as not available: the page shows "not available yet" rather than guessing. */
export async function loadAvailability(dataRoot) {
  const res = await fetchOptional(dataRoot + 'availability.json');
  return res.ok ? res.doc : {};
}
export const byelAvailable = (av, year) => !!(av.ls && av.ls.byel && av.ls.byel[year]);
export const lsDetailAvailable = (av, year) => !!(av.ls && av.ls.detail && av.ls.detail[year]);
export const unionRoster = (av, year) =>
  (av.cabinet && av.cabinet.union && av.cabinet.union[year]) || { sworn_in: false, as_it_stands: false };
export const stateRoster = (av, state, cycle) =>
  (av.cabinet && av.cabinet.state && av.cabinet.state[state] && av.cabinet.state[state][cycle]) ||
  { sworn_in: false, as_it_stands: false };
/* The state's real assembly cycles, oldest first, each with whether it is present. */
export const acCycles = (av, state) =>
  Object.entries((av.ac && av.ac[state] && av.ac[state].cycles) || {})
    .map(([y, ok]) => ({ year: Number(y), ok: !!ok }))
    .sort((a, b) => a.year - b.year);
export const listed = (av, kind, state, key) =>
  !!(av[kind] && av[kind][state] && av[kind][state].includes(key));
export const hasPhoto = (av, year, uid) =>
  !!(av.photos && av.photos.ls && av.photos.ls[year] && av.photos.ls[year].includes(uid));

/* The one sentence a view shows when its data has not been added. It names what
   is missing and who publishes it; it never shows a number, a name or a zero. */
export const notAvailable = (what, publisher, verb = 'has') =>
  `Not available yet — ${what} ${verb} not been added from ${publisher}.`;
export const voidHTML = (what, publisher, verb = 'has') =>
  `<div class="void"><p>${notAvailable(what, publisher, verb)}</p></div>`;

export const ECI = 'the Election Commission of India';
export const PRESIDENT = 'the President’s Secretariat';
export const CMO_UP = 'the Chief Minister’s Office, Uttar Pradesh';

/* A year button with no data stays in its row, marked rather than removed, so an
   old link carrying that year still lands on a working page. */
export function markUnavailable(btn, title) {
  btn.setAttribute('aria-disabled', 'true');
  btn.title = title;
  btn.classList.add('na');
}

/* ── portraits ────────────────────────────────────────────────────────── */
export const initials = name =>
  String(name || '').replace(/^(shri|smt|dr|prof)\.?\s+/i, '').split(/[\s,]+/)
    .filter(Boolean).map(w => w[0]).slice(0, 2).join('').toUpperCase() || '?';

export const monogramHTML = name =>
  `<span class="monogram" aria-hidden="true">${initials(name)}</span>`;

/* A portrait <img> that falls back to the monogram if it fails to load. */
export const portraitHTML = (src, name) =>
  `<img src="${src}" alt="" decoding="async" loading="lazy" data-monogram="${initials(name)}">`;

/* One listener for the whole page: image errors do not bubble, so it listens on
   the capture phase and swaps any failed portrait for its monogram. */
export function installPortraitFallback() {
  document.addEventListener('error', e => {
    const img = e.target;
    if (!(img instanceof HTMLImageElement) || img.dataset.monogram === undefined) return;
    const m = document.createElement('span');
    m.className = 'monogram';
    m.setAttribute('aria-hidden', 'true');
    m.textContent = img.dataset.monogram;
    img.replaceWith(m);
  }, true);
}

/* Cabinet portrait files are named ls-<Lok Sabha member id>.jpg or
   rs-<Rajya Sabha member id>.jpg, which is all a credit line needs. */
export function photoMember(file) {
  const m = String(file || '').match(/(ls|rs)-(\d+)\.\w+$/);
  return m ? { house: m[1], id: m[2] } : { house: 'ls', id: '' };
}

/* Visible credit under a portrait. Lok Sabha portraits link to the member's
   biography; Rajya Sabha portraits to the Rajya Sabha list of ministers. */
export function photoCreditHTML(house, memberId) {
  if (house === 'rs') {
    return `<span class="photo-credit">Photo: Rajya Sabha Secretariat · ` +
      `<a href="https://sansad.in/rs/members/in-council-of-ministers" target="_blank" rel="noopener">sansad.in ↗</a></span>`;
  }
  const href = memberId
    ? `https://sansad.in/ls/members/biography/${memberId}?locale=en`
    : 'https://sansad.in/ls/members';
  return `<span class="photo-credit">Photo: Lok Sabha Secretariat · ` +
    `<a href="${href}" target="_blank" rel="noopener">sansad.in ↗</a></span>`;
}
