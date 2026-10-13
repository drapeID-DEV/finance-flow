import { baseApi } from './baseApi';

export interface UserDashboardSummary {
	role: 'user';
	portfolio_items: number;
	active_alerts: number;
	triggered_alerts: number;
	active_instruments: number;
	latest_rate_date: string | null;
}

export interface AdminDashboardSummary {
	role: 'admin';
	total_users: number;
	active_users: number;
	total_instruments: number;
	active_instruments: number;
	total_rates: number;
	total_alerts: number;
	latest_rate_date: string | null;
}

export type DashboardSummary = UserDashboardSummary | AdminDashboardSummary;

export const dashboardApi = baseApi.injectEndpoints({
	endpoints: (builder) => ({
		getDashboardSummary: builder.query<DashboardSummary, void>({
			query: () => '/dashboard/summary'
		})
	})
});

export const { useGetDashboardSummaryQuery } = dashboardApi;
