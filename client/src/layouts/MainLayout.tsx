import { NavLink, Outlet } from 'react-router-dom';
import {
	Bell,
	ChartNoAxesCombined,
	Wallet,
	LayoutDashboard
} from 'lucide-react';

export function MainLayout() {
	return (
		<div className="app">
			<aside className="sidebar">
				<div className="logo">FinanceFlow</div>
				<nav className="navigation">
					<NavLink to="/">
						<LayoutDashboard size={20} />
						<span>Dashboard</span>
					</NavLink>
					<NavLink to="/portfolio">
						<Wallet size={20} />
						<span>Portfolio</span>
					</NavLink>
					<NavLink to="/alerts">
						<Bell size={20} />
						<span>Alerts</span>
					</NavLink>
					<NavLink to="/analytics">
						<ChartNoAxesCombined size={20} />
						<span>Analytics</span>
					</NavLink>
				</nav>
			</aside>
			<main className="main-content">
				<header className="header">
					<h2>FinanceFlow</h2>
					<div className="header-actions">
						<NavLink to="/login">Login</NavLink>
					</div>
				</header>
				<section className="content">
					<Outlet />
				</section>
			</main>
		</div>
	);
}
