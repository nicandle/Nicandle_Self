/**
 * 星际驿站 (Stellar Station) - v2.2 Core Logic
 * 修复了白屏问题，增加了更多基因，优化了循环
 */

// ==========================================
// 0. Global Error Handling
// ==========================================
window.onerror = function(msg, url, line, col, error) {
    console.error("Global Error:", msg, error);
    // Optional: Visual feedback
};

// ==========================================
// 1. Constants & Config
// ==========================================

const Rarity = {
    COMMON: { id: 'common', name: '普通', color: '#b2bec3', mult: 1.0 },
    UNCOMMON: { id: 'uncommon', name: '优秀', color: '#2ecc71', mult: 1.2 },
    RARE: { id: 'rare', name: '稀有', color: '#3498db', mult: 1.5 },
    EPIC: { id: 'epic', name: '史诗', color: '#9b59b6', mult: 2.5 },
    LEGENDARY: { id: 'legendary', name: '传说', color: '#f1c40f', mult: 5.0 }
};

const ItemTypes = {
    GENE_FRAG: 'gene_frag', // 物种碎片
    GENE_MOD: 'gene_mod',   // 特征基因
    RESOURCE: 'resource',   // 资源/材料
    FURNITURE: 'furniture', // 家具
    FOOD: 'food',           // 食物
    BIOMASS: 'biomass'      // 生物质包
};

// ==========================================
// 2. Database (Expanded to 30+ Genes)
// ==========================================

const DB = {
    items: {
        // --- Species Fragments (Need 10) ---
        frag_fire_lizard: { id: 'frag_fire_lizard', name: '火蜥蜴碎片', type: ItemTypes.GENE_FRAG, element: 'fire', icon: '🦎', desc: '集齐10个可复原火蜥蜴' },
        frag_water_ball: { id: 'frag_water_ball', name: '水波球碎片', type: ItemTypes.GENE_FRAG, element: 'water', icon: '💧', desc: '集齐10个可复原水波球' },
        frag_grass_cat: { id: 'frag_grass_cat', name: '草叶猫碎片', type: ItemTypes.GENE_FRAG, element: 'grass', icon: '🐱', desc: '集齐10个可复原草叶猫' },
        frag_rock_golem: { id: 'frag_rock_golem', name: '岩石人碎片', type: ItemTypes.GENE_FRAG, element: 'earth', icon: '🗿', desc: '集齐10个可复原岩石人' },
        frag_wind_bird: { id: 'frag_wind_bird', name: '风灵鸟碎片', type: ItemTypes.GENE_FRAG, element: 'wind', icon: '🐦', desc: '集齐10个可复原风灵鸟' },
        frag_elec_mouse: { id: 'frag_elec_mouse', name: '闪电鼠碎片', type: ItemTypes.GENE_FRAG, element: 'electric', icon: '⚡', desc: '集齐10个可复原闪电鼠' },
        frag_ice_bear: { id: 'frag_ice_bear', name: '冰霜熊碎片', type: ItemTypes.GENE_FRAG, element: 'ice', icon: '🐻', desc: '集齐10个可复原冰霜熊' },
        frag_shadow_wolf: { id: 'frag_shadow_wolf', name: '暗影狼碎片', type: ItemTypes.GENE_FRAG, element: 'dark', icon: '🐺', desc: '集齐10个可复原暗影狼' },
        frag_light_fairy: { id: 'frag_light_fairy', name: '光之妖碎片', type: ItemTypes.GENE_FRAG, element: 'light', icon: '🧚', desc: '集齐10个可复原光之妖' },
        frag_metal_ant: { id: 'frag_metal_ant', name: '合金蚁碎片', type: ItemTypes.GENE_FRAG, element: 'metal', icon: '🐜', desc: '集齐10个可复原合金蚁' },
        // New Species
        frag_magma_turtle: { id: 'frag_magma_turtle', name: '熔岩龟碎片', type: ItemTypes.GENE_FRAG, element: 'fire', icon: '🐢', desc: '集齐10个可复原熔岩龟' },
        frag_void_squid: { id: 'frag_void_squid', name: '虚空鱿碎片', type: ItemTypes.GENE_FRAG, element: 'dark', icon: '🦑', desc: '集齐10个可复原虚空鱿' },
        frag_crystal_deer: { id: 'frag_crystal_deer', name: '晶体鹿碎片', type: ItemTypes.GENE_FRAG, element: 'light', icon: '🦌', desc: '集齐10个可复原晶体鹿' },
        frag_swamp_frog: { id: 'frag_swamp_frog', name: '沼泽蛙碎片', type: ItemTypes.GENE_FRAG, element: 'water', icon: '🐸', desc: '集齐10个可复原沼泽蛙' },
        frag_thunder_tiger: { id: 'frag_thunder_tiger', name: '雷霆虎碎片', type: ItemTypes.GENE_FRAG, element: 'electric', icon: '🐯', desc: '集齐10个可复原雷霆虎' },

        // --- Feature Modifiers (Need 1) ---
        mod_wings: { id: 'mod_wings', name: '幻光翼', type: ItemTypes.GENE_MOD, icon: '🦋', desc: '赋予飞行能力' },
        mod_horns: { id: 'mod_horns', name: '水晶角', type: ItemTypes.GENE_MOD, icon: '🦄', desc: '增加威慑力' },
        mod_scales: { id: 'mod_scales', name: '硬化鳞', type: ItemTypes.GENE_MOD, icon: '🛡️', desc: '增加防御' },
        mod_glow: { id: 'mod_glow', name: '生物光', type: ItemTypes.GENE_MOD, icon: '💡', desc: '在黑暗中发光' },
        mod_claw: { id: 'mod_claw', name: '利爪', type: ItemTypes.GENE_MOD, icon: '💅', desc: '增加采集效率' },
        mod_tail: { id: 'mod_tail', name: '长尾', type: ItemTypes.GENE_MOD, icon: '➰', desc: '增加平衡性' },
        mod_eye: { id: 'mod_eye', name: '千里眼', type: ItemTypes.GENE_MOD, icon: '👁️', desc: '增加探索视野' },
        mod_fur: { id: 'mod_fur', name: '厚皮毛', type: ItemTypes.GENE_MOD, icon: '🧶', desc: '增加抗寒性' },
        mod_fin: { id: 'mod_fin', name: '鱼鳍', type: ItemTypes.GENE_MOD, icon: '🦈', desc: '增加游泳速度' },
        mod_spikes: { id: 'mod_spikes', name: '尖刺', type: ItemTypes.GENE_MOD, icon: '🌵', desc: '反弹伤害' },
        mod_pattern: { id: 'mod_pattern', name: '迷彩纹', type: ItemTypes.GENE_MOD, icon: '🦓', desc: '增加隐蔽性' },
        mod_big: { id: 'mod_big', name: '巨大化', type: ItemTypes.GENE_MOD, icon: '🐘', desc: '体型变大' },
        mod_mini: { id: 'mod_mini', name: '迷你化', type: ItemTypes.GENE_MOD, icon: '🐭', desc: '体型变小' },
        mod_cute: { id: 'mod_cute', name: '萌化', type: ItemTypes.GENE_MOD, icon: '🎀', desc: '更容易被访客喜爱' },
        mod_scary: { id: 'mod_scary', name: '凶猛化', type: ItemTypes.GENE_MOD, icon: '👹', desc: '更容易吓跑敌人' },
        mod_ghost: { id: 'mod_ghost', name: '幽灵化', type: ItemTypes.GENE_MOD, icon: '👻', desc: '穿透物体' },
        mod_slime: { id: 'mod_slime', name: '粘液质', type: ItemTypes.GENE_MOD, icon: '💧', desc: '免疫物理伤害' },
        mod_metal: { id: 'mod_metal', name: '金属化', type: ItemTypes.GENE_MOD, icon: '🤖', desc: '极高防御' },

        // --- Resources ---
        res_biomass_s: { id: 'res_biomass_s', name: '生物质(小)', type: ItemTypes.BIOMASS, value: 10, icon: '🦠' },
        res_biomass_l: { id: 'res_biomass_l', name: '生物质(大)', type: ItemTypes.BIOMASS, value: 50, icon: '🧫' },
        res_coal: { id: 'res_coal', name: '燃煤', type: ItemTypes.RESOURCE, value: 20, icon: '⚫' },
        res_crystal: { id: 'res_crystal', name: '水晶', type: ItemTypes.RESOURCE, value: 50, icon: '💎' },
        res_herb: { id: 'res_herb', name: '草药', type: ItemTypes.RESOURCE, value: 15, icon: '🌿' },
        res_pearl: { id: 'res_pearl', name: '珍珠', type: ItemTypes.RESOURCE, value: 40, icon: '⚪' },
        res_feather: { id: 'res_feather', name: '风羽', type: ItemTypes.RESOURCE, value: 25, icon: '🪶' },
        
        // --- Food & Furniture ---
        food_can: { id: 'food_can', name: '高级罐头', type: ItemTypes.FOOD, price: 50, icon: '🥫', desc: '心情+50' },
        fur_bed: { id: 'fur_bed', name: '舒适软窝', type: ItemTypes.FURNITURE, price: 200, icon: '🛌', element: 'neutral', desc: '通用休息设施' },
        fur_heater: { id: 'fur_heater', name: '火山暖炉', type: ItemTypes.FURNITURE, price: 500, icon: '🔥', element: 'fire', desc: '火属性宠物最爱' },
        fur_pool: { id: 'fur_pool', name: '清凉泳池', type: ItemTypes.FURNITURE, price: 500, icon: '🏊', element: 'water', desc: '水属性宠物最爱' },
    }
};

