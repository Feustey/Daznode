// Configuration et variables
const API_BASE_URL = '/api/v1';
let nodeInfo = {};
let charts = {};
let updateInterval = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des composants
    initSidebar();
    loadNodeInfo();
    loadBalances();
    loadChannelStats();
    initCharts();
    loadRecommendations();

    // Mise à jour automatique des données toutes les 5 minutes
    setInterval(function() {
        loadNodeInfo();
        loadBalances();
        loadChannelStats();
        updateCharts();
        loadRecommendations();
    }, 300000); // 5 minutes en millisecondes
});

// Gestion de la barre latérale responsive
function initSidebar() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Marquer l'élément de navigation actif
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Charger les informations du nœud
function loadNodeInfo() {
    fetch('/api/node/info')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des informations du nœud');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('node-alias').textContent = data.alias;
            document.getElementById('node-pubkey').textContent = data.identity_pubkey;
            document.getElementById('node-version').textContent = data.version;
            document.getElementById('node-synced').textContent = data.synced_to_chain ? 'Oui' : 'Non';
            document.getElementById('node-blockheight').textContent = data.block_height;
            
            // Mise à jour du statut de connexion
            updateConnectionStatus(true);
        })
        .catch(error => {
            console.error('Erreur :', error);
            updateConnectionStatus(false);
        });
}

// Charger les informations de solde
function loadBalances() {
    fetch('/api/wallet/balance')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des soldes');
            }
            return response.json();
        })
        .then(data => {
            // Format des montants en sats et BTC
            document.getElementById('onchain-balance').textContent = formatSats(data.total_balance);
            document.getElementById('onchain-balance-btc').textContent = formatBtc(data.total_balance);
            
            document.getElementById('lightning-balance').textContent = formatSats(data.channel_balance);
            document.getElementById('lightning-balance-btc').textContent = formatBtc(data.channel_balance);
            
            document.getElementById('pending-balance').textContent = formatSats(data.pending_open_balance);
            document.getElementById('pending-balance-btc').textContent = formatBtc(data.pending_open_balance);
            
            // Calcul du solde total
            const totalSats = data.total_balance + data.channel_balance + data.pending_open_balance;
            document.getElementById('total-balance').textContent = formatSats(totalSats);
            document.getElementById('total-balance-btc').textContent = formatBtc(totalSats);
        })
        .catch(error => {
            console.error('Erreur :', error);
        });
}

// Charger les statistiques des canaux
function loadChannelStats() {
    fetch('/api/channels')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des statistiques des canaux');
            }
            return response.json();
        })
        .then(data => {
            // Nombre de canaux
            document.getElementById('active-channels').textContent = data.active_channels.length;
            document.getElementById('pending-channels').textContent = data.pending_channels.length;
            document.getElementById('inactive-channels').textContent = data.inactive_channels.length;
            
            // Capacité totale
            let totalCapacity = 0;
            let totalLocalBalance = 0;
            let totalRemoteBalance = 0;
            
            data.active_channels.forEach(channel => {
                totalCapacity += parseInt(channel.capacity, 10);
                totalLocalBalance += parseInt(channel.local_balance, 10);
                totalRemoteBalance += parseInt(channel.remote_balance, 10);
            });
            
            document.getElementById('total-capacity').textContent = formatSats(totalCapacity);
            document.getElementById('total-capacity-btc').textContent = formatBtc(totalCapacity);
            
            document.getElementById('local-balance').textContent = formatSats(totalLocalBalance);
            document.getElementById('local-balance-btc').textContent = formatBtc(totalLocalBalance);
            
            document.getElementById('remote-balance').textContent = formatSats(totalRemoteBalance);
            document.getElementById('remote-balance-btc').textContent = formatBtc(totalRemoteBalance);
            
            // Afficher les canaux récents
            displayRecentChannels(data.active_channels);
        })
        .catch(error => {
            console.error('Erreur :', error);
        });
}

