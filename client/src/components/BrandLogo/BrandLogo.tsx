import { Link } from 'react-router-dom';
import './BrandLogo.css';

type BrandLogoProps = {
	className?: string;
};

export function BrandLogo({ className = '' }: BrandLogoProps) {
	return (
		<Link
			className={`brand-logo ${className}`.trim()}
			to="/"
			aria-label="FinanceFlow home"
		>
			<svg
				className="brand-logo__mark"
				viewBox="0 0 40 40"
				fill="none"
				aria-hidden="true"
			>
				<rect
					x="1"
					y="1"
					width="38"
					height="38"
					rx="11"
					fill="#171d24"
				/>
				<path
					d="M9 26.5L16 19.5L21 23L31 12.5"
					stroke="#72E0B2"
					strokeWidth="3"
					strokeLinecap="round"
					strokeLinejoin="round"
				/>
				<path
					d="M24.5 12.5H31V19"
					stroke="#72E0B2"
					strokeWidth="3"
					strokeLinecap="round"
					strokeLinejoin="round"
				/>
			</svg>
			<span className="brand-logo__name">
				Finance<span>Flow</span>
			</span>
		</Link>
	);
}
