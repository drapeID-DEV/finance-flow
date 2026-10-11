import type { Instrument } from '../../../api/instrumentsApi';

interface AnalyticsInstrumentInfoProps {
	instrument?: Instrument;
	from: string;
	to: string;
}

export function AnalyticsInstrumentInfo({
	instrument,
	from,
	to
}: AnalyticsInstrumentInfoProps) {
	if (!instrument) {
		return null;
	}

	return (
		<div className="analytics-instrument">
			<div>
				<span>{instrument.code}</span>
				<h2>{instrument.name}</h2>
			</div>
			<span className="analytics-date-range">
				{from} — {to}
			</span>
		</div>
	);
}
