import { useGetInstrumentsQuery } from '../api/instrumentsApi';
import './InstrumentsPage.css';

export function InstrumentsPage() {
	const {
		data: instruments,
		isLoading,
		isError,
		refetch
	} = useGetInstrumentsQuery();

	if (isLoading) {
		return <p className="instruments-message">Loading instruments...</p>;
	}

	if (isError) {
		return (
			<div className="instruments-message">
				<p>Failed to load instruments.</p>
				<button onClick={() => refetch()}>Try again</button>
			</div>
		);
	}

	if (!instruments?.length) {
		return (
			<div className="instruments-page">
				<h1>Currencies & Metals</h1>
				<p className="instruments-message">
					No active instruments found.
				</p>
			</div>
		);
	}

	return (
		<div className="instruments-page">
			<div className="instruments-heading">
				<div>
					<h1>Currencies & Metals</h1>
					<p>Browse available financial instruments.</p>
				</div>
				<span className="instruments-count">
					{instruments.length} instruments
				</span>
			</div>
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
		</div>
	);
}
