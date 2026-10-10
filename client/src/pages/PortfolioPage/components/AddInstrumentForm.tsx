import { Button } from '../../../shared/ui/Button/Button';

interface InstrumentOption {
	id: number;
	code: string;
	name: string;
}

interface AddInstrumentFormProps {
	instruments: InstrumentOption[];
	selectedInstrumentId: string;
	quantity: string;
	isBusy: boolean;
	isAdding: boolean;
	onInstrumentChange: (value: string) => void;
	onQuantityChange: (value: string) => void;
	onSubmit: () => void;
}

export function AddInstrumentForm({
	instruments,
	selectedInstrumentId,
	quantity,
	isBusy,
	isAdding,
	onInstrumentChange,
	onQuantityChange,
	onSubmit
}: AddInstrumentFormProps) {
	return (
		<form
			className="portfolio-add-form"
			onSubmit={(event) => {
				event.preventDefault();
				onSubmit();
			}}
		>
			<h2>Add instrument</h2>
			<div className="portfolio-add-fields">
				<select
					value={selectedInstrumentId}
					onChange={(event) => onInstrumentChange(event.target.value)}
					aria-label="Select instrument"
					required
				>
					<option value="">Select an instrument</option>
					{instruments.map((instrument) => (
						<option key={instrument.id} value={instrument.id}>
							{instrument.code} — {instrument.name}
						</option>
					))}
				</select>
				<input
					type="number"
					min="0.000001"
					step="any"
					value={quantity}
					onChange={(event) => onQuantityChange(event.target.value)}
					aria-label="Initial quantity"
					required
				/>
				<Button
					type="submit"
					disabled={isBusy || instruments.length === 0}
				>
					{isAdding ? 'Adding...' : 'Add to portfolio'}
				</Button>
			</div>
			{instruments.length === 0 && (
				<p className="portfolio-message">
					All loaded active instruments are already in your portfolio.
				</p>
			)}
		</form>
	);
}
