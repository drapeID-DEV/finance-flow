import type { Instrument } from '../../../api/instrumentsApi';

interface InstrumentsTableProps {
	instruments: Instrument[];
}

export function InstrumentsTable({ instruments }: InstrumentsTableProps) {
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
								<span className="instrument-status">
									Active
								</span>
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	);
}
