import { useI18n } from '../contexts/I18nContext';

export function I18nToggle() {
    const { lang, switchLanguage } = useI18n();

    return (
        <div id="i18n-widget" style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'var(--bg-card)', padding: '4px', borderRadius: '20px', border: '1px solid var(--border)' }}>
            <button 
                onClick={() => switchLanguage('en')}
                data-active={lang === 'en' ? 'true' : 'false'}
                style={{ 
                    padding: '4px 12px', fontSize: '0.8rem', fontWeight: 600, borderRadius: '16px', border: 'none', cursor: 'pointer', transition: 'all 0.2s',
                    background: lang === 'en' ? 'var(--accent)' : 'transparent',
                    color: lang === 'en' ? '#fff' : 'var(--text-secondary)'
                }}
            >
                EN
            </button>
            <button 
                onClick={() => switchLanguage('zh')}
                data-active={lang === 'zh' ? 'true' : 'false'}
                style={{ 
                    padding: '4px 12px', fontSize: '0.8rem', fontWeight: 600, borderRadius: '16px', border: 'none', cursor: 'pointer', transition: 'all 0.2s',
                    background: lang === 'zh' ? 'var(--accent)' : 'transparent',
                    color: lang === 'zh' ? '#fff' : 'var(--text-secondary)'
                }}
            >
                简
            </button>
        </div>
    );
}
