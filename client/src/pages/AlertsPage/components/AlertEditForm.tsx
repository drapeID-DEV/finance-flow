import { useState } from 'react';
import type { FormEvent } from 'react';
import {
	useUpdateAlertMutation,
	type Alert,
	type AlertDirection
} from '../../../api/alertApi';
import { Button } from '../../../shared/ui/Button/Button';

interface AlertEditFormProps {
	alert: Alert;
	onCancel: () => void;
	onSaved: () => void;
}

export function AlertEditForm({
	alert,
	onCancel,
	onSaved
}: AlertEditFormProps) {
	const [direction, setDirection] = useState<AlertDirection>(alert.direction);
	const [value, setValue] = useState(String(alert.value));
	const [errorMessage, setErrorMessage] = useState('');

	const [updateAlert, { isLoading: isUpdating }] = useUpdateAlertMutation();

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
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

			onSaved();
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

	return (
		<form className="alert-edit-form" onSubmit={handleSubmit}>
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
						setDirection(event.target.value as AlertDirection)
					}
					disabled={isUpdating}
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
					onChange={(event) => setValue(event.target.value)}
					disabled={isUpdating}
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
					onClick={onCancel}
				>
					Cancel
				</Button>
			</div>
		</form>
	);
}