// ==========================================
// 3. Game State
// ==========================================

const State = {
    resources: { biomass: 200, coins: 500 }, // Increased starting coins
    pets: [],
    activePetId: null, // For exploration
    inventory: [], // Exploration Backpack (max 6)
    storage: [],   // Home Warehouse (unlimited)
    furniture: [], // Placed furniture
    
    // Map State
    map: { nodes: [], edges: [], currentId: 0 },
    
    // Lab State
    lab: { selectedSpecies: null, selectedMods: [] },
    
    // System State
    scene: 'base',
    tempLoot: [], // For looting modal
    visitor: null,
    droppedItems: [] // Items on floor
};

// ==========================================
// 4. Systems
// ==========================================

const Factory = {
    createItem(templateId) {
        const t = DB.items[templateId];
        if (!t) return null;
        
        // Roll Rarity
        const r = Math.random();
        let rarity = Rarity.COMMON;
        if (r > 0.98) rarity = Rarity.LEGENDARY;
        else if (r > 0.9) rarity = Rarity.EPIC;
        else if (r > 0.75) rarity = Rarity.RARE;
        else if (r > 0.5) rarity = Rarity.UNCOMMON;

        // Calculate Score/Value
        const baseValue = t.value || 10;
        const value = Math.floor(baseValue * rarity.mult);
        
        return {
            uid: Math.random().toString(36).substr(2, 9),
            ...t,
            rarity: rarity,
            value: value,
            score: Math.floor(10 * rarity.mult) // Item score contribution
        };
    },

    createPet(speciesId, modIds) {
        const speciesItem = DB.items[speciesId];
        const mods = modIds.map(id => DB.items[id]);
        
        const analysis = this.analyzeGenetics(speciesItem, mods);

        return {
            id: 'pet_' + Date.now(),
            name: speciesItem.name.replace('碎片', ''),
            icon: speciesItem.icon,
            element: speciesItem.element,
            visualMods: mods.map(m => m.icon),
            score: analysis.score,
            mood: 100,
            tags: analysis.tags,
            drops: analysis.drops, // Store potential drops
            x: 300, y: 200,
            targetX: 300, targetY: 200,
            logs: [],
            lastDropTime: Date.now()
        };
    },

    // New Helper for AI Analysis
    analyzeGenetics(species, mods) {
        const tags = [];
        const drops = [];
        let scoreBonus = 0;

        // 1. Element Analysis
        if (species.element === 'fire') { tags.push('🔥 热情'); drops.push('res_coal'); }
        if (species.element === 'water') { tags.push('💧 冷静'); drops.push('res_pearl'); }
        if (species.element === 'grass') { tags.push('🌱 温和'); drops.push('res_herb'); }
        if (species.element === 'electric') { tags.push('⚡ 急躁'); drops.push('res_crystal'); }
        if (species.element === 'wind') { tags.push('🍃 自由'); drops.push('res_feather'); }
        
        // 2. Mod Analysis
        mods.forEach(m => {
            scoreBonus += 50;
            if (m.id === 'mod_wings') { tags.push('✈️ 飞行'); drops.push('res_feather'); }
            if (m.id === 'mod_horns') { tags.push('⚔️ 好斗'); }
            if (m.id === 'mod_cute') { tags.push('💖 社牛'); }
            if (m.id === 'mod_glow') { tags.push('💡 显眼'); drops.push('res_crystal'); }
        });

        // Default Drop
        drops.push('res_biomass_s');

        // 3. Random Personality
        const personalities = ['吃货', '懒癌', '多动症', '强迫症', '乐天派', '社恐', '霸道'];
        tags.push(personalities[Math.floor(Math.random() * personalities.length)]);

        // 4. Score Calculation (Base 100 + Mods + Random Flux)
        const totalScore = 100 + scoreBonus + Math.floor(Math.random() * 50);

        return { tags, drops, score: totalScore };
    }
};

