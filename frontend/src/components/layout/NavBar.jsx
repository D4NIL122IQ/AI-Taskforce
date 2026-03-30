/**
 * @file NavBar.jsx
 * @description Barre de navigation principale de l'application.
 *
 * STRUCTURE :
 *   [Logo "AI Taskforce"] ── [Liens centrés] ── [Icône utilisateur]
 *
 * COMPORTEMENT :
 *   - Utilise <NavLink> de react-router-dom pour détecter la route active.
 *   - Le lien actif reçoit un encadrement pill en dégradé (rose → violet → orange).
 *   - Les liens inactifs s'éclaircissent au survol.
 *
 * LIENS CONFIGURABLES :
 *   Modifier le tableau NAV_LINKS pour ajouter, retirer ou réordonner des liens
 *   sans toucher au JSX. Chaque entrée : { label, to }.
 */

import { NavLink, Link } from 'react-router-dom';

// ─── Configuration des liens de navigation ───────────────────────────────────
// Modifiez ici pour ajouter des routes sans toucher au JSX.

const NAV_LINKS = [
  { label: 'Accueil',        to: '/' },
  { label: 'Gestion Agents', to: '/agents' },
  { label: 'Workflow',       to: '/workflow' },
];

// ─── Sous-composant : NavItem ─────────────────────────────────────────────────
/**
 * Rend un lien de navigation avec l'état actif géré automatiquement.
 * Actif → pill avec bordure en dégradé de marque.
 * Inactif → texte semi-transparent + transition hover.
 */
const NavItem = ({ label, to }) => (
  <NavLink to={to} end={to === '/'} className="focus-visible:outline-none">
    {({ isActive }) =>
      isActive ? (
        // ── Lien actif : wrapper gradient + fond sombre ──
        <span
          className="inline-flex rounded-full"
          style={{
            background: 'linear-gradient(90deg, #f43f5e 0%, #8b5cf6 50%, #f97316 100%)',
            padding: '1px',
          }}
          aria-current="page"
        >
          <span className="px-5 py-[7px] rounded-full bg-[#080808] text-white text-sm font-semibold whitespace-nowrap">
            {label}
          </span>
        </span>
      ) : (
        // ── Lien inactif ──
        <span className="px-5 py-[7px] text-white/55 hover:text-white text-sm font-medium transition-colors duration-200 whitespace-nowrap">
          {label}
        </span>
      )
    }
  </NavLink>
);

// ─── Icône utilisateur (SVG inline — évite une dépendance externe) ─────────────
const UserIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="28"
    height="28"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-label="Profil utilisateur"
    role="img"
  >
    <circle cx="12" cy="8" r="4" />
    <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
  </svg>
);

// ─── Composant principal NavBar ───────────────────────────────────────────────

const NavBar = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      {/* Fond semi-transparent avec séparation inférieure subtile */}
      <div className="bg-[#080808]/80 backdrop-blur-md border-b border-white/[0.06]">
        <nav
          className="max-w-7xl mx-auto px-6 h-[68px] flex items-center justify-between"
          aria-label="Navigation principale"
        >
          {/* ── Logo ── */}
          <Link
            to="/"
            className="text-white font-display font-bold text-lg tracking-tight hover:opacity-85 transition-opacity duration-200 flex-shrink-0"
          >
            AI Taskforce
          </Link>

          {/* ── Liens de navigation (centrés) ── */}
          <ul className="hidden md:flex items-center gap-1" role="list">
            {NAV_LINKS.map(({ label, to }) => (
              <li key={to}>
                <NavItem label={label} to={to} />
              </li>
            ))}
          </ul>

          {/* ── Actions utilisateur ── */}
          <div className="flex items-center gap-4 flex-shrink-0">
            {/* Bouton profil utilisateur */}
            <button
              type="button"
              className="text-white/60 hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/30 rounded-full p-0.5"
              aria-label="Accéder au profil"
            >
              <UserIcon />
            </button>
          </div>
        </nav>
      </div>
    </header>
  );
};

export default NavBar;