import { Outlet } from 'react-router-dom';
import { Header } from '../components/Header/Header';
import { Sidebar } from '../components/Sidebar/Sidebar';
import './MainLayout.css';
import { AlertNotificationListener } from '../components/AlertNotificationListener/AlertNotificationListener';

export function MainLayout() {
	return (
		<div className="app">
			<AlertNotificationListener />
			<Sidebar />
			<main className="main-content">
				<Header />
				<section className="content">
					<Outlet />
				</section>
			</main>
		</div>
	);
}