const MapSystem = {
    ctx: null,

    init() {
        const canvas = document.getElementById('map-canvas');
        if (!canvas) return;
        this.ctx = canvas.getContext('2d');
        canvas.addEventListener('mousedown', (e) => this.handleClick(e));
    },

    generate() {
        State.map.nodes = [];
        State.map.edges = [];
        const layers = 5;
        const width = 600;
        const height = 400;

        // Start Node
        State.map.nodes.push({ id: 0, x: 50, y: height/2, type: 'start', revealed: true });

        let nodeId = 1;
        for (let i = 1; i <= layers; i++) {
            const count = 2 + Math.floor(Math.random() * 2);
            for (let j = 0; j < count; j++) {
                const typeRoll = Math.random();
                let type = 'resource';
                if (typeRoll > 0.7) type = 'danger';
                if (typeRoll > 0.9) type = 'event';

                State.map.nodes.push({
                    id: nodeId,
                    x: 50 + i * 100 + Math.random() * 20,
                    y: (height / (count + 1)) * (j + 1) + Math.random() * 20,
                    type: type,
                    element: ['fire', 'water', 'grass'][Math.floor(Math.random() * 3)],
                    revealed: false,
                    looted: false
                });

                // Connect to previous layer
                const prevLayerStart = State.map.nodes.length - count - (i===1?1:3); // Rough approximation
                const target = Math.max(0, nodeId - Math.floor(Math.random() * 2) - 1);
                State.map.edges.push({ from: target, to: nodeId });
                
                nodeId++;
            }
        }
        
        State.map.currentId = 0;
        this.reveal(0);
        this.draw();
        this.updateExplorerInfo();
    },

    reveal(nodeId) {
        State.map.edges.forEach(e => {
            if (e.from === nodeId) {
                const n = State.map.nodes.find(node => node.id === e.to);
                if (n) n.revealed = true;
            }
        });
    },

    handleClick(e) {
        const rect = e.target.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (e.target.width / rect.width);
        const y = (e.clientY - rect.top) * (e.target.height / rect.height);

        State.map.nodes.forEach(node => {
            if (!node.revealed) return;
            const dist = Math.hypot(node.x - x, node.y - y);
            if (dist < 15) {
                this.selectNode(node);
            }
        });
    },

    selectNode(node) {
        const pet = State.pets.find(p => p.id === State.activePetId);
        if (!pet) { alert("请先在实验室制造并选择一只宠物！"); return; }

        // Check adjacency
        const isConnected = State.map.edges.some(e => 
            (e.from === State.map.currentId && e.to === node.id) || 
            (e.to === State.map.currentId && e.from === node.id)
        );

        if (node.id === State.map.currentId) return;

        if (isConnected) {
            // Move logic
            if (node.type === 'danger' && node.element !== pet.element) {
                if (!confirm(`警告：前方是【${node.element}】环境，你的宠物是【${pet.element}】，可能会受伤。继续吗？`)) return;
                pet.mood -= 20;
                UISystem.log(`宠物因环境不适，心情下降了。`);
            }

            State.map.currentId = node.id;
            this.reveal(node.id);
            this.draw();
            
            // Trigger Event
            if (!node.looted) {
                if (node.type === 'resource' || node.type === 'danger') {
                    this.spawnLoot(node);
                }
            }
        }
    },

    spawnLoot(node) {
        State.tempLoot = [];
        const count = 2 + Math.floor(Math.random() * 3);
        const pool = Object.keys(DB.items).filter(k => k.startsWith('frag') || k.startsWith('res'));
        
        for(let i=0; i<count; i++) {
            const id = pool[Math.floor(Math.random() * pool.length)];
            State.tempLoot.push(Factory.createItem(id));
        }
        
        node.looted = true;
        UISystem.openLootModal();
    },

    updateExplorerInfo() {
        const div = document.getElementById('explorer-info');
        if (!div) return;
        const pet = State.pets.find(p => p.id === State.activePetId);
        if (pet) {
            div.innerHTML = `
                <div style="font-size:24px;">${pet.icon}</div>
                <div>
                    <div><strong>${pet.name}</strong></div>
                    <div style="font-size:12px; color:#666;">评分:${pet.score}</div>
                </div>
            `;
        } else {
            div.innerHTML = "未选择宠物";
        }
    },

    draw() {
        if (!this.ctx) return;
        const ctx = this.ctx;
        ctx.fillStyle = '#2c3e50';
        ctx.fillRect(0, 0, 600, 400);

        // Draw Edges
        ctx.strokeStyle = '#7f8c8d';
        ctx.lineWidth = 2;
        State.map.edges.forEach(e => {
            const n1 = State.map.nodes.find(n => n.id === e.from);
            const n2 = State.map.nodes.find(n => n.id === e.to);
            if (n1 && n2 && n1.revealed && n2.revealed) {
                ctx.beginPath();
                ctx.moveTo(n1.x, n1.y);
                ctx.lineTo(n2.x, n2.y);
                ctx.stroke();
            }
        });

        // Draw Nodes
        State.map.nodes.forEach(n => {
            if (!n.revealed) return;
            ctx.beginPath();
            ctx.arc(n.x, n.y, 12, 0, Math.PI*2);
            
            // Color
            if (n.id === State.map.currentId) ctx.fillStyle = '#f1c40f'; // Current
            else if (n.type === 'start') ctx.fillStyle = '#2ecc71';
            else if (n.type === 'danger') ctx.fillStyle = '#e74c3c';
            else if (n.type === 'resource') ctx.fillStyle = n.looted ? '#95a5a6' : '#3498db';
            else ctx.fillStyle = '#9b59b6';
            
            ctx.fill();
            ctx.stroke();

            // Icon
            ctx.fillStyle = 'white';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            let icon = '';
            if (n.id === State.map.currentId) icon = '🤠';
            else if (n.type === 'resource') icon = n.looted ? '❌' : '📦';
            else if (n.type === 'danger') icon = '⚠️';
            ctx.fillText(icon, n.x, n.y);
        });
    }
};

