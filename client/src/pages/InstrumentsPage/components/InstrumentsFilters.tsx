import { Button } from '../../../shared/ui/Button/Button';

interface InstrumentsFiltersProps {
	search: string;
	type: '' | 'currency' | 'metal';
	onSearchChange: (value: string) => void;
	onTypeChange: (value: '' | 'currency' | 'metal') => void;
	onReset: () => void;
}

export function InstrumentsFilters({
	search,
	type,
	onSearchChange,
	onTypeChange,
	onReset
}: InstrumentsFiltersProps) {
	return (
		<div className="instruments-filters">
			<input
				type="search"
				placeholder="Search by code or name..."
				value={search}
				onChange={(event) => onSearchChange(event.target.value)}
				aria-label="Search instruments"
			/>
			<select
				value={type}
				onChange={(event) =>
					onTypeChange(
						event.target.value as '' | 'currency' | 'metal'
					)
				}
				aria-label="Filter by instrument type"
			>
				<option value="">All types</option>
				<option value="currency">Currencies</option>
				<option value="metal">Metals</option>
			</select>
			<Button
				variant="secondary"
				onClick={onReset}
				disabled={!search && !type}
			>
				Reset
			</Button>
		</div>
	);
}