// Afficher les canaux récents dans le tableau
function displayRecentChannels(channels) {
    const tableBody = document.getElementById('recent-channels-table-body');
    if (!tableBody) return;
    
    // Trier les canaux par date d'ouverture (du plus récent au plus ancien)
    channels.sort((a, b) => {
        return new Date(b.chan_point) - new Date(a.chan_point);
    });
    
    // Afficher les 5 canaux les plus récents
    tableBody.innerHTML = '';
    
    const channelsToShow = channels.slice(0, 5);
    channelsToShow.forEach(channel => {
        const row = document.createElement('tr');
        
        const aliasCell = document.createElement('td');
        aliasCell.textContent = channel.node_alias || channel.remote_pubkey.substring(0, 10) + '...';
        
        const capacityCell = document.createElement('td');
        capacityCell.textContent = formatSats(channel.capacity);
        
        const localBalanceCell = document.createElement('td');
        const localPercentage = (channel.local_balance / channel.capacity) * 100;
        localBalanceCell.innerHTML = `
            <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-success" role="progressbar" style="width: ${localPercentage}%"></div>
            </div>
            <span class="small">${formatSats(channel.local_balance)}</span>
        `;
        
        const statusCell = document.createElement('td');
        const statusBadge = document.createElement('span');
        statusBadge.classList.add('badge');
        
        if (channel.active) {
            statusBadge.classList.add('bg-success');
            statusBadge.textContent = 'Actif';
        } else {
            statusBadge.classList.add('bg-warning');
            statusBadge.textContent = 'Inactif';
        }
        
        statusCell.appendChild(statusBadge);
        
        row.appendChild(aliasCell);
        row.appendChild(capacityCell);
        row.appendChild(localBalanceCell);
        row.appendChild(statusCell);
        
        tableBody.appendChild(row);
    });
}

// Initialiser les graphiques
function initCharts() {
    // Graphique de solde
    initBalanceChart();
    
    // Graphique des transactions
    initTransactionsChart();
    
    // Graphique de répartition des canaux
    initChannelDistributionChart();
}

// Initialiser le graphique de solde
function initBalanceChart() {
    fetch('/api/metrics/balance/history')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération de l\'historique des soldes');
            }
            return response.json();
        })
        .then(data => {
            const ctx = document.getElementById('balance-chart');
            if (!ctx) return;
            
            const dates = data.map(item => item.date);
            const onchainBalance = data.map(item => item.onchain_balance);
            const lightningBalance = data.map(item => item.lightning_balance);
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [
                        {
                            label: 'Solde on-chain',
                            data: onchainBalance,
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Solde Lightning',
                            data: lightningBalance,
                            borderColor: '#f39c12',
                            backgroundColor: 'rgba(243, 156, 18, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + formatSats(context.raw) + ' sats';
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            ticks: {
                                callback: function(value) {
                                    return formatSatsCompact(value);
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erreur :', error);
        });
}

// Initialiser le graphique des transactions
function initTransactionsChart() {
    fetch('/api/metrics/forwarding/history')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération de l\'historique des transactions');
            }
            return response.json();
        })
        .then(data => {
            const ctx = document.getElementById('transactions-chart');
            if (!ctx) return;
            
            const dates = data.map(item => item.date);
            const forwardingCount = data.map(item => item.forwarding_count);
            const forwardingFees = data.map(item => item.forwarding_fees);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: dates,
                    datasets: [
                        {
                            label: 'Nombre de transactions',
                            data: forwardingCount,
                            backgroundColor: 'rgba(46, 204, 113, 0.7)',
                            borderColor: 'rgba(46, 204, 113, 1)',
                            borderWidth: 1,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Frais collectés (sats)',
                            data: forwardingFees,
                            backgroundColor: 'rgba(52, 152, 219, 0.7)',
                            borderColor: 'rgba(52, 152, 219, 1)',
                            borderWidth: 1,
                            type: 'line',
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    if (context.dataset.label === 'Frais collectés (sats)') {
                                        return context.dataset.label + ': ' + formatSats(context.raw) + ' sats';
                                    } else {
                                        return context.dataset.label + ': ' + context.raw;
                                    }
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Nombre de transactions'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Frais (sats)'
                            },
                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erreur :', error);
        });
}

