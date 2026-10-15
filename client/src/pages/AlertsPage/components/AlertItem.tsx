import { useCallback, useState } from 'react';
import type { FormEvent } from 'react';
import type { Alert, AlertDirection } from '../../../api/alertApi';
import {
	useDeleteAlertMutation,
	useUpdateAlertMutation
} from '../../../api/alertApi';
import type { Instrument } from '../../../api/instrumentsApi';
import { Button } from '../../../shared/ui/Button/Button';
import { ConfirmModal } from '../../../shared/ui/ConfirmModal/ConfirmModal';

interface AlertItemProps {
	alert: Alert;
	instrument?: Instrument;
}

export function AlertItem({ alert, instrument }: AlertItemProps) {
	const [isModalOpen, setIsModalOpen] = useState(false);
	const [isEditing, setIsEditing] = useState(false);
	const [direction, setDirection] = useState<AlertDirection>(alert.direction);
	const [value, setValue] = useState(String(alert.value));
	const [errorMessage, setErrorMessage] = useState('');

	const [deleteAlert, { isLoading: isDeleting }] = useDeleteAlertMutation();
	const [updateAlert, { isLoading: isUpdating }] = useUpdateAlertMutation();

	const closeModal = useCallback(() => {
		if (!isDeleting) {
			setIsModalOpen(false);
		}
	}, [isDeleting]);

	const startEditing = () => {
		setDirection(alert.direction);
		setValue(String(alert.value));
		setErrorMessage('');
		setIsEditing(true);
	};

	const handleUpdate = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setErrorMessage('');

		const numericValue = Number(value);

		if (!Number.isFinite(numericValue) || numericValue <= 0) {
			setErrorMessage('Target rate must be greater than zero.');
			return;
		}

		try {
			await updateAlert({
				alertId: alert.id,
				body: {
					direction,
					value: numericValue
				}
			}).unwrap();

			setIsEditing(false);
		} catch (error) {
			const apiError = error as {
				status?: number | string;
				data?: { detail?: string };
			};

			if (
				apiError.status === 409 ||
				apiError.data?.detail === 'Alert already exists'
			) {
				setErrorMessage(
					'An alert with this condition and target rate already exists.'
				);
			} else {
				setErrorMessage(
					apiError.data?.detail ??
						'Failed to update alert. Please try again.'
				);
			}
		}
	};

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
				{isEditing ? (
					<form className="alert-edit-form" onSubmit={handleUpdate}>
						{errorMessage && (
							<p className="alert-form-error" role="alert">
								{errorMessage}
							</p>
						)}
						<label>
							Condition
							<select
								value={direction}
								onChange={(event) =>
									setDirection(
										event.target.value as AlertDirection
									)
								}
							>
								<option value="above">Rate goes above</option>
								<option value="below">Rate goes below</option>
							</select>
						</label>
						<label>
							Target rate (UAH)
							<input
								type="number"
								min="0.00000001"
								step="any"
								value={value}
								onChange={(event) =>
									setValue(event.target.value)
								}
								required
							/>
						</label>
						<div className="alert-actions">
							<Button type="submit" disabled={isUpdating}>
								{isUpdating ? 'Saving...' : 'Save'}
							</Button>
							<Button
								type="button"
								variant="secondary"
								disabled={isUpdating}
								onClick={() => {
									setIsEditing(false);
									setErrorMessage('');
								}}
							>
								Cancel
							</Button>
						</div>
					</form>
				) : (
					<>
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
						<div className="alert-actions">
							<Button type="button" onClick={startEditing}>
								Edit
							</Button>
							<Button
								type="button"
								variant="danger"
								onClick={() => setIsModalOpen(true)}
							>
								Delete
							</Button>
						</div>
					</>
				)}
			</article>
			<ConfirmModal
				isOpen={isModalOpen}
				isLoading={isDeleting}
				title="Delete price alert?"
				description={
					<>
						Are you sure you want to delete the alert for{' '}
						<strong>
							{instrument?.code ?? `#${alert.instrument_id}`}
						</strong>
						? This action cannot be undone.
					</>
				}
				confirmText="Delete alert"
				variant="danger"
				onClose={closeModal}
				onConfirm={() => void handleDelete()}
			/>
		</>
	);
}
