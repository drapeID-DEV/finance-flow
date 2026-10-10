import { useState } from 'react';
import { useGetInstrumentsQuery } from '../../api/instrumentsApi';
import './InstrumentsPage.css';

const PAGE_SIZE = 20;

export function InstrumentsPage() {
	const [page, setPage] = useState(1);
	const [search, setSearch] = useState('');
	const [type, setType] = useState<'' | 'currency' | 'metal'>('');

	const { data, isLoading, isFetching, isError, refetch } =
		useGetInstrumentsQuery({
			page,
			page_size: PAGE_SIZE,
			search,
			...(type ? { type } : {})
		});

	const handleSearchChange = (value: string) => {
		setSearch(value);
		setPage(1);
	};

	const handleTypeChange = (value: '' | 'currency' | 'metal') => {
		setType(value);
		setPage(1);
	};

	if (isLoading) {
		return <p className="instruments-message">Loading instruments...</p>;
	}

	if (isError || !data) {
		return (
			<div className="instruments-message">
				<p>Failed to load instruments.</p>
				<button onClick={() => refetch()}>Try again</button>
			</div>
		);
	}

	const instruments = data.items;
	const totalPages = Math.ceil(data.total / data.page_size);

	return (
		<div className="instruments-page">
			<div className="instruments-heading">
				<div>
					<h1>Currencies & Metals</h1>
					<p>Browse available financial instruments.</p>
				</div>
				<span className="instruments-count">
					{data.total} instruments
				</span>
			</div>
			<div className="instruments-filters">
				<input
					type="search"
					placeholder="Search by code or name..."
					value={search}
					onChange={(event) => handleSearchChange(event.target.value)}
					aria-label="Search instruments"
				/>
				<select
					value={type}
					onChange={(event) =>
						handleTypeChange(
							event.target.value as '' | 'currency' | 'metal'
						)
					}
					aria-label="Filter by instrument type"
				>
					<option value="">All types</option>
					<option value="currency">Currencies</option>
					<option value="metal">Metals</option>
				</select>
				<button
					type="button"
					onClick={() => {
						setSearch('');
						setType('');
						setPage(1);
					}}
					disabled={!search && !type}
				>
					Reset
				</button>
			</div>
			{instruments.length === 0 ? (
				<p className="instruments-message">
					No instruments match your filters.
				</p>
			) : (
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
			)}
			<div className="instruments-pagination">
				<button
					type="button"
					onClick={() => setPage((current) => current - 1)}
					disabled={page === 1 || isFetching}
				>
					Previous
				</button>
				<span>
					Page {page} of {Math.max(totalPages, 1)}
				</span>
				<button
					type="button"
					onClick={() => setPage((current) => current + 1)}
					disabled={
						page >= totalPages || isFetching || totalPages === 0
					}
				>
					Next
				</button>
			</div>
			{isFetching && !isLoading && (
				<p className="instruments-message">Updating instruments...</p>
			)}
		</div>
	);
}