const PetSystem = {
    update() {
        const now = Date.now();
        State.pets.forEach(pet => {
            // 1. Movement
            const dx = pet.targetX - pet.x;
            const dy = pet.targetY - pet.y;
            if (Math.hypot(dx, dy) > 5) {
                pet.x += dx * 0.05;
                pet.y += dy * 0.05;
            } else {
                // Random wander
                if (Math.random() < 0.02) {
                    pet.targetX = 50 + Math.random() * 500;
                    pet.targetY = 50 + Math.random() * 300;
                }
            }

            // 2. Passive Drop
            if (now - pet.lastDropTime > 5000) { // Every 5s
                pet.lastDropTime = now;
                // Chance based on mood
                if (Math.random() < (pet.mood / 200)) { 
                    this.dropItem(pet);
                }
            }
        });
    },

    dropItem(pet) {
        // Use pet's specific drops if available, else random
        let itemId = 'res_biomass_s';
        if (pet.drops && pet.drops.length > 0) {
            itemId = pet.drops[Math.floor(Math.random() * pet.drops.length)];
        } else {
            itemId = Math.random() > 0.5 ? 'res_biomass_s' : 'res_crystal';
        }

        const item = Factory.createItem(itemId);
        // Value modifier based on mood
        item.value = Math.floor(item.value * (0.5 + pet.mood/100));
        
        State.droppedItems.push({
            item: item,
            x: pet.x,
            y: pet.y,
            vx: (Math.random() - 0.5) * 5,
            vy: -5
        });
        UISystem.showFloat(`💎`, pet.x, pet.y);
        pet.logs.unshift(`${new Date().toLocaleTimeString()} 掉落了 ${item.name}`);
    },

    interact(petId) {
        const pet = State.pets.find(p => p.id === petId);
        if (!pet) return;
        
        // Show Details Modal
        const content = `
            <div style="display:flex; gap:20px;">
                <div style="font-size:60px;">${pet.icon}</div>
                <div>
                    <h3>${pet.name}</h3>
                    <p>综合评分: <span style="color:gold; font-weight:bold;">${pet.score}</span></p>
                    <p>心情: ${pet.mood}/100</p>
                    <p>性格: ${pet.tags.join(', ')}</p>
                </div>
            </div>
            <hr>
            <h4>📜 玩耍日志</h4>
            <div style="height:150px; overflow-y:auto; background:#f9f9f9; padding:5px; font-size:12px;">
                ${pet.logs.map(l => `<div>${l}</div>`).join('')}
            </div>
            <div style="margin-top:10px; display:flex; gap:10px;">
                <button class="btn primary" onclick="PetSystem.feed('${pet.id}')">喂食 (消耗罐头)</button>
                <button class="btn success" onclick="PetSystem.play('${pet.id}')">抚摸 (+心情)</button>
            </div>
        `;
        UISystem.showModal("伙伴详情", content);
    },

    feed(petId) {
        const pet = State.pets.find(p => p.id === petId);
        const foodIdx = State.storage.findIndex(i => i.id === 'food_can');
        if (foodIdx === -1) { alert("仓库里没有高级罐头！"); return; }
        
        State.storage.splice(foodIdx, 1);
        pet.mood = Math.min(100, pet.mood + 50);
        pet.logs.unshift(`${new Date().toLocaleTimeString()} 吃了一个美味罐头`);
        UISystem.closeModal();
        UISystem.update();
    },

    play(petId) {
        const pet = State.pets.find(p => p.id === petId);
        pet.mood = Math.min(100, pet.mood + 10);
        pet.logs.unshift(`${new Date().toLocaleTimeString()} 被主人摸了摸头`);
        UISystem.closeModal();
        UISystem.update();
    }
};

