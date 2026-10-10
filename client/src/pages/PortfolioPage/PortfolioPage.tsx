import { useState } from 'react';

import { useGetInstrumentsQuery } from '../../api/instrumentsApi';
import {
	useGetPortfolioQuery,
	useAddPortfolioItemMutation,
	useUpdatePortfolioItemMutation,
	useDeletePortfolioItemMutation
} from '../../api/portfolioApi';

import { PortfolioSummary } from './components/PortfolioSummary';
import { AddInstrumentForm } from './components/AddInstrumentForm';
import { PortfolioTable } from './components/PortfolioTable';
import {
	PortfolioMessages,
	PortfolioLoadError,
	PortfolioEmpty
} from './components/PortfolioMessages';

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
		return <PortfolioLoadError onRetry={() => void refetch()} />;
	}

	const portfolioInstrumentIds = new Set(
		portfolio.items.map((item) => item.instrument_id)
	);

	const availableInstruments = instruments.filter(
		(instrument) => !portfolioInstrumentIds.has(instrument.id)
	);

	const isBusy = isAdding || isUpdating || isDeleting;

	return (
		<section className="portfolio-page">
			<header className="portfolio-heading">
				<div>
					<h1>My Portfolio</h1>
					<p>Manage your currencies and precious metals.</p>
				</div>
			</header>
			<PortfolioSummary
				totalValue={portfolio.total_value}
				baseCurrency={portfolio.base_currency}
			/>
			<AddInstrumentForm
				instruments={availableInstruments}
				selectedInstrumentId={selectedInstrumentId}
				quantity={newQuantity}
				isBusy={isBusy}
				isAdding={isAdding}
				onInstrumentChange={setSelectedInstrumentId}
				onQuantityChange={setNewQuantity}
				onSubmit={() => void handleAdd()}
			/>
			<PortfolioMessages
				errorMessage={errorMessage}
				successMessage={successMessage}
			/>
			{portfolio.items.length === 0 ? (
				<PortfolioEmpty />
			) : (
				<PortfolioTable
					items={portfolio.items}
					instruments={instruments}
					quantities={quantities}
					totalValue={portfolio.total_value}
					baseCurrency={portfolio.base_currency}
					isBusy={isBusy}
					onQuantityChange={(instrumentId, value) =>
						setQuantities((current) => ({
							...current,
							[instrumentId]: value
						}))
					}
					onUpdate={(instrumentId) => void handleUpdate(instrumentId)}
					onDelete={(instrumentId) => void handleDelete(instrumentId)}
				/>
			)}
		</section>
	);
}
