import { useGetCurrentUserQuery } from '../../api/authApi';
import { Loader } from '../../shared/ui/Loader/Loader';
import { DashboardError } from './components/DashboardError';
import { WelcomeSection } from './components/WelcomeSection/WelcomeSection';
import './DashboardPage.css';

export default function DashboardPage() {
	const { data: user, isLoading, isError } = useGetCurrentUserQuery();

	if (isLoading) {
		return <Loader />;
	}

	if (isError || !user) {
		return <DashboardError />;
	}

	return (
		<div className="dashboard-page">
			<WelcomeSection email={user.email} />
		</div>
	);
}
