import { useState } from 'react';
import type { Instrument } from '../../../../api/instrumentsApi';
import { useGetInstrumentComparisonQuery } from '../../../../api/ratesApi';
import { InstrumentComparisonChart } from './InstrumentComparisonChart';

interface InstrumentComparisonSectionProps {
	instruments: Instrument[];
	selectedCode: string;
	from: string;
	to: string;
}

export function InstrumentComparisonSection({
	instruments,
	selectedCode,
	from,
	to
}: InstrumentComparisonSectionProps) {
	const [selectedCompareCode, setSelectedCompareCode] = useState('');

	const availableInstruments = instruments.filter(
		(instrument) => instrument.code !== selectedCode
	);

	const compareCode = availableInstruments.some(
		(instrument) => instrument.code === selectedCompareCode
	)
		? selectedCompareCode
		: (availableInstruments[0]?.code ?? '');

	const {
		data: comparisonData,
		isLoading,
		isFetching,
		isError
	} = useGetInstrumentComparisonQuery(
		{
			first: selectedCode,
			second: compareCode,
			from,
			to
		},
		{
			skip: !selectedCode || !compareCode || selectedCode === compareCode
		}
	);

	if (!selectedCode || availableInstruments.length === 0) {
		return null;
	}

	return (
		<section className="analytics-comparison">
			<div className="analytics-controls">
				<label>
					Compare with
					<select
						value={compareCode}
						onChange={(event) =>
							setSelectedCompareCode(event.target.value)
						}
					>
						{availableInstruments.map((instrument) => (
							<option key={instrument.id} value={instrument.code}>
								{instrument.code} — {instrument.name}
							</option>
						))}
					</select>
				</label>
			</div>
			{isLoading ? (
				<p className="analytics-message">Loading comparison...</p>
			) : isError ? (
				<div className="analytics-message">
					<p>Failed to load comparison data.</p>
				</div>
			) : comparisonData && comparisonData.length > 0 ? (
				<InstrumentComparisonChart
					data={comparisonData}
					firstCode={selectedCode}
					secondCode={compareCode}
					isFetching={isFetching}
				/>
			) : (
				<div className="analytics-message">
					<p>No matching rate history for these instruments.</p>
				</div>
			)}
		</section>
	);
}
