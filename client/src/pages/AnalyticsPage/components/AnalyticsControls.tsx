import type { Instrument } from '../../../api/instrumentsApi';
import type { RateAggregation } from '../../../api/ratesApi';
import {
	AGGREGATION_OPTIONS,
	ANALYTICS_PERIODS,
	type AnalyticsPeriod
} from '../utils/analyticsUtils';

interface AnalyticsControlsProps {
	instruments: Instrument[];
	selectedCode: string;
	period: AnalyticsPeriod;
	aggregation: RateAggregation;
	onAggregationChange: (aggregation: RateAggregation) => void;
	onInstrumentChange: (code: string) => void;
	onPeriodChange: (period: AnalyticsPeriod) => void;
}

export function AnalyticsControls({
	instruments,
	selectedCode,
	period,
	aggregation,
	onInstrumentChange,
	onPeriodChange,
	onAggregationChange
}: AnalyticsControlsProps) {
	return (
		<div className="analytics-controls">
			<label>
				Instrument
				<select
					value={selectedCode}
					onChange={(event) => onInstrumentChange(event.target.value)}
					disabled={instruments.length === 0}
				>
					{instruments.length === 0 && (
						<option value="">No instruments available</option>
					)}
					{instruments.map((instrument) => (
						<option key={instrument.id} value={instrument.code}>
							{instrument.code} — {instrument.name}
						</option>
					))}
				</select>
			</label>

			<div className="analytics-period">
				<span>Period</span>
				<div className="analytics-period-buttons">
					{ANALYTICS_PERIODS.map((days) => (
						<button
							key={days}
							type="button"
							className={period === days ? 'is-active' : ''}
							aria-pressed={period === days}
							onClick={() => onPeriodChange(days)}
						>
							{days} days
						</button>
					))}
				</div>
			</div>

			<div className="analytics-period">
				<span>Aggregation</span>
				<div className="analytics-period-buttons">
					{AGGREGATION_OPTIONS.map((option) => (
						<button
							key={option.value}
							type="button"
							className={aggregation === option.value ? 'is-active' : ''}
							aria-pressed={aggregation === option.value}
							onClick={() => onAggregationChange(option.value)}
						>
							{option.label}
						</button>
					))}
				</div>
			</div>
		</div>
	);
}
