import { Button } from '../../../shared/ui/Button/Button';
import type { PortfolioItem } from '../../../api/portfolioApi';

interface PortfolioInstrument {
	id: number;
	code: string;
	name: string;
	type: string;
}

interface PortfolioTableProps {
	items: PortfolioItem[];
	instruments: PortfolioInstrument[];
	quantities: Record<number, string>;
	totalValue: number | string;
	baseCurrency: string;
	isBusy: boolean;
	onQuantityChange: (instrumentId: number, value: string) => void;
	onUpdate: (instrumentId: number) => void;
	onDelete: (instrumentId: number) => void;
}

export function PortfolioTable({
	items,
	instruments,
	quantities,
	totalValue,
	baseCurrency,
	isBusy,
	onQuantityChange,
	onUpdate,
	onDelete
}: PortfolioTableProps) {
	const getInstrument = (instrumentId: number) =>
		instruments.find((instrument) => instrument.id === instrumentId);

	const formattedValue = (value: number | string) =>
		Number(value).toLocaleString(undefined, {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		});

	return (
		<div className="portfolio-table-wrapper">
			<table className="portfolio-table">
				<thead>
					<tr>
						<th>Code</th>
						<th>Name</th>
						<th>Type</th>
						<th>Quantity</th>
						<th>Current rate</th>
						<th>Value ({baseCurrency})</th>
						<th>Portfolio share</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{items.map((item) => {
						const instrument = getInstrument(item.instrument_id);
						const code =
							instrument?.code ?? String(item.instrument_id);

						const share =
							item.value != null && Number(totalValue) > 0
								? (
										(Number(item.value) /
											Number(totalValue)) *
										100
									).toFixed(2)
								: null;

						return (
							<tr key={item.instrument_id}>
								<td>
									{instrument?.code ??
										`#${item.instrument_id}`}
								</td>
								<td>
									{instrument?.name ?? 'Unknown instrument'}
								</td>
								<td>{instrument?.type ?? '—'}</td>
								<td>
									<input
										className="portfolio-quantity"
										type="number"
										min="0.000001"
										step="any"
										aria-label={`Quantity for ${code}`}
										value={
											quantities[item.instrument_id] ??
											String(item.quantity)
										}
										onChange={(event) =>
											onQuantityChange(
												item.instrument_id,
												event.target.value
											)
										}
									/>
								</td>
								<td>
									{item.current_rate != null &&
									item.rate_unit != null
										? `${Number(item.current_rate).toLocaleString()} / ${item.rate_unit}`
										: '—'}
								</td>
								<td>
									{item.value != null
										? `${formattedValue(item.value)} ${baseCurrency}`
										: '—'}
								</td>
								<td>{share != null ? `${share}%` : '—'}</td>
								<td className="portfolio-actions">
									<Button
										variant="primary"
										onClick={() =>
											onUpdate(item.instrument_id)
										}
										disabled={isBusy}
									>
										Save
									</Button>
									<Button
										variant="danger"
										onClick={() =>
											onDelete(item.instrument_id)
										}
										disabled={isBusy}
									>
										Remove
									</Button>
								</td>
							</tr>
						);
					})}
				</tbody>
			</table>
		</div>
	);
}
