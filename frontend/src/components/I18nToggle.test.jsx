import { render, screen, fireEvent } from '@testing-library/react';
import { I18nToggle } from './I18nToggle';

describe('I18nToggle Component (TDD)', () => {
    beforeEach(() => {
        localStorage.clear();
        // mock navigator.language
        Object.defineProperty(navigator, 'language', {
            value: 'en-US',
            configurable: true,
        });
    });

    it('should render language options and default to navigator language (en)', () => {
        render(<I18nToggle />);
        const btnEn = screen.getByRole('button', { name: /EN/i });
        const btnZh = screen.getByRole('button', { name: /简/i });
        
        expect(btnEn).toBeInTheDocument();
        expect(btnZh).toBeInTheDocument();
        
        // Custom attribute to indicate active state
        expect(btnEn).toHaveAttribute('data-active', 'true');
        expect(btnZh).toHaveAttribute('data-active', 'false');
    });

    it('should switch language and persist to localStorage when clicked', () => {
        render(<I18nToggle />);
        const btnZh = screen.getByRole('button', { name: /简/i });
        
        fireEvent.click(btnZh);
        
        expect(btnZh).toHaveAttribute('data-active', 'true');
        expect(localStorage.getItem('lang-pref')).toBe('zh');
    });

    it('should load language preference from localStorage on mount', () => {
        localStorage.setItem('lang-pref', 'zh');
        render(<I18nToggle />);
        const btnZh = screen.getByRole('button', { name: /简/i });
        expect(btnZh).toHaveAttribute('data-active', 'true');
    });
});
