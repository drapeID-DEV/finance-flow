import {
	BrowserRouter,
	Navigate,
	Route,
	Routes,
	useNavigate
} from 'react-router-dom';
import { MainLayout } from '../layouts/MainLayout';
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from '../store/store';
import { sessionRestored } from '../store/authSlice';
import { ProtectedRoute } from './ProtectedRoute';
import { InstrumentsPage } from '../pages/InstrumentsPage/InstrumentsPage';
import AlertsPage from '../pages/AlertsPage/AlertsPage';
import DashboardPage from '../pages/DashboardPage/DashboardPage';
import PortfolioPage from '../pages/PortfolioPage/PortfolioPage';
import AnalyticsPage from '../pages/AnalyticsPage/AnalyticsPage';
import LoginPage from '../pages/LoginPage/LoginPage';
import RegisterPage from '../pages/RegisterPage/RegisterPage';

function SessionHandler() {
	const dispatch = useDispatch<AppDispatch>();
	const navigate = useNavigate();
	const sessionExpired = useSelector(
		(state: RootState) => state.auth.sessionExpired
	);

	useEffect(() => {
		if (sessionExpired) {
			dispatch(sessionRestored());
			navigate('/login', { replace: true });
		}
	}, [sessionExpired, dispatch, navigate]);

	return null;
}

export function AppRouter() {
	return (
		<BrowserRouter>
			<SessionHandler />
			<Routes>
				<Route element={<ProtectedRoute />}>
					<Route element={<MainLayout />}>
						<Route path="/" element={<DashboardPage />} />
						<Route path="/portfolio" element={<PortfolioPage />} />
						<Route path="/alerts" element={<AlertsPage />} />
						<Route path="/analytics" element={<AnalyticsPage />} />
						<Route
							path="/instruments"
							element={<InstrumentsPage />}
						/>
					</Route>
				</Route>
				<Route path="/login" element={<LoginPage />} />
				<Route path="/register" element={<RegisterPage />} />
				<Route path="*" element={<Navigate to="/" replace />} />
			</Routes>
		</BrowserRouter>
	);
}
