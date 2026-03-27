import { render, screen, fireEvent } from '@testing-library/react';
import { AnalyticsWidget } from './AnalyticsWidget';

describe('AnalyticsWidget Component (TDD)', () => {
    it('should render the default collapsed view with today visitors count', () => {
        render(<AnalyticsWidget todayVisitors={150} />);
        expect(screen.getByText(/Today's Visitors/i)).toBeInTheDocument();
        expect(screen.getByText('150')).toBeInTheDocument();
        
        const chartContainer = screen.getByTestId('analytics-chart-container');
        expect(chartContainer).toHaveClass('hidden');
    });

    it('should expand chart container when toggle is clicked', () => {
        render(<AnalyticsWidget todayVisitors={150} />);
        const toggleBtn = screen.getByTestId('analytics-toggle');
        
        fireEvent.click(toggleBtn);
        
        const chartContainer = screen.getByTestId('analytics-chart-container');
        expect(chartContainer).not.toHaveClass('hidden');
    });

    it('should render fallback empty state when traffic api fails (error prop)', () => {
        render(<AnalyticsWidget todayVisitors={0} hasError={true} />);
        expect(screen.getByText(/Data unavailable/i)).toBeInTheDocument();
    });
});
