interface PortfolioSummaryProps {
	totalValue: number | string;
	baseCurrency: string;
}

export function PortfolioSummary({
	totalValue,
	baseCurrency
}: PortfolioSummaryProps) {
	return (
		<div className="portfolio-summary">
			<span>Total portfolio value</span>
			<strong>
				{Number(totalValue).toLocaleString(undefined, {
					minimumFractionDigits: 2,
					maximumFractionDigits: 2
				})}{' '}
				{baseCurrency}
			</strong>
		</div>
	);
}
