import { useEffect, useState } from 'react';
import { useGetInstrumentsQuery } from '../../api/instrumentsApi';
import type { RateAggregation } from '../../api/ratesApi';
import { AnalyticsControls } from './components/AnalyticsControls';
import { AnalyticsInstrumentInfo } from './components/AnalyticsInstrumentInfo';
import { AnalyticsStats } from './components/AnalyticsStats';
import { AnalyticsState } from './components/AnalyticsState';
import { InstrumentComparisonSection } from './components/InstrumentComparison/InstrumentComparisonSection';
import { RateHistoryChart } from './components/RateHistoryChart';
import { useAnalyticsData } from './hooks/useAnalyticsData';
import type { AnalyticsPeriod } from './utils/analyticsUtils';
import './AnalyticsPage.css';

export default function AnalyticsPage() {
	const [selectedCode, setSelectedCode] = useState('');
	const [period, setPeriod] = useState<AnalyticsPeriod>(30);
	const [aggregation, setAggregation] = useState<RateAggregation>('day');

	const {
		data: instrumentsData,
		isLoading: isInstrumentsLoading,
		isError: isInstrumentsError,
		refetch: refetchInstruments
	} = useGetInstrumentsQuery({ page: 1, page_size: 100 });

	const instruments = (instrumentsData?.items ?? []).filter(
		(instrument) => instrument.is_active
	);

	useEffect(() => {
		if (!selectedCode && instruments.length > 0) {
			setSelectedCode(instruments[0].code);
		}
	}, [instruments, selectedCode]);

	const {
		from,
		to,
		chartData,
		stats,
		isHistoryLoading,
		isHistoryFetching,
		isHistoryError,
		refetchHistory
	} = useAnalyticsData({
		selectedCode,
		period,
		aggregation
	});

	const selectedInstrument = instruments.find(
		(instrument) => instrument.code === selectedCode
	);

	if (isInstrumentsLoading) {
		return <p className="analytics-message">Loading instruments...</p>;
	}

	if (isInstrumentsError || !instrumentsData) {
		return (
			<div className="analytics-message">
				<p>Failed to load instruments.</p>
				<button type="button" onClick={() => void refetchInstruments()}>
					Try again
				</button>
			</div>
		);
	}

	return (
		<section className="analytics-page">
			<header className="analytics-heading">
				<div>
					<h1>Market analytics</h1>
					<p>
						Explore historical exchange rates for currencies and
						metals.
					</p>
				</div>
			</header>

			<AnalyticsControls
				instruments={instruments}
				selectedCode={selectedCode}
				period={period}
				aggregation={aggregation}
				onInstrumentChange={setSelectedCode}
				onPeriodChange={setPeriod}
				onAggregationChange={setAggregation}
			/>

			<AnalyticsInstrumentInfo
				instrument={selectedInstrument}
				from={from}
				to={to}
			/>

			<InstrumentComparisonSection
				instruments={instruments}
				selectedCode={selectedCode}
				from={from}
				to={to}
			/>

			{!selectedCode ? (
				<AnalyticsState type="empty" />
			) : isHistoryLoading ? (
				<AnalyticsState type="loading" />
			) : isHistoryError ? (
				<AnalyticsState
					type="error"
					onRetry={() => void refetchHistory()}
				/>
			) : chartData.length === 0 || !stats ? (
				<AnalyticsState type="empty" />
			) : (
				<>
					<AnalyticsStats stats={stats} />
					<RateHistoryChart
						data={chartData}
						isFetching={isHistoryFetching}
					/>
				</>
			)}
		</section>
	);
}
