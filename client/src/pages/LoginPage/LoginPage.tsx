import { Link, useLocation, useNavigate } from 'react-router-dom';
import { sessionRestored } from '../../store/authSlice';
import { useState } from 'react';
import { useLoginMutation } from '../../api/authApi';
import { useDispatch } from 'react-redux';
import type { AppDispatch } from '../../store/store';
import '../AuthPage.css';

export default function LoginPage() {
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
