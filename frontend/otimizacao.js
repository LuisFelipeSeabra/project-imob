/**
 * Sistema de Otimização de Performance para Modelos 3D
 * Implementa LOD (Level of Detail) e compressão de modelos
 */

class OtimizadorPerformance {
    constructor() {
        this.lodLevels = [
            { distance: 0, quality: 1.0 },    // Alta qualidade
            { distance: 10, quality: 0.7 },   // Média qualidade
            { distance: 25, quality: 0.4 },   // Baixa qualidade
            { distance: 50, quality: 0.1 }    // Mínima qualidade
        ];
        
        this.cache = new Map();
        this.maxCacheSize = 100 * 1024 * 1024; // 100MB
        this.currentCacheSize = 0;
    }
    
    /**
     * Cria sistema LOD para um modelo
     * @param {THREE.Object3D} modelo - Modelo 3D original
     * @param {string} id - Identificador do modelo
     * @returns {THREE.LOD} Objeto LOD configurado
     */
    criarLOD(modelo, id) {
        const lod = new THREE.LOD();
        
        // Adicionar níveis de detalhe
        this.lodLevels.forEach((level, index) => {
            const modeloLOD = this.criarVersaoReduzida(modelo, level.quality);
            lod.addLevel(modeloLOD, level.distance);
        });
        
        // Configurar nome e posição
        lod.name = `LOD_${id}`;
        lod.position.copy(modelo.position);
        lod.rotation.copy(modelo.rotation);
        lod.scale.copy(modelo.scale);
        
        return lod;
    }
    
    /**
     * Cria versão reduzida do modelo
     * @param {THREE.Object3D} modelo - Modelo original
     * @param {number} quality - Qualidade (0-1)
     * @returns {THREE.Object3D} Modelo reduzido
     */
    criarVersaoReduzida(modelo, quality) {
        const clone = modelo.clone();
        
        // Reduzir complexidade baseada na qualidade
        clone.traverse((child) => {
            if (child.isMesh) {
                // Reduzir número de vértices
                if (child.geometry) {
                    const originalCount = child.geometry.attributes.position.count;
                    const targetCount = Math.floor(originalCount * quality);
                    
                    if (targetCount < originalCount) {
                        this.reduzirVertices(child.geometry, targetCount);
                    }
                }
                
                // Reduzir qualidade das texturas
                if (child.material && child.material.map) {
                    child.material.map = this.reduzirTextura(child.material.map, quality);
                }
            }
        });
        
        return clone;
    }
    
    /**
     * Reduz número de vértices de uma geometria
     * @param {THREE.BufferGeometry} geometry - Geometria original
     * @param {number} targetCount - Número alvo de vértices
     */
    reduzirVertices(geometry, targetCount) {
        const positions = geometry.attributes.position.array;
        const indices = geometry.index ? geometry.index.array : null;
        
        // Algoritmo de redução simples (pode ser melhorado)
        const step = Math.floor(positions.length / 3 / targetCount);
        
        if (step > 1) {
            const newPositions = [];
            const newIndices = [];
            
            for (let i = 0; i < positions.length; i += step * 3) {
                newPositions.push(positions[i], positions[i + 1], positions[i + 2]);
            }
            
            geometry.setAttribute('position', new THREE.Float32BufferAttribute(newPositions, 3));
            
            if (indices) {
                // Ajustar índices
                for (let i = 0; i < indices.length; i++) {
                    newIndices.push(Math.floor(indices[i] / step));
                }
                geometry.setIndex(newIndices);
            }
        }
    }
    
    /**
     * Reduz qualidade de uma textura
     * @param {THREE.Texture} texture - Textura original
     * @param {number} quality - Qualidade (0-1)
     * @returns {THREE.Texture} Textura reduzida
     */
    reduzirTextura(texture, quality) {
        if (!texture.image) return texture;
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        const newWidth = Math.floor(texture.image.width * quality);
        const newHeight = Math.floor(texture.image.height * quality);
        
        canvas.width = newWidth;
        canvas.height = newHeight;
        
        ctx.drawImage(texture.image, 0, 0, newWidth, newHeight);
        
        const newTexture = new THREE.Texture(canvas);
        newTexture.needsUpdate = true;
        
        return newTexture;
    }
    
