import type {
	AggregatedRateHistoryItem,
	RateAggregation,
	RateHistoryItem,
	RateHistoryResponse
} from '../../../api/ratesApi';

export type AnalyticsPeriod = 7 | 30 | 90;

export interface ChartRate {
	date: string;
	rate: number;
	label: string;
	periodMin: number;
	periodMax: number;
}

export interface RateStats {
	current: number;
	min: number;
	max: number;
}

export const ANALYTICS_PERIODS: AnalyticsPeriod[] = [7, 30, 90];

export const AGGREGATION_OPTIONS: {
	value: RateAggregation;
	label: string;
}[] = [
	{ value: 'day', label: 'Daily' },
	{ value: 'week', label: 'Weekly' },
	{ value: 'month', label: 'Monthly' }
];

export function formatDate(date: Date): string {
	const year = date.getFullYear();
	const month = String(date.getMonth() + 1).padStart(2, '0');
	const day = String(date.getDate()).padStart(2, '0');

	return `${year}-${month}-${day}`;
}

export function formatRate(value: number): string {
	return value.toLocaleString('en-US', {
		minimumFractionDigits: 2,
		maximumFractionDigits: 6
	});
}

export function mapHistoryToChart(
	history: RateHistoryResponse,
	aggregation: RateAggregation
): ChartRate[] {
	if (aggregation === 'day') {
		return (history as RateHistoryItem[]).map((item) => {
			const rate = Number(item.rate);

			return {
				date: item.date,
				rate,
				periodMin: rate,
				periodMax: rate,
				label: new Date(`${item.date}T00:00:00`).toLocaleDateString(
					'en-US',
					{ day: '2-digit', month: 'short' }
				)
			};
		});
	}

	return (history as AggregatedRateHistoryItem[]).map((item) => ({
		date: item.period,
		rate: Number(item.close),
		periodMin: Number(item.min),
		periodMax: Number(item.max),
		label: item.period
	}));
}

export function calculateRateStats(data: ChartRate[]): RateStats | null {
	if (data.length === 0) {
		return null;
	}

	return {
		current: data[data.length - 1].rate,
		min: Math.min(...data.map((item) => item.periodMin)),
		max: Math.max(...data.map((item) => item.periodMax))
	};
}
