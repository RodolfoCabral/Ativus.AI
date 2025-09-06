/**
 * JavaScript para Dashboard de Analytics PMP
 */

class PMPAnalytics {
    constructor() {
        this.charts = {};
        this.data = {};
        this.init();
    }

    init() {
        console.log('🚀 Inicializando PMP Analytics Dashboard');
        this.setupEventListeners();
        this.setupDateSelectors();
        this.loadAllData();
    }

    setupEventListeners() {
        // Botão de refresh
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadAllData();
        });

        // Botão de export
        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportData();
        });

        // Botão de gerar relatório
        document.getElementById('gerar-relatorio-btn').addEventListener('click', () => {
            this.gerarRelatorioMensal();
        });
    }

    setupDateSelectors() {
        // Preencher anos (últimos 3 anos + próximo ano)
        const anoSelect = document.getElementById('ano-select');
        const currentYear = new Date().getFullYear();
        
        for (let year = currentYear - 2; year <= currentYear + 1; year++) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            if (year === currentYear) option.selected = true;
            anoSelect.appendChild(option);
        }

        // Selecionar mês atual
        const mesSelect = document.getElementById('mes-select');
        mesSelect.value = new Date().getMonth() + 1;
    }

    async loadAllData() {
        this.showLoading(true);
        
        try {
            console.log('📊 Carregando dados de analytics...');
            
            // Carregar dados em paralelo
            const [dashboardData, alertasData] = await Promise.all([
                this.fetchDashboardData(),
                this.fetchAlertasData()
            ]);

            this.data.dashboard = dashboardData;
            this.data.alertas = alertasData;

            // Renderizar componentes
            this.renderAlertas();
            this.renderMetricas();
            this.renderCharts();
            this.renderPerformanceTable();

            this.showLoading(false);
            this.showSections();

            console.log('✅ Dados carregados com sucesso');

        } catch (error) {
            console.error('❌ Erro ao carregar dados:', error);
            this.showError('Erro ao carregar dados de analytics');
            this.showLoading(false);
        }
    }

    async fetchDashboardData() {
        const response = await fetch('/api/pmp/analytics/dashboard');
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Erro desconhecido');
        }
        return data;
    }

    async fetchAlertasData() {
        const response = await fetch('/api/pmp/analytics/alertas');
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Erro desconhecido');
        }
        return data;
    }

    renderAlertas() {
        const container = document.getElementById('alertas-container');
        const alertas = this.data.alertas.alertas || [];

        if (alertas.length === 0) {
            container.innerHTML = '<p class="no-data">Nenhum alerta no momento</p>';
            return;
        }

        container.innerHTML = alertas.map(alerta => `
            <div class="alerta-card ${alerta.nivel}">
                <div class="alerta-icon">
                    <i class="fas ${this.getAlertIcon(alerta.nivel)}"></i>
                </div>
                <div class="alerta-content">
                    <h4>${alerta.titulo}</h4>
                    <p>${alerta.descricao}</p>
                    <div class="alerta-acao">${alerta.acao_sugerida}</div>
                </div>
            </div>
        `).join('');
    }

    getAlertIcon(nivel) {
        const icons = {
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'success': 'fa-check-circle'
        };
        return icons[nivel] || 'fa-info-circle';
    }

    renderMetricas() {
        const metricas = this.data.dashboard.metricas_gerais || {};
        
        document.getElementById('total-pmps').textContent = metricas.total_pmps || 0;
        document.getElementById('pmps-ativas').textContent = metricas.pmps_ativas || 0;
        document.getElementById('total-os').textContent = metricas.total_os_geradas || 0;
        document.getElementById('os-mes').textContent = metricas.os_mes_atual || 0;
        document.getElementById('taxa-ativacao').textContent = `${metricas.taxa_ativacao || 0}%`;
    }

    renderCharts() {
        this.renderStatusChart();
        this.renderFrequenciasChart();
        this.renderTendenciaChart();
    }

    renderStatusChart() {
        const ctx = document.getElementById('chart-status').getContext('2d');
        const statusData = this.data.dashboard.os_por_status || [];

        if (this.charts.status) {
            this.charts.status.destroy();
        }

        this.charts.status = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: statusData.map(item => item.status),
                datasets: [{
                    data: statusData.map(item => item.quantidade),
                    backgroundColor: [
                        '#10b981', // Verde - finalizada
                        '#3b82f6', // Azul - programada
                        '#f59e0b', // Amarelo - aberta
                        '#ef4444', // Vermelho - cancelada
                        '#8b5cf6'  // Roxo - outros
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    renderFrequenciasChart() {
        const ctx = document.getElementById('chart-frequencias').getContext('2d');
        const freqData = this.data.dashboard.frequencias_populares || [];

        if (this.charts.frequencias) {
            this.charts.frequencias.destroy();
        }

        this.charts.frequencias = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: freqData.map(item => item.frequencia),
                datasets: [{
                    label: 'Quantidade',
                    data: freqData.map(item => item.quantidade),
                    backgroundColor: '#3b82f6',
                    borderColor: '#2563eb',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderTendenciaChart() {
        const ctx = document.getElementById('chart-tendencia').getContext('2d');
        const tendenciaData = this.data.dashboard.tendencia_7_dias || [];

        if (this.charts.tendencia) {
            this.charts.tendencia.destroy();
        }

        this.charts.tendencia = new Chart(ctx, {
            type: 'line',
            data: {
                labels: tendenciaData.map(item => {
                    const date = new Date(item.data);
                    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
                }),
                datasets: [{
                    label: 'OS Geradas',
                    data: tendenciaData.map(item => item.os_geradas),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderPerformanceTable() {
        const tbody = document.querySelector('#performance-table tbody');
        const performanceData = this.data.dashboard.performance_frequencia || [];

        if (performanceData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">Nenhum dado de performance disponível</td></tr>';
            return;
        }

        tbody.innerHTML = performanceData.map(item => `
            <tr>
                <td>${item.frequencia || 'N/A'}</td>
                <td>${item.total_os}</td>
                <td>${item.tempo_medio_horas}h</td>
                <td>
                    <span class="performance-badge ${this.getPerformanceBadge(item.tempo_medio_horas)}">
                        ${this.getPerformanceText(item.tempo_medio_horas)}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    getPerformanceBadge(horas) {
        if (horas <= 24) return 'excelente';
        if (horas <= 72) return 'boa';
        if (horas <= 168) return 'regular';
        return 'ruim';
    }

    getPerformanceText(horas) {
        if (horas <= 24) return 'Excelente';
        if (horas <= 72) return 'Boa';
        if (horas <= 168) return 'Regular';
        return 'Ruim';
    }

    async gerarRelatorioMensal() {
        const mes = document.getElementById('mes-select').value;
        const ano = document.getElementById('ano-select').value;
        const container = document.getElementById('relatorio-content');

        try {
            container.innerHTML = '<div class="loading-spinner"></div><p>Gerando relatório...</p>';

            const response = await fetch(`/api/pmp/analytics/relatorio-mensal?mes=${mes}&ano=${ano}`);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Erro ao gerar relatório');
            }

            this.renderRelatorioMensal(data);

        } catch (error) {
            console.error('❌ Erro ao gerar relatório:', error);
            container.innerHTML = `<p class="error">Erro ao gerar relatório: ${error.message}</p>`;
        }
    }

    renderRelatorioMensal(data) {
        const container = document.getElementById('relatorio-content');
        const resumo = data.resumo_geral || {};
        const performance = data.performance_por_frequencia || {};

        container.innerHTML = `
            <div class="relatorio-resumo">
                <div class="resumo-item">
                    <h4>${resumo.total_os_geradas || 0}</h4>
                    <p>OS Geradas</p>
                </div>
                <div class="resumo-item">
                    <h4>${resumo.os_finalizadas || 0}</h4>
                    <p>Finalizadas</p>
                </div>
                <div class="resumo-item">
                    <h4>${resumo.os_pendentes || 0}</h4>
                    <p>Pendentes</p>
                </div>
                <div class="resumo-item">
                    <h4>${resumo.taxa_conclusao_geral || 0}%</h4>
                    <p>Taxa Conclusão</p>
                </div>
            </div>
            
            <h4>Performance por Frequência</h4>
            <div class="performance-frequencia">
                ${Object.entries(performance).map(([freq, stats]) => `
                    <div class="freq-stats">
                        <h5>${freq}</h5>
                        <p>Total: ${stats.total} | Finalizadas: ${stats.finalizadas} | Taxa: ${stats.taxa_conclusao}%</p>
                        <p>Tempo médio: ${stats.tempo_medio_horas}h</p>
                    </div>
                `).join('')}
            </div>
        `;
    }

    exportData() {
        const dataToExport = {
            timestamp: new Date().toISOString(),
            dashboard: this.data.dashboard,
            alertas: this.data.alertas
        };

        const blob = new Blob([JSON.stringify(dataToExport, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pmp-analytics-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('📁 Dados exportados com sucesso');
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        loading.style.display = show ? 'flex' : 'none';
    }

    showSections() {
        const sections = [
            'alertas-section',
            'metricas-section', 
            'graficos-section',
            'performance-section',
            'relatorio-section'
        ];

        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            section.style.display = 'block';
            section.classList.add('fade-in');
        });
    }

    showError(message) {
        const container = document.querySelector('.main-content');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <div class="alerta-card error">
                <div class="alerta-icon">
                    <i class="fas fa-exclamation-circle"></i>
                </div>
                <div class="alerta-content">
                    <h4>Erro</h4>
                    <p>${message}</p>
                </div>
            </div>
        `;
        container.appendChild(errorDiv);

        // Remover após 5 segundos
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new PMPAnalytics();
});

