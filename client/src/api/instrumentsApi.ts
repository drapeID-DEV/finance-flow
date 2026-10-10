import { baseApi } from './baseApi';

export interface Instrument {
	id: number;
	code: string;
	name: string;
	type: string;
	is_active: boolean;
}

export interface InstrumentsResponse {
	items: Instrument[];
	page: number;
	page_size: number;
	total: number;
}

export interface InstrumentsQuery {
	page: number;
	page_size: number;
}

export const instrumentsApi = baseApi.injectEndpoints({
	endpoints: (builder) => ({
		getInstruments: builder.query<InstrumentsResponse, InstrumentsQuery>({
			query: ({ page, page_size }) => ({
				url: '/instruments',
				params: { page, page_size }
			}),
			providesTags: ['Instrument']
		})
	})
});

export const { useGetInstrumentsQuery } = instrumentsApi;
