interface AnalyticsStateProps {
	type: 'loading' | 'error' | 'empty';
	onRetry?: () => void;
}

const stateContent = {
	loading: {
		title: 'Loading rate history...',
		description: ''
	},
	error: {
		title: 'Failed to load rate history.',
		description: 'Please try again.'
	},
	empty: {
		title: 'No historical data',
		description:
			'There are no recorded rates for this instrument during the selected period.'
	}
};

export function AnalyticsState({ type, onRetry }: AnalyticsStateProps) {
	const content = stateContent[type];

	return (
		<div
			className={`analytics-panel analytics-state analytics-state--${type}`}
		>
			<h2>{content.title}</h2>
			{content.description && <p>{content.description}</p>}
			{type === 'error' && onRetry && (
				<button type="button" onClick={onRetry}>
					Try again
				</button>
			)}
		</div>
	);
}
