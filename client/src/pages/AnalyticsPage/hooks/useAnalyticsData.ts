import { useMemo } from 'react';
import {
	useGetRateHistoryQuery,
	type RateAggregation
} from '../../../api/ratesApi';
import {
	calculateRateStats,
	formatDate,
	mapHistoryToChart,
	type AnalyticsPeriod
} from '../utils/analyticsUtils';

interface UseAnalyticsDataParams {
	selectedCode: string;
	period: AnalyticsPeriod;
	aggregation: RateAggregation;
}

export function useAnalyticsData({
	selectedCode,
	period,
	aggregation
}: UseAnalyticsDataParams) {
	const { from, to } = useMemo(() => {
		const end = new Date();
		const start = new Date(end);
		start.setDate(start.getDate() - (period - 1));

		return {
			from: formatDate(start),
			to: formatDate(end)
		};
	}, [period]);

	const {
		data: history,
		isLoading: isHistoryLoading,
		isFetching: isHistoryFetching,
		isError: isHistoryError,
		refetch: refetchHistory
	} = useGetRateHistoryQuery(
		{ code: selectedCode, from, to, aggregation },
		{ skip: !selectedCode }
	);

	const chartData = useMemo(
		() => mapHistoryToChart(history ?? [], aggregation),
		[history, aggregation]
	);

	const stats = useMemo(() => calculateRateStats(chartData), [chartData]);

	return {
		from,
		to,
		chartData,
		stats,
		isHistoryLoading,
		isHistoryFetching,
		isHistoryError,
		refetchHistory
	};
}
