// CineMetric AI - Main Frontend Logic
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initMovieSearch();
    initMLSimulator();
    initEDACalls();
    initModelsLeaderboard();
    initDatasetExplorer();
    initSettingsModal();

    // Auto-search a flagship movie on first load so user immediately sees a rich preview!
    setTimeout(() => {
        searchMovie('Oppenheimer');
    }, 400);
});

// Global state
let charts = {};
let currentDatasetPage = 1;

// =========================================================================
// 1. Navigation & Tab Switching
// =========================================================================
function initNavigation() {
    const tabButtons = document.querySelectorAll('.nav-tab');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }

            // Trigger chart resize if navigating to EDA tab
            if (targetId === 'tab-eda' || targetId === 'tab-models') {
                setTimeout(() => {
                    Object.values(charts).forEach(c => c && c.resize && c.resize());
                }, 100);
            }
        });
    });
}

// =========================================================================
// 2. Movie Search & LLM Box Office Query
// =========================================================================
function initMovieSearch() {
    const form = document.getElementById('movie-search-form');
    const input = document.getElementById('movie-search-input');
    const chips = document.querySelectorAll('.chip-btn');

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = input.value.trim();
        if (query) {
            searchMovie(query);
        }
    });

    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const q = chip.getAttribute('data-query');
            input.value = q;
            searchMovie(q);
        });
    });
}

async function searchMovie(movieName) {
    const loadingState = document.getElementById('movie-loading-state');
    const resultContainer = document.getElementById('movie-result-container');
    const btnSearch = document.getElementById('btn-search-movie');
    const btnText = btnSearch.querySelector('.btn-text');
    const btnLoader = btnSearch.querySelector('.btn-loader');

    // UI Loading state
    loadingState.classList.remove('d-none');
    resultContainer.classList.add('d-none');
    btnText.classList.add('d-none');
    btnLoader.classList.remove('d-none');
    btnSearch.disabled = true;

    try {
        const response = await fetch('/api/movie-lookup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: jsonStringify({ query: movieName })
        });

        const data = await response.json();

        if (response.ok && data.movie) {
            renderMovieResult(data.movie, data.source);
            resultContainer.classList.remove('d-none');
        } else {
            resultContainer.innerHTML = `
                <div class="movie-card" style="border-color: #ef4444; text-align: center; padding: 40px;">
                    <i class="fa-solid fa-triangle-exclamation red" style="font-size: 2.5rem; margin-bottom: 16px;"></i>
                    <h3 style="margin-bottom: 8px;">Movie Not Found</h3>
                    <p style="color: #94a3b8;">${data.error || 'Could not find box office metrics for this title. Please try another query.'}</p>
                </div>
            `;
            resultContainer.classList.remove('d-none');
        }
    } catch (err) {
        console.error('Error fetching movie:', err);
        resultContainer.innerHTML = `
            <div class="movie-card" style="border-color: #ef4444; text-align: center; padding: 40px;">
                <i class="fa-solid fa-circle-exclamation red" style="font-size: 2.5rem; margin-bottom: 16px;"></i>
                <h3 style="margin-bottom: 8px;">Network or Server Error</h3>
                <p style="color: #94a3b8;">Unable to contact the box office intelligence engine.</p>
            </div>
        `;
        resultContainer.classList.remove('d-none');
    } finally {
        loadingState.classList.add('d-none');
        btnText.classList.remove('d-none');
        btnLoader.classList.add('d-none');
        btnSearch.disabled = false;
    }
}

