import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import { useState } from 'react';
import { useRegisterMutation } from '../../api/authApi';
import '../AuthPage.css';

export default function RegisterPage() {
	const navigate = useNavigate();
	const [register, { isLoading }] = useRegisterMutation();

	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [confirmPassword, setConfirmPassword] = useState('');
	const [showPassword, setShowPassword] = useState(false);
	const [showConfirmPassword, setShowConfirmPassword] = useState(false);
	const [error, setError] = useState('');
	const [success, setSuccess] = useState('');

	async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
		event.preventDefault();
		setError('');
		setSuccess('');

		if (password.length < 8) {
			setError('Password must contain at least 8 characters');
			return;
		}

		if (password !== confirmPassword) {
			setError('Passwords do not match');
			return;
		}

		try {
			await register({ email, password }).unwrap();
			setSuccess('Account created successfully. Redirecting to login...');

			setTimeout(() => {
				navigate('/login', { replace: true });
			}, 1000);
		} catch (err: unknown) {
			const message =
				typeof err === 'object' &&
				err !== null &&
				'data' in err &&
				typeof err.data === 'object' &&
				err.data !== null &&
				'detail' in err.data &&
				typeof err.data.detail === 'string'
					? err.data.detail
					: 'Registration failed. Please try again.';

			setError(message);
		}
	}

	return (
		<div className="auth-page">
			<div className="auth-card">
				<h1>FinanceFlow</h1>
				<p>Create your account</p>
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
								placeholder="At least 8 characters"
								autoComplete="new-password"
								minLength={8}
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
					<label>
						Confirm password
						<div className="auth-password-wrapper">
							<input
								type={showConfirmPassword ? 'text' : 'password'}
								value={confirmPassword}
								onChange={(event) =>
									setConfirmPassword(event.target.value)
								}
								placeholder="Repeat your password"
								autoComplete="new-password"
								minLength={8}
								required
							/>
							<button
								type="button"
								className="auth-password-toggle"
								onClick={() =>
									setShowConfirmPassword(
										(visible) => !visible
									)
								}
								aria-label={
									showConfirmPassword
										? 'Hide confirmation password'
										: 'Show confirmation password'
								}
								aria-pressed={showConfirmPassword}
							>
								{showConfirmPassword ? (
									<EyeOff size={20} />
								) : (
									<Eye size={20} />
								)}
							</button>
						</div>
					</label>
					{error && <div className="auth-error">{error}</div>}
					{success && <p role="status">{success}</p>}
					<button type="submit" disabled={isLoading}>
						{isLoading ? 'Creating account...' : 'Create account'}
					</button>
				</form>
				<p className="auth-footer">
					Already have an account? <Link to="/login">Sign in</Link>
				</p>
			</div>
		</div>
	);
}
