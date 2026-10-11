import { baseApi } from './baseApi';

export type AlertDirection = 'above' | 'below';
export type AlertStatus = 'active' | 'triggered';

export interface Alert {
	id: number;
	instrument_id: number;
	direction: AlertDirection;
	value: number | string;
	status: AlertStatus;
}

export interface CreateAlertRequest {
	instrument_id: number;
	direction: AlertDirection;
	value: number;
}

export const alertApi = baseApi.injectEndpoints({
	endpoints: (builder) => ({
		getAlerts: builder.query<Alert[], void>({
			query: () => '/alerts',
			providesTags: ['Alert']
		}),
		createAlert: builder.mutation<Alert, CreateAlertRequest>({
			query: (body) => ({
				url: '/alerts',
				method: 'POST',
				body
			}),
			invalidatesTags: ['Alert']
		}),
		deleteAlert: builder.mutation<void, number>({
			query: (alertId) => ({
				url: `/alerts/${alertId}`,
				method: 'DELETE'
			}),
			invalidatesTags: ['Alert']
		})
	})
});

export const {
	useGetAlertsQuery,
	useCreateAlertMutation,
	useDeleteAlertMutation
} = alertApi;