function renderMovieResult(m, source) {
    const container = document.getElementById('movie-result-container');

    const wwGross = formatCurrency(m.worldwide_gross);
    const budget = formatCurrency(m.budget);
    const domGross = formatCurrency(m.domestic_gross || (m.worldwide_gross * 0.38));
    const intGross = formatCurrency(m.international_gross || (m.worldwide_gross * 0.62));
    const opening = formatCurrency(m.opening_weekend || (m.domestic_gross ? m.domestic_gross * 0.3 : 0));
    const roi = m.roi_percentage ? `${m.roi_percentage > 0 ? '+' : ''}${m.roi_percentage}%` : 'N/A';
    const multiplier = m.profit_multiplier ? `${m.profit_multiplier}x` : 'N/A';
    const badgeColor = m.badge_color || '#10b981';

    const castPills = (m.top_cast || []).map(actor => `<span class="cast-pill"><i class="fa-solid fa-user"></i> ${actor}</span>`).join('');
    const genrePills = (m.genres || []).map(g => `<span class="genre-pill"><i class="fa-solid fa-tag"></i> ${g}</span>`).join('');
    const factorsList = (m.key_success_factors || []).map(f => `<li>${f}</li>`).join('');

    container.innerHTML = `
        <div class="movie-card">
            <!-- Header -->
            <div class="movie-header">
                <div>
                    <div class="movie-title-wrap">
                        <h2 class="movie-main-title">${m.title}</h2>
                        <span class="movie-year-badge">${m.release_year || 'N/A'}</span>
                    </div>
                    ${m.local_currency_note ? `<div style="margin-top: 6px;"><span class="range-pill" style="color: #fbbf24; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.35); font-weight: 600;"><i class="fa-solid fa-money-bill-wave"></i> ${m.local_currency_note}</span></div>` : ''}
                    <div class="movie-source-tag"><i class="fa-solid fa-circle-info"></i> Source: ${source || 'AI Intelligence Engine'}</div>
                </div>
                <div>
                    <div class="verdict-badge" style="background: ${hexToRgba(badgeColor, 0.15)}; color: ${badgeColor}; border: 1px solid ${badgeColor};">
                        <i class="fa-solid fa-trophy"></i> ${m.verdict || 'Commercial Success'}
                    </div>
                </div>
            </div>

            <!-- Primary Metric Cards -->
            <div class="movie-stats-showcase">
                <div class="big-stat-box highlight-gold">
                    <span class="stat-box-label"><i class="fa-solid fa-earth-americas"></i> Worldwide Box Office</span>
                    <div class="stat-box-value gold">${wwGross}</div>
                    <span class="stat-box-sub">${multiplier} Budget Multiplier</span>
                </div>
                <div class="big-stat-box highlight-emerald">
                    <span class="stat-box-label"><i class="fa-solid fa-coins"></i> Production Budget</span>
                    <div class="stat-box-value emerald">${budget}</div>
                    <span class="stat-box-sub">ROI: <strong style="color: ${badgeColor};">${roi}</strong></span>
                </div>
                <div class="big-stat-box">
                    <span class="stat-box-label"><i class="fa-solid fa-flag-usa"></i> Domestic Collections</span>
                    <div class="stat-box-value sky">${domGross}</div>
                    <span class="stat-box-sub">Opening Wknd: ${opening}</span>
                </div>
                <div class="big-stat-box">
                    <span class="stat-box-label"><i class="fa-solid fa-globe"></i> International Overseas</span>
                    <div class="stat-box-value violet">${intGross}</div>
                    <span class="stat-box-sub">Overseas Share: ~${Math.round(((m.international_gross || m.worldwide_gross * 0.62) / (m.worldwide_gross || 1)) * 100)}%</span>
                </div>
            </div>

            <!-- Detailed Analysis & Metadata Grid -->
            <div class="movie-details-grid">
                <div>
                    <!-- Synopsis -->
                    <div class="movie-synopsis-box">
                        <h4><i class="fa-solid fa-book-open"></i> Story Premise & Concept</h4>
                        <p style="color: #cbd5e1; line-height: 1.65;">${m.synopsis || 'An acclaimed theatrical feature film that captured worldwide box office audiences.'}</p>
                    </div>

                    <!-- AI Financial Breakdown -->
                    <div class="financial-analysis-box">
                        <h4><i class="fa-solid fa-chart-line"></i> Theatrical Financial Breakdown & Trajectory</h4>
                        <p style="color: #cbd5e1; line-height: 1.65; margin-bottom: 12px;">${m.financial_breakdown || ''}</p>
                        
                        <h5 style="color: #fff; font-size: 0.92rem; margin-top: 14px;"><i class="fa-solid fa-star gold"></i> Key Box Office Drivers:</h5>
                        <ul class="success-factors-list">
                            ${factorsList}
                        </ul>
                    </div>

                    ${m.fun_fact ? `
                        <div class="fun-fact-callout">
                            <strong><i class="fa-solid fa-lightbulb gold"></i> Box Office Trivia:</strong> ${m.fun_fact}
                        </div>
                    ` : ''}
                </div>

                <!-- Meta Sidebar -->
                <div class="movie-meta-sidebar">
                    <div class="meta-group">
                        <span class="meta-label"><i class="fa-solid fa-bullhorn"></i> Director</span>
                        <div class="meta-value">${m.director || 'N/A'}</div>
                    </div>

                    <div class="meta-group">
                        <span class="meta-label"><i class="fa-solid fa-users"></i> Leading Cast</span>
                        <div class="cast-pills">
                            ${castPills || '<span class="cast-pill">Ensemble Cast</span>'}
                        </div>
                    </div>

                    <div class="meta-group">
                        <span class="meta-label"><i class="fa-solid fa-tags"></i> Genres</span>
                        <div class="genre-pills">
                            ${genrePills || '<span class="genre-pill">Drama</span>'}
                        </div>
                    </div>

                    <div class="meta-group" style="margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08);">
                        <button class="btn btn-outline btn-block btn-sm" onclick="sendToSimulator('${escapeQuotes(m.title)}', ${m.budget || 100000000})">
                            <i class="fa-solid fa-sliders"></i> Test in ML Simulator
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

window.sendToSimulator = function(title, budget) {
    document.getElementById('tab-btn-ml').click();
    document.getElementById('sim-title').value = title;
    const budgetSlider = document.getElementById('sim-budget');
    budgetSlider.value = budget;
    budgetSlider.dispatchEvent(new Event('input'));
    document.getElementById('btn-predict-ml').click();
};

// =========================================================================
// 3. ML Simulator & Custom Revenue Prediction
// =========================================================================
function initMLSimulator() {
    const form = document.getElementById('ml-predict-form');
    const budgetSlider = document.getElementById('sim-budget');
    const budgetBadge = document.getElementById('budget-val-badge');
    const runtimeSlider = document.getElementById('sim-runtime');
    const runtimeBadge = document.getElementById('runtime-val-badge');
    const genreCheckboxes = document.querySelectorAll('#genre-checkboxes label');

    budgetSlider.addEventListener('input', () => {
        budgetBadge.textContent = formatCurrency(budgetSlider.value);
    });

    runtimeSlider.addEventListener('input', () => {
        runtimeBadge.textContent = `${runtimeSlider.value} min`;
    });

    genreCheckboxes.forEach(label => {
        label.addEventListener('click', (e) => {
            const cb = label.querySelector('input');
            setTimeout(() => {
                if (cb.checked) {
                    label.classList.add('selected');
                } else {
                    label.classList.remove('selected');
                }
            }, 10);
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await runMLPrediction();
    });
}

async function runMLPrediction() {
    const budget = parseFloat(document.getElementById('sim-budget').value);
    const runtime = parseFloat(document.getElementById('sim-runtime').value);
    const popularity = parseFloat(document.getElementById('sim-popularity').value) || 25.0;
    const releaseMonth = parseInt(document.getElementById('sim-month').value);
    const castTier = document.getElementById('sim-cast-tier').value;
    const directorTier = document.getElementById('sim-director-tier').value;
    const hasCollection = document.getElementById('sim-collection').checked ? 1 : 0;
    const hasHomepage = document.getElementById('sim-homepage').checked ? 1 : 0;

    const selectedGenres = [];
    document.querySelectorAll('#genre-checkboxes input:checked').forEach(cb => {
        selectedGenres.push(cb.value);
    });

    const payload = {
        budget: budget,
        runtime: runtime,
        popularity: popularity,
        release_month: releaseMonth,
        release_year: 2026,
        has_collection: hasCollection,
        has_homepage: hasHomepage,
        cast_tier: castTier,
        director_tier: directorTier,
        genres: selectedGenres.length ? selectedGenres : ['Action', 'Adventure']
    };

    try {
        const btn = document.getElementById('btn-predict-ml');
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running Machine Learning Forecast...';

        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: jsonStringify(payload)
        });

        const data = await res.json();
        if (res.ok && data.prediction) {
            renderPredictionResult(data.prediction, budget);
        }
    } catch (err) {
        console.error('Error running ML prediction:', err);
    } finally {
        const btn = document.getElementById('btn-predict-ml');
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-circle-play"></i> Run ML Box Office Prediction';
    }
}

function renderPredictionResult(p, budget) {
    document.getElementById('pred-revenue-display').textContent = p.formatted_revenue;
    document.getElementById('pred-range-display').textContent = `$${p.lower_bound_millions}M - $${p.upper_bound_millions}M`;
    
    const verdictBadge = document.getElementById('pred-verdict-badge');
    verdictBadge.style.background = hexToRgba(p.badge_color, 0.15);
    verdictBadge.style.color = p.badge_color;
    verdictBadge.style.border = `1px solid ${p.badge_color}`;
    verdictBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${p.verdict}`;

    document.getElementById('pred-roi-display').textContent = `${p.roi_percentage > 0 ? '+' : ''}${p.roi_percentage}%`;
    document.getElementById('pred-multiplier-display').textContent = `${p.profit_multiplier}x`;
    
    const profit = p.predicted_revenue - budget;
    document.getElementById('pred-profit-display').textContent = `${profit >= 0 ? '+' : '-'}$${Math.abs(profit / 1e6).toFixed(1)}M`;
    document.getElementById('pred-model-display').textContent = p.model_used;
}

