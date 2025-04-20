/**
 * Charts.js - Gestionnaire de graphiques pour Daznode
 * Ce module crée et met à jour les graphiques à partir des données de l'API
 * Utilise Chart.js pour le rendu des graphiques
 */

class DaznodeCharts {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#FFB000',
            secondary: '#0088CC',
            success: '#4CAF50',
            warning: '#FF9800',
            danger: '#F44336',
            info: '#2196F3',
            dark: '#333333',
            light: '#E9ECEF',
            transparent: 'rgba(0, 0, 0, 0)'
        };
    }

    /**
     * Initialise tous les graphiques de la page
     */
    async initCharts() {
        await this.initBalanceChart();
        await this.initForwardingChart();
        await this.initChannelsChart();
    }

    /**
     * Crée le graphique d'évolution des soldes
     */
    async initBalanceChart() {
        try {
            const metricsHistory = await api.getMetricsHistory(30);
            if (!metricsHistory || !metricsHistory.length) return;

            // Préparation des données
            const labels = metricsHistory.map(m => new Date(m.date).toLocaleDateString());
            const onchainData = metricsHistory.map(m => m.node_metrics?.wallet_balance?.confirmed_balance || 0);
            const channelsData = metricsHistory.map(m => m.channel_metrics?.local_balance?.total || 0);
            const pendingData = metricsHistory.map(m => (m.node_metrics?.wallet_balance?.unconfirmed_balance || 0) + (m.channel_metrics?.pending_balance || 0));

            const ctx = document.getElementById('balanceChart');
            if (!ctx) return;

            this.charts.balance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Balance On-Chain',
                            data: onchainData,
                            borderColor: this.colors.primary,
                            backgroundColor: this._hexToRgba(this.colors.primary, 0.1),
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: 'Balance Canaux',
                            data: channelsData,
                            borderColor: this.colors.secondary,
                            backgroundColor: this._hexToRgba(this.colors.secondary, 0.1),
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: 'En attente',
                            data: pendingData,
                            borderColor: this.colors.warning,
                            backgroundColor: this._hexToRgba(this.colors.warning, 0.1),
                            fill: true,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString() + ' sats';
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + context.parsed.y.toLocaleString() + ' sats';
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Erreur lors de l\'initialisation du graphique de balance:', error);
        }
    }

    /**
     * Crée le graphique de forwarding
     */
    async initForwardingChart() {
        try {
            const forwardingStats = await api.getForwardingStats(30);
            if (!forwardingStats || !forwardingStats.daily_stats || !forwardingStats.daily_stats.length) return;

            // Préparation des données
            const stats = forwardingStats.daily_stats;
            const labels = stats.map(s => new Date(s.date).toLocaleDateString());
            const volumeData = stats.map(s => s.amount);
            const feesData = stats.map(s => s.fees);
            const countData = stats.map(s => s.count);

            const ctx = document.getElementById('forwardingChart');
            if (!ctx) return;

            this.charts.forwarding = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Volume (sats)',
                            data: volumeData,
                            backgroundColor: this._hexToRgba(this.colors.primary, 0.7),
                            borderColor: this.colors.primary,
                            borderWidth: 1,
                            order: 1,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Frais (sats)',
                            data: feesData,
                            backgroundColor: this._hexToRgba(this.colors.secondary, 0.7),
                            borderColor: this.colors.secondary,
                            borderWidth: 1,
                            order: 1,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Nombre de Forwards',
                            data: countData,
                            type: 'line',
                            borderColor: this.colors.success,
                            backgroundColor: this._hexToRgba(this.colors.success, 0.1),
                            borderWidth: 2,
                            pointRadius: 3,
                            tension: 0.4,
                            order: 0,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            type: 'linear',
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Montant (sats)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString();
                                }
                            }
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Nombre'
                            },
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    if (context.dataset.label.includes('Nombre')) {
                                        return context.dataset.label + ': ' + context.parsed.y.toLocaleString();
                                    } else {
                                        return context.dataset.label + ': ' + context.parsed.y.toLocaleString() + ' sats';
                                    }
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Erreur lors de l\'initialisation du graphique de forwarding:', error);
        }
    }

    /**
     * Crée le graphique de canaux
     */
    async initChannelsChart() {
        try {
            const channels = await api.getEnrichedChannels();
            if (!channels || !channels.length) return;

            // Préparation des données pour le graphique en donut
            const totalCapacity = channels.reduce((sum, channel) => sum + channel.capacity, 0);
            const activeCapacity = channels
                .filter(channel => channel.active)
                .reduce((sum, channel) => sum + channel.capacity, 0);
            const inactiveCapacity = totalCapacity - activeCapacity;

            const localBalance = channels.reduce((sum, channel) => sum + (channel.local_balance || 0), 0);
            const remoteBalance = channels.reduce((sum, channel) => sum + (channel.remote_balance || 0), 0);

            const ctx = document.getElementById('channelsChart');
            if (!ctx) return;

            this.charts.channels = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Balance Locale', 'Balance Distance'],
                    datasets: [{
                        data: [localBalance, remoteBalance],
                        backgroundColor: [
                            this.colors.primary,
                            this.colors.secondary
                        ],
                        borderColor: [
                            this.colors.primary,
                            this.colors.secondary
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.raw;
                                    const percentage = Math.round((value / (localBalance + remoteBalance)) * 100);
                                    return context.label + ': ' + value.toLocaleString() + ' sats (' + percentage + '%)';
                                }
                            }
                        }
                    }
                }
            });

            // Création du graphique de capacité active/inactive
            const ctxActive = document.getElementById('channelsActiveChart');
            if (!ctxActive) return;

            this.charts.channelsActive = new Chart(ctxActive, {
                type: 'doughnut',
                data: {
                    labels: ['Canaux Actifs', 'Canaux Inactifs'],
                    datasets: [{
                        data: [activeCapacity, inactiveCapacity],
                        backgroundColor: [
                            this.colors.success,
                            this.colors.danger
                        ],
                        borderColor: [
                            this.colors.success,
                            this.colors.danger
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.raw;
                                    const percentage = Math.round((value / totalCapacity) * 100);
                                    return context.label + ': ' + value.toLocaleString() + ' sats (' + percentage + '%)';
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Erreur lors de l\'initialisation du graphique de canaux:', error);
        }
    }

    /**
     * Utilitaire pour convertir une couleur hex en rgba
     * @param {string} hex - Code couleur hexadécimal
     * @param {number} alpha - Valeur d'opacité
     * @returns {string} - Couleur au format rgba
     */
    _hexToRgba(hex, alpha = 1) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
}

// Exporte une instance unique
const charts = new DaznodeCharts(); 