const HomeSystem = {
    canvas: null,
    ctx: null,

    init() {
        const c = document.getElementById('base-canvas');
        if (!c) return;
        this.canvas = c;
        this.ctx = c.getContext('2d');
        
        this.canvas.addEventListener('mousedown', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
            const y = (e.clientY - rect.top) * (this.canvas.height / rect.height);
            
            // 1. Check Drops
            for (let i = State.droppedItems.length - 1; i >= 0; i--) {
                const d = State.droppedItems[i];
                if (Math.hypot(d.x - x, d.y - y) < 20) {
                    State.storage.push(d.item);
                    State.droppedItems.splice(i, 1);
                    UISystem.showFloat(`+${d.item.name}`, x, y, 'green');
                    UISystem.update();
                    return;
                }
            }

            // 2. Check Pets
            for (let p of State.pets) {
                if (Math.hypot(p.x - x, p.y - y) < 30) {
                    PetSystem.interact(p.id);
                    return;
                }
            }
            
            // 3. Check Visitor
            if (State.visitor) {
                if (Math.hypot(State.visitor.x - x, State.visitor.y - y) < 30) {
                    VisitorSystem.interact();
                    return;
                }
            }
        });
        
        VisitorSystem.init();
    },

    draw() {
        if (!this.ctx) return;
        const ctx = this.ctx;
        ctx.clearRect(0, 0, 600, 400);

        // Furniture
        State.furniture.forEach(f => {
            ctx.font = '30px Arial';
            ctx.fillText(f.icon, f.x, f.y);
        });

        // Visitor
        if (State.visitor) {
            ctx.font = '40px Arial';
            ctx.fillText(State.visitor.icon, State.visitor.x, State.visitor.y);
            ctx.font = '12px Arial';
            ctx.fillStyle = 'orange';
            ctx.fillText("!", State.visitor.x + 10, State.visitor.y - 20);
        }

        // Pets
        State.pets.forEach(p => {
            ctx.font = '40px Arial';
            ctx.fillText(p.icon, p.x, p.y);
            
            // Mood bar
            ctx.fillStyle = 'red';
            ctx.fillRect(p.x - 20, p.y - 40, 40, 4);
            ctx.fillStyle = '#2ecc71';
            ctx.fillRect(p.x - 20, p.y - 40, 40 * (p.mood/100), 4);
            
            // Name
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(p.name, p.x, p.y + 25);
        });

        // Drops
        State.droppedItems.forEach(d => {
            // Physics
            d.x += d.vx;
            d.y += d.vy;
            d.vy += 0.5; // Gravity
            d.vx *= 0.9;
            if (d.y > 380) { d.y = 380; d.vy *= -0.5; }

            ctx.font = '20px Arial';
            ctx.fillText(d.item.icon, d.x, d.y);
        });
    }
};

const VisitorSystem = {
    init() {
        // Spawn first visitor quickly
        setTimeout(() => this.spawn(), 3000);

        setInterval(() => {
            if (!State.visitor && Math.random() < 0.5) { // Increased chance
                this.spawn();
            }
        }, 5000);
    },

    spawn() {
        if (State.visitor) return;
        
        State.visitor = {
            x: 50, y: 350,
            icon: ['👽', '🤖', '👩‍🚀'][Math.floor(Math.random()*3)],
            req: { id: 'res_biomass_s', count: 5 },
            reward: { coins: 200 }
        };
        UISystem.showFloat("访客到访!", 50, 320, 'orange');
    },

    interact() {
        if (!State.visitor) return;
        const v = State.visitor;
        const has = State.storage.filter(i => i.id === v.req.id).length;
        const itemInfo = DB.items[v.req.id];
        
        const content = `
            <h3>访客委托</h3>
            <p>我需要 ${v.req.count} 个 ${itemInfo.name}。</p>
            <p>当前拥有: ${has}/${v.req.count}</p>
            <p>奖励: ${v.reward.coins} 星际币</p>
            <button class="btn primary" onclick="VisitorSystem.complete()" ${has < v.req.count ? 'disabled' : ''}>交付</button>
            <button class="btn danger" onclick="VisitorSystem.leave()">送客</button>
        `;
        UISystem.showModal("访客", content);
    },

    complete() {
        const v = State.visitor;
        let removed = 0;
        for (let i = State.storage.length - 1; i >= 0; i--) {
            if (State.storage[i].id === v.req.id) {
                State.storage.splice(i, 1);
                removed++;
                if (removed >= v.req.count) break;
            }
        }
        State.resources.coins += v.reward.coins;
        this.leave();
    },

    leave() {
        State.visitor = null;
        UISystem.closeModal();
        UISystem.update();
    }
};

