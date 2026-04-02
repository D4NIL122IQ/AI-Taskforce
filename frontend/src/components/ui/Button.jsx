/**
 * @file Button.jsx
 * @description Composant bouton réutilisable.
 *
 * VARIANTS :
 *   - "primary"   → Verre sombre opaque + icône optionnelle (ex. CTA principal)
 *   - "secondary" → Contour translucide (ex. CTA secondaire, "Se connecter")
 *
 * UTILISATION :
 *   <Button to="/register" variant="primary" icon={<BotIcon />}>
 *     Commencer
 *   </Button>
 *
 *   <Button to="/login" variant="secondary" icon={<LogInIcon />}>
 *     Se connecter
 *   </Button>
 *
 * PROPS :
 *   to        {string}          – Route react-router (rend un <Link>)
 *   onClick   {function}        – Handler alternatif si pas de `to`
 *   variant   {'primary'|'secondary'} – Style visuel
 *   icon      {ReactNode}       – Icône affichée à gauche du label
 *   className {string}          – Classes Tailwind additionnelles
 *   children  {ReactNode}       – Label du bouton
 *   disabled  {boolean}         – Désactive le bouton
 */

import { Link } from 'react-router-dom';

// ─── Styles par variant ──────────────────────────────────────────────────────

const VARIANT_CLASSES = {
  primary: [
    'bg-gray-900/8 border border-gray-900/15 text-gray-900',
    'hover:bg-gray-900/12 hover:border-gray-900/25',
    'dark:bg-white/10 dark:border-white/20 dark:text-white',
    'dark:hover:bg-white/15 dark:hover:border-white/30',
  ].join(' '),

  secondary: [
    'bg-transparent border border-gray-400/40 text-gray-600',
    'hover:bg-gray-100 hover:text-gray-900 hover:border-gray-400/60',
    'dark:border-white/20 dark:text-white/80',
    'dark:hover:bg-white/5 dark:hover:text-white dark:hover:border-white/30',
  ].join(' '),
};

// ─── Composant ───────────────────────────────────────────────────────────────

const Button = ({
  to,
  onClick,
  variant = 'primary',
  icon,
  className = '',
  children,
  disabled = false,
}) => {
  const baseClasses = [
    'inline-flex items-center gap-2.5',
    'px-6 py-3',
    'rounded-xl',
    'text-sm font-medium',
    'transition-all duration-200 ease-in-out',
    'cursor-pointer select-none',
    'backdrop-blur-sm',
    disabled ? 'opacity-40 pointer-events-none' : '',
    VARIANT_CLASSES[variant] ?? VARIANT_CLASSES.primary,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  // Icône : wrapper garantissant une taille cohérente
  const IconWrapper = icon ? (
    <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
      {icon}
    </span>
  ) : null;

  // Rend un <Link> si une route est fournie, sinon un <button>
  if (to) {
    return (
      <Link to={to} className={baseClasses} aria-disabled={disabled}>
        {IconWrapper}
        {children}
      </Link>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={baseClasses}
      disabled={disabled}
    >
      {IconWrapper}
      {children}
    </button>
  );
};

export default Button;