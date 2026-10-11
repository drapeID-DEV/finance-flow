import {
	CartesianGrid,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis
} from 'recharts';
import type { ChartRate } from '../utils/analyticsUtils';
import { formatRate } from '../utils/analyticsUtils';

interface RateHistoryChartProps {
	data: ChartRate[];
	isFetching: boolean;
}

export function RateHistoryChart({ data, isFetching }: RateHistoryChartProps) {
	return (
		<div className="analytics-panel">
			<div className="analytics-chart-heading">
				<div>
					<h2>Exchange rate history</h2>
					<p>Rate in UAH over time</p>
				</div>
				{isFetching && (
					<span className="analytics-updating">Updating...</span>
				)}
			</div>
			<div className="analytics-chart">
				<ResponsiveContainer width="100%" height="100%">
					<LineChart
						data={data}
						margin={{ top: 12, right: 20, left: 8, bottom: 4 }}
					>
						<CartesianGrid stroke="#2a303b" strokeDasharray="4 4" />
						<XAxis
							dataKey="label"
							tick={{ fill: '#9299a5', fontSize: 12 }}
							tickLine={false}
							axisLine={{ stroke: '#374151' }}
							minTickGap={24}
						/>
						<YAxis
							domain={['auto', 'auto']}
							tick={{ fill: '#9299a5', fontSize: 12 }}
							tickLine={false}
							axisLine={false}
							width={75}
							tickFormatter={(value: number) => formatRate(value)}
						/>
						<Tooltip
							contentStyle={{
								background: '#111827',
								border: '1px solid #374151',
								borderRadius: 10,
								color: '#f9fafb'
							}}
							labelStyle={{ color: '#9ca3af' }}
							formatter={(value) => [
								`${formatRate(Number(value))} UAH`,
								'Rate'
							]}
						/>
						<Line
							type="monotone"
							dataKey="rate"
							name="Rate"
							stroke="#818cf8"
							strokeWidth={2.5}
							dot={false}
							activeDot={{ r: 5, strokeWidth: 0 }}
						/>
					</LineChart>
				</ResponsiveContainer>
			</div>
			<p className="analytics-chart-footnote">
				Showing {data.length} recorded data points.
			</p>
		</div>
	);
}