const ShopSystem = {
    open() {
        const content = `
            <div class="storage-tabs">
                <button class="tab-btn active" onclick="ShopSystem.renderBuy()">购买</button>
                <button class="tab-btn" onclick="ShopSystem.renderSell()">出售</button>
            </div>
            <div id="shop-list" style="height:300px; overflow-y:auto; padding:10px;"></div>
        `;
        UISystem.showModal("星际商店", content);
        this.renderBuy();
    },

    renderBuy() {
        const list = document.getElementById('shop-list');
        if (!list) return;
        list.innerHTML = '';

        // Filter buyable items (Furniture, Food)
        const buyables = Object.values(DB.items).filter(i => i.price);

        buyables.forEach(item => {
            const div = document.createElement('div');
            div.className = 'shop-item';
            div.innerHTML = `
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:24px;">${item.icon}</span>
                    <div>
                        <div>${item.name}</div>
                        <div style="font-size:12px; color:#666;">${item.desc || ''}</div>
                    </div>
                </div>
                <button class="btn sm success" onclick="ShopSystem.buy('${item.id}')">💰 ${item.price}</button>
            `;
            list.appendChild(div);
        });
    },

    renderSell() {
        const list = document.getElementById('shop-list');
        if (!list) return;
        list.innerHTML = '';

        // Filter sellable items (Resources, Biomass)
        const sellables = State.storage.map((item, index) => ({...item, index})).filter(i => i.value);

        if (sellables.length === 0) {
            list.innerHTML = '<div style="text-align:center; color:#999; padding:20px;">没有可出售的物品</div>';
            return;
        }

        sellables.forEach(item => {
            const div = document.createElement('div');
            div.className = 'shop-item';
            div.innerHTML = `
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:24px;">${item.icon}</span>
                    <div>
                        <div>${item.name}</div>
                        <div style="font-size:12px; color:#666;">品质: ${item.rarity.name}</div>
                    </div>
                </div>
                <button class="btn sm action" onclick="ShopSystem.sell(${item.index})">💰 +${item.value}</button>
            `;
            list.appendChild(div);
        });
    },

    buy(itemId) {
        const item = DB.items[itemId];
        if (State.resources.coins >= item.price) {
            State.resources.coins -= item.price;
            State.storage.push(Factory.createItem(itemId));
            
            // If furniture, place it immediately for simplicity in this demo
            if (item.type === ItemTypes.FURNITURE) {
                State.furniture.push({
                    id: item.id,
                    icon: item.icon,
                    x: 100 + Math.random() * 400,
                    y: 100 + Math.random() * 200
                });
                alert(`购买成功！${item.name} 已放置在家园中。`);
            } else {
                alert(`购买成功！${item.name} 已放入仓库。`);
            }
            
            UISystem.update();
            this.renderBuy(); // Refresh
        } else {
            alert("星际币不足！");
        }
    },

    sell(index) {
        // Re-find item by index is tricky if array mutates, but since we re-render every time, it's ok for simple demo
        // Actually, better to filter and map index first.
        // But here, let's just trust the index passed from renderSell which reads current State.storage
        const item = State.storage[index];
        if (item) {
            State.resources.coins += item.value;
            State.storage.splice(index, 1);
            UISystem.update();
            this.renderSell();
        }
    }
};

const LabSystem = {
    render() {
        const list = document.getElementById('gene-list');
        if (!list) return;
        list.innerHTML = '';
        
        // Count fragments and calculate Average Score
        const geneData = {}; // { id: { count: 0, totalScore: 0 } }

        State.storage.forEach(i => {
            if (i.type === ItemTypes.GENE_FRAG || i.type === ItemTypes.GENE_MOD) {
                if (!geneData[i.id]) geneData[i.id] = { count: 0, totalScore: 0 };
                geneData[i.id].count++;
                geneData[i.id].totalScore += (i.score || 10);
            }
        });

        // Helper to render items
        const renderGroup = (title, filterFn, reqCount) => {
            const header = document.createElement('h4');
            header.innerText = title;
            header.style.borderBottom = "1px solid #eee";
            header.style.paddingBottom = "5px";
            header.style.marginTop = "10px";
            list.appendChild(header);

            Object.values(DB.items).filter(filterFn).forEach(item => {
                const data = geneData[item.id] || { count: 0, totalScore: 0 };
                const count = data.count;
                const avgScore = count > 0 ? Math.floor(data.totalScore / count) : 0;
                
                const div = document.createElement('div');
                div.className = 'gene-item';
                div.innerHTML = `
                    <div style="display:flex; flex-direction:column;">
                        <span>${item.icon} ${item.name}</span>
                        <span style="font-size:10px; color:#666;">均分: <span style="color:orange">${avgScore}</span></span>
                    </div>
                    <span style="color:${count>=reqCount?'green':'red'}; font-weight:bold;">${count}/${reqCount}</span>
                `;
                
                if (count >= reqCount) {
                    div.onclick = () => reqCount === 10 ? this.selectSpecies(item) : this.toggleMod(item);
                    div.style.cursor = 'pointer';
                    div.style.background = reqCount === 10 ? '#e8f5e9' : '#e3f2fd';
                    
                    // Highlight selected
                    if (State.lab.selectedSpecies && State.lab.selectedSpecies.id === item.id) div.style.border = "2px solid green";
                    if (State.lab.selectedMods.some(m => m.id === item.id)) div.style.border = "2px solid blue";

                } else {
                    div.style.opacity = 0.5;
                }
                list.appendChild(div);
            });
        };

        renderGroup("🧬 物种基因 (需10碎片)", i => i.type === ItemTypes.GENE_FRAG, 10);
        renderGroup("✨ 特征基因 (需1碎片)", i => i.type === ItemTypes.GENE_MOD, 1);
    },

    selectSpecies(item) {
        State.lab.selectedSpecies = item;
        this.updatePreview();
        this.render(); // Re-render to show selection highlight
    },

    toggleMod(item) {
        const idx = State.lab.selectedMods.findIndex(m => m.id === item.id);
        if (idx >= 0) State.lab.selectedMods.splice(idx, 1);
        else {
            if (State.lab.selectedMods.length >= 2) State.lab.selectedMods.shift();
            State.lab.selectedMods.push(item);
        }
        this.updatePreview();
        this.render(); // Re-render to show selection highlight
    },

    updatePreview() {
        const preview = document.getElementById('preview-image');
        const label = document.getElementById('preview-label');
        const btn = document.getElementById('realize-btn');
        const aiDiv = document.getElementById('ai-analysis');
        
        if (!State.lab.selectedSpecies) {
            preview.innerHTML = '<span>请选择物种</span>';
            btn.disabled = true;
            aiDiv.classList.add('hidden');
            return;
        }

        const s = State.lab.selectedSpecies;
        const mods = State.lab.selectedMods;
        
        // Generate AI Analysis
        const analysis = Factory.analyzeGenetics(s, mods);

        preview.innerHTML = `
            <div style="font-size:80px; position:relative;">
                ${s.icon}
                ${mods.map((m, i) => `<span style="position:absolute; font-size:30px; top:${i*20}px; right:-20px;">${m.icon}</span>`).join('')}
            </div>
        `;
        label.innerText = "模拟中...";
        btn.disabled = false;

        // Update AI Analysis Panel
        aiDiv.classList.remove('hidden');
        aiDiv.innerHTML = `
            <h4 style="margin:0 0 10px 0; border-bottom:1px solid #555; padding-bottom:5px;">🤖 AI 基因分析</h4>
            <div style="font-size:13px; line-height:1.6;">
                <div><strong>预计评分:</strong> <span style="color:gold; font-size:1.2em;">${analysis.score}</span></div>
                <div><strong>性格特征:</strong> ${analysis.tags.map(t => `<span style="background:#34495e; padding:2px 4px; border-radius:3px; margin-right:2px;">${t}</span>`).join('')}</div>
                <div style="margin-top:5px;"><strong>潜在掉落:</strong></div>
                <div style="display:flex; gap:5px; flex-wrap:wrap;">
                    ${analysis.drops.map(dId => {
                        const item = DB.items[dId];
                        return `<span style="border:1px solid #7f8c8d; padding:2px 5px; border-radius:10px;">${item.icon} ${item.name}</span>`;
                    }).join('')}
                </div>
            </div>
        `;
    },

    realize() {
        if (State.resources.biomass < 100) { alert("生物质不足！"); return; }
        
        // Consume items
        const sId = State.lab.selectedSpecies.id;
        for(let i=0; i<10; i++) {
            const idx = State.storage.findIndex(item => item.id === sId);
            if (idx > -1) State.storage.splice(idx, 1);
        }
        State.lab.selectedMods.forEach(m => {
            const idx = State.storage.findIndex(item => item.id === m.id);
            if (idx > -1) State.storage.splice(idx, 1);
        });
        
        State.resources.biomass -= 100;
        
        const newPet = Factory.createPet(sId, State.lab.selectedMods.map(m => m.id));
        State.pets.push(newPet);
        if (!State.activePetId) State.activePetId = newPet.id;
        
        alert(`恭喜！${newPet.name} 诞生了！`);
        State.scene = 'base';
        UISystem.switchScene('base');
    }
};