    /**
     * Comprime modelo usando Draco
     * @param {THREE.Object3D} modelo - Modelo a comprimir
     * @returns {Promise<THREE.Object3D>} Modelo comprimido
     */
    async comprimirModelo(modelo) {
        try {
            // Verificar se Draco está disponível
            if (typeof DRACO === 'undefined') {
                console.warn('Draco não disponível, retornando modelo original');
                return modelo;
            }
            
            const exporter = new THREE.GLTFExporter();
            const dracoExporter = new THREE.DRACOExporter();
            
            // Exportar para GLB
            const gltf = await exporter.parseAsync(modelo, {
                binary: true,
                includeCustomExtensions: true
            });
            
            // Comprimir com Draco
            const compressed = await dracoExporter.encode(gltf);
            
            // Importar de volta
            const loader = new THREE.GLTFLoader();
            const compressedModel = await loader.parseAsync(compressed);
            
            return compressedModel.scene;
            
        } catch (error) {
            console.error('Erro ao comprimir modelo:', error);
            return modelo;
        }
    }
    
    /**
     * Implementa lazy loading de modelos
     * @param {string} url - URL do modelo
     * @param {THREE.Vector3} posicao - Posição para carregar
     * @param {number} raio - Raio de carregamento
     * @returns {Promise<THREE.Object3D>} Modelo carregado
     */
    async carregarLazy(url, posicao, raio = 50) {
        // Verificar se já está no cache
        if (this.cache.has(url)) {
            return this.cache.get(url).clone();
        }
        
        // Calcular distância até a posição
        const distancia = this.calcularDistancia(posicao);
        
        // Se muito longe, carregar versão de baixa qualidade
        if (distancia > raio) {
            return this.carregarModeloBaixaQualidade(url);
        }
        
        // Carregar modelo completo
        const modelo = await this.carregarModelo(url);
        
        // Adicionar ao cache
        this.adicionarCache(url, modelo);
        
        return modelo;
    }
    
    /**
     * Calcula distância até uma posição
     * @param {THREE.Vector3} posicao - Posição de referência
     * @returns {number} Distância calculada
     */
    calcularDistancia(posicao) {
        // Implementação simplificada - pode usar posição da câmera
        const camera = document.querySelector('a-camera');
        if (camera) {
            const cameraPos = camera.getAttribute('position');
            return Math.sqrt(
                Math.pow(cameraPos.x - posicao.x, 2) +
                Math.pow(cameraPos.y - posicao.y, 2) +
                Math.pow(cameraPos.z - posicao.z, 2)
            );
        }
        return 0;
    }
    
    /**
     * Carrega modelo de baixa qualidade
     * @param {string} url - URL do modelo
     * @returns {Promise<THREE.Object3D>} Modelo de baixa qualidade
     */
    async carregarModeloBaixaQualidade(url) {
        // Criar modelo simplificado
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const material = new THREE.MeshBasicMaterial({ color: 0xcccccc });
        return new THREE.Mesh(geometry, material);
    }
    
    /**
     * Carrega modelo completo
     * @param {string} url - URL do modelo
     * @returns {Promise<THREE.Object3D>} Modelo carregado
     */
    async carregarModelo(url) {
        return new Promise((resolve, reject) => {
            const loader = new THREE.GLTFLoader();
            
            loader.load(
                url,
                (gltf) => {
                    resolve(gltf.scene);
                },
                (progress) => {
                    // Progresso de carregamento
                    const percent = (progress.loaded / progress.total) * 100;
                    this.atualizarProgresso(percent);
                },
                (error) => {
                    reject(error);
                }
            );
        });
    }
    
