import { useGetCurrentUserQuery } from '../../api/authApi';
import { Loader } from '../../shared/ui/Loader/Loader';

export default function DashboardPage() {
	const { data: user, isLoading, isError } = useGetCurrentUserQuery();

	if (isLoading) {
		return <Loader />;
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
