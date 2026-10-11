import type { Alert } from '../../../api/alertApi';
import type { Instrument } from '../../../api/instrumentsApi';

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
						<article className="alert-card" key={alert.id}>
							<div className="alert-card-heading">
								<h3>
									{instrument?.code ??
										`#${alert.instrument_id}`}
								</h3>
								<span
									className={`alert-status alert-status--${alert.status}`}
								>
									{alert.status === 'active'
										? 'Active'
										: 'Triggered'}
								</span>
							</div>
							<p>{instrument?.name ?? 'Unknown instrument'}</p>
							<p className="alert-condition">
								Rate {alert.direction === 'above' ? '≥' : '≤'}{' '}
								{Number(alert.value).toLocaleString(undefined, {
									maximumFractionDigits: 8
								})}{' '}
								UAH
							</p>
						</article>
					);
				})}
			</div>
		</section>
	);
}
