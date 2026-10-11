import type { Alert } from '../../../api/alertApi';
import type { Instrument } from '../../../api/instrumentsApi';
import { AlertItem } from './AlertItem';

interface AlertsListProps {
	alerts: Alert[];
	instruments: Instrument[];
}

export function AlertsList({ alerts, instruments }: AlertsListProps) {
	if (alerts.length === 0) {
		return (
			<div className="alerts-empty">
				<h2>No alerts yet</h2>
				<p>Create an alert to track your target exchange rate.</p>
			</div>
		);
	}

	return (
		<section className="alerts-list">
			<h2>My alerts</h2>
			<div className="alerts-grid">
				{alerts.map((alert) => {
					const instrument = instruments.find(
						(item) => item.id === alert.instrument_id
					);
					return (
						<AlertItem
							key={alert.id}
							alert={alert}
							instrument={instrument}
						/>
					);
				})}
			</div>
		</section>
	);
}
