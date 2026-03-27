import { useState, useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import { useI18n } from '../contexts/I18nContext';

export function AnalyticsWidget({ todayVisitors, hasError }) {
    const { t } = useI18n();
    const [isOpen, setIsOpen] = useState(false);
    const chartRef = useRef(null);
    const canvasRef = useRef(null);

    useEffect(() => {
        if (isOpen && !hasError && canvasRef.current && !chartRef.current) {
            chartRef.current = new Chart(canvasRef.current, {
                type: 'line',
                data: {
                    labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Today'],
                    datasets: [{
                        label: 'Visitors (UV)',
                        data: [65, 82, 90, 81, 110, 135, todayVisitors],
                        borderColor: '#22d3ee',
                        backgroundColor: 'rgba(34, 211, 238, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    color: '#94a3b8',
                    scales: {
                        x: { grid: { color: '#1e2d45' }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: '#1e2d45' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }
        
        return () => {
            if (chartRef.current) {
                chartRef.current.destroy();
                chartRef.current = null;
            }
        };
    }, [isOpen, hasError, todayVisitors]);

    if (hasError) {
        return <div style={{ padding: '16px', color: 'var(--danger)' }}>Data unavailable</div>;
    }

    return (
        <div className="analytics-container" style={{ position: 'relative', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '4px', boxShadow: 'var(--shadow-card)', width: '100%' }}>
            <button 
                data-testid="analytics-toggle"
                onClick={() => setIsOpen(!isOpen)} 
                style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', padding: '12px 16px', fontSize: '0.9rem', color: 'var(--text-secondary)', width: '100%', background: 'transparent', border: 'none', cursor: 'pointer', outline: 'none' }}
            >
                <span>{t('visitors')}<span style={{ fontWeight: 800, color: 'var(--accent-2)', fontSize: '1.2rem' }}>{todayVisitors}</span></span>
            </button>
            
            <div 
                data-testid="analytics-chart-container" 
                style={{ display: isOpen ? 'block' : 'none', padding: '12px' }}
            >
                <div style={{ height: '200px', width: '100%' }}>
                    <canvas ref={canvasRef}></canvas>
                </div>
            </div>
        </div>
    );
}
