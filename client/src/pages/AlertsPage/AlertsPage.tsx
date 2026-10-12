import { useGetInstrumentsQuery } from '../../api/instrumentsApi';
import { useCreateAlertMutation, useGetAlertsQuery } from '../../api/alertApi';
import { AlertForm } from './components/AlertForm';
import { AlertsList } from './components/AlertsList';
import './AlertsPage.css';

export default function AlertsPage() {
	const {
		data: alerts,
		isLoading: isAlertsLoading,
		isError: isAlertsError,
		refetch
	} = useGetAlertsQuery(undefined, {
		pollingInterval: 30_000,
		refetchOnFocus: true,
		refetchOnReconnect: true
	});

	const {
		data: instrumentsData,
		isLoading: isInstrumentsLoading,
		isError: isInstrumentsError
	} = useGetInstrumentsQuery({
		page: 1,
		page_size: 100
	});

	const [createAlert, { isLoading: isCreating }] = useCreateAlertMutation();

	const instruments = (instrumentsData?.items ?? []).filter(
		(instrument) => instrument.is_active
	);

	const handleCreate = async (data: {
		instrument_id: number;
		direction: 'above' | 'below';
		value: number;
	}) => {
		try {
			await createAlert(data).unwrap();
		} catch (error) {
			console.error('Failed to create alert:', error);
			throw error;
		}
	};

	if (isAlertsLoading || isInstrumentsLoading) {
		return <p className="alerts-message">Loading alerts...</p>;
	}

	if (isAlertsError || isInstrumentsError || !alerts || !instrumentsData) {
		return (
			<div className="alerts-message">
				<p>Failed to load alerts.</p>
				<button type="button" onClick={() => void refetch()}>
					Try again
				</button>
			</div>
		);
	}

	return (
		<section className="alerts-page">
			<header className="alerts-heading">
				<h1>Price alerts</h1>
				<p>Get notified when an exchange rate reaches your target.</p>
			</header>
			<AlertForm
				instruments={instruments}
				isSubmitting={isCreating}
				onSubmit={handleCreate}
			/>
			<AlertsList alerts={alerts} instruments={instruments} />
		</section>
	);
}