const UISystem = {
    currentStorageTab: 'all',

    init() {
        // Bind Nav
        document.getElementById('nav-base').onclick = () => this.switchScene('base');
        document.getElementById('nav-lab').onclick = () => this.switchScene('lab');
        document.getElementById('nav-exploration').onclick = () => this.switchScene('exploration');
        
        // Bind Lab
        document.getElementById('realize-btn').onclick = () => LabSystem.realize();
        
        // Bind Exploration
        document.getElementById('node-action-btn').onclick = () => MapSystem.selectNode(MapSystem.selectedNode); 
        document.getElementById('retreat-btn').onclick = () => this.switchScene('base');

        // Bind Shop (NEW)
        const shopBtn = document.getElementById('shop-btn');
        if(shopBtn) shopBtn.onclick = () => ShopSystem.open();

        this.update();
    },

    setStorageTab(tab) {
        this.currentStorageTab = tab;
        
        // Update Buttons
        const map = { 'all': 0, 'gene': 1, 'item': 2, 'living': 3 };
        const buttons = document.querySelectorAll('.storage-tabs .tab-btn');
        buttons.forEach((b, i) => {
            if (i === map[tab]) b.classList.add('active');
            else b.classList.remove('active');
        });

        this.renderStorage();
    },

    switchScene(scene) {
        State.scene = scene;
        
        // Update Nav Buttons
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`nav-${scene}`).classList.add('active');

        // Update Views
        document.querySelectorAll('.view').forEach(el => {
            el.classList.remove('active');
            el.classList.add('hidden');
        });
        
        const view = document.getElementById(`${scene}-view`);
        view.classList.remove('hidden');
        view.classList.add('active');
        
        if (scene === 'exploration') {
            if (State.pets.length === 0) {
                alert("请先去实验室创造一只宠物！");
                this.switchScene('lab');
                return;
            }
            if (!State.activePetId) State.activePetId = State.pets[0].id;
            MapSystem.generate();
        } else if (scene === 'lab') {
            LabSystem.render();
        }
        
        this.update();
    },

    update() {
        // Resources
        document.getElementById('biomass-display').innerText = State.resources.biomass;
        document.getElementById('coins-display').innerText = State.resources.coins;
        
        // Pet Status
        const pet = State.pets.find(p => p.id === State.activePetId);
        document.getElementById('pet-name').innerText = pet ? pet.name : '无';
        
        // Storage
        this.renderStorage();
        
        // Backpack
        const bpCount = document.getElementById('backpack-count');
        const bpGrid = document.getElementById('backpack-grid');
        if (bpCount && bpGrid) {
            bpCount.innerText = State.inventory.length;
            bpGrid.innerHTML = '';
            State.inventory.forEach(item => {
                const div = document.createElement('div');
                div.className = 'slot filled';
                div.innerText = item.icon;
                div.style.borderColor = item.rarity.color;
                bpGrid.appendChild(div);
            });
        }
    },

    renderStorage() {
        const list = document.getElementById('storage-list');
        if (!list) return;
        list.innerHTML = '';
        
        const tab = this.currentStorageTab;
        const filtered = State.storage.filter(item => {
            if (tab === 'all') return true;
            if (tab === 'gene') return item.type === ItemTypes.GENE_FRAG || item.type === ItemTypes.GENE_MOD;
            if (tab === 'item') return item.type === ItemTypes.RESOURCE || item.type === ItemTypes.BIOMASS;
            if (tab === 'living') return item.type === ItemTypes.FURNITURE || item.type === ItemTypes.FOOD;
            return true;
        });

        if (filtered.length === 0) {
            list.innerHTML = '<div style="padding:10px; color:#999; text-align:center;">暂无此类物品</div>';
            return;
        }

        filtered.forEach(item => {
            const div = document.createElement('div');
            div.className = 'item-card';
            div.style.borderLeft = `4px solid ${item.rarity.color}`;
            
            let actionBtn = '';
            if (item.type === ItemTypes.FOOD) {
                actionBtn = `<button class="btn sm primary" style="margin-left:auto;" onclick="PetSystem.feed('${State.activePetId}')">喂食</button>`;
            }

            div.innerHTML = `
                <span>${item.icon} ${item.name}</span>
                <span style="font-size:10px; color:#666; margin-left:5px;">${item.rarity.name}</span>
                ${actionBtn}
            `;
            list.appendChild(div);
        });
    },

    openLootModal() {
        const content = `
            <div style="display:flex; gap:20px; height:300px;">
                <div style="flex:1; background:#eee; padding:10px; border-radius:4px;">
                    <h4>📦 发现物资</h4>
                    <div id="loot-container" style="display:grid; grid-template-columns:repeat(4,1fr); gap:5px;"></div>
                </div>
                <div style="flex:1; background:#dce4e8; padding:10px; border-radius:4px;">
                    <h4>🎒 背包 (${State.inventory.length}/6)</h4>
                    <div id="loot-backpack" style="display:grid; grid-template-columns:repeat(4,1fr); gap:5px;"></div>
                </div>
            </div>
            <div style="text-align:right; margin-top:10px;">
                <button class="btn primary" onclick="UISystem.lootTakeAll()">全部拿走</button>
                <button class="btn success" onclick="UISystem.closeLootModal()">完成搜刮</button>
            </div>
        `;
        this.showModal("搜刮", content);
        this.renderLoot();
    },

    renderLoot() {
        const cDiv = document.getElementById('loot-container');
        const bDiv = document.getElementById('loot-backpack');
        if (!cDiv || !bDiv) return;

        cDiv.innerHTML = '';
        State.tempLoot.forEach((item, idx) => {
            const div = document.createElement('div');
            div.className = 'slot filled';
            div.innerText = item.icon;
            div.style.borderColor = item.rarity.color;
            div.onclick = () => {
                if (State.inventory.length >= 6) { alert("背包已满！"); return; }
                State.inventory.push(item);
                State.tempLoot.splice(idx, 1);
                this.renderLoot();
            };
            cDiv.appendChild(div);
        });

        bDiv.innerHTML = '';
        State.inventory.forEach((item, idx) => {
            const div = document.createElement('div');
            div.className = 'slot filled';
            div.innerText = item.icon;
            div.style.borderColor = item.rarity.color;
            div.onclick = () => {
                State.tempLoot.push(item);
                State.inventory.splice(idx, 1);
                this.renderLoot();
            };
            bDiv.appendChild(div);
        });
    },

    lootTakeAll() {
        while (State.tempLoot.length > 0) {
            if (State.inventory.length >= 6) break;
            State.inventory.push(State.tempLoot.shift());
        }
        this.renderLoot();
    },

    closeLootModal() {
        this.closeModal();
        this.update();
    },

    showModal(title, content) {
        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-content').innerHTML = content;
        document.getElementById('modal-overlay').classList.remove('hidden');
    },

    closeModal() {
        document.getElementById('modal-overlay').classList.add('hidden');
    },

    showFloat(text, x, y, color='gold') {
        const div = document.createElement('div');
        div.innerText = text;
        div.style.position = 'absolute';
        div.style.left = x + 'px';
        div.style.top = y + 'px';
        div.style.color = color;
        div.style.fontWeight = 'bold';
        div.style.pointerEvents = 'none';
        div.style.transition = '1s';
        document.getElementById('base-view').appendChild(div); 
        
        setTimeout(() => {
            div.style.top = (y - 50) + 'px';
            div.style.opacity = 0;
        }, 50);
        setTimeout(() => div.remove(), 1000);
    },
    
    log(msg) {
        const box = document.getElementById('log-box');
        if (box) box.innerHTML = `<div>> ${msg}</div>` + box.innerHTML;
    }
};

