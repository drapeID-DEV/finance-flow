import { InstrumentsFilters } from './components/InstrumentsFilters';
import { InstrumentsTable } from './components/InstrumentsTable';
import { InstrumentsPagination } from './components/InstrumentsPagination';
import { useInstrumentsPage } from './hooks/useInstrumentsPage';
import './InstrumentsPage.css';
import { InstrumentStatusModal } from './components/InstrumentStatusModal';

export function InstrumentsPage() {
	const {
		isAdmin,
		page,
		setPage,
		search,
		type,
		actionError,
		instrumentToToggle,
		setInstrumentToToggle,
		data,
		isLoading,
		isFetching,
		isError,
		isUpdating,
		refetch,
		handleSearchChange,
		handleTypeChange,
		handleReset,
		handleToggleStatus
	} = useInstrumentsPage();

	if (isLoading) {
		return <p className="instruments-message">Loading instruments...</p>;
	}

	if (isError || !data) {
		return (
			<div className="instruments-message">
				<p>Failed to load instruments.</p>
				<button type="button" onClick={() => void refetch()}>
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
					<h1>
						{isAdmin
							? 'Instrument Management'
							: 'Currencies & Metals'}
					</h1>
					<p>
						{isAdmin
							? 'Manage available currencies and precious metals.'
							: 'Browse available financial instruments.'}
					</p>
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
			{actionError && (
				<p className="instruments-action-error" role="alert">
					{actionError}
				</p>
			)}
			<InstrumentsTable
				instruments={data.items}
				isAdmin={isAdmin}
				isUpdating={isUpdating}
				onToggleStatus={setInstrumentToToggle}
			/>
			<InstrumentsPagination
				page={page}
				totalPages={totalPages}
				isFetching={isFetching}
				onPageChange={setPage}
			/>
			{isFetching && (
				<p className="instruments-message">Updating instruments...</p>
			)}
			<InstrumentStatusModal
				instrument={instrumentToToggle}
				isLoading={isUpdating}
				onClose={() => setInstrumentToToggle(null)}
				onConfirm={() => {
					if (instrumentToToggle) {
						void handleToggleStatus(instrumentToToggle);
					}
				}}
			/>
		</div>
	);
}
