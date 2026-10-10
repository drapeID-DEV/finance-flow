import { Link } from 'react-router-dom';
import { useGetCurrentUserQuery, useLogoutMutation } from '../../api/authApi';
import './Header.css';
import { Button } from '../../shared/ui/Button/Button';

export function Header() {
	const { data: user, isLoading, isError } = useGetCurrentUserQuery();
	const [logout, { isLoading: isLoggingOut }] = useLogoutMutation();

	const handleLogout = async () => {
		try {
			await logout().unwrap();
		} catch (error) {
			console.error('Logout failed:', error);
		}
	};

	return (
		<header className="header">
			<h2>FinanceFlow</h2>
			<div className="header-actions">
				{!isLoading && !isError && user ? (
					<div className="logged-actions">
						<span>{user.email}</span>
						<Button
							variant="danger"
							onClick={handleLogout}
							disabled={isLoggingOut}
						>
							{isLoggingOut ? 'Logging out...' : 'Logout'}
						</Button>
					</div>
				) : (
					<Link to="/login">Login</Link>
				)}
			</div>
		</header>
	);
}
