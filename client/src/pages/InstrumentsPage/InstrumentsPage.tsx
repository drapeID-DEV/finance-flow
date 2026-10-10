import { useState } from 'react';
import { useGetInstrumentsQuery } from '../../api/instrumentsApi';
import { InstrumentsFilters } from './components/InstrumentsFilters';
import { InstrumentsTable } from './components/InstrumentsTable';
import { InstrumentsPagination } from './components/InstrumentsPagination';
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

	const handleReset = () => {
		setSearch('');
		setType('');
		setPage(1);
	};

	if (isLoading) {
		return <p className="instruments-message">Loading instruments...</p>;
	}

	if (isError || !data) {
		return (
			<div className="instruments-message">
				<p>Failed to load instruments.</p>
				<button type="button" onClick={() => refetch()}>
					Try again
				</button>
			</div>
		);
	}

	const totalPages = Math.ceil(data.total / data.page_size);

	return (
		<div className="instruments-page">
			<div className="instruments-heading">
				<div>
					<h1>Currencies &amp; Metals</h1>
					<p>Browse available financial instruments.</p>
				</div>
				<span className="instruments-count">
					{data.total} instruments
				</span>
			</div>
			<InstrumentsFilters
				search={search}
				type={type}
				onSearchChange={handleSearchChange}
				onTypeChange={handleTypeChange}
				onReset={handleReset}
			/>
			<InstrumentsTable instruments={data.items} />
			<InstrumentsPagination
				page={page}
				totalPages={totalPages}
				isFetching={isFetching}
				onPageChange={setPage}
			/>
			{isFetching && (
				<p className="instruments-message">Updating instruments...</p>
			)}
		</div>
	);
}
