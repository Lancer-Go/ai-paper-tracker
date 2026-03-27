import React, { createContext, useContext, useState, useEffect } from 'react';

const I18nContext = createContext();

const DICT = {
  zh: {
    appTitle: "AI 论文热榜",
    dailyUpdate: "每日更新",
    heroTitle: "AI 学术热度追踪",
    heroSub: "基于学术引用量，每日自动聚合 arXiv 最新 AI 论文热榜",
    statToday: "今日论文",
    statCitation: "总引用量",
    statDomain: "覆盖领域",
    searchPh: "搜索论文标题、关键词...",
    filterAll: "全部",
    loading: "正在加载热榜数据...",
    emptyError: "运行 python run.py 开始采集",
    emptySearch: "没有找到匹配的论文",
    dataSource: "数据来源：arXiv API · Semantic Scholar API  |  每日 UTC 06:00 自动更新",
    visitors: "今日访客: ",
    citation: "引用",
    hasCode: "有代码",
    hotScore: "热度分",
    etAl: "等",
    people: "人",
    translationHighFi: "🔬 保真翻译",
    translationBasic: "📝 简版翻译",
    translationNone: "暂无翻译",
    scoreBreakdown: "评分拆解",
    domainDist: "领域分布",
    top10Citations: "Top 10 引用量",
    citationSpeed: "引用速度",
    citationTotal: "引用总量",
    authorImpact: "作者影响",
    freshness: "新鲜度",
    buzz: "社区讨论"
  },
  en: {
    appTitle: "AI Paper Tracker",
    dailyUpdate: "Daily Update",
    heroTitle: "AI Academic Trend Tracker",
    heroSub: "Daily aggregation of the latest arXiv AI paper trends based on citation metrics",
    statToday: "Today's Papers",
    statCitation: "Total Citations",
    statDomain: "Domains Covered",
    searchPh: "Search paper titles, keywords...",
    filterAll: "All",
    loading: "Loading trending data...",
    emptyError: "Run `python run.py` to start fetching",
    emptySearch: "No matching papers found",
    dataSource: "Data Source: arXiv API · Semantic Scholar API  |  Updated daily at 06:00 UTC",
    visitors: "Today's Visitors: ",
    citation: "Citations",
    hasCode: "Code",
    hotScore: "Score",
    etAl: "et al.",
    people: "",
    translationHighFi: "🔬 Pro Trans",
    translationBasic: "📝 Basic Trans",
    translationNone: "No Translation",
    scoreBreakdown: "Score Breakdown",
    domainDist: "Domain Distribution",
    top10Citations: "Top 10 Citations",
    citationSpeed: "Velocity",
    citationTotal: "Volume",
    authorImpact: "Author",
    freshness: "Freshness",
    buzz: "Buzz"
  }
};

export function I18nProvider({ children }) {
    const [lang, setLang] = useState('zh');

    useEffect(() => {
        let savedLang = localStorage.getItem('lang-pref');
        if (!savedLang) {
            const browserLang = navigator.language || '';
            savedLang = browserLang.toLowerCase().includes('zh') ? 'zh' : 'en';
        }
        setLang(savedLang);
    }, []);

    const switchLanguage = (newLang) => {
        localStorage.setItem('lang-pref', newLang);
        setLang(newLang);
    };

    const t = (key) => {
        return DICT[lang]?.[key] || key;
    };

    return (
        <I18nContext.Provider value={{ lang, switchLanguage, t }}>
            {children}
        </I18nContext.Provider>
    );
}

export const useI18n = () => useContext(I18nContext);