// Initialiser le graphique de répartition des canaux
function initChannelDistributionChart() {
    fetch('/api/channels')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des canaux');
            }
            return response.json();
        })
        .then(data => {
            const ctx = document.getElementById('channel-distribution-chart');
            if (!ctx) return;
            
            // Répartition des capacités par canaux
            const channelCapacities = data.active_channels.map(channel => parseInt(channel.capacity, 10));
            
            // Créer des groupes de capacité
            const capacityRanges = [
                { name: '< 1M sats', count: 0 },
                { name: '1M - 2M sats', count: 0 },
                { name: '2M - 5M sats', count: 0 },
                { name: '5M - 10M sats', count: 0 },
                { name: '> 10M sats', count: 0 }
            ];
            
            channelCapacities.forEach(capacity => {
                if (capacity < 1000000) {
                    capacityRanges[0].count++;
                } else if (capacity < 2000000) {
                    capacityRanges[1].count++;
                } else if (capacity < 5000000) {
                    capacityRanges[2].count++;
                } else if (capacity < 10000000) {
                    capacityRanges[3].count++;
                } else {
                    capacityRanges[4].count++;
                }
            });
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: capacityRanges.map(range => range.name),
                    datasets: [{
                        data: capacityRanges.map(range => range.count),
                        backgroundColor: [
                            'rgba(52, 152, 219, 0.7)',
                            'rgba(46, 204, 113, 0.7)',
                            'rgba(155, 89, 182, 0.7)',
                            'rgba(243, 156, 18, 0.7)',
                            'rgba(231, 76, 60, 0.7)'
                        ],
                        borderColor: 'white',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erreur :', error);
        });
}

// Mise à jour des graphiques (appelée périodiquement)
function updateCharts() {
    // Réinitialiser les graphiques
    initCharts();
}

// Charger les recommandations
function loadRecommendations() {
    fetch('/api/recommendations')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des recommandations');
            }
            return response.json();
        })
        .then(data => {
            const recommendationsContainer = document.getElementById('recommendations-container');
            if (!recommendationsContainer) return;
            
            // Effacer les recommandations existantes
            recommendationsContainer.innerHTML = '';
            
            if (data.length === 0) {
                const noRecommendations = document.createElement('div');
                noRecommendations.className = 'recommendation-item success';
                noRecommendations.innerHTML = '<h6>Aucune recommandation</h6><p>Félicitations ! Votre nœud fonctionne de façon optimale.</p>';
                recommendationsContainer.appendChild(noRecommendations);
                return;
            }
            
            // Afficher les recommandations
            data.forEach(recommendation => {
                const item = document.createElement('div');
                item.className = 'recommendation-item';
                
                // Déterminer la classe en fonction de la priorité
                switch (recommendation.priority.toLowerCase()) {
                    case 'high':
                        item.classList.add('danger');
                        break;
                    case 'medium':
                        item.classList.add('warning');
                        break;
                    case 'low':
                        item.classList.add('success');
                        break;
                    default:
                        break;
                }
                
                item.innerHTML = `<h6>${recommendation.title}</h6><p>${recommendation.description}</p>`;
                
                // Ajouter les détails supplémentaires si présents
                if (recommendation.details) {
                    const details = document.createElement('small');
                    details.className = 'text-muted d-block mt-2';
                    details.textContent = recommendation.details;
                    item.appendChild(details);
                }
                
                recommendationsContainer.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Erreur :', error);
        });
}

// Mettre à jour le statut de connexion
function updateConnectionStatus(isConnected) {
    const statusIndicator = document.getElementById('connection-status');
    const statusText = document.getElementById('connection-status-text');
    
    if (!statusIndicator || !statusText) return;
    
    if (isConnected) {
        statusIndicator.className = 'badge bg-success';
        statusText.textContent = 'Connecté';
    } else {
        statusIndicator.className = 'badge bg-danger';
        statusText.textContent = 'Déconnecté';
    }
}

// Fonctions utilitaires pour le formatage
function formatSats(sats) {
    return parseInt(sats).toLocaleString('fr-FR') + ' sats';
}

function formatSatsCompact(sats) {
    if (sats >= 1000000) {
        return (sats / 1000000).toFixed(1) + 'M';
    } else if (sats >= 1000) {
        return (sats / 1000).toFixed(1) + 'k';
    } else {
        return sats;
    }
}

function formatBtc(sats) {
    const btc = parseFloat(sats) / 100000000;
    return btc.toFixed(8) + ' BTC';
}