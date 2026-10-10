import { NavLink } from 'react-router-dom';
import './Header.css';

export function Header() {
	return (
		<header className="header">
			<h2>FinanceFlow</h2>
			<div className="header-actions">
				<NavLink to="/login">Login</NavLink>
			</div>
		</header>
	);
}
