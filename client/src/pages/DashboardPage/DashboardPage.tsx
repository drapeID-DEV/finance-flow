import { useGetCurrentUserQuery } from '../../api/authApi';
import { useGetDashboardSummaryQuery } from '../../api/dashboardApi';
import { Loader } from '../../shared/ui/Loader/Loader';
import { DashboardError } from './components/DashboardError';
import { WelcomeSection } from './components/WelcomeSection/WelcomeSection';
import './DashboardPage.css';

function StatCard({
	title,
	value,
	description
}: {
	title: string;
	value: string | number;
	description: string;
}) {
	return (
		<article className="dashboard-stat-card">
			<p className="dashboard-stat-title">{title}</p>
			<strong className="dashboard-stat-value">{value}</strong>
			<p className="dashboard-stat-description">{description}</p>
		</article>
	);
}

export default function DashboardPage() {
	const {
		data: user,
		isLoading: isUserLoading,
		isError: isUserError
	} = useGetCurrentUserQuery();

	const {
		data: summary,
		isLoading: isSummaryLoading,
		isError: isSummaryError,
		refetch
	} = useGetDashboardSummaryQuery();

	if (isUserLoading || isSummaryLoading) {
		return <Loader />;
	}

	if (isUserError || isSummaryError || !user || !summary) {
		return (
			<div className="dashboard-error">
				<DashboardError />
				<button type="button" onClick={() => void refetch()}>
					Try again
				</button>
			</div>
		);
	}

	const latestRateDate = summary.latest_rate_date
		? new Date(`${summary.latest_rate_date}T00:00:00`).toLocaleDateString()
		: 'No data yet';

	return (
		<div className="dashboard-page">
			<WelcomeSection email={user.email} />
			<div className="dashboard-stats-grid">
				{summary.role === 'admin' ? (
					<>
						<StatCard
							title="Total users"
							value={summary.total_users}
							description={`${summary.active_users} active`}
						/>
						<StatCard
							title="Instruments"
							value={summary.total_instruments}
							description={`${summary.active_instruments} active`}
						/>
						<StatCard
							title="Rate records"
							value={summary.total_rates}
							description="Historical rate data"
						/>
						<StatCard
							title="Alerts"
							value={summary.total_alerts}
							description="Created by all users"
						/>
					</>
				) : (
					<>
						<StatCard
							title="Portfolio instruments"
							value={summary.portfolio_items}
							description="In your portfolio"
						/>
						<StatCard
							title="Active alerts"
							value={summary.active_alerts}
							description="Waiting for a target rate"
						/>
						<StatCard
							title="Triggered alerts"
							value={summary.triggered_alerts}
							description="Target rate reached"
						/>
						<StatCard
							title="Available instruments"
							value={summary.active_instruments}
							description="Currencies and metals"
						/>
					</>
				)}
			</div>
			<section className="dashboard-rate-info">
				<h2>Exchange rate data</h2>
				<p>
					Latest available rate date:{' '}
					<strong>{latestRateDate}</strong>
				</p>
			</section>
		</div>
	);
}
