import type { RateStats } from '../utils/analyticsUtils';
import { formatRate } from '../utils/analyticsUtils';

interface AnalyticsStatsProps {
	stats: RateStats;
}

export function AnalyticsStats({ stats }: AnalyticsStatsProps) {
	const items = [
		{ label: 'Latest rate', value: stats.current },
		{ label: 'Period minimum', value: stats.min },
		{ label: 'Period maximum', value: stats.max }
	];

	return (
		<div className="analytics-stats">
			{items.map((item) => (
				<div className="analytics-stat" key={item.label}>
					<span>{item.label}</span>
					<strong>{formatRate(item.value)} UAH</strong>
				</div>
			))}
		</div>
	);
}
