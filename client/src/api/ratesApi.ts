import { baseApi } from './baseApi';

export type RateAggregation = 'day' | 'week' | 'month';

export interface RateHistoryItem {
	date: string;
	rate: number | string;
	unit: number;
}

export interface AggregatedRateHistoryItem {
	period: string;
	open: number | string;
	close: number | string;
	min: number | string;
	max: number | string;
	avg: number | string;
	unit: number;
}

export interface RateHistoryParams {
	code: string;
	from: string;
	to: string;
	aggregation: RateAggregation;
}

export type RateHistoryResponse =
	| RateHistoryItem[]
	| AggregatedRateHistoryItem[];

export const ratesApi = baseApi.injectEndpoints({
	endpoints: (builder) => ({
		getRateHistory: builder.query<RateHistoryResponse, RateHistoryParams>({
			query: ({ code, from, to, aggregation }) => ({
				url: `/instruments/${encodeURIComponent(code)}/rates`,
				params: { from, to, agg: aggregation }
			}),
			providesTags: ['Rate']
		})
	})
});

export const { useGetRateHistoryQuery } = ratesApi;
