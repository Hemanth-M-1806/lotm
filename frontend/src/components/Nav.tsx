import { NavLink, Link } from 'react-router-dom';
import { useAuth } from '../contexts/useAuth';

export function Nav() {
  const { user, logout } = useAuth();

  return (
    <nav className="nav" role="navigation" aria-label="Main navigation">
      <Link to="/" className="nav__brand" aria-label="Lord of the Mysteries Tarot home">
        L.o.M. Tarot
      </Link>
      <ul className="nav__links">
        <li>
          <NavLink
            to="/"
            end
            className={({ isActive }) => `nav__link${isActive ? ' nav__link--active' : ''}`}
          >
            Oracle
          </NavLink>
        </li>
        {user && (
          <li>
            <NavLink
              to="/history"
              className={({ isActive }) => `nav__link${isActive ? ' nav__link--active' : ''}`}
            >
              Archive
            </NavLink>
          </li>
        )}
        {user ? (
          <li>
            <button
              onClick={logout}
              className="btn btn--ghost btn--sm"
              aria-label={`Sign out as ${user.display_name}`}
            >
              Sign out
            </button>
          </li>
        ) : (
          <li>
            <NavLink
              to="/login"
              className={({ isActive }) => `nav__link${isActive ? ' nav__link--active' : ''}`}
            >
              Sign in
            </NavLink>
          </li>
        )}
      </ul>
    </nav>
  );
}
