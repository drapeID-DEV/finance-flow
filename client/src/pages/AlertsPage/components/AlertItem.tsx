import type { Alert } from '../../../api/alertApi';
import { useDeleteAlertMutation } from '../../../api/alertApi';
import type { Instrument } from '../../../api/instrumentsApi';
import { Button } from '../../../shared/ui/Button/Button';

interface AlertItemProps {
	alert: Alert;
	instrument?: Instrument;
}

export function AlertItem({ alert, instrument }: AlertItemProps) {
	const [deleteAlert, { isLoading }] = useDeleteAlertMutation();

	const handleDelete = async () => {
		const confirmed = window.confirm(
			'Are you sure you want to delete this alert?'
		);

		if (!confirmed) {
			return;
		}

		try {
			await deleteAlert(alert.id).unwrap();
		} catch (error) {
			console.error('Failed to delete alert:', error);
			window.alert('Failed to delete alert. Please try again.');
		}
	};

	return (
		<article className="alert-card">
			<div className="alert-card-heading">
				<h3>{instrument?.code ?? `#${alert.instrument_id}`}</h3>
				<span className={`alert-status alert-status--${alert.status}`}>
					{alert.status === 'active' ? 'Active' : 'Triggered'}
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
			<Button
				type="button"
				variant="danger"
				disabled={isLoading}
				onClick={() => void handleDelete()}
			>
				{isLoading ? 'Deleting...' : 'Delete'}
			</Button>
		</article>
	);
}
