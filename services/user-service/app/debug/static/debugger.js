// MDA-GENERATED-START: debugger-js
const { createApp } = Vue;

createApp({
    data() {
        return {
            serviceName: 'User Service',
            flows: [],
            selectedFlow: '',
            currentFlow: null,
            sessionId: null,
            ws: null,
            currentStep: null,
            context: {},
            breakpoints: new Set(),
            history: [],
            status: 'idle'
        }
    },
    
    computed: {
        canStart() {
            return this.selectedFlow && (this.status === 'idle' || this.status === 'completed' || this.status === 'error');
        },
        canContinue() {
            return this.status === 'paused';
        },
        canStep() {
            return this.status === 'paused';
        },
        canStop() {
            return this.status === 'running' || this.status === 'paused';
        }
    },
    
    async mounted() {
        // Initialize Mermaid
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }
        });
        
        // Load service info
        try {
            const response = await fetch('/debug/');
            const data = await response.json();
            this.serviceName = data.service;
            
            // Load flows
            await this.loadFlows();
        } catch (error) {
            console.error('Failed to load debug info:', error);
        }
    },
    
    methods: {
        async loadFlows() {
            try {
                const response = await fetch('/debug/flows');
                const data = await response.json();
                this.flows = data.flows;
            } catch (error) {
                console.error('Failed to load flows:', error);
            }
        },
        
        async loadFlow() {
            if (!this.selectedFlow) {
                this.currentFlow = null;
                return;
            }
            
            try {
                const response = await fetch(`/debug/flows/${this.selectedFlow}`);
                const data = await response.json();
                this.currentFlow = data;
                
                // Render flow diagram
                this.$nextTick(() => {
                    this.renderDiagram(data.diagram);
                });
            } catch (error) {
                console.error('Failed to load flow:', error);
            }
        },
        
        renderDiagram(mermaidCode) {
            const element = document.getElementById('mermaid-diagram');
            element.innerHTML = '';
            
            // Remove the markdown code block markers if present
            const cleanCode = mermaidCode.replace(/```mermaid\n?/, '').replace(/\n?```/, '').trim();
            
            // Create a div for the diagram with mermaid class
            const graphDiv = document.createElement('div');
            graphDiv.className = 'mermaid';
            graphDiv.textContent = cleanCode;
            element.appendChild(graphDiv);
            
            // Render with Mermaid
            mermaid.init(undefined, graphDiv);
            
            // Add click handlers to nodes after rendering
            setTimeout(() => {
                this.attachNodeClickHandlers();
            }, 500);
        },
        
        attachNodeClickHandlers() {
            // Find all nodes in the diagram
            const nodes = document.querySelectorAll('#mermaid-diagram .node');
            nodes.forEach(node => {
                // Extract step ID from the node
                const text = node.textContent;
                const step = this.currentFlow?.steps.find(s => text.includes(s.name));
                if (step) {
                    node.style.cursor = 'pointer';
                    node.addEventListener('click', () => {
                        this.toggleBreakpoint(step.id);
                    });
                }
            });
        },
        
        async startDebug() {
            try {
                // Create debug session
                const response = await fetch('/debug/sessions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        flow_name: this.selectedFlow,
                        initial_context: {}
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to create debug session');
                }
                
                const data = await response.json();
                this.sessionId = data.session_id;
                
                // Reset state
                this.history = [];
                this.context = {};
                this.currentStep = null;
                
                // Connect WebSocket
                this.connectWebSocket();
            } catch (error) {
                console.error('Failed to start debug session:', error);
                alert('Failed to start debug session: ' + error.message);
            }
        },
        
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/debug/sessions/${this.sessionId}/ws`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('Debug WebSocket connected');
                this.status = 'connected';
                // Start execution
                this.ws.send(JSON.stringify({ command: 'start' }));
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.status = 'error';
            };
            
            this.ws.onclose = () => {
                console.log('Debug WebSocket closed');
                if (this.status !== 'completed' && this.status !== 'stopped') {
                    this.status = 'disconnected';
                }
                this.ws = null;
            };
        },
        
        handleWebSocketMessage(data) {
            switch (data.type) {
                case 'state_update':
                    if (data.session) {
                        this.currentStep = data.session.current_step;
                        this.context = data.session.context || {};
                        this.status = data.session.status;
                        this.history = data.session.history || [];
                    }
                    this.highlightCurrentStep();
                    break;
                
                case 'execution_started':
                    this.status = 'running';
                    console.log('Execution started');
                    break;
                
                case 'step_started':
                    if (data.data) {
                        this.currentStep = data.data.step_id;
                        console.log('Step started:', data.data.step_name);
                    }
                    if (data.session) {
                        this.context = data.session.context || {};
                        this.history = data.session.history || [];
                    }
                    this.highlightCurrentStep();
                    break;
                
                case 'step_completed':
                    console.log('Step completed:', data.data);
                    if (data.session) {
                        this.context = data.session.context || {};
                        this.history = data.session.history || [];
                    }
                    break;
                
                case 'execution_completed':
                    this.status = 'completed';
                    console.log('Execution completed');
                    break;
                
                case 'execution_error':
                    this.status = 'error';
                    console.error('Execution error:', data.error);
                    alert('Execution error: ' + data.error);
                    break;
                    
                case 'inspection':
                    console.log('Inspection result:', data.path, data.value);
                    break;
                    
                case 'error':
                    console.error('Debug error:', data.message);
                    this.status = 'error';
                    alert('Debug error: ' + data.message);
                    break;
            }
        },
        
        highlightCurrentStep() {
            // Remove all highlights
            document.querySelectorAll('#mermaid-diagram .node').forEach(node => {
                node.classList.remove('current', 'executed', 'has-breakpoint');
            });
            
            // Highlight executed steps and current step
            this.history.forEach(record => {
                const nodes = document.querySelectorAll('#mermaid-diagram .node');
                nodes.forEach(node => {
                    if (node.textContent.includes(record.step_name)) {
                        node.classList.add('executed');
                        if (!record.success) {
                            node.classList.add('error');
                        }
                    }
                });
            });
            
            // Highlight current step
            if (this.currentStep) {
                const currentStepData = this.currentFlow?.steps.find(s => s.id === this.currentStep);
                if (currentStepData) {
                    const nodes = document.querySelectorAll('#mermaid-diagram .node');
                    nodes.forEach(node => {
                        if (node.textContent.includes(currentStepData.name)) {
                            node.classList.add('current');
                        }
                    });
                }
            }
            
            // Show breakpoints
            this.breakpoints.forEach(stepId => {
                const step = this.currentFlow?.steps.find(s => s.id === stepId);
                if (step) {
                    const nodes = document.querySelectorAll('#mermaid-diagram .node');
                    nodes.forEach(node => {
                        if (node.textContent.includes(step.name)) {
                            node.classList.add('has-breakpoint');
                        }
                    });
                }
            });
        },
        
        continueDebug() {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ command: 'continue' }));
            }
        },
        
        stepOver() {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ command: 'step' }));
            }
        },
        
        stopDebug() {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ command: 'stop' }));
                this.ws.close();
            }
            this.status = 'stopped';
        },
        
        toggleBreakpoint(stepId) {
            if (this.breakpoints.has(stepId)) {
                this.breakpoints.delete(stepId);
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({ 
                        command: 'remove_breakpoint', 
                        step_id: stepId 
                    }));
                }
            } else {
                this.breakpoints.add(stepId);
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({ 
                        command: 'add_breakpoint', 
                        step_id: stepId 
                    }));
                }
            }
            this.highlightCurrentStep();
        },
        
        formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                fractionalSecondDigits: 3
            });
        }
    }
}).mount('#app');
// MDA-GENERATED-END: debugger-js