// ==========================================
// 5. Main Loop
// ==========================================

function gameLoop() {
    if (State.scene === 'base') {
        PetSystem.update();
        HomeSystem.draw();
    }
    requestAnimationFrame(gameLoop);
}

// Start
window.onload = () => {
    try {
        UISystem.init();
        HomeSystem.init();
        MapSystem.init();
        gameLoop();
        
        // Give starter items - ENHANCED for better early game
        // 1. Fire Lizard Set (Enough for 1)
        for(let i=0; i<10; i++) State.storage.push(Factory.createItem('frag_fire_lizard'));
        // 2. Water Ball Set (Enough for 1)
        for(let i=0; i<10; i++) State.storage.push(Factory.createItem('frag_water_ball'));
        // 3. Grass Cat Set (Enough for 1)
        for(let i=0; i<10; i++) State.storage.push(Factory.createItem('frag_grass_cat'));
        
        // 3. Modifiers
        State.storage.push(Factory.createItem('mod_wings'));
        State.storage.push(Factory.createItem('mod_cute'));
        State.storage.push(Factory.createItem('mod_glow'));
        State.storage.push(Factory.createItem('mod_horns'));
        
        // 4. Consumables
        State.storage.push(Factory.createItem('food_can'));
        State.storage.push(Factory.createItem('food_can'));
        State.storage.push(Factory.createItem('fur_bed')); // Give a basic bed
        
        // Initial Notification
        setTimeout(() => {
            alert("欢迎来到星际驿站！\n已为您发放【火蜥蜴】【水波球】【草叶猫】的完整基因片段。\n请前往【基因实验室】孵化您的第一只伙伴！");
            UISystem.switchScene('lab'); // Auto-switch to lab for first time
        }, 100);

        UISystem.update();
    } catch (e) {
        alert("Init Error: " + e.message);
    }
};

// Expose for HTML
window.PetSystem = PetSystem;
window.VisitorSystem = VisitorSystem;
window.UISystem = UISystem;
window.LabSystem = LabSystem;
window.MapSystem = MapSystem;
window.ShopSystem = ShopSystem;