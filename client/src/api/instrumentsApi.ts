import { baseApi } from './baseApi';

export interface Instrument {
	id: number;
	code: string;
	name: string;
	type: string;
	is_active: boolean;
}

export const instrumentsApi = baseApi.injectEndpoints({
	endpoints: (builder) => ({
		getInstruments: builder.query<Instrument[], void>({
			query: () => '/instruments',
			providesTags: ['Instrument']
		})
	})
});

export const { useGetInstrumentsQuery } = instrumentsApi;
