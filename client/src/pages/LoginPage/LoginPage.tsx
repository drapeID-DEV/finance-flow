import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
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
	const [showPassword, setShowPassword] = useState(false);
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
							autoComplete="email"
							required
						/>
					</label>
					<label>
						Password
						<div className="auth-password-wrapper">
							<input
								type={showPassword ? 'text' : 'password'}
								value={password}
								onChange={(event) =>
									setPassword(event.target.value)
								}
								placeholder="••••••••"
								autoComplete="current-password"
								required
							/>
							<button
								type="button"
								className="auth-password-toggle"
								onClick={() =>
									setShowPassword((visible) => !visible)
								}
								aria-label={
									showPassword
										? 'Hide password'
										: 'Show password'
								}
								aria-pressed={showPassword}
							>
								{showPassword ? (
									<EyeOff size={20} />
								) : (
									<Eye size={20} />
								)}
							</button>
						</div>
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
