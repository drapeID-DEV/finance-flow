import { NavLink } from 'react-router-dom';
import {
	Bell,
	ChartNoAxesCombined,
	Wallet,
	LayoutDashboard,
	Coins
} from 'lucide-react';
import './Sidebar.css';

export function Sidebar() {
	return (
		<aside className="sidebar">
			<NavLink className="logo" to="/">
				FinanceFlow
			</NavLink>

			<nav className="navigation">
				<NavLink to="/" end>
					<LayoutDashboard size={20} />
					<span>Dashboard</span>
				</NavLink>

				<NavLink to="/instruments">
					<Coins size={20} />
					<span>Instruments</span>
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
	);
}
