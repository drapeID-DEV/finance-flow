import { useState } from 'react';
import { useLoginMutation } from '../api/authApi';
import { useGetCurrentUserQuery } from '../api/authApi';
import {
	BrowserRouter,
	Link,
	Navigate,
	Route,
	Routes,
	useLocation,
	useNavigate
} from 'react-router-dom';
import { MainLayout } from '../layouts/MainLayout';
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from '../store/store';
import { sessionRestored } from '../store/authSlice';
import { ProtectedRoute } from './ProtectedRoute';

function DashboardPage() {
	const { data: user, isLoading, isError } = useGetCurrentUserQuery();

	if (isLoading) {
		return <h1>Loading...</h1>;
	}

	if (isError || !user) {
		return <h1>Not authenticated</h1>;
	}

	return (
		<div>
			<h1>Dashboard</h1>
			<p>Welcome, {user.email}</p>
		</div>
	);
}

function PortfolioPage() {
	return <h1>Portfolio</h1>;
}

function AlertsPage() {
	return <h1>Alerts</h1>;
}

function AnalyticsPage() {
	return <h1>Analytics</h1>;
}

function LoginPage() {
	const navigate = useNavigate();
	const dispatch = useDispatch<AppDispatch>();
	const location = useLocation();

	const from = location.state?.from?.pathname || '/';
	const [login, { isLoading }] = useLoginMutation();

	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState('');

	async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
		event.preventDefault();

		setError('');

		try {
			await login({ email, password }).unwrap();
			dispatch(sessionRestored());
			navigate(from, { replace: true });
		} catch {
			setError('Invalid email or password');
		}
	}

	return (
		<div className="auth-page">
			<div className="auth-card">
				<h1>FinanceFlow</h1>
				<p>Sign in to your account</p>
				<form onSubmit={handleSubmit} className="auth-form">
					<label>
						Email
						<input
							type="email"
							value={email}
							onChange={(event) => setEmail(event.target.value)}
							placeholder="you@example.com"
							required
						/>
					</label>
					<label>
						Password
						<input
							type="password"
							value={password}
							onChange={(event) =>
								setPassword(event.target.value)
							}
							placeholder="••••••••"
							required
						/>
					</label>

					{error && <div className="auth-error">{error}</div>}

					<button type="submit" disabled={isLoading}>
						{isLoading ? 'Signing in...' : 'Sign in'}
					</button>
				</form>
				<p className="auth-footer">
					Don't have an account? <Link to="/register">Register</Link>
				</p>
			</div>
		</div>
	);
}

function RegisterPage() {
	return <h1>Register</h1>;
}

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
					</Route>
				</Route>
				<Route path="/login" element={<LoginPage />} />
				<Route path="/register" element={<RegisterPage />} />
				<Route path="*" element={<Navigate to="/" replace />} />
			</Routes>
		</BrowserRouter>
	);
}
