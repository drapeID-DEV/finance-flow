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
