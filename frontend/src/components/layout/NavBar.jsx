import { NavLink, Link, useNavigate } from 'react-router-dom';

const NAV_LINKS = [
  { label: 'Accueil',        to: '/' },
  { label: 'Gestion Agents', to: '/agents' },
  { label: 'Workflow',       to: '/workflow' },
];

const NavItem = ({ label, to }) => (
  <NavLink to={to} end={to === '/'} className="focus-visible:outline-none">
    {({ isActive }) =>
      isActive ? (
        <span
          className="inline-flex px-5 py-[7px] rounded-full text-white text-sm font-semibold whitespace-nowrap bg-white/5"
          style={{ boxShadow: '0 0 0 1.5px #8b5cf6' }}
          aria-current="page"
        >
          {label}
        </span>
      ) : (
        <span className="inline-flex px-5 py-[7px] text-white/55 hover:text-white text-sm font-medium transition-colors duration-200 whitespace-nowrap">
          {label}
        </span>
      )
    }
  </NavLink>
);

const UserIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="28" height="28"
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

const NavBar = () => {
  const navigate = useNavigate();
  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      <div className="bg-[#080808]/80 backdrop-blur-md border-b border-white/[0.06]">
        <nav
          className="max-w-7xl mx-auto px-6 h-[68px] flex items-center justify-between"
          aria-label="Navigation principale"
        >
          {/* Logo */}
          <Link
            to="/"
            className="text-white font-display font-bold text-lg tracking-tight hover:opacity-85 transition-opacity duration-200 flex-shrink-0"
          >
            AI Taskforce
          </Link>

          {/* Liens centrés */}
          <ul className=" md:flex items-center gap-1" role="list">
            {NAV_LINKS.map(({ label, to }) => (
              <li key={to}>
                <NavItem label={label} to={to} />
              </li>
            ))}
          </ul>

          {/* Icône utilisateur */}
          <div className="flex items-center gap-4 flex-shrink-0">
            <button
              type="button"
              onClick={() => navigate('/auth')}
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
