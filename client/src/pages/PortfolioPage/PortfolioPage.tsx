import { useState } from 'react';
import { useGetInstrumentsQuery } from '../../api/instrumentsApi';
import {
	useGetPortfolioQuery,
	useAddPortfolioItemMutation,
	useUpdatePortfolioItemMutation,
	useDeletePortfolioItemMutation
} from '../../api/portfolioApi';
import './PortfolioPage.css';

const INSTRUMENTS_PAGE_SIZE = 100;

export default function PortfolioPage() {
	const [quantities, setQuantities] = useState<Record<number, string>>({});
	const [selectedInstrumentId, setSelectedInstrumentId] = useState('');
	const [newQuantity, setNewQuantity] = useState('1');
	const [errorMessage, setErrorMessage] = useState('');
	const [successMessage, setSuccessMessage] = useState('');

	const {
		data: portfolio,
		isLoading: isPortfolioLoading,
		isError: isPortfolioError,
		refetch
	} = useGetPortfolioQuery();

	const {
		data: instrumentsData,
		isLoading: isInstrumentsLoading,
		isError: isInstrumentsError
	} = useGetInstrumentsQuery({
		page: 1,
		page_size: INSTRUMENTS_PAGE_SIZE
	});

	const [addItem, { isLoading: isAdding }] = useAddPortfolioItemMutation();
	const [updateItem, { isLoading: isUpdating }] =
		useUpdatePortfolioItemMutation();
	const [deleteItem, { isLoading: isDeleting }] =
		useDeletePortfolioItemMutation();

	const instruments = (instrumentsData?.items ?? []).filter(
		(instrument) => instrument.is_active
	);

	const getInstrument = (instrumentId: number) =>
		instruments.find((instrument) => instrument.id === instrumentId);

	const handleAdd = async () => {
		const instrumentId = Number(selectedInstrumentId);
		const quantity = Number(newQuantity);

		if (!selectedInstrumentId || !Number.isInteger(instrumentId)) {
			setErrorMessage('Select an instrument.');
			return;
		}

		if (!Number.isFinite(quantity) || quantity <= 0) {
			setErrorMessage('Quantity must be greater than zero.');
			return;
		}

		setErrorMessage('');
		setSuccessMessage('');

		try {
			await addItem({
				instrument_id: instrumentId,
				quantity
			}).unwrap();

			setSelectedInstrumentId('');
			setNewQuantity('1');
			setSuccessMessage('Instrument added to your portfolio.');
		} catch {
			setErrorMessage('Failed to add the instrument.');
		}
	};

	const handleUpdate = async (instrumentId: number) => {
		const item = portfolio?.items.find(
			(entry) => entry.instrument_id === instrumentId
		);

		const quantity = Number(
			quantities[instrumentId] ?? String(item?.quantity ?? '')
		);

		if (!Number.isFinite(quantity) || quantity <= 0) {
			setErrorMessage('Quantity must be greater than zero.');
			setSuccessMessage('');
			return;
		}

		setErrorMessage('');
		setSuccessMessage('');

		try {
			await updateItem({
				instrument_id: instrumentId,
				quantity
			}).unwrap();

			setQuantities((current) => {
				const next = { ...current };
				delete next[instrumentId];
				return next;
			});

			setSuccessMessage('Quantity updated.');
		} catch {
			setErrorMessage('Failed to update the quantity.');
		}
	};

	const handleDelete = async (instrumentId: number) => {
		setErrorMessage('');
		setSuccessMessage('');

		try {
			await deleteItem(instrumentId).unwrap();

			setQuantities((current) => {
				const next = { ...current };
				delete next[instrumentId];
				return next;
			});

			setSuccessMessage('Instrument removed from your portfolio.');
		} catch {
			setErrorMessage('Failed to delete the instrument.');
		}
	};

	if (isPortfolioLoading || isInstrumentsLoading) {
		return <p className="portfolio-message">Loading portfolio...</p>;
	}

	if (
		isPortfolioError ||
		isInstrumentsError ||
		!portfolio ||
		!instrumentsData
	) {
		return (
			<div className="portfolio-message">
				<p>Failed to load portfolio.</p>
				<button type="button" onClick={() => refetch()}>
					Try again
				</button>
			</div>
		);
	}

	const portfolioInstrumentIds = new Set(
		portfolio.items.map((item) => item.instrument_id)
	);

	const availableInstruments = instruments.filter(
		(instrument) => !portfolioInstrumentIds.has(instrument.id)
	);

	return (
		<section className="portfolio-page">
			<header className="portfolio-heading">
				<div>
					<h1>My Portfolio</h1>
					<p>Manage your currencies and precious metals.</p>
				</div>
			</header>
			<div className="portfolio-summary">
				<span>Total portfolio value</span>
				<strong>
					{Number(portfolio.total_value).toLocaleString(undefined, {
						minimumFractionDigits: 2,
						maximumFractionDigits: 2
					})}{' '}
					{portfolio.base_currency}
				</strong>
			</div>
			<form
				className="portfolio-add-form"
				onSubmit={(event) => {
					event.preventDefault();
					void handleAdd();
				}}
			>
				<h2>Add instrument</h2>
				<div className="portfolio-add-fields">
					<select
						value={selectedInstrumentId}
						onChange={(event) =>
							setSelectedInstrumentId(event.target.value)
						}
						aria-label="Select instrument"
						required
					>
						<option value="">Select an instrument</option>
						{availableInstruments.map((instrument) => (
							<option key={instrument.id} value={instrument.id}>
								{instrument.code} — {instrument.name}
							</option>
						))}
					</select>
					<input
						type="number"
						min="0.000001"
						step="any"
						value={newQuantity}
						onChange={(event) => setNewQuantity(event.target.value)}
						aria-label="Initial quantity"
						required
					/>
					<button
						type="submit"
						disabled={
							isAdding ||
							isUpdating ||
							isDeleting ||
							availableInstruments.length === 0
						}
					>
						{isAdding ? 'Adding...' : 'Add to portfolio'}
					</button>
				</div>
				{availableInstruments.length === 0 && (
					<p className="portfolio-message">
						All loaded active instruments are already in your
						portfolio.
					</p>
				)}
			</form>
			{errorMessage && (
				<p className="portfolio-error" role="alert">
					{errorMessage}
				</p>
			)}
			{successMessage && (
				<p className="portfolio-success" role="status">
					{successMessage}
				</p>
			)}
			{portfolio.items.length === 0 ? (
				<div className="portfolio-empty">
					<h2>Your portfolio is empty</h2>
					<p>Add a currency or metal using the form above.</p>
				</div>
			) : (
				<div className="portfolio-table-wrapper">
					<table className="portfolio-table">
						<thead>
							<tr>
								<th>Code</th>
								<th>Name</th>
								<th>Type</th>
								<th>Quantity</th>
								<th>Current rate</th>
								<th>Value (UAH)</th>
								<th>Portfolio share</th>
								<th>Actions</th>
							</tr>
						</thead>
						<tbody>
							{portfolio.items.map((item) => {
								const instrument = getInstrument(
									item.instrument_id
								);

								return (
									<tr key={item.instrument_id}>
										<td>
											{instrument?.code ??
												`#${item.instrument_id}`}
										</td>
										<td>
											{instrument?.name ??
												'Unknown instrument'}
										</td>
										<td>{instrument?.type ?? '—'}</td>
										<td>
											<input
												className="portfolio-quantity"
												type="number"
												min="0.000001"
												step="any"
												aria-label={`Quantity for ${instrument?.code ?? item.instrument_id}`}
												value={
													quantities[
														item.instrument_id
													] ?? String(item.quantity)
												}
												onChange={(event) =>
													setQuantities(
														(current) => ({
															...current,
															[item.instrument_id]:
																event.target
																	.value
														})
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
												? `${Number(
														item.value
													).toLocaleString(
														undefined,
														{
															minimumFractionDigits: 2,
															maximumFractionDigits: 2
														}
													)} ${portfolio.base_currency}`
												: '—'}
										</td>
										<td>
											{item.value != null &&
											Number(portfolio.total_value) > 0
												? `${(
														(Number(item.value) /
															Number(
																portfolio.total_value
															)) *
														100
													).toFixed(2)}%`
												: '—'}
										</td>
										<td className="portfolio-actions">
											<button
												type="button"
												onClick={() =>
													void handleUpdate(
														item.instrument_id
													)
												}
												disabled={
													isAdding ||
													isUpdating ||
													isDeleting
												}
											>
												Save
											</button>
											<button
												type="button"
												className="portfolio-delete"
												onClick={() =>
													void handleDelete(
														item.instrument_id
													)
												}
												disabled={
													isAdding ||
													isUpdating ||
													isDeleting
												}
											>
												Remove
											</button>
										</td>
									</tr>
								);
							})}
						</tbody>
					</table>
				</div>
			)}
		</section>
	);
}