    /**
     * Atualiza barra de progresso
     * @param {number} percent - Percentual de progresso
     */
    atualizarProgresso(percent) {
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = percent + '%';
        }
    }
    
    /**
     * Adiciona modelo ao cache
     * @param {string} url - URL do modelo
     * @param {THREE.Object3D} modelo - Modelo a cachear
     */
    adicionarCache(url, modelo) {
        // Estimar tamanho do modelo
        const size = this.estimarTamanho(modelo);
        
        // Verificar se cabe no cache
        if (this.currentCacheSize + size > this.maxCacheSize) {
            this.limparCache();
        }
        
        this.cache.set(url, modelo);
        this.currentCacheSize += size;
    }
    
    /**
     * Estima tamanho de um modelo
     * @param {THREE.Object3D} modelo - Modelo a estimar
     * @returns {number} Tamanho estimado em bytes
     */
    estimarTamanho(modelo) {
        let size = 0;
        
        modelo.traverse((child) => {
            if (child.isMesh && child.geometry) {
                // Estimar tamanho da geometria
                const positions = child.geometry.attributes.position;
                if (positions) {
                    size += positions.array.length * 4; // 4 bytes por float
                }
                
                // Estimar tamanho da textura
                if (child.material && child.material.map) {
                    const texture = child.material.map;
                    if (texture.image) {
                        size += texture.image.width * texture.image.height * 4; // RGBA
                    }
                }
            }
        });
        
        return size;
    }
    
    /**
     * Limpa cache removendo itens antigos
     */
    limparCache() {
        // Converter para array e ordenar por uso
        const entries = Array.from(this.cache.entries());
        
        // Remover metade dos itens mais antigos
        const toRemove = entries.slice(0, Math.floor(entries.length / 2));
        
        toRemove.forEach(([url, modelo]) => {
            this.cache.delete(url);
            this.currentCacheSize -= this.estimarTamanho(modelo);
        });
    }
    
    /**
     * Otimiza cena completa
     * @param {THREE.Scene} scene - Cena a otimizar
     */
    otimizarCena(scene) {
        // Otimizar todas as meshes
        scene.traverse((child) => {
            if (child.isMesh) {
                // Frustum culling
                child.frustumCulled = true;
                
                // Otimizar material
                if (child.material) {
                    child.material.needsUpdate = false;
                }
            }
        });
        
        // Configurar renderer
        const renderer = document.querySelector('a-scene').renderer;
        if (renderer) {
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        }
    }
    
    /**
     * Monitora performance e ajusta qualidade
     * @param {number} targetFPS - FPS alvo
     */
    monitorarPerformance(targetFPS = 60) {
        let lastTime = performance.now();
        let frameCount = 0;
        let currentFPS = 0;
        
        const checkPerformance = () => {
            const currentTime = performance.now();
            frameCount++;
            
            if (currentTime - lastTime >= 1000) {
                currentFPS = frameCount;
                frameCount = 0;
                lastTime = currentTime;
                
                // Ajustar qualidade se necessário
                if (currentFPS < targetFPS * 0.8) {
                    this.reduzirQualidade();
                } else if (currentFPS > targetFPS * 1.2) {
                    this.aumentarQualidade();
                }
            }
            
            requestAnimationFrame(checkPerformance);
        };
        
        checkPerformance();
    }
    
    /**
     * Reduz qualidade para melhorar performance
     */
    reduzirQualidade() {
        // Reduzir resolução
        const scene = document.querySelector('a-scene');
        if (scene) {
            scene.setAttribute('renderer', 'antialias: false');
        }
        
        // Reduzir sombras
        const lights = document.querySelectorAll('a-entity[light]');
        lights.forEach(light => {
            const lightComp = light.getAttribute('light');
            if (lightComp && lightComp.castShadow) {
                lightComp.castShadow = false;
            }
        });
    }
    
    /**
     * Aumenta qualidade quando performance está boa
     */
    aumentarQualidade() {
        // Aumentar resolução
        const scene = document.querySelector('a-scene');
        if (scene) {
            scene.setAttribute('renderer', 'antialias: true');
        }
        
        // Aumentar sombras
        const lights = document.querySelectorAll('a-entity[light]');
        lights.forEach(light => {
            const lightComp = light.getAttribute('light');
            if (lightComp && lightComp.castShadow) {
                lightComp.castShadow = true;
            }
        });
    }
}

// Instância global
window.otimizadorPerformance = new OtimizadorPerformance();

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OtimizadorPerformance;
}
