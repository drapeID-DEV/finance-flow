import { baseApi } from './baseApi';

export interface Instrument {
	id: number;
	code: string;
	name: string;
	type: string;
	is_active: boolean;
	current_rate: string | null;
	rate_unit: number | null;
	rate_date: string | null;
	previous_rate: string | null;
	daily_change: string | null;
	daily_change_percent: string | null;
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

export interface UpdateInstrumentStatusRequest {
	code: string;
	is_active: boolean;
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
		}),
		getAllAdminInstruments: builder.query<
			InstrumentsResponse,
			InstrumentsQuery
		>({
			query: ({ page, page_size, search, type }) => ({
				url: '/instruments/admin/all',
				params: {
					page,
					page_size,
					...(search?.trim() ? { search: search.trim() } : {}),
					...(type ? { type } : {})
				}
			}),
			providesTags: ['Instrument']
		}),
		updateInstrumentStatus: builder.mutation<
			{ code: string; is_active: boolean },
			UpdateInstrumentStatusRequest
		>({
			query: ({ code, is_active }) => ({
				url: `/instruments/${encodeURIComponent(code)}/status`,
				method: 'PATCH',
				body: { is_active }
			}),
			invalidatesTags: ['Instrument']
		})
	})
});

export const {
	useGetInstrumentsQuery,
	useGetAllAdminInstrumentsQuery,
	useUpdateInstrumentStatusMutation
} = instrumentsApi;
