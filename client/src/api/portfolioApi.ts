import { baseApi } from './baseApi';

export interface PortfolioItem {
	instrument_id: number;
	quantity: number | string;
	current_rate: number | string | null;
	rate_unit: number | null;
	rate_date: string | null;
	value: number | string | null;
}

export interface PortfolioResponse {
	id: number;
	base_currency: string;
	total_value: number | string;
	items: PortfolioItem[];
}

export interface UpdatePortfolioItemRequest {
	instrument_id: number;
	quantity: number;
}

export const portfolioApi = baseApi.injectEndpoints({
	endpoints: (builder) => ({
		getPortfolio: builder.query<PortfolioResponse, void>({
			query: () => '/portfolio',
			providesTags: ['Portfolio']
		}),
		updatePortfolioItem: builder.mutation<
			PortfolioItem,
			UpdatePortfolioItemRequest
		>({
			query: ({ instrument_id, quantity }) => ({
				url: `/portfolio/items/${instrument_id}`,
				method: 'PUT',
				body: { quantity }
			}),
			invalidatesTags: ['Portfolio']
		}),
		deletePortfolioItem: builder.mutation<
			{ message: string; instrument_id: number },
			number
		>({
			query: (instrumentId) => ({
				url: `/portfolio/items/${instrumentId}`,
				method: 'DELETE'
			}),
			invalidatesTags: ['Portfolio']
		}),
		addPortfolioItem: builder.mutation<
			PortfolioItem,
			UpdatePortfolioItemRequest
		>({
			query: ({ instrument_id, quantity }) => ({
				url: `/portfolio/items/${instrument_id}`,
				method: 'POST',
				body: { quantity }
			}),
			invalidatesTags: ['Portfolio']
		})
	})
});

export const {
	useGetPortfolioQuery,
	useUpdatePortfolioItemMutation,
	useDeletePortfolioItemMutation,
	useAddPortfolioItemMutation
} = portfolioApi;
