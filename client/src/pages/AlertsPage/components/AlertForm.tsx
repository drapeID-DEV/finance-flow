import { useState } from 'react';
import type { FormEvent } from 'react';
import type { Instrument } from '../../../api/instrumentsApi';
import type { AlertDirection } from '../../../api/alertApi';
import { Button } from '../../../shared/ui/Button/Button';

interface AlertFormProps {
	instruments: Instrument[];
	isSubmitting: boolean;
	onSubmit: (data: {
		instrument_id: number;
		direction: AlertDirection;
		value: number;
	}) => Promise<void>;
}

export function AlertForm({
	instruments,
	isSubmitting,
	onSubmit
}: AlertFormProps) {
	const [instrumentId, setInstrumentId] = useState('');
	const [direction, setDirection] = useState<AlertDirection>('above');
	const [value, setValue] = useState('');
	const [errorMessage, setErrorMessage] = useState('');

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setErrorMessage('');

		const numericValue = Number(value);
		const numericInstrumentId = Number(instrumentId);

		if (
			!instrumentId ||
			!Number.isInteger(numericInstrumentId) ||
			!Number.isFinite(numericValue) ||
			numericValue <= 0
		) {
			return;
		}

		try {
			await onSubmit({
				instrument_id: numericInstrumentId,
				direction,
				value: numericValue
			});

			setInstrumentId('');
			setDirection('above');
			setValue('');
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
					'An alert with this instrument, condition, and target rate already exists.'
				);
			} else {
				setErrorMessage(
					apiError.data?.detail ??
						'Failed to create alert. Please try again.'
				);
			}
		}
	};

	return (
		<form className="alert-form" onSubmit={handleSubmit}>
			<h2>Create price alert</h2>
			{errorMessage && (
				<p className="alert-form-error" role="alert">
					{errorMessage}
				</p>
			)}
			<div className="alert-form-fields">
				<label>
					Instrument
					<select
						value={instrumentId}
						onChange={(event) =>
							setInstrumentId(event.target.value)
						}
						required
					>
						<option value="">Select instrument</option>
						{instruments.map((instrument) => (
							<option key={instrument.id} value={instrument.id}>
								{instrument.code} — {instrument.name}
							</option>
						))}
					</select>
				</label>
				<label>
					Condition
					<select
						value={direction}
						onChange={(event) =>
							setDirection(event.target.value as AlertDirection)
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
						onChange={(event) => setValue(event.target.value)}
						placeholder="Enter target rate"
						required
					/>
				</label>
				<Button
					type="submit"
					disabled={isSubmitting || instruments.length === 0}
				>
					{isSubmitting ? 'Creating...' : 'Create alert'}
				</Button>
			</div>
		</form>
	);
}
