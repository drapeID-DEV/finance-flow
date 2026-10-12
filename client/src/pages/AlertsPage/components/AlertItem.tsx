import { useCallback, useState } from 'react';
import type { Alert } from '../../../api/alertApi';
import { useDeleteAlertMutation } from '../../../api/alertApi';
import type { Instrument } from '../../../api/instrumentsApi';
import { Button } from '../../../shared/ui/Button/Button';
import { DeleteAlertModal } from './DeleteAlertModal/DeleteAlertModal';

interface AlertItemProps {
	alert: Alert;
	instrument?: Instrument;
}

export function AlertItem({ alert, instrument }: AlertItemProps) {
	const [isModalOpen, setIsModalOpen] = useState(false);
	const [deleteAlert, { isLoading: isDeleting }] = useDeleteAlertMutation();

	const closeModal = useCallback(() => {
		if (!isDeleting) {
			setIsModalOpen(false);
		}
	}, [isDeleting]);

	const handleDelete = async () => {
		try {
			await deleteAlert(alert.id).unwrap();
			setIsModalOpen(false);
		} catch (error) {
			console.error('Failed to delete alert:', error);
			window.alert('Failed to delete alert. Please try again.');
		}
	};

	return (
		<>
			<article className="alert-card">
				<div className="alert-card-heading">
					<h3>{instrument?.code ?? `#${alert.instrument_id}`}</h3>

					<span
						className={`alert-status alert-status--${alert.status}`}
					>
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
				{alert.status === 'triggered' && alert.triggered_at && (
					<p className="alert-triggered-at">
						Triggered:{' '}
						{new Date(alert.triggered_at).toLocaleString()}
					</p>
				)}
				<Button
					type="button"
					variant="danger"
					onClick={() => setIsModalOpen(true)}
				>
					Delete
				</Button>
			</article>
			<DeleteAlertModal
				isOpen={isModalOpen}
				isDeleting={isDeleting}
				alertName={instrument?.code ?? `#${alert.instrument_id}`}
				onClose={closeModal}
				onConfirm={() => void handleDelete()}
			/>
		</>
	);
}
