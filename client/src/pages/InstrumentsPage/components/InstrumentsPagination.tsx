interface InstrumentsPaginationProps {
	page: number;
	totalPages: number;
	isFetching: boolean;
	onPageChange: (page: number) => void;
}

export function InstrumentsPagination({
	page,
	totalPages,
	isFetching,
	onPageChange
}: InstrumentsPaginationProps) {
	return (
		<div className="instruments-pagination">
			<button
				type="button"
				onClick={() => onPageChange(page - 1)}
				disabled={page <= 1 || isFetching}
			>
				Previous
			</button>
			<span>
				Page {page} of {Math.max(totalPages, 1)}
			</span>
			<button
				type="button"
				onClick={() => onPageChange(page + 1)}
				disabled={page >= totalPages || isFetching || totalPages === 0}
			>
				Next
			</button>
		</div>
	);
}
