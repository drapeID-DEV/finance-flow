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
	search?: string;
	type?: 'currency' | 'metal';
}

export const instrumentsApi = baseApi.injectEndpoints({
	endpoints: (builder) => ({
		getInstruments: builder.query<InstrumentsResponse, InstrumentsQuery>({
			query: ({ page, page_size, search, type }) => ({
				url: '/instruments',
				params: {
					page,
					page_size,
					...(search?.trim() ? { search: search.trim() } : {}),
					...(type ? { type } : {})
				}
			}),
			providesTags: ['Instrument']
		})
	})
});

export const { useGetInstrumentsQuery } = instrumentsApi;
