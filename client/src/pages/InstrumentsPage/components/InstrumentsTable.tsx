import type { Instrument } from '../../../api/instrumentsApi';

interface InstrumentsTableProps {
	instruments: Instrument[];
	isAdmin?: boolean;
	isUpdating?: boolean;
	onToggleStatus?: (instrument: Instrument) => void;
}

export function InstrumentsTable({
	instruments,
	isAdmin = false,
	isUpdating = false,
	onToggleStatus
}: InstrumentsTableProps) {
	if (instruments.length === 0) {
		return (
			<p className="instruments-message">
				No instruments match your filters.
			</p>
		);
	}

	return (
		<div className="instruments-table-wrapper">
			<table className="instruments-table">
				<thead>
					<tr>
						<th>Code</th>
						<th>Name</th>
						<th>Current rate</th>
						<th>Daily change</th>
						<th>Type</th>
						<th>Status</th>
						{isAdmin && <th>Action</th>}
					</tr>
				</thead>
				<tbody>
					{instruments.map((instrument) => (
						<tr key={instrument.code}>
							<td className="instrument-code">
								{instrument.code}
							</td>
							<td>{instrument.name}</td>
							<td>
								{instrument.current_rate !== null &&
								instrument.current_rate !== undefined ? (
									<div>
										<strong>
											{Number(
												instrument.current_rate
											).toLocaleString('en-US', {
												maximumFractionDigits: 8
											})}
										</strong>
										<div className="instrument-rate-date">
											{instrument.rate_date
												? new Date(
														`${instrument.rate_date}T00:00:00`
													).toLocaleDateString(
														'uk-UA'
													)
												: ''}
										</div>
									</div>
								) : (
									<span>—</span>
								)}
							</td>
							<td>
								{instrument.daily_change !== null &&
								instrument.daily_change_percent !== null ? (
									<div>
										<strong>
											{Number(instrument.daily_change) > 0
												? '+'
												: ''}
											{Number(
												instrument.daily_change
											).toLocaleString('en-US', {
												maximumFractionDigits: 8
											})}
										</strong>
										<div className="instrument-rate-date">
											{Number(
												instrument.daily_change_percent
											) > 0
												? '+'
												: ''}
											{Number(
												instrument.daily_change_percent
											).toFixed(2)}
											%
										</div>
									</div>
								) : (
									<span>—</span>
								)}
							</td>
							<td>{instrument.type}</td>
							<td>
								<span
									className={
										instrument.is_active
											? 'instrument-status'
											: 'instrument-status instrument-status-inactive'
									}
								>
									{instrument.is_active
										? 'Active'
										: 'Disabled'}
								</span>
							</td>
							{isAdmin && (
								<td>
									<button
										type="button"
										className="instrument-toggle-button"
										disabled={isUpdating}
										onClick={() =>
											onToggleStatus?.(instrument)
										}
									>
										{instrument.is_active
											? 'Disable'
											: 'Enable'}
									</button>
								</td>
							)}
						</tr>
					))}
				</tbody>
			</table>
		</div>
	);
}