// =========================================================================
// 4. EDA Analytics & Interactive Visualizations
// =========================================================================
async function initEDACalls() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        if (res.ok && data.stats) {
            renderCharts(data.stats);
            renderTopMoviesTable(data.stats.top_movies || []);
        }
    } catch (err) {
        console.error('Error loading EDA stats:', err);
    }
}

function renderCharts(stats) {
    // 1. Scatter Chart: Budget vs Revenue
    const scatterCtx = document.getElementById('budgetRevenueChart');
    if (scatterCtx && stats.scatter_sample) {
        const scatterData = stats.scatter_sample.map(d => ({
            x: d.budget / 1e6,
            y: d.revenue / 1e6,
            title: d.title
        }));

        charts.scatter = new Chart(scatterCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Movie (Budget vs Gross)',
                    data: scatterData,
                    backgroundColor: 'rgba(245, 158, 11, 0.65)',
                    borderColor: '#f59e0b',
                    pointRadius: 4.5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const pt = ctx.raw;
                                return `${pt.title}: Budget $${pt.x.toFixed(1)}M | Gross $${pt.y.toFixed(1)}M`;
                            }
                        }
                    },
                    legend: { display: false }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Budget ($ Millions)', color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        title: { display: true, text: 'Worldwide Gross ($ Millions)', color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    // 2. Bar Chart: Genre Revenue
    const genreCtx = document.getElementById('genreRevenueChart');
    if (genreCtx && stats.genre_stats) {
        const topGenres = stats.genre_stats.slice(0, 8);
        charts.genre = new Chart(genreCtx, {
            type: 'bar',
            data: {
                labels: topGenres.map(g => g.genre),
                datasets: [{
                    label: 'Avg Revenue ($M)',
                    data: topGenres.map(g => (g.avg_revenue / 1e6).toFixed(1)),
                    backgroundColor: [
                        '#f59e0b', '#38bdf8', '#10b981', '#8b5cf6',
                        '#fbbf24', '#0ea5e9', '#34d399', '#a78bfa'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                    y: {
                        title: { display: true, text: 'Avg Revenue ($M)', color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    // 3. Line Chart: Monthly Seasonality
    const monthCtx = document.getElementById('monthlyTrendChart');
    if (monthCtx && stats.month_stats) {
        charts.month = new Chart(monthCtx, {
            type: 'line',
            data: {
                labels: stats.month_stats.map(m => m.month),
                datasets: [{
                    label: 'Avg Revenue ($M)',
                    data: stats.month_stats.map(m => (m.avg_revenue / 1e6).toFixed(1)),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#10b981',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                    y: {
                        title: { display: true, text: 'Avg Revenue ($M)', color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    // 4. Doughnut Chart: Franchise vs Solo
    const collCtx = document.getElementById('collectionChart');
    if (collCtx && stats.collection_comparison) {
        const c = stats.collection_comparison;
        charts.collection = new Chart(collCtx, {
            type: 'doughnut',
            data: {
                labels: ['Franchise / Collection', 'Standalone Film'],
                datasets: [{
                    data: [(c.in_collection_avg_revenue / 1e6).toFixed(1), (c.out_collection_avg_revenue / 1e6).toFixed(1)],
                    backgroundColor: ['#f59e0b', '#38bdf8'],
                    borderColor: '#111827',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { family: 'Outfit', size: 12 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` Avg Gross: $${ctx.raw}M`
                        }
                    }
                }
            }
        });
    }
}

function renderTopMoviesTable(movies) {
    const tbody = document.getElementById('top-movies-tbody');
    if (!tbody) return;

    tbody.innerHTML = movies.map((m, idx) => {
        const roiMult = m.budget > 0 ? (m.revenue / m.budget).toFixed(2) + 'x' : 'N/A';
        return `
            <tr>
                <td><strong>#${idx + 1}</strong></td>
                <td><strong style="color: #fff;">${m.title}</strong></td>
                <td>${m.release_year || 'N/A'}</td>
                <td>${formatCurrency(m.budget)}</td>
                <td style="color: #f59e0b; font-weight: 700;">${formatCurrency(m.revenue)}</td>
                <td><span class="range-pill" style="color: #10b981;">${roiMult}</span></td>
                <td>${m.popularity ? m.popularity.toFixed(1) : 'N/A'}</td>
            </tr>
        `;
    }).join('');
}

// =========================================================================
// 5. ML Models Benchmark & Kaggle Submission
// =========================================================================
async function initModelsLeaderboard() {
    try {
        const res = await fetch('/api/models-info');
        const data = await res.json();
        if (res.ok && data.metrics) {
            renderModelsTable(data.metrics, data.best_model);
            if (data.metrics.feature_importance) {
                renderFeatureImportanceChart(data.metrics.feature_importance);
            }
        }

        // Fetch submission preview
        const subRes = await fetch('/api/submission-preview');
        const subData = await subRes.json();
        if (subRes.ok && subData.preview) {
            renderSubmissionPreview(subData.preview);
        }
    } catch (err) {
        console.error('Error loading models info:', err);
    }
}

function renderModelsTable(metrics, bestModel) {
    const tbody = document.getElementById('models-table-tbody');
    if (!tbody) return;

    const modelKeys = ['GradientBoosting', 'RandomForest', 'HistGradientBoosting', 'Ridge', 'Lasso', 'LinearRegression'];

    tbody.innerHTML = modelKeys.map(key => {
        const m = metrics[key];
        if (!m) return '';
        const isBest = key === bestModel;
        return `
            <tr style="${isBest ? 'background: rgba(16, 185, 129, 0.08); font-weight: 600;' : ''}">
                <td>
                    <strong style="color: ${isBest ? '#10b981' : '#fff'};">${m.name}</strong>
                    ${isBest ? '<span class="badge" style="background:#10b981; color:#000; padding:2px 8px; border-radius:4px; font-size:0.7rem; margin-left:8px;">BEST</span>' : ''}
                </td>
                <td style="font-family: var(--font-mono); color: #f59e0b;">${m.rmsle}</td>
                <td style="font-family: var(--font-mono); color: #38bdf8;">${m.r2_score}</td>
                <td>${m.formatted_rmse}</td>
                <td>${m.formatted_mae}</td>
                <td><span style="color: #10b981;"><i class="fa-solid fa-circle-check"></i> Trained</span></td>
            </tr>
        `;
    }).join('');
}

function renderFeatureImportanceChart(features) {
    const ctx = document.getElementById('featureImportanceChart');
    if (!ctx) return;

    const topFeats = features.slice(0, 10);
    charts.featImp = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topFeats.map(f => f.feature.replace(/_/g, ' ')),
            datasets: [{
                label: 'Relative Importance',
                data: topFeats.map(f => f.importance),
                backgroundColor: '#38bdf8',
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                y: { ticks: { color: '#cbd5e1', font: { size: 11 } } }
            }
        }
    });
}

function renderSubmissionPreview(rows) {
    const tbody = document.getElementById('submission-preview-tbody');
    if (!tbody) return;

    tbody.innerHTML = rows.map(r => `
        <tr>
            <td><strong>#${r.id}</strong></td>
            <td style="font-family: var(--font-mono); color: #f59e0b;">$${Math.round(r.revenue).toLocaleString()}</td>
            <td><span class="range-pill" style="color: #10b981;">${formatCurrency(r.revenue)}</span></td>
        </tr>
    `).join('');
}

// =========================================================================
// 6. Dataset Explorer Table & Pagination
// =========================================================================
function initDatasetExplorer() {
    const searchInput = document.getElementById('dataset-search-input');
    const genreFilter = document.getElementById('dataset-genre-filter');
    const btnPrev = document.getElementById('btn-prev-page');
    const btnNext = document.getElementById('btn-next-page');

    let debounceTimer;
    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            currentDatasetPage = 1;
            loadDatasetPage();
        }, 300);
    });

    genreFilter.addEventListener('change', () => {
        currentDatasetPage = 1;
        loadDatasetPage();
    });

    btnPrev.addEventListener('click', () => {
        if (currentDatasetPage > 1) {
            currentDatasetPage--;
            loadDatasetPage();
        }
    });

    btnNext.addEventListener('click', () => {
        currentDatasetPage++;
        loadDatasetPage();
    });

    loadDatasetPage();
}

async function loadDatasetPage() {
    const search = document.getElementById('dataset-search-input').value.trim();
    const genre = document.getElementById('dataset-genre-filter').value;
    const tbody = document.getElementById('dataset-table-tbody');
    const pageInfo = document.getElementById('pagination-info');
    const btnPrev = document.getElementById('btn-prev-page');
    const btnNext = document.getElementById('btn-next-page');

    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 24px;"><i class="fa-solid fa-spinner fa-spin gold"></i> Loading movies...</td></tr>';

    try {
        const url = `/api/movies?page=${currentDatasetPage}&limit=12&q=${encodeURIComponent(search)}&genre=${encodeURIComponent(genre)}`;
        const res = await fetch(url);
        const data = await res.json();

        if (res.ok && data.movies) {
            if (data.movies.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 24px; color: #94a3b8;">No matching movies found.</td></tr>';
                pageInfo.textContent = '0 movies';
                btnPrev.disabled = true;
                btnNext.disabled = true;
                return;
            }

            tbody.innerHTML = data.movies.map(m => `
                <tr>
                    <td><strong>#${m.id}</strong></td>
                    <td>
                        <strong style="color: #fff; cursor: pointer;" onclick="searchMovie('${escapeQuotes(m.title)}'); document.getElementById('tab-btn-llm').click();">
                            ${m.title}
                        </strong>
                        ${m.tagline ? `<br><small style="color: #64748b; font-style: italic;">"${m.tagline.slice(0, 50)}..."</small>` : ''}
                    </td>
                    <td>${m.release_date || 'N/A'}</td>
                    <td>${m.runtime ? m.runtime + ' min' : 'N/A'}</td>
                    <td>${formatCurrency(m.budget)}</td>
                    <td style="color: #f59e0b; font-weight: 700;">${formatCurrency(m.revenue)}</td>
                    <td>${m.popularity}</td>
                </tr>
            `).join('');

            const startIdx = (currentDatasetPage - 1) * 12 + 1;
            const endIdx = Math.min(startIdx + data.movies.length - 1, data.total);
            pageInfo.textContent = `Showing ${startIdx} - ${endIdx} of ${data.total.toLocaleString()} movies`;

            btnPrev.disabled = currentDatasetPage <= 1;
            btnNext.disabled = currentDatasetPage >= data.pages;
        }
    } catch (err) {
        console.error('Error fetching dataset movies:', err);
    }
}

// =========================================================================
// 7. Settings Modal (API Key Configuration)
// =========================================================================
function initSettingsModal() {
    const modal = document.getElementById('settings-modal');
    const openBtn = document.getElementById('open-settings-btn');
    const closeBtn = document.getElementById('close-settings-btn');
    const cancelBtn = document.getElementById('cancel-settings-btn');
    const form = document.getElementById('api-key-form');

    const toggleModal = (show) => {
        if (show) modal.classList.remove('d-none');
        else modal.classList.add('d-none');
    };

    openBtn.addEventListener('click', () => toggleModal(true));
    closeBtn.addEventListener('click', () => toggleModal(false));
    cancelBtn.addEventListener('click', () => toggleModal(false));

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const provider = document.getElementById('llm-provider').value;
        const apiKey = document.getElementById('llm-api-key').value.trim();
        const model = document.getElementById('llm-model-name').value.trim();

        try {
            const res = await fetch('/api/set-api-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: jsonStringify({ provider, api_key: apiKey, model })
            });
            if (res.ok) {
                alert('API Configuration saved successfully!');
                toggleModal(false);
            }
        } catch (err) {
            alert('Failed to save API configuration.');
        }
    });
}

// =========================================================================
// Utility Helper Functions
// =========================================================================
function formatCurrency(val) {
    if (!val || isNaN(val) || val <= 0) return '$0';
    if (val >= 1e9) {
        return `$${(val / 1e9).toFixed(2)}B`;
    }
    if (val >= 1e6) {
        return `$${(val / 1e6).toFixed(1)}M`;
    }
    return `$${Math.round(val).toLocaleString()}`;
}

function hexToRgba(hex, alpha) {
    if (!hex || !hex.startsWith('#')) return `rgba(16, 185, 129, ${alpha})`;
    const r = parseInt(hex.slice(1, 3), 16) || 16;
    const g = parseInt(hex.slice(3, 5), 16) || 185;
    const b = parseInt(hex.slice(5, 7), 16) || 129;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function escapeQuotes(str) {
    return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function jsonStringify(obj) {
    return JSON.stringify(obj);
}
