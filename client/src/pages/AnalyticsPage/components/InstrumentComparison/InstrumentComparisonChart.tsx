import {
	CartesianGrid,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis
} from 'recharts';
import type { InstrumentComparisonItem } from '../../../../api/ratesApi';
import { formatRate } from '../../utils/analyticsUtils';

interface InstrumentComparisonChartProps {
	data: InstrumentComparisonItem[];
	firstCode: string;
	secondCode: string;
	isFetching: boolean;
}

export function InstrumentComparisonChart({
	data,
	firstCode,
	secondCode,
	isFetching
}: InstrumentComparisonChartProps) {
	const chartData = data.map((item) => ({
		date: item.date,
		firstRate: Number(item.first_rate),
		secondRate: Number(item.second_rate),
		label: new Date(`${item.date}T00:00:00`).toLocaleDateString('en-US', {
			day: '2-digit',
			month: 'short'
		})
	}));

	return (
		<div className="analytics-panel">
			<div className="analytics-chart-heading">
				<div>
					<h2>Instrument comparison</h2>
					<p>Exchange rates in UAH over time</p>
				</div>
				{isFetching && (
					<span className="analytics-updating">Updating...</span>
				)}
			</div>
			<div className="analytics-comparison-legend">
				<span>
					<i className="comparison-dot comparison-dot-first" />
					{firstCode}
				</span>
				<span>
					<i className="comparison-dot comparison-dot-second" />
					{secondCode}
				</span>
			</div>
			<div className="analytics-chart">
				<ResponsiveContainer width="100%" height="100%">
					<LineChart
						data={chartData}
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
							formatter={(value, name) => [
								`${formatRate(Number(value))} UAH`,
								String(name)
							]}
						/>
						<Line
							type="monotone"
							dataKey="firstRate"
							name={firstCode}
							stroke="#818cf8"
							strokeWidth={2.5}
							dot={false}
							connectNulls={false}
						/>
						<Line
							type="monotone"
							dataKey="secondRate"
							name={secondCode}
							stroke="#34d399"
							strokeWidth={2.5}
							dot={false}
							connectNulls={false}
						/>
					</LineChart>
				</ResponsiveContainer>
			</div>
			<p className="analytics-chart-footnote">
				Showing {chartData.length} matching dates.
			</p>
		</div>
	);
}
