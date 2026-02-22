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
            // --- Species Fragments (Need 10) - Varied Sizes ---
            frag_fire_lizard: { id: 'frag_fire_lizard', name: '火蜥蜴碎片', type: ItemTypes.GENE_FRAG, element: 'fire', icon: '🦎', desc: '集齐10个可复原火蜥蜴', w: 1, h: 2 },
            frag_water_ball: { id: 'frag_water_ball', name: '水波球碎片', type: ItemTypes.GENE_FRAG, element: 'water', icon: '💧', desc: '集齐10个可复原水波球', w: 2, h: 1 },
            frag_grass_cat: { id: 'frag_grass_cat', name: '草叶猫碎片', type: ItemTypes.GENE_FRAG, element: 'grass', icon: '🐱', desc: '集齐10个可复原草叶猫', w: 1, h: 1 },
            frag_rock_golem: { id: 'frag_rock_golem', name: '岩石人碎片', type: ItemTypes.GENE_FRAG, element: 'earth', icon: '🗿', desc: '集齐10个可复原岩石人', w: 2, h: 2 },
            frag_wind_bird: { id: 'frag_wind_bird', name: '风灵鸟碎片', type: ItemTypes.GENE_FRAG, element: 'wind', icon: '🐦', desc: '集齐10个可复原风灵鸟', w: 1, h: 2 },
            frag_elec_mouse: { id: 'frag_elec_mouse', name: '闪电鼠碎片', type: ItemTypes.GENE_FRAG, element: 'electric', icon: '⚡', desc: '集齐10个可复原闪电鼠', w: 1, h: 1 },
            frag_ice_bear: { id: 'frag_ice_bear', name: '冰霜熊碎片', type: ItemTypes.GENE_FRAG, element: 'ice', icon: '🐻', desc: '集齐10个可复原冰霜熊', w: 2, h: 2 },
            frag_shadow_wolf: { id: 'frag_shadow_wolf', name: '暗影狼碎片', type: ItemTypes.GENE_FRAG, element: 'dark', icon: '🐺', desc: '集齐10个可复原暗影狼', w: 2, h: 1 },
            frag_light_fairy: { id: 'frag_light_fairy', name: '光之妖碎片', type: ItemTypes.GENE_FRAG, element: 'light', icon: '🧚', desc: '集齐10个可复原光之妖', w: 1, h: 1 },
            frag_metal_ant: { id: 'frag_metal_ant', name: '合金蚁碎片', type: ItemTypes.GENE_FRAG, element: 'metal', icon: '🐜', desc: '集齐10个可复原合金蚁', w: 1, h: 1 },
            // New Species
            frag_magma_turtle: { id: 'frag_magma_turtle', name: '熔岩龟碎片', type: ItemTypes.GENE_FRAG, element: 'fire', icon: '🐢', desc: '集齐10个可复原熔岩龟', w: 2, h: 2 },
            frag_void_squid: { id: 'frag_void_squid', name: '虚空鱿碎片', type: ItemTypes.GENE_FRAG, element: 'dark', icon: '🦑', desc: '集齐10个可复原虚空鱿', w: 1, h: 2 },
            frag_crystal_deer: { id: 'frag_crystal_deer', name: '晶体鹿碎片', type: ItemTypes.GENE_FRAG, element: 'light', icon: '🦌', desc: '集齐10个可复原晶体鹿', w: 2, h: 1 },
            frag_swamp_frog: { id: 'frag_swamp_frog', name: '沼泽蛙碎片', type: ItemTypes.GENE_FRAG, element: 'water', icon: '🐸', desc: '集齐10个可复原沼泽蛙', w: 1, h: 1 },
            frag_thunder_tiger: { id: 'frag_thunder_tiger', name: '雷霆虎碎片', type: ItemTypes.GENE_FRAG, element: 'electric', icon: '🐯', desc: '集齐10个可复原雷霆虎', w: 2, h: 2 },

            // --- Feature Modifiers (Need 1) - Size Varied ---
            mod_wings: { id: 'mod_wings', name: '幻光翼', type: ItemTypes.GENE_MOD, icon: '🦋', desc: '赋予飞行能力', w: 2, h: 1 },
            mod_horns: { id: 'mod_horns', name: '水晶角', type: ItemTypes.GENE_MOD, icon: '🦄', desc: '增加威慑力', w: 1, h: 2 },
            mod_scales: { id: 'mod_scales', name: '硬化鳞', type: ItemTypes.GENE_MOD, icon: '🛡️', desc: '增加防御', w: 1, h: 1 },
            mod_glow: { id: 'mod_glow', name: '生物光', type: ItemTypes.GENE_MOD, icon: '💡', desc: '在黑暗中发光', w: 1, h: 1 },
            mod_claw: { id: 'mod_claw', name: '利爪', type: ItemTypes.GENE_MOD, icon: '💅', desc: '增加采集效率', w: 1, h: 1 },
            mod_tail: { id: 'mod_tail', name: '长尾', type: ItemTypes.GENE_MOD, icon: '➰', desc: '增加平衡性', w: 2, h: 1 },
            mod_eye: { id: 'mod_eye', name: '千里眼', type: ItemTypes.GENE_MOD, icon: '👁️', desc: '增加探索视野', w: 1, h: 1 },
            mod_fur: { id: 'mod_fur', name: '厚皮毛', type: ItemTypes.GENE_MOD, icon: '🧶', desc: '增加抗寒性', w: 2, h: 1 },
            mod_fin: { id: 'mod_fin', name: '鱼鳍', type: ItemTypes.GENE_MOD, icon: '🦈', desc: '增加游泳速度', w: 1, h: 2 },
            mod_spikes: { id: 'mod_spikes', name: '尖刺', type: ItemTypes.GENE_MOD, icon: '🌵', desc: '反弹伤害', w: 1, h: 1 },
            mod_pattern: { id: 'mod_pattern', name: '迷彩纹', type: ItemTypes.GENE_MOD, icon: '🦓', desc: '增加隐蔽性', w: 2, h: 1 },
            mod_big: { id: 'mod_big', name: '巨大化', type: ItemTypes.GENE_MOD, icon: '🐘', desc: '体型变大', w: 2, h: 2 },
            mod_mini: { id: 'mod_mini', name: '迷你化', type: ItemTypes.GENE_MOD, icon: '🐭', desc: '体型变小', w: 1, h: 1 },
            mod_cute: { id: 'mod_cute', name: '萌化', type: ItemTypes.GENE_MOD, icon: '🎀', desc: '更容易被访客喜爱', w: 1, h: 1 },
            mod_scary: { id: 'mod_scary', name: '凶猛化', type: ItemTypes.GENE_MOD, icon: '👹', desc: '更容易吓跑敌人', w: 1, h: 1 },
            mod_ghost: { id: 'mod_ghost', name: '幽灵化', type: ItemTypes.GENE_MOD, icon: '👻', desc: '穿透物体', w: 1, h: 1 },
            mod_slime: { id: 'mod_slime', name: '粘液质', type: ItemTypes.GENE_MOD, icon: '💧', desc: '免疫物理伤害', w: 1, h: 1 },
            mod_metal: { id: 'mod_metal', name: '金属化', type: ItemTypes.GENE_MOD, icon: '🤖', desc: '极高防御', w: 1, h: 1 },

            // --- Resources ---
            res_biomass_s: { id: 'res_biomass_s', name: '生物质', type: ItemTypes.BIOMASS, value: 10, icon: '🦠', w: 1, h: 1 },
            res_biomass_l: { id: 'res_biomass_l', name: '生物质(大)', type: ItemTypes.BIOMASS, value: 50, icon: '🧫', w: 2, h: 1 },
            res_coal: { id: 'res_coal', name: '燃煤', type: ItemTypes.RESOURCE, value: 20, icon: '⚫', w: 1, h: 2 },
            res_crystal: { id: 'res_crystal', name: '水晶', type: ItemTypes.RESOURCE, value: 50, icon: '💎', w: 1, h: 1 },
            res_herb: { id: 'res_herb', name: '草药', type: ItemTypes.RESOURCE, value: 15, icon: '🌿', w: 2, h: 1 },
            res_pearl: { id: 'res_pearl', name: '珍珠', type: ItemTypes.RESOURCE, value: 40, icon: '⚪', w: 1, h: 1 },
            res_feather: { id: 'res_feather', name: '风羽', type: ItemTypes.RESOURCE, value: 25, icon: '🪶', w: 1, h: 2 },
            res_wool: { id: 'res_wool', name: '软羊毛', type: ItemTypes.RESOURCE, value: 30, icon: '🧶', w: 1, h: 1, desc: '从宠物身上薅下来的' },
            res_poop: { id: 'res_poop', name: '便便', type: ItemTypes.RESOURCE, value: 1, icon: '💩', w: 1, h: 1, desc: '如果不清理会影响心情' },
            
            // --- Buildings & Service Furniture ---
            bld_shop: { id: 'bld_shop', name: '星际商店', type: 'building', icon: '🏪', desc: '买卖物资的地方', size: 0, x: 500, y: 50 },
            bld_travel: { id: 'bld_travel', name: '旅行向导', type: 'building', icon: '🛸', desc: '前往好友家园', size: 0, x: 50, y: 50 },
            
            fur_feeder: { id: 'fur_feeder', name: '自动喂食器', type: ItemTypes.FURNITURE, price: 300, icon: '🥣', element: 'neutral', desc: '自动解决饥饿问题', w: 2, h: 1, radius: 60 },
            fur_toy_box: { id: 'fur_toy_box', name: '玩具箱', type: ItemTypes.FURNITURE, price: 400, icon: '🧸', element: 'neutral', desc: '快速恢复心情', w: 2, h: 1, radius: 60 },
            fur_shower: { id: 'fur_shower', name: '声波淋浴', type: ItemTypes.FURNITURE, price: 600, icon: '🚿', element: 'water', desc: '保持清洁', w: 2, h: 2, radius: 60 },
            
            // --- New Buildings (V2.3) ---
            bld_gym: { id: 'bld_gym', name: '重力训练场', type: 'building', price: 800, icon: '🏋️', desc: '锻炼可提升宠物评分', size: 0, x: 100, y: 100, radius: 80 },
            bld_music: { id: 'bld_music', name: '安抚音箱', type: 'building', price: 600, icon: '🎵', desc: '播放舒缓音乐，禁止周围打架', size: 0, x: 100, y: 100, radius: 150 },
            bld_med: { id: 'bld_med', name: '纳米治疗舱', type: 'building', price: 1000, icon: '🚑', desc: '快速恢复健康', size: 0, x: 100, y: 100, radius: 60 },
            bld_cleaner: { id: 'bld_cleaner', name: '清洁机器人', type: 'building', price: 1500, icon: '🤖', desc: '自动清理范围内的便便', size: 0, x: 100, y: 100, radius: 200 },
            fur_scratch: { id: 'fur_scratch', name: '全息猫抓板', type: ItemTypes.FURNITURE, price: 250, icon: '🧶', element: 'neutral', desc: '大幅提升心情', w: 1, h: 2, radius: 60 },
            fur_bonfire: { id: 'fur_bonfire', name: '社交营火', type: ItemTypes.FURNITURE, price: 400, icon: '🔥', element: 'fire', desc: '吸引宠物聚集', w: 2, h: 2, radius: 100 },

            // --- Strange Food & Toys ---
            food_slime_jelly: { id: 'food_slime_jelly', name: '史莱姆凝胶', type: ItemTypes.FOOD, price: 30, icon: '🍮', desc: '口感奇怪的果冻', w: 1, h: 1 },
            food_rock_candy: { id: 'food_rock_candy', name: '发光岩糖', type: ItemTypes.FOOD, price: 40, icon: '🍬', desc: '硬得像石头的糖', w: 1, h: 1 },
            toy_laser: { id: 'toy_laser', name: '激光笔', type: ItemTypes.FURNITURE, price: 150, icon: '🔦', element: 'neutral', desc: '宠物都爱追着跑', w: 1, h: 1, radius: 40 },
            toy_bone: { id: 'toy_bone', name: '奇怪的骨头', type: ItemTypes.FURNITURE, price: 100, icon: '🦴', element: 'neutral', desc: '不知道是什么生物的', w: 2, h: 1, radius: 40 },

            // --- Food & Furniture ---
            food_can: { id: 'food_can', name: '高级罐头', type: ItemTypes.FOOD, price: 50, icon: '🥫', desc: '心情+50', w: 1, h: 1 },
            fur_bed: { id: 'fur_bed', name: '舒适软窝', type: ItemTypes.FURNITURE, price: 200, icon: '🛌', element: 'neutral', desc: '通用休息设施', w: 2, h: 1, radius: 80 },
            fur_heater: { id: 'fur_heater', name: '火山暖炉', type: ItemTypes.FURNITURE, price: 500, icon: '🔥', element: 'fire', desc: '火属性宠物最爱', w: 1, h: 2, radius: 120 },
            fur_pool: { id: 'fur_pool', name: '清凉泳池', type: ItemTypes.FURNITURE, price: 500, icon: '🏊', element: 'water', desc: '水属性宠物最爱', w: 2, h: 2, radius: 120 },
        }
    };

// ==========================================
// 3. Game State
// ==========================================

const State = {
    resources: { biomass: 500, coins: 2000 }, // Increased starting coins
    pets: [],
    activePetId: null, // For exploration
    inventory: [], // Exploration Backpack (Array of {id, x, y})
    maxLoad: 9,   // 3x3 Grid
    storage: [],   // Home Warehouse (unlimited)
    furniture: [], // Placed furniture
    
    // Map State
    map: { nodes: [], edges: [], currentId: 0 },
    
    // Lab State
    lab: { selectedSpecies: null, selectedMods: [], candidates: [], selectedCandidateIdx: -1 },
    
    // System State
    scene: 'base',
    tempLoot: [], // For looting modal
    visitor: null,
    droppedItems: [], // Items on floor
    
    // Interaction State (NEW)
    drag: { petId: null, startX: 0, startY: 0, isDragging: false, vx: 0, vy: 0 },
    hoveredFurnitureId: null, // Track hovered furniture for radius display,
    
    // Exploration State
    carriedBiomass: 0, // Stackable biomass during exploration

    // Friend Home State
    friendHome: {
        pets: [],
        furniture: [],
        droppedItems: [],
        ownerName: "土豪金"
    }
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
        let value = Math.floor(baseValue * rarity.mult);
        
        // Randomize Biomass Value
        if (t.type === ItemTypes.BIOMASS) {
            value = 5 + Math.floor(Math.random() * 15); // 5-20
        }

        return {
            uid: Math.random().toString(36).substr(2, 9),
            ...t,
            rarity: rarity,
            value: value,
            score: Math.floor(10 * rarity.mult) // Item score contribution
        };
    },

    createPet(speciesId, modIds, analysisData = null) {
        const speciesItem = DB.items[speciesId];
        const mods = modIds.map(id => DB.items[id]);
        
        // Use provided analysis or generate new one
        const analysis = analysisData || this.analyzeGenetics(speciesItem, mods);

        return {
            id: 'pet_' + Date.now(),
            name: speciesItem.name.replace('碎片', ''),
            icon: speciesItem.icon,
            element: speciesItem.element,
            visualMods: mods.map(m => m.icon),
            score: analysis.score,
            mood: 100,
            hunger: 80, 
            health: 100, // New: Health stat
            poopMeter: 0, 
            currentEmoji: '', 
            actionState: 'idle', 
            actionTimer: 0,
            fightCooldown: 0, // New: Cooldown for fighting
            woolGrowth: 0, // 0-100, for shearing
            tags: analysis.tags,
            drops: analysis.drops, // Store potential drops
            x: 300, y: 200,
            targetX: 300, targetY: 200,
            vx: 0, vy: 0, // Physics
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

        // 3. Random Personality (The Reroll Target)
        const personalities = ['吃货', '懒癌', '多动症', '强迫症', '乐天派', '社牛', '霸道', '好奇宝宝', '邋遢', '好斗'];
        
        let p = '';
        // Force personality for first 2 pets (Demo Scripting)
        if (State.pets.length === 0) p = '邋遢';
        else if (State.pets.length === 1) p = '好斗';
        else p = personalities[Math.floor(Math.random() * personalities.length)];

        if (!tags.includes(p)) tags.push(p);

        // 4. Score Calculation (Base 100 + Mods + Random Flux)
        const totalScore = 100 + scoreBonus + Math.floor(Math.random() * 50);

        return { tags, drops, score: totalScore };
    }
};

// ==========================================
// Map System (Rewritten V3.0)
// ==========================================
// ==========================================
// Inventory System (Tetris Grid)
// ==========================================
const InventorySystem = {
    cols: 3,
    rows: 3,
    
    // Check if item fits at x,y
    canPlace(item, x, y, excludeUid = null) {
        if (x < 0 || y < 0 || x + item.w > this.cols || y + item.h > this.rows) return false;
        
        // Check collision
        for (const slot of State.inventory) {
            if (slot.uid === excludeUid) continue; // Skip self when moving
            const slotItem = DB.items[slot.id];
            
            // AABB Collision
            if (x < slot.x + slotItem.w &&
                x + item.w > slot.x &&
                y < slot.y + slotItem.h &&
                y + item.h > slot.y) {
                return false;
            }
        }
        return true;
    },

    // Find first empty spot
    findSpot(item) {
        for (let y = 0; y < this.rows; y++) {
            for (let x = 0; x < this.cols; x++) {
                if (this.canPlace(item, x, y)) {
                    return { x, y };
                }
            }
        }
        return null;
    },

    add(item) {
        const spot = this.findSpot(item);
        if (spot) {
            State.inventory.push({
                ...item, // Preserve Rarity/Value
                x: spot.x,
                y: spot.y
            });
            return true;
        }
        return false;
    },

    addAt(item, x, y) {
        if (this.canPlace(item, x, y)) {
            State.inventory.push({
                ...item, // Preserve Rarity/Value
                x: x,
                y: y
            });
            return true;
        }
        return false;
    },
    
    remove(uid) {
        const idx = State.inventory.findIndex(i => i.uid === uid);
        if (idx > -1) State.inventory.splice(idx, 1);
    }
};

const MapSystem = {
    canvas: null,
    ctx: null,
    nodes: [],
    edges: [],
    currentNodeId: 0,
    riskLevel: 0,
    mapElement: 'neutral',
    width: 0,
    height: 0,

    // Called once on startup
    init() {
        console.log("MapSystem V3: Init");
        this.canvas = document.getElementById('map-canvas');
        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d');
            this.canvas.addEventListener('mousedown', (e) => this.handleClick(e));
            window.addEventListener('resize', () => this.resize());
        }
    },

    // Called when switching to Exploration Scene
    show() {
        console.log("MapSystem V3: Show");
        
        if (State.pets.length === 0) {
            alert("请先在实验室创造一只宠物！");
            UISystem.switchScene('lab');
            return;
        }

        // Show Pet Selection Modal
        const content = `
            <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(120px, 1fr)); gap:10px;">
                ${State.pets.map(p => `
                    <div onclick="MapSystem.selectPet('${p.id}')" style="
                        border:2px solid ${p.id === State.activePetId ? '#f1c40f' : '#ddd'}; 
                        padding:10px; border-radius:8px; cursor:pointer; text-align:center;
                        background:${p.health < 50 || p.hunger < 20 ? '#fff5f5' : 'white'};
                        transition: all 0.2s;
                    " onmouseover="this.style.borderColor='#3498db'" onmouseout="this.style.borderColor='${p.id === State.activePetId ? '#f1c40f' : '#ddd'}'">
                        <div style="font-size:40px;">${p.icon}</div>
                        <div style="font-weight:bold; margin:5px 0;">${p.name}</div>
                        <div style="font-size:12px; line-height:1.5;">
                            <div>❤️ ${Math.floor(p.health)}/100</div>
                            <div>🍖 ${Math.floor(p.hunger)}/100</div>
                            <div>😊 ${Math.floor(p.mood)}/100</div>
                        </div>
                        ${p.health < 20 || p.hunger < 10 ? '<div style="color:red; font-size:10px; margin-top:5px;">⚠️ 状态不佳</div>' : ''}
                    </div>
                `).join('')}
            </div>
            <div style="margin-top:10px; font-size:12px; color:#666; text-align:center;">
                点击选择一只宠物作为队长。状态过低无法出战。
            </div>
        `;
        
        UISystem.showModal("🚩 选择探险队长", content);
    },

    selectPet(petId) {
        const pet = State.pets.find(p => p.id === petId);
        if (!pet) return;

        if (pet.health < 20) {
            alert("这只宠物太虚弱了(HP<20)，无法探险！请先去治疗。");
            return;
        }
        if (pet.hunger < 10) {
            alert("这只宠物太饿了(饱食<10)，无法探险！请先喂食。");
            return;
        }

        State.activePetId = petId;
        UISystem.closeModal();
        
        // Proceed with Map Init
        setTimeout(() => {
            this.resize();
            this.startNewExploration();
        }, 100);
    },

    resize() {
        if (!this.canvas) return;
        const parent = this.canvas.parentElement;
        if (parent) {
            this.width = parent.clientWidth;
            this.height = parent.clientHeight;
            this.canvas.width = this.width;
            this.canvas.height = this.height;
            console.log(`MapSystem V3: Resized to ${this.width}x${this.height}`);
            this.draw();
        }
    },

    startNewExploration() {
        const elements = ['fire', 'water', 'grass', 'electric', 'wind'];
        this.mapElement = elements[Math.floor(Math.random() * elements.length)];
        this.riskLevel = 0;
        State.carriedBiomass = 0; // Reset carried biomass
        this.generateGraph();
        this.currentNodeId = 0; // Start at 0
        
        UISystem.log(`进入了 [${this.mapElement}] 区域。`);
        this.updateUI();
        this.draw();
    },

    generateGraph() {
        this.nodes = [];
        this.edges = [];
        let idCounter = 0;

        const layers = 6;
        const layerWidth = (this.width - 100) / layers;
        const startX = 50;

        // 1. Generate Layers
        const layerNodes = [];
        
        for (let l = 0; l <= layers; l++) {
            const currentLayer = [];
            // Node count: Start/End = 1, Middle = 2-3
            const count = (l === 0 || l === layers) ? 1 : (2 + Math.floor(Math.random() * 2));
            const sectorH = this.height / count;

            for (let i = 0; i < count; i++) {
                const node = {
                    id: idCounter++,
                    layer: l,
                    x: startX + l * layerWidth + (Math.random() - 0.5) * 20,
                    y: (i * sectorH) + (sectorH / 2) + (Math.random() - 0.5) * 40,
                    type: 'resource', // Default
                    revealed: l === 0, // Reveal start
                    cleared: l === 0
                };

                // Assign Types
                if (l === 0) node.type = 'start';
                else if (l === layers) node.type = 'extract';
                else {
                    const r = Math.random();
                    if (r < 0.5) node.type = 'resource';
                    else if (r < 0.8) node.type = 'danger';
                    else node.type = 'event';
                }

                this.nodes.push(node);
                currentLayer.push(node);
            }
            layerNodes.push(currentLayer);
        }

        // 2. Connect Layers (Forward only)
        for (let l = 0; l < layers; l++) {
            const current = layerNodes[l];
            const next = layerNodes[l+1];

            // Each current node connects to at least 1 next node
            current.forEach(n1 => {
                // Connect to random 1-2 nodes in next layer
                const targets = [...next].sort(() => Math.random() - 0.5).slice(0, Math.min(next.length, 2));
                targets.forEach(n2 => {
                    this.edges.push({ from: n1.id, to: n2.id });
                });
            });

            // Ensure each next node has at least 1 incoming
            next.forEach(n2 => {
                const hasIncoming = this.edges.some(e => e.to === n2.id);
                if (!hasIncoming) {
                    const n1 = current[Math.floor(Math.random() * current.length)];
                    this.edges.push({ from: n1.id, to: n2.id });
                }
            });
        }
        
        console.log(`MapSystem V3: Generated ${this.nodes.length} nodes.`);
    },

    handleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        // Calculate scale in case of CSS resizing
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;

        // Check Node Clicks
        for (const node of this.nodes) {
            // Allow clicking if revealed OR visible neighbor (Fog of War logic)
            if (!node.revealed && !this.isNeighborRevealed(node.id)) continue;
            
            const dist = Math.hypot(node.x - x, node.y - y);
            if (dist < 30) { // Increased hit area
                this.onNodeClick(node);
                return;
            }
        }
    },

    onNodeClick(node) {
        if (node.id === this.currentNodeId) return;

        // Check connectivity
        const connected = this.edges.some(e => 
            (e.from === this.currentNodeId && e.to === node.id) || 
            (e.from === node.id && e.to === this.currentNodeId)
        );

        if (!connected) {
            UISystem.log("太远了，无法到达。");
            return;
        }

        // Check Hunger
        const pet = State.pets.find(p => p.id === State.activePetId);
        if (pet.hunger < 2) {
            alert("饱食度不足，无法移动！");
            return;
        }
        pet.hunger -= 2;

        // Show Float
        const container = document.querySelector('.map-container');
        UISystem.showFloat(`-2 🍖`, node.x, node.y, '#e74c3c', container);

        // Move
        this.currentNodeId = node.id;
        this.riskLevel += 5;
        this.revealNeighbors(node.id);
        this.triggerEvent(node);
        this.draw();
        this.updateUI();
    },

    revealNeighbors(nodeId) {
        this.edges.forEach(e => {
            if (e.from === nodeId) {
                const target = this.nodes.find(n => n.id === e.to);
                if (target) target.revealed = true;
            }
        });
    },

    triggerEvent(node) {
        const pet = State.pets.find(p => p.id === State.activePetId);

        if (node.cleared) {
            // Re-loot Logic
            if (node.type === 'resource') {
                if (confirm(`该区域已探索。是否消耗 10 饱食度再次搜刮？\n(当前饱食: ${Math.floor(pet.hunger)})`)) {
                    if (pet.hunger >= 10) {
                        pet.hunger -= 10;
                        UISystem.log("🔍 再次搜刮...");
                        this.spawnLoot(1); // Re-loot gets 1 Biomass + 1 Random
                    } else {
                        alert("饱食度不足！");
                    }
                }
            }
            return;
        }
        node.cleared = true;
        
        if (node.type === 'resource') {
            UISystem.log("📦 发现物资！");
            this.spawnLoot(1 + Math.floor(Math.random() * 2)); // 1 Biomass + 1-2 Random
        } else if (node.type === 'danger') {
            const roll = Math.random() * 100;
            const difficulty = 30 + this.riskLevel - (pet.element === this.mapElement ? 20 : 0);
            if (roll < difficulty) {
                UISystem.log(`⚠️ 遭遇危险！(判定失败)`);
                pet.health -= 15;
                pet.mood -= 15;
            } else {
                UISystem.log(`🛡️ 成功化解危机！`);
                this.spawnLoot(2 + Math.floor(Math.random() * 2)); // Better loot for danger
            }
        } else if (node.type === 'event') {
            UISystem.log("✨ 奇遇：心情变好了。");
            pet.mood = Math.min(100, pet.mood + 20);
        } else if (node.type === 'extract') {
            if (confirm("抵达撤离点！要返航吗？")) {
                UISystem.switchScene('base');
                UISystem.log("✅ 探险成功返航！");
            }
        }
    },

    spawnLoot(count) {
        State.tempLoot = [];
        
        // 1. Guaranteed Biomass
        State.tempLoot.push(Factory.createItem('res_biomass_s'));

        // 2. Weighted Pool (Food/Toys : Gene Frag : Gene Mod = 3 : 2 : 1)
        const pools = {
            foodToy: Object.values(DB.items).filter(i => i.type === ItemTypes.FOOD || (i.type === ItemTypes.FURNITURE && i.price < 500)),
            geneFrag: Object.values(DB.items).filter(i => i.type === ItemTypes.GENE_FRAG),
            geneMod: Object.values(DB.items).filter(i => i.type === ItemTypes.GENE_MOD)
        };

        for(let i=0; i<count; i++) {
            const r = Math.random() * 6; // Total weight 6 (3+2+1)
            let template = null;

            if (r < 3) {
                // Food/Toy (Weight 3)
                template = pools.foodToy[Math.floor(Math.random() * pools.foodToy.length)];
            } else if (r < 5) {
                // Gene Frag (Weight 2)
                template = pools.geneFrag[Math.floor(Math.random() * pools.geneFrag.length)];
            } else {
                // Gene Mod (Weight 1)
                template = pools.geneMod[Math.floor(Math.random() * pools.geneMod.length)];
            }

            if (template) {
                State.tempLoot.push(Factory.createItem(template.id));
            }
        }
        
        UISystem.openLootModal();
    },

    updateUI() {
        const pet = State.pets.find(p => p.id === State.activePetId);
        const div = document.getElementById('explorer-info');
        if (div && pet) {
            div.innerHTML = `
                <div style="font-size:24px;">${pet.icon}</div>
                <div>
                    <div><strong>${pet.name}</strong></div>
                    <div style="font-size:12px;">HP:${Math.floor(pet.health)} | Mood:${Math.floor(pet.mood)}</div>
                    <div style="font-size:12px; color:#e74c3c;">危险: ${this.riskLevel}%</div>
                </div>
            `;
        }
    },

    draw() {
        if (!this.ctx) return;
        const ctx = this.ctx;

        // Clear
        ctx.fillStyle = '#2c3e50';
        ctx.fillRect(0, 0, this.width, this.height);

        // Edges
        ctx.lineWidth = 2;
        this.edges.forEach(e => {
            const n1 = this.nodes.find(n => n.id === e.from);
            const n2 = this.nodes.find(n => n.id === e.to);
            
            // Fix: Draw if either end is revealed (Fog of War logic)
            if (n1 && n2 && (n1.revealed || n2.revealed)) {
                ctx.strokeStyle = '#7f8c8d';
                
                // Highlight fully explored paths
                if (n1.revealed && n2.revealed) ctx.strokeStyle = '#ecf0f1';
                
                ctx.beginPath();
                ctx.moveTo(n1.x, n1.y);
                ctx.lineTo(n2.x, n2.y);
                ctx.stroke();
            }
        });

        // Nodes
        this.nodes.forEach(n => {
            if (!n.revealed && !this.isNeighborRevealed(n.id)) return;

            ctx.beginPath();
            ctx.arc(n.x, n.y, 15, 0, Math.PI*2);
            
            // Color
            if (n.id === this.currentNodeId) ctx.fillStyle = '#f1c40f';
            else if (n.type === 'start') ctx.fillStyle = '#2ecc71';
            else if (n.type === 'extract') ctx.fillStyle = '#9b59b6';
            else if (n.type === 'danger') ctx.fillStyle = '#e74c3c';
            else if (n.type === 'resource') ctx.fillStyle = '#3498db';
            else ctx.fillStyle = '#95a5a6';
            
            if (!n.revealed) ctx.fillStyle = '#34495e'; // Fog

            ctx.fill();
            ctx.strokeStyle = 'white';
            ctx.stroke();

            // Icon
            ctx.fillStyle = 'white';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            let icon = '?';
            if (n.revealed) {
                if (n.type === 'start') icon = '🏠';
                else if (n.type === 'extract') icon = '🚀';
                else if (n.type === 'danger') icon = '⚠️';
                else if (n.type === 'resource') icon = '📦';
                else if (n.type === 'event') icon = '✨';
                
                if (n.cleared && n.type !== 'start' && n.type !== 'extract') icon = '✅';
            }
            if (n.id === this.currentNodeId) icon = '🤠';
            
            ctx.fillText(icon, n.x, n.y);
        });
    },

    isNeighborRevealed(nodeId) {
        return this.edges.some(e => 
            (e.to === nodeId && e.from === this.currentNodeId) ||
            (e.from === nodeId && e.to === this.currentNodeId)
        );
    }
};

const PetSystem = {
    update() {
        const now = Date.now();
        // Update pets based on current scene
        const pets = State.scene === 'friend_home' ? State.friendHome.pets : State.pets;
        const droppedItems = State.scene === 'friend_home' ? State.friendHome.droppedItems : State.droppedItems;

        pets.forEach(pet => {
            // 0. Dragging Physics Override
            if (State.drag.petId === pet.id && State.drag.isDragging) {
                pet.vx = 0; pet.vy = 0;
                pet.currentEmoji = '😵'; // Dizzy when dragged
                return;
            }

            // --- Status Updates ---
            // Decay
            if (now % 100 < 20) { // Relaxed check (0-19ms window) to ensure it hits roughly every 100ms
                 pet.hunger = Math.max(0, pet.hunger - 0.02);
                 pet.mood = Math.max(0, pet.mood - 0.01);
                 pet.poopMeter += 0.2; // Passive poop buildup
                 if (pet.fightCooldown > 0) pet.fightCooldown--;
                 
                 // Wool Growth
                 if (pet.woolGrowth < 100) {
                     pet.woolGrowth += 0.05; // Grows slowly
                 }

                 // Poop Check
                 const nearbyPoop = droppedItems.find(d => d.item.id === 'res_poop' && Math.hypot(d.x - pet.x, d.y - pet.y) < 60);
                 if (nearbyPoop) {
                     pet.mood = Math.max(0, pet.mood - 0.05); 
                     pet.health = Math.max(0, pet.health - 0.02); // Poop hurts health
                     if (Math.random() < 0.02) pet.currentEmoji = '🤢';
                 }
                 
                 // Poop Drop Check
                 if (pet.poopMeter > 100) {
                     pet.poopMeter = 0;
                     PetSystem.dropPoop(pet, droppedItems);
                 }
            }

            // --- Fighting Logic ---
            if (pet.actionState === 'idle' && pet.fightCooldown <= 0) {
                // Find nearby pets
                const enemy = pets.find(p => p.id !== pet.id && Math.hypot(p.x - pet.x, p.y - pet.y) < 50);
                if (enemy) {
                    // Calculate Aggression
                    let aggression = 0.001; // Base chance
                    if (pet.tags.includes('好斗') || pet.tags.includes('霸道') || pet.tags.includes('急躁')) aggression += 0.02;
                    if (pet.mood < 30) aggression += 0.01; // Grumpy pets fight more
                    
                    if (Math.random() < aggression) {
                        // Start Fight
                        pet.actionState = 'fighting';
                        pet.actionTimer = 60;
                        pet.fightCooldown = 500; // Cooldown
                        pet.currentEmoji = '⚔️';
                        pet.mood -= 10;
                        pet.health -= 10;
                        pet.logs.unshift(`${new Date().toLocaleTimeString()} 和 ${enemy.name} 打了一架`);
                        
                        // Enemy reacts too
                        if (enemy.actionState === 'idle') {
                            enemy.actionState = 'fighting';
                            enemy.actionTimer = 60;
                            enemy.fightCooldown = 500;
                            enemy.currentEmoji = '💢';
                            enemy.mood -= 10;
                            enemy.health -= 5; // Defender takes less dmg?
                        }
                        return;
                    }
                }
            }

            // --- AI Decision Making ---
            // Priority: 1. Action Locked -> 2. Health -> 3. Hunger -> 4. Mood -> 5. Wander
            
            // State Machine
            if (pet.actionTimer > 0) {
                pet.actionTimer--;
                if (pet.actionState === 'eating') pet.currentEmoji = '😋';
                else if (pet.actionState === 'playing') pet.currentEmoji = '🎵';
                else if (pet.actionState === 'showering') pet.currentEmoji = '🚿';
                else if (pet.actionState === 'fighting') pet.currentEmoji = '⚔️';
                else if (pet.actionState === 'sleeping') pet.currentEmoji = '💤';
                return; 
            } else {
                pet.actionState = 'idle';
            }

            // Determine Emoji & Target
            let targetFurniture = null;
            const furnitureList = State.scene === 'friend_home' ? State.friendHome.furniture : State.furniture;
            
            if (pet.health < 50) {
                pet.currentEmoji = '😷'; // Sick
                // Go to bed to heal
                targetFurniture = furnitureList.find(f => f.id === 'fur_bed');
                if (targetFurniture && Math.hypot(pet.x - targetFurniture.x, pet.y - targetFurniture.y) < 30) {
                    pet.actionState = 'sleeping';
                    pet.actionTimer = 200; 
                    pet.health = Math.min(100, pet.health + 20);
                    pet.mood = Math.min(100, pet.mood + 10);
                    return;
                }
            } else if (pet.hunger < 30) {
                pet.currentEmoji = '🍖'; // Hungry
                targetFurniture = furnitureList.find(f => f.id === 'fur_feeder');
                if (targetFurniture && Math.hypot(pet.x - targetFurniture.x, pet.y - targetFurniture.y) < 30) {
                    // Arrived at feeder
                    pet.actionState = 'eating';
                    pet.actionTimer = 100; // Eat for a while
                    pet.hunger = Math.min(100, pet.hunger + 50);
                    return;
                }
            } else if (pet.mood < 40) {
                pet.currentEmoji = '🌧️'; // Sad
                targetFurniture = furnitureList.find(f => f.id === 'fur_toy_box');
                if (targetFurniture && Math.hypot(pet.x - targetFurniture.x, pet.y - targetFurniture.y) < 30) {
                    // Arrived at toy box
                    pet.actionState = 'playing';
                    pet.actionTimer = 100;
                    pet.mood = Math.min(100, pet.mood + 30);
                    return;
                }
            } else {
                // Normal / Happy
                pet.currentEmoji = pet.mood > 80 ? '✨' : '';
                
                // Occasional random emoji
                if (Math.random() < 0.005) {
                    const randomEmojis = ['💤', '👀', '💭', '❤️'];
                    pet.currentEmoji = randomEmojis[Math.floor(Math.random() * randomEmojis.length)];
                    pet.actionTimer = 50; // Show for a bit
                }

                // Occasional Shower (Hygiene simulation)
                if (Math.random() < 0.002) {
                    targetFurniture = furnitureList.find(f => f.id === 'fur_shower');
                    if (targetFurniture) {
                        pet.currentEmoji = '💩'; // Feel dirty
                    }
                }
                
                // If we decided to shower (target set above)
                if (targetFurniture && targetFurniture.id === 'fur_shower') {
                     if (Math.hypot(pet.x - targetFurniture.x, pet.y - targetFurniture.y) < 30) {
                        pet.actionState = 'showering';
                        pet.currentEmoji = '🚿';
                        pet.actionTimer = 100;
                        pet.mood = Math.min(100, pet.mood + 10);
                        return;
                    }
                }
            }

            // 1. Movement & Physics
            if (Math.abs(pet.vx) > 0.1 || Math.abs(pet.vy) > 0.1) {
                // Physics Mode (Thrown)
                pet.x += pet.vx;
                pet.y += pet.vy;
                pet.vy += 0.5; // Gravity
                pet.vx *= 0.95; // Air friction
                
                // Bounce off floor
                if (pet.y > 350) {
                    pet.y = 350;
                    pet.vy *= -0.6;
                    pet.vx *= 0.8;
                }
                // Bounce off walls
                if (pet.x < 20 || pet.x > 580) {
                    pet.vx *= -0.8;
                    pet.x = Math.max(20, Math.min(580, pet.x));
                }
                
                // Stop physics if slow
                if (Math.abs(pet.vy) < 0.5 && Math.abs(pet.vx) < 0.5 && pet.y >= 349) {
                    pet.vx = 0; pet.vy = 0;
                    pet.targetX = pet.x; pet.targetY = pet.y;
                }
            } else {
                // AI Movement Mode
                
                // --- Collision & Squeezing Logic (Enhanced) ---
                let collisionForceX = 0;
                let collisionForceY = 0;
                let squeezeIntensity = 0; // Accumulates squeeze force

                pets.forEach(other => {
                    if (other.id === pet.id) return;
                    const dist = Math.hypot(pet.x - other.x, pet.y - other.y);
                    const minDist = 40; // Assumed radius sum (20 + 20)
                    
                    if (dist < minDist && dist > 0) {
                        // Calculate repulsion
                        const push = (minDist - dist) / minDist; // 0 to 1 strength
                        const angle = Math.atan2(pet.y - other.y, pet.x - other.x);
                        
                        collisionForceX += Math.cos(angle) * push * 2;
                        collisionForceY += Math.sin(angle) * push * 2;
                        
                        squeezeIntensity += push; // Add up squeeze
                    }
                });

                // Smoothly update squeeze factor (Spring effect)
                if (!pet.squeezeFactor) pet.squeezeFactor = 0;
                pet.squeezeFactor = pet.squeezeFactor * 0.8 + squeezeIntensity * 0.2;

                // Apply Squeeze Visual (Dynamic Scale & Wobble)
                if (pet.squeezeFactor > 0.01) {
                    // Oscillate scale based on time and intensity
                    const wobble = Math.sin(Date.now() / 50) * pet.squeezeFactor * 0.2;
                    pet.scaleX = 1 + pet.squeezeFactor * 0.5 - wobble; // Get wider
                    pet.scaleY = 1 - pet.squeezeFactor * 0.3 + wobble; // Get flatter
                    
                    // Add rotation wobble
                    pet.rotation = Math.sin(Date.now() / 80) * pet.squeezeFactor * 0.5;

                    // Change expression if squeezed hard
                    if (pet.squeezeFactor > 0.3 && !pet.actionState.startsWith('fight')) {
                        pet.currentEmoji = '😣';
                    }
                } else {
                    pet.scaleX = 1;
                    pet.scaleY = 1;
                    pet.rotation = 0;
                    if (pet.currentEmoji === '😣') pet.currentEmoji = ''; // Reset expression
                }

                // Override target if we have a need
                if (targetFurniture) {
                    pet.targetX = targetFurniture.x;
                    pet.targetY = targetFurniture.y;
                }

                // --- Personality Logic (Speed) ---
                let moveSpeed = 0.05;
                let wanderChance = 0.02;
                
                if (pet.tags.includes('多动症')) {
                    moveSpeed = 0.15; wanderChance = 0.05;
                } else if (pet.tags.includes('懒癌')) {
                    moveSpeed = 0.01; wanderChance = 0.005;
                }

                const dx = pet.targetX - pet.x;
                const dy = pet.targetY - pet.y;
                
                // Apply Movement + Collision Force
                if (Math.hypot(dx, dy) > 5) {
                    pet.x += dx * moveSpeed + collisionForceX;
                    pet.y += dy * moveSpeed + collisionForceY;
                } else {
                    // Just collision push if idle
                    pet.x += collisionForceX;
                    pet.y += collisionForceY;

                    // Random wander (Only if no urgent need)
                    if (!targetFurniture && Math.random() < wanderChance) {
                        // Tendency to move towards compatible furniture
                        const compatibleFurniture = furnitureList.find(f => {
                            const fData = DB.items[f.id];
                            return fData.element === pet.element || fData.element === 'neutral';
                        });

                        if (compatibleFurniture && Math.random() < 0.6) {
                            pet.targetX = compatibleFurniture.x + (Math.random()-0.5)*50;
                            pet.targetY = compatibleFurniture.y + (Math.random()-0.5)*50;
                        } else {
                            pet.targetX = 50 + Math.random() * 500;
                            pet.targetY = 50 + Math.random() * 300;
                        }
                    }
                }
                
                // Bounds Check for AI movement
                pet.x = Math.max(20, Math.min(580, pet.x));
                pet.y = Math.max(20, Math.min(350, pet.y));
            }

            // 2. Furniture Buffs (Resonance)
            let buffed = false;
            furnitureList.forEach(f => {
                if (f.type === 'building') return; // Skip buildings
                const fData = DB.items[f.id];
                if (!fData.radius) return;
                
                const dist = Math.hypot(pet.x - f.x, pet.y - f.y);
                if (dist < fData.radius) {
                    if (fData.element === pet.element) {
                        pet.mood = Math.min(100, pet.mood + 0.05); // Fast recovery
                        buffed = true;
                    } else if (fData.element === 'neutral') {
                        pet.mood = Math.min(100, pet.mood + 0.01); // Slow recovery
                    }
                }
            });
            pet.isBuffed = buffed;

            // 3. Passive Drop
            if (now - pet.lastDropTime > 5000) { // Every 5s
                pet.lastDropTime = now;
                // Chance based on mood
                if (Math.random() < (pet.mood / 200)) { 
                    this.dropItem(pet, droppedItems);
                }
            }
        });
    },

    createPet(speciesId, modIds) {
         // ... existing createPet logic ...
         // I need to patch the factory method or ensure new pets have vx/vy
         // Since Factory is separate, I'll just ensure Factory.createPet adds vx/vy
         // But wait, I can't easily patch Factory here without replacing it.
         // Let's assume Factory returns basic object and we add props if missing in update loop?
         // Or better, update Factory.createPet in the next tool call.
    },

    dropItem(pet, droppedItems = State.droppedItems) {
        // Enhanced Drop Logic: Favor specific drops
        let itemId = 'res_biomass_s';
        
        if (pet.drops && pet.drops.length > 0) {
            // Filter out common biomass to increase weight of exclusives
            const exclusives = pet.drops.filter(id => !id.startsWith('res_biomass'));
            
            // 60% chance to pick from exclusives if available
            if (exclusives.length > 0 && Math.random() < 0.6) {
                itemId = exclusives[Math.floor(Math.random() * exclusives.length)];
            } else {
                // Fallback to full list
                itemId = pet.drops[Math.floor(Math.random() * pet.drops.length)];
            }
        } else {
            itemId = Math.random() > 0.5 ? 'res_biomass_s' : 'res_crystal';
        }

        const item = Factory.createItem(itemId);
        // Value modifier based on mood
        item.value = Math.floor(item.value * (0.5 + pet.mood/100));
        
        droppedItems.push({
            item: item,
            x: pet.x,
            y: pet.y,
            vx: (Math.random() - 0.5) * 5,
            vy: (Math.random() - 0.5) * 5 // Spread out, no gravity
        });
        UISystem.showFloat(`💎`, pet.x, pet.y);
        pet.logs.unshift(`${new Date().toLocaleTimeString()} 掉落了 ${item.name}`);
    },

    dropPoop(pet, droppedItems = State.droppedItems) {
        const item = Factory.createItem('res_poop');
        droppedItems.push({
            item: item,
            x: pet.x,
            y: pet.y,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2
        });
        UISystem.showFloat(`💩`, pet.x, pet.y);
        pet.logs.unshift(`${new Date().toLocaleTimeString()} 拉了一坨便便`);
        pet.mood = Math.min(100, pet.mood + 10); // Relief
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
                    <p>健康: <span style="color:${pet.health<50?'red':'green'}">${Math.floor(pet.health)}</span>/100</p>
                    <p>心情: ${Math.floor(pet.mood)}/100</p>
                    <p>饱食: ${Math.floor(pet.hunger)}/100</p>
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
                ${pet.woolGrowth >= 100 ? `<button class="btn" style="background:#f1c40f; color:white;" onclick="PetSystem.shear('${pet.id}')">✂️ 薅羊毛</button>` : `<button class="btn" disabled style="background:#ccc;">毛没长齐 (${Math.floor(pet.woolGrowth)}%)</button>`}
                ${State.scene === 'friend_home' ? `<button class="btn" style="background:#e74c3c; color:white;" onclick="PetSystem.steal('${pet.id}')">😈 诱拐 (10%)</button>` : ''}
            </div>
        `;
        UISystem.showModal("伙伴详情", content);
    },

    shear(petId) {
        const pet = State.pets.find(p => p.id === petId) || State.friendHome.pets.find(p => p.id === petId);
        if (!pet || pet.woolGrowth < 100) return;

        pet.woolGrowth = 0;
        pet.mood = Math.max(0, pet.mood - 10); // Shearing might annoy them slightly
        
        // Create Wool Item
        const item = Factory.createItem('res_wool');
        
        const droppedItems = State.scene === 'friend_home' ? State.friendHome.droppedItems : State.droppedItems;
        
        droppedItems.push({
            item: item,
            x: pet.x,
            y: pet.y,
            vx: (Math.random() - 0.5) * 5,
            vy: (Math.random() - 0.5) * 5
        });
        
        UISystem.showFloat(`✂️`, pet.x, pet.y);
        pet.logs.unshift(`${new Date().toLocaleTimeString()} 被薅了羊毛，有点不爽`);
        pet.currentEmoji = '💢'; // Annoyed expression
        
        UISystem.closeModal();
        UISystem.update();
    },

    feed(petId) {
        // Find pet in either own pets or friend pets
        let pet = State.pets.find(p => p.id === petId);
        if (!pet) pet = State.friendHome.pets.find(p => p.id === petId);
        
        const foodIdx = State.storage.findIndex(i => i.id === 'food_can');
        if (foodIdx === -1) { alert("仓库里没有高级罐头！"); return; }
        
        State.storage.splice(foodIdx, 1);
        pet.mood = Math.min(100, pet.mood + 50);
        pet.hunger = Math.min(100, pet.hunger + 80); // Also restore hunger
        pet.poopMeter += 60; // Increase poop meter (High chance to poop soon)
        pet.logs.unshift(`${new Date().toLocaleTimeString()} 吃了一个美味罐头`);
        UISystem.closeModal();
        UISystem.update();
    },

    play(petId) {
        let pet = State.pets.find(p => p.id === petId);
        if (!pet) pet = State.friendHome.pets.find(p => p.id === petId);

        pet.mood = Math.min(100, pet.mood + 10);
        pet.logs.unshift(`${new Date().toLocaleTimeString()} 被主人摸了摸头`);
        UISystem.closeModal();
        UISystem.update();
    },

    steal(petId) {
        const petIdx = State.friendHome.pets.findIndex(p => p.id === petId);
        if (petIdx === -1) return;
        const pet = State.friendHome.pets[petIdx];

        // 10% Chance
        if (Math.random() < 0.1) {
            // Success
            State.friendHome.pets.splice(petIdx, 1);
            pet.id = 'pet_' + Date.now(); // Re-ID to avoid conflicts
            pet.x = 300; pet.y = 200;
            State.pets.push(pet);
            alert(`诱拐成功！${pet.name} 跟你回家了！`);
            pet.logs.unshift(`${new Date().toLocaleTimeString()} 被诱拐到了新家`);
        } else {
            // Fail
            alert("诱拐失败！它咬了你一口！");
            pet.currentEmoji = '💢';
            pet.mood -= 20;
        }
        UISystem.closeModal();
        UISystem.update();
    }
};

const HomeSystem = {
    canvas: null,
    ctx: null,
    
    // Helper to get current context
    getContext() {
        if (State.scene === 'friend_home') {
            return {
                pets: State.friendHome.pets,
                furniture: State.friendHome.furniture,
                drops: State.friendHome.droppedItems,
                isFriend: true
            };
        }
        return {
            pets: State.pets,
            furniture: State.furniture,
            drops: State.droppedItems,
            isFriend: false
        };
    },

    init() {
        const c = document.getElementById('base-canvas');
        if (!c) return;
        this.canvas = c;
        this.ctx = c.getContext('2d');
        
        // Mouse Down
        this.canvas.addEventListener('mousedown', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
            const y = (e.clientY - rect.top) * (this.canvas.height / rect.height);
            
            const ctx = this.getContext();

            // 1. Check Pets for Drag
            for (let p of ctx.pets) {
                if (Math.hypot(p.x - x, p.y - y) < 30) {
                    State.drag.petId = p.id;
                    State.drag.startX = x;
                    State.drag.startY = y;
                    State.drag.isDragging = false;
                    State.drag.lastX = x;
                    State.drag.lastY = y;
                    State.drag.lastTime = Date.now();
                    return; // Swallow event
                }
            }

            // 2. Check Drops (Only if not clicking pet)
            for (let i = ctx.drops.length - 1; i >= 0; i--) {
                const d = ctx.drops[i];
                if (Math.hypot(d.x - x, d.y - y) < 20) {
                    // Auto-convert Biomass
                    if (d.item.type === ItemTypes.BIOMASS) {
                        const val = d.item.value || 10;
                        State.resources.biomass += val;
                        UISystem.showFloat(`+${val} 🧬`, x, y, '#2ecc71');
                    } else {
                        State.storage.push(d.item);
                        UISystem.showFloat(`+${d.item.name}`, x, y, 'green');
                    }
                    
                    ctx.drops.splice(i, 1);
                    UISystem.update();
                    return;
                }
            }
            
            // 3. Check Buildings (Shop & Travel) - Only in Base
            if (!ctx.isFriend) {
                const shop = ctx.furniture.find(f => f.id === 'bld_shop');
                if (shop && Math.hypot(shop.x - x, shop.y - y) < 40) {
                    ShopSystem.open();
                    return;
                }
                
                const travel = ctx.furniture.find(f => f.id === 'bld_travel');
                if (travel && Math.hypot(travel.x - x, travel.y - y) < 40) {
                    // Travel Logic
                    if (confirm("消耗 100 星际币前往好友【土豪金】的家园？")) {
                        if (State.resources.coins >= 100) {
                            State.resources.coins -= 100;
                            State.scene = 'friend_home';
                            UISystem.update();
                            alert("已抵达好友家园！\n你可以：\n1. 捡地上的垃圾\n2. 薅宠物的羊毛\n3. 尝试诱拐宠物");
                        } else {
                            alert("星际币不足！");
                        }
                    }
                    return;
                }
            }

            // 4. Check Visitor (Only in Base)
            if (!ctx.isFriend && State.visitor) {
                if (Math.hypot(State.visitor.x - x, State.visitor.y - y) < 30) {
                    VisitorSystem.interact();
                    return;
                }
            }
        });

        // Mouse Move
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
            const y = (e.clientY - rect.top) * (this.canvas.height / rect.height);

            // Check Furniture Hover (for Radius)
            let found = null;
            // Iterate backwards to find top-most
            for (let i = State.furniture.length - 1; i >= 0; i--) {
                const f = State.furniture[i];
                // Simple hitbox approx
                if (Math.hypot(f.x - x, f.y - y) < 30) {
                    found = f;
                    break;
                }
            }
            State.hoveredFurnitureId = found ? found.uid : null; // Use uid

            if (!State.drag.petId) return;

            // Check drag threshold
            if (!State.drag.isDragging && Math.hypot(x - State.drag.startX, y - State.drag.startY) > 5) {
                State.drag.isDragging = true;
            }

            if (State.drag.isDragging) {
                const pet = State.pets.find(p => p.id === State.drag.petId);
                if (pet) {
                    // Calculate velocity for throw
                    const now = Date.now();
                    const dt = now - State.drag.lastTime;
                    if (dt > 0) {
                        State.drag.vx = (x - State.drag.lastX) / dt * 15; // Scale up
                        State.drag.vy = (y - State.drag.lastY) / dt * 15;
                    }
                    
                    pet.x = x;
                    pet.y = y;
                    pet.vx = 0; pet.vy = 0; // Stop physics while holding
                    
                    State.drag.lastX = x;
                    State.drag.lastY = y;
                    State.drag.lastTime = now;
                }
            }
        });

        // Mouse Up
        this.canvas.addEventListener('mouseup', (e) => {
            if (State.drag.petId) {
                if (!State.drag.isDragging) {
                    // It was a click
                    PetSystem.interact(State.drag.petId);
                } else {
                    // It was a drop/throw
                    const pet = State.pets.find(p => p.id === State.drag.petId);
                    if (pet) {
                        pet.vx = Math.max(-20, Math.min(20, State.drag.vx || 0));
                        pet.vy = Math.max(-20, Math.min(20, State.drag.vy || 0));
                        pet.targetX = pet.x; // Reset target
                        pet.targetY = pet.y;
                    }
                }
                State.drag.petId = null;
                State.drag.isDragging = false;
            }
        });
        
        VisitorSystem.init();
    },

    draw() {
        if (!this.ctx) return;
        const ctx = this.ctx;
        ctx.clearRect(0, 0, 600, 400);

        // Furniture & Buildings
        State.furniture.forEach(f => {
            const fData = DB.items[f.id];
            
            // Draw Radius
            if (fData.radius) {
                const isHovered = f.uid === State.hoveredFurnitureId;
                
                ctx.beginPath();
                ctx.arc(f.x, f.y, fData.radius, 0, Math.PI*2);
                
                // Base style
                let fillStyle = 'rgba(255,255,255,0.05)';
                let strokeStyle = 'rgba(255,255,255,0.2)';
                
                if (fData.element === 'fire') {
                    fillStyle = 'rgba(231, 76, 60, 0.05)';
                    strokeStyle = 'rgba(231, 76, 60, 0.2)';
                } else if (fData.element === 'water') {
                    fillStyle = 'rgba(52, 152, 219, 0.05)';
                    strokeStyle = 'rgba(52, 152, 219, 0.2)';
                }

                // Hover style (Brighter)
                if (isHovered) {
                    fillStyle = fillStyle.replace('0.05', '0.2');
                    strokeStyle = strokeStyle.replace('0.2', '0.8');
                    ctx.lineWidth = 2;
                } else {
                    ctx.lineWidth = 1;
                }

                ctx.fillStyle = fillStyle;
                ctx.fill();
                ctx.strokeStyle = strokeStyle;
                ctx.stroke();
            }

            // Draw Icon
            ctx.font = f.type === 'building' ? '50px Arial' : '30px Arial';
            ctx.fillText(f.icon, f.x, f.y);
            
            // Label for Building
            if (f.type === 'building') {
                ctx.font = '12px Arial';
                ctx.fillStyle = '#333';
                ctx.textAlign = 'center';
                ctx.fillText(fData.name, f.x, f.y + 35);
            }
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
            ctx.save(); // Save context state
            ctx.translate(p.x, p.y);
            
            // Apply Squeeze Scale & Rotation
            if (p.scaleX && p.scaleY) {
                ctx.scale(p.scaleX, p.scaleY);
            }
            if (p.rotation) {
                ctx.rotate(p.rotation);
            }

            ctx.font = '40px Arial';
            ctx.fillText(p.icon, 0, 0); // Draw at 0,0 relative to translate
            
            ctx.restore(); // Restore context state

            // Mood bar (Absolute position relative to pet, ignoring scale for readability)
            ctx.fillStyle = 'red';
            ctx.fillRect(p.x - 20, p.y - 40, 40, 4);
            ctx.fillStyle = '#2ecc71';
            ctx.fillRect(p.x - 20, p.y - 40, 40 * (p.mood/100), 4);
            
            // Buff Indicator
            if (p.isBuffed) {
                ctx.font = '16px Arial';
                ctx.fillText("🎵", p.x + 20, p.y - 30);
            }

            // Status Emoji Bubble
            if (p.currentEmoji) {
                // Bubble background
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(p.x, p.y - 50, 15, 0, Math.PI*2);
                ctx.fill();
                ctx.strokeStyle = '#333';
                ctx.stroke();
                
                // Emoji
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(p.currentEmoji, p.x, p.y - 50);
            }
            
            // Name
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'alphabetic';
            ctx.fillText(p.name, p.x, p.y + 25);
        });

        // Drops
        State.droppedItems.forEach(d => {
            // Physics - No Gravity, just friction
            d.x += d.vx;
            d.y += d.vy;
            d.vx *= 0.9;
            d.vy *= 0.9;
            
            // Stop if slow
            if (Math.abs(d.vx) < 0.1) d.vx = 0;
            if (Math.abs(d.vy) < 0.1) d.vy = 0;

            // Bounds
            d.x = Math.max(20, Math.min(580, d.x));
            d.y = Math.max(20, Math.min(380, d.y));

            ctx.font = '20px Arial';
            ctx.fillText(d.item.icon, d.x, d.y);
        });
    }
};

// ==========================================
// Config System (AI & Settings)
// ==========================================
const ConfigSystem = {
    load() {
        const data = localStorage.getItem('stellar_station_config');
        return data ? JSON.parse(data) : { difyUrl: '', difyKey: '', difyPrompt: '' };
    },

    save() {
        const url = document.getElementById('dify-url').value.trim();
        const key = document.getElementById('dify-key').value.trim();
        const prompt = document.getElementById('dify-prompt').value.trim();

        if (url && !url.startsWith('http')) {
            alert('URL 必须以 http 或 https 开头');
            return;
        }

        const config = { difyUrl: url, difyKey: key, difyPrompt: prompt };
        localStorage.setItem('stellar_station_config', JSON.stringify(config));
        
        document.getElementById('config-modal').style.display = 'none';
        
        // Test connection if key is provided
        if (key) {
            alert('设置已保存！下次访客刷新时将尝试使用 AI 生成。');
        }
    },

    open() {
        const config = this.load();
        document.getElementById('dify-url').value = config.difyUrl || '';
        document.getElementById('dify-key').value = config.difyKey || '';
        document.getElementById('dify-prompt').value = config.difyPrompt || '';
        
        document.getElementById('config-modal').style.display = 'block';
    },

    close() {
        document.getElementById('config-modal').style.display = 'none';
    }
};

const VisitorSystem = {
    init() {
        // Spawn first visitor quickly
        setTimeout(() => this.spawn(), 3000);

        setInterval(() => {
            if (!State.visitor && Math.random() < 0.5) { 
                this.spawn();
            }
        }, 5000);
    },

    async spawn() {
        if (State.visitor) return;
        
        // Find Shop Location
        const shop = State.furniture.find(f => f.id === 'bld_shop');
        const spawnX = shop ? shop.x - 60 : 440;
        const spawnY = shop ? shop.y + 30 : 80;

        // Default Fallback
        let requests = [];
        let visitorName = '星际访客';
        let visitorDesc = '来自遥远星系的旅行者';
        let isAi = false;

        // Check AI Config
        const config = ConfigSystem.load();
        if (config.difyKey && config.difyUrl) {
            UISystem.showFloat("📡 正在联络星际访客...", spawnX, spawnY - 20, 'cyan');
            try {
                const aiData = await this.callAI(config);
                if (aiData) {
                    requests = aiData.requests;
                    visitorName = aiData.name || visitorName;
                    visitorDesc = aiData.desc || visitorDesc;
                    isAi = true;
                }
            } catch (e) {
                console.error("AI Spawn Failed:", e);
                UISystem.showFloat("⚠️ 联络失败，使用本地备用方案", spawnX, spawnY - 40, 'red');
                // Fallback to local generation
                requests = this.generateRequests();
            }
        } else {
            requests = this.generateRequests();
        }

        // Validate requests structure
        if (!requests || !Array.isArray(requests) || requests.length === 0) {
            requests = this.generateRequests();
        }

        // Initialize Visitor
        State.visitor = {
            x: spawnX,
            y: spawnY,
            icon: ['👽', '🤖', '👩‍🚀', '🐙', '👾'][Math.floor(Math.random()*5)],
            name: visitorName,
            desc: visitorDesc,
            requests: requests,
            isAi: isAi
        };
        
        UISystem.showFloat(isAi ? "🤖 AI访客抵达!" : "访客到访!", spawnX, spawnY, isAi ? '#00ff00' : 'orange');
    },

    async callAI(config) {
        // Prepare Context
        const inventorySummary = State.storage.map(i => i.name).join(', ');
        const petSummary = State.pets.map(p => `${p.name}(${p.element}属性, 评分${p.score})`).join(', ');
        const itemsDB = Object.values(DB.items).filter(i => i.type === 'resource' || i.type === 'food').map(i => `${i.name}(ID:${i.id})`).join(', ');

        const systemPrompt = config.difyPrompt || `
        你是一个游戏NPC生成器。请生成一个星际访客及其委托任务。
        
        **当前玩家状态**:
        - 拥有物品: ${inventorySummary || '无'}
        - 拥有宠物: ${petSummary || '无'}
        - 游戏物品库: ${itemsDB}

        **要求**:
        1. 返回纯 JSON 格式，不要包含 markdown 代码块标记。
        2. JSON 结构如下:
        {
            "name": "访客名字",
            "desc": "一句话描述",
            "requests": [
                {
                    "type": "item", 
                    "id": "物品ID (必须从游戏物品库中选择)", 
                    "name": "物品名称", 
                    "count": 数量(1-5), 
                    "reward": 奖励金币数, 
                    "done": false
                },
                {
                    "type": "trait_pet",
                    "id": "unique_id",
                    "name": "借用宠物",
                    "count": 1,
                    "reward": 奖励金币数,
                    "done": false,
                    "desc": "任务描述 (例如: 我需要一只火属性宠物生火)",
                    "reqType": "element",
                    "reqVal": "fire" (可选值: fire, water, grass, electric, wind)
                }
            ]
        }
        3. 生成 2-3 个任务。任务类型可以是 'item' (索要物品) 或 'trait_pet' (索要特定属性宠物)。
        4. 访客性格要有趣，可以是海盗、商人、迷路的游客等。
        `;

        const body = {
            inputs: {},
            query: systemPrompt,
            response_mode: "blocking",
            user: "player-local"
        };

        const response = await fetch(config.difyUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.difyKey}`
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        const answer = data.answer;
        
        // Clean up markdown code blocks if present
        const jsonStr = answer.replace(/```json/g, '').replace(/```/g, '').trim();
        return JSON.parse(jsonStr);
    },

    refresh() {
        State.visitor = null;
        this.spawn(); // Re-spawn (will trigger AI again if configured)
    },

    generateRequests() {
        const requests = [];
        const count = 2 + Math.floor(Math.random() * 2); // 2-3 requests
        
        for(let i=0; i<count; i++) {
            const r = Math.random();
            if (r < 0.5) {
                // Resource Request
                const target = Object.values(DB.items).filter(it => it.type === ItemTypes.RESOURCE || it.type === ItemTypes.FOOD);
                const item = target[Math.floor(Math.random() * target.length)];
                const amount = 1 + Math.floor(Math.random() * 5);
                requests.push({
                    type: 'item',
                    id: item.id,
                    name: item.name,
                    count: amount,
                    reward: item.value * amount * 2, // Double market price
                    done: false
                });
            } else if (r < 0.8) {
                // Borrow Pet Request (Simplified to "Show Pet")
                requests.push({
                    type: 'show_pet',
                    id: 'pet_show',
                    name: '展示高分宠物',
                    count: 1,
                    reward: 500,
                    done: false,
                    desc: "让我看看评分>200的宠物"
                });
            } else {
                // Dynamic Pet Request (Element/Trait)
                const elements = ['fire', 'water', 'grass', 'electric', 'wind'];
                const targetElement = elements[Math.floor(Math.random() * elements.length)];
                const elementNames = { fire: '火', water: '水', grass: '草', electric: '雷', wind: '风' };
                
                const scenarios = [
                    { desc: `我家炉子坏了，借只【${elementNames[targetElement]}】宠物生火`, req: 'element', val: targetElement },
                    { desc: `需要一只【${elementNames[targetElement]}】宠物帮忙干活`, req: 'element', val: targetElement },
                    { desc: `想看看【${elementNames[targetElement]}】属性的宠物`, req: 'element', val: targetElement }
                ];
                const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];

                requests.push({
                    type: 'trait_pet',
                    id: 'pet_trait_' + Date.now(),
                    name: '借用宠物',
                    count: 1,
                    reward: 800,
                    done: false,
                    desc: scenario.desc,
                    reqType: scenario.req,
                    reqVal: scenario.val
                });
            }
        }
        return requests;
    },

    interact() {
        if (!State.visitor) return;
        
        let content = `<div style="display:flex; flex-direction:column; gap:10px;">`;
        const greeting = State.visitor.desc || "你好！我正在寻找这些东西...";
        content += `<p>${State.visitor.icon} <b>${State.visitor.name}</b>: "${greeting}"</p>`;
        
        let allDone = true;
        
        State.visitor.requests.forEach((req, idx) => {
            if (!req.done) allDone = false;
            
            // Check if player has enough
            let hasEnough = false;
            if (req.type === 'item') {
                const count = State.storage.filter(i => i.id === req.id).length;
                hasEnough = count >= req.count;
            } else if (req.type === 'show_pet') {
                hasEnough = State.pets.some(p => p.score > 200);
            } else if (req.type === 'trait_pet') {
                if (req.reqType === 'element') {
                    hasEnough = State.pets.some(p => p.element === req.reqVal);
                }
            }

            content += `
                <div style="background:#f9f9f9; padding:10px; border-radius:4px; display:flex; justify-content:space-between; align-items:center; opacity:${req.done?0.5:1}">
                    <div>
                        <div>${req.type === 'item' ? `📦 <b>${req.name}</b> x${req.count}` : `🦁 <b>${req.desc}</b>`}</div>
                        <div style="font-size:12px; color:gold;">💰 报酬: ${req.reward}</div>
                    </div>
                    ${req.done ? 
                        `<span style="color:green;">✅ 已完成</span>` : 
                        `<button class="btn sm ${hasEnough?'primary':'disabled'}" onclick="${hasEnough ? `VisitorSystem.deliver(${idx})` : ''}">${hasEnough ? '交付' : '不足'}</button>`
                    }
                </div>
            `;
        });
        
        content += `</div>`;
        
        if (allDone) {
            content += `<div style="margin-top:10px; color:green; text-align:center;">🎉 所有委托已完成！</div>`;
            content += `<button class="btn success full-width" onclick="VisitorSystem.refresh()">🔄 刷新委托 (访客休息一下)</button>`;
        } else {
            content += `<button class="btn danger full-width" onclick="VisitorSystem.refresh()" style="margin-top:10px;">🚪 没货了，换一批 (刷新)</button>`;
        }

        UISystem.showModal("访客", content);
    },

    deliver(idx) {
        const req = State.visitor.requests[idx];
        if (req.done) return;

        // Remove items
        let removed = 0;
        for (let i = State.storage.length - 1; i >= 0; i--) {
            if (State.storage[i].id === req.id) {
                State.storage.splice(i, 1);
                removed++;
                if (removed >= req.count) break;
            }
        }
        
        // Give Reward
        State.resources.coins += req.reward;
        req.done = true;
        
        UISystem.showFloat(`+💰${req.reward}`, 300, 300, 'gold'); // Center float
        UISystem.update();
        this.interact(); // Refresh Modal
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

        // Filter sellable items (Resources, Biomass, but NO Genes)
        const sellables = State.storage.map((item, index) => ({...item, index})).filter(i => 
            i.value && 
            i.type !== ItemTypes.GENE_FRAG && 
            i.type !== ItemTypes.GENE_MOD
        );

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
                    uid: Date.now() + Math.random(), // Add UID
                    id: item.id,
                    icon: item.icon,
                    type: item.type, // Ensure type is passed
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

        // Helper to create item div
        const createItemDiv = (item, count, reqCount, avgScore) => {
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
                div.style.opacity = 0.6;
                div.style.background = '#f0f0f0';
            }
            return div;
        };

        // Helper to render groups
        const renderGroup = (title, filterFn, reqCount) => {
            const header = document.createElement('h4');
            header.innerText = title;
            header.style.borderBottom = "1px solid #eee";
            header.style.paddingBottom = "5px";
            header.style.marginTop = "10px";
            list.appendChild(header);

            const items = Object.values(DB.items).filter(filterFn);
            const available = [];
            const locked = [];

            items.forEach(item => {
                const data = geneData[item.id] || { count: 0, totalScore: 0 };
                if (data.count >= reqCount) available.push(item);
                else locked.push(item);
            });

            // Render Available
            available.forEach(item => {
                const data = geneData[item.id];
                const avgScore = data.count > 0 ? Math.floor(data.totalScore / data.count) : 0;
                list.appendChild(createItemDiv(item, data.count, reqCount, avgScore));
            });

            // Render Locked (Collapsed)
            if (locked.length > 0) {
                const details = document.createElement('details');
                const summary = document.createElement('summary');
                summary.innerText = `未集齐 (${locked.length}) - 点击展开`;
                summary.style.fontSize = '12px';
                summary.style.color = '#7f8c8d';
                summary.style.cursor = 'pointer';
                summary.style.marginTop = '5px';
                details.appendChild(summary);
                
                locked.forEach(item => {
                    const data = geneData[item.id] || { count: 0, totalScore: 0 };
                    const avgScore = data.count > 0 ? Math.floor(data.totalScore / data.count) : 0;
                    details.appendChild(createItemDiv(item, data.count, reqCount, avgScore));
                });
                list.appendChild(details);
            } else if (available.length === 0) {
                const empty = document.createElement('div');
                empty.innerText = "暂无基因";
                empty.style.color = "#999";
                empty.style.fontSize = "12px";
                empty.style.padding = "5px";
                list.appendChild(empty);
            }
        };

        renderGroup("🧬 物种基因 (需10碎片)", i => i.type === ItemTypes.GENE_FRAG, 10);
        renderGroup("✨ 特征基因 (需1碎片)", i => i.type === ItemTypes.GENE_MOD, 1);
    },

    selectSpecies(item) {
        State.lab.selectedSpecies = item;
        State.lab.candidates = []; // Clear candidates
        State.lab.selectedCandidateIdx = -1;
        this.updatePreview();
        this.render(); 
    },

    toggleMod(item) {
        const idx = State.lab.selectedMods.findIndex(m => m.id === item.id);
        if (idx >= 0) State.lab.selectedMods.splice(idx, 1);
        else {
            if (State.lab.selectedMods.length >= 2) State.lab.selectedMods.shift();
            State.lab.selectedMods.push(item);
        }
        State.lab.candidates = []; // Clear candidates
        State.lab.selectedCandidateIdx = -1;
        this.updatePreview();
        this.render(); 
    },

    simulate() {
        if (State.resources.biomass < 10) {
            alert("生物质不足 (需要10)！");
            return;
        }
        State.resources.biomass -= 10;
        
        // Generate 3 candidates
        State.lab.candidates = [];
        for(let i=0; i<3; i++) {
            State.lab.candidates.push(Factory.analyzeGenetics(State.lab.selectedSpecies, State.lab.selectedMods));
        }
        State.lab.selectedCandidateIdx = -1;
        
        this.updatePreview();
        UISystem.update();
    },

    selectCandidate(idx) {
        State.lab.selectedCandidateIdx = idx;
        this.updatePreview();
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
        
        // --- NEW GACHA UI ---
        
        if (State.lab.candidates.length === 0) {
            // State 1: Ready to Simulate
            preview.innerHTML = `
                <div style="font-size:80px; position:relative; opacity:0.5;">
                    ${s.icon}
                    <div style="position:absolute; top:30%; left:20%; font-size:20px; color:black; background:white; padding:5px;">?</div>
                </div>
            `;
            label.innerText = "准备模拟";
            
            aiDiv.classList.remove('hidden');
            aiDiv.innerHTML = `
                <div style="text-align:center; padding:20px;">
                    <p>投入生物质进行模拟，生成3个潜在的性格方案。</p>
                    <button class="btn primary" onclick="LabSystem.simulate()">🧪 开始模拟 (10生物质)</button>
                </div>
            `;
            btn.disabled = true;
            
        } else {
            // State 2: Choose Candidate
            preview.innerHTML = `
                <div style="font-size:60px;">${s.icon}</div>
            `;
            label.innerText = "选择方案";
            
            let candidatesHTML = `<div style="display:flex; gap:10px; justify-content:center;">`;
            State.lab.candidates.forEach((c, idx) => {
                const isSelected = State.lab.selectedCandidateIdx === idx;
                candidatesHTML += `
                    <div onclick="LabSystem.selectCandidate(${idx})" 
                         style="border:2px solid ${isSelected ? '#2ecc71' : '#ccc'}; 
                                background:${isSelected ? '#eafaf1' : 'white'}; 
                                padding:5px; border-radius:5px; cursor:pointer; width:30%; font-size:11px;">
                        <div style="color:gold; font-weight:bold;">${c.score}分</div>
                        <div>${c.tags[0]}</div>
                        <div style="color:#666;">${c.tags.slice(1).join(',')}</div>
                    </div>
                `;
            });
            candidatesHTML += `</div>`;

            aiDiv.classList.remove('hidden');
            aiDiv.innerHTML = `
                <h4 style="margin:0 0 10px 0;">🧬 模拟结果</h4>
                ${candidatesHTML}
                <div style="margin-top:10px; font-size:12px; color:#666;">
                    * 选中一个方案进行实体化
                </div>
                <div style="margin-top:10px; text-align:center;">
                    <button class="btn sm action" onclick="LabSystem.simulate()">🔄 不满意? 重随 (10生物质)</button>
                </div>
            `;
            
            btn.disabled = State.lab.selectedCandidateIdx === -1;
        }
    },

    realize() {
        if (State.lab.selectedCandidateIdx === -1) return;
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
        
        const chosenAnalysis = State.lab.candidates[State.lab.selectedCandidateIdx];
        const newPet = Factory.createPet(sId, State.lab.selectedMods.map(m => m.id), chosenAnalysis);
        State.pets.push(newPet);
        if (!State.activePetId) State.activePetId = newPet.id;
        
        // Reset Lab
        State.lab.candidates = [];
        State.lab.selectedCandidateIdx = -1;
        
        alert(`恭喜！${newPet.name} 诞生了！`);
        State.scene = 'base';
        UISystem.switchScene('base');
    }
};

const UISystem = {
    currentStorageTab: 'item', // Default to Item (Resource)

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

        // Bind Pet List (NEW)
        const petListBtn = document.getElementById('pet-list-btn');
        if(petListBtn) petListBtn.onclick = () => this.showPetList();

        this.update();
    },

    showPetList() {
        if (State.pets.length === 0) {
            alert("你还没有任何伙伴！快去基因实验室创造一个吧。");
            return;
        }

        const content = `
            <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(120px, 1fr)); gap:10px; max-height:400px; overflow-y:auto;">
                ${State.pets.map(p => `
                    <div style="
                        border:1px solid #ddd; 
                        padding:10px; border-radius:8px; text-align:center;
                        background:${p.health < 50 ? '#fff5f5' : 'white'};
                        position:relative;
                    ">
                        <div style="font-size:40px; cursor:pointer;" onclick="PetSystem.interact('${p.id}')">${p.icon}</div>
                        <div style="font-weight:bold; margin:5px 0;">${p.name}</div>
                        <div style="font-size:12px; line-height:1.5; color:#666;">
                            <div>❤️ ${Math.floor(p.health)} | 🍖 ${Math.floor(p.hunger)}</div>
                            <div>😊 ${Math.floor(p.mood)} | 💩 ${Math.floor(p.poopMeter)}%</div>
                            <div>🏆 评分: ${p.score}</div>
                            <div style="color:#3498db; margin-top:2px;">🏷️ ${p.tags.join(', ')}</div>
                        </div>
                        <div style="margin-top:5px; display:flex; gap:5px; justify-content:center;">
                            <button class="btn sm primary" onclick="PetSystem.feed('${p.id}')">喂</button>
                            <button class="btn sm success" onclick="PetSystem.play('${p.id}')">摸</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        this.showModal("🐶 伙伴列表", content);
    },

    setStorageTab(tab) {
        this.currentStorageTab = tab;
        
        // Update Buttons
        const map = { 'item': 0, 'gene': 1, 'living': 2 }; 
        const buttons = document.querySelectorAll('.storage-tabs .tab-btn');
        buttons.forEach((b, i) => {
            if (i === map[tab]) b.classList.add('active');
            else b.classList.remove('active');
        });

        this.renderStorage();
    },

    switchScene(scene) {
        // Leaving Exploration? Transfer Loot
        if (State.scene === 'exploration' && scene === 'base') {
            let count = 0;
            let biomassGained = State.carriedBiomass; // From stacking
            
            // Transfer Backpack Items
            if (State.inventory.length > 0) {
                State.inventory.forEach(item => {
                    // Double check (though biomass shouldn't be in grid now)
                    if (item.type === ItemTypes.BIOMASS) {
                        biomassGained += (item.value || 10);
                    } else {
                        // Push the FULL item (with rarity/value) to storage
                        // Remove x,y from grid
                        const { x, y, ...storedItem } = item;
                        State.storage.push(storedItem);
                        count++;
                    }
                });
                State.inventory = []; // Clear Backpack
            }

            // Apply Biomass
            if (biomassGained > 0) {
                State.resources.biomass += biomassGained;
                State.carriedBiomass = 0; // Reset
            }

            if (count > 0 || biomassGained > 0) {
                let msg = "探险结束！";
                if (count > 0) msg += `\n📦 ${count} 个物品已存入仓库。`;
                if (biomassGained > 0) msg += `\n🧬 获得 ${biomassGained} 生物质。`;
                alert(msg);
            }
        }

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
            MapSystem.show(); // Use new show method
        } else if (scene === 'lab') {
            LabSystem.render();
        }
        
        this.update();
    },

    update() {
        // Resources
        const bioDisplay = document.getElementById('biomass-display');
        if (bioDisplay) bioDisplay.innerText = State.resources.biomass;
        
        const coinsDisplay = document.getElementById('coins-display');
        if (coinsDisplay) coinsDisplay.innerText = State.resources.coins;
        
        // Pet Status
        const pet = State.pets.find(p => p.id === State.activePetId);
        const petName = document.getElementById('pet-name');
        if (petName) petName.innerText = pet ? pet.name : '无';
        
        // Storage
        this.renderStorage();
        
        // Backpack Grid (Tetris) - Check BOTH potential locations
        const bpGrid = document.getElementById('backpack-grid');
        const bpCount = document.getElementById('backpack-count');
        const carriedBio = document.getElementById('carried-biomass');
        
        // Update Side Panel Backpack (Exploration View)
        if (bpGrid) {
            if (bpCount) bpCount.innerText = State.inventory.length;
            if (carriedBio) carriedBio.innerText = State.carriedBiomass || 0;

            bpGrid.innerHTML = '';
            bpGrid.style.display = 'grid';
            bpGrid.style.gridTemplateColumns = `repeat(3, 1fr)`;
            bpGrid.style.gridTemplateRows = `repeat(3, 1fr)`;
            bpGrid.style.gap = '2px';
            bpGrid.style.width = '200px';
            bpGrid.style.height = '200px';
            bpGrid.style.position = 'relative';
            bpGrid.style.background = '#bdc3c7';
            
            // Draw Slots
            for(let i=0; i<9; i++) {
                const slot = document.createElement('div');
                slot.style.background = 'rgba(255,255,255,0.3)';
                slot.style.border = '1px solid rgba(0,0,0,0.1)';
                bpGrid.appendChild(slot);
            }

            // Draw Items
            const GAP = 2;
            const TOTAL_SIZE = 200;
            const CELL_SIZE = (TOTAL_SIZE - 2 * GAP) / 3; // (200 - 4) / 3 = 65.33

            State.inventory.forEach(slot => {
                const item = DB.items[slot.id];
                const div = document.createElement('div');
                div.className = 'bp-item';
                div.innerHTML = item.icon;
                div.style.position = 'absolute';
                
                // Correct Grid Math
                div.style.left = (slot.x * (CELL_SIZE + GAP)) + 'px';
                div.style.top = (slot.y * (CELL_SIZE + GAP)) + 'px';
                div.style.width = (item.w * CELL_SIZE + (item.w - 1) * GAP) + 'px';
                div.style.height = (item.h * CELL_SIZE + (item.h - 1) * GAP) + 'px';
                
                div.style.background = item.element ? this.getElementColor(item.element) : '#ecf0f1';
                div.style.border = '2px solid #333';
                div.style.borderRadius = '4px';
                div.style.display = 'flex';
                div.style.alignItems = 'center';
                div.style.justifyContent = 'center';
                div.style.fontSize = '24px';
                div.style.cursor = 'grab';
                div.style.zIndex = 10;
                div.title = item.name;
                
                div.onmousedown = (e) => {
                    e.preventDefault();
                    this.startDragItem(e, slot, div, CELL_SIZE, GAP);
                };

                bpGrid.appendChild(div);
            });
        }
    },

    getElementColor(el) {
        const colors = { fire:'#e74c3c', water:'#3498db', grass:'#2ecc71', electric:'#f1c40f', wind:'#1abc9c', dark:'#8e44ad', light:'#f39c12' };
        return colors[el] || '#95a5a6';
    },

    startDragItem(e, slot, div, cellSize, gap) {
        const startX = e.clientX;
        const startY = e.clientY;
        const origLeft = parseFloat(div.style.left);
        const origTop = parseFloat(div.style.top);
        
        div.style.zIndex = 100;
        div.style.opacity = 0.8;

        const onMove = (moveE) => {
            const dx = moveE.clientX - startX;
            const dy = moveE.clientY - startY;
            div.style.left = (origLeft + dx) + 'px';
            div.style.top = (origTop + dy) + 'px';
        };

        const onUp = (upE) => {
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
            
            div.style.zIndex = 10;
            div.style.opacity = 1;

            // Calculate new grid pos
            const gridRect = document.getElementById('backpack-grid').getBoundingClientRect();
            // Use center of the item for snapping
            const itemCenterX = div.getBoundingClientRect().left + div.offsetWidth/2;
            const itemCenterY = div.getBoundingClientRect().top + div.offsetHeight/2;
            
            const relX = itemCenterX - gridRect.left;
            const relY = itemCenterY - gridRect.top;
            
            // Snap to nearest slot
            const newX = Math.floor(relX / (cellSize + gap));
            const newY = Math.floor(relY / (cellSize + gap));
            
            const item = DB.items[slot.id];
            
            // Try to place at new position (temporarily remove self)
            if (InventorySystem.canPlace(item, newX, newY, slot.uid)) {
                slot.x = newX;
                slot.y = newY;
                this.update(); // Snap visually
            } else {
                // Revert
                div.style.left = origLeft + 'px';
                div.style.top = origTop + 'px';
            }
        };

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
    },

    startDragLoot(e, item, idx, originalDiv) {
        const startX = e.clientX;
        const startY = e.clientY;
        
        // Create Ghost
        const ghost = originalDiv.cloneNode(true);
        ghost.style.position = 'fixed';
        ghost.style.left = startX + 'px';
        ghost.style.top = startY + 'px';
        ghost.style.zIndex = 2000;
        ghost.style.opacity = 0.8;
        ghost.style.pointerEvents = 'none';
        ghost.style.width = originalDiv.offsetWidth + 'px';
        ghost.style.height = originalDiv.offsetHeight + 'px';
        ghost.className = 'slot filled'; // Remove animation class
        document.body.appendChild(ghost);

        let isDragging = false;

        const onMove = (moveE) => {
            if (Math.hypot(moveE.clientX - startX, moveE.clientY - startY) > 5) isDragging = true;
            ghost.style.left = (moveE.clientX - originalDiv.offsetWidth/2) + 'px';
            ghost.style.top = (moveE.clientY - originalDiv.offsetHeight/2) + 'px';
        };

        const onUp = (upE) => {
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
            ghost.remove();

            if (!isDragging) return; // Treat as click

            // Check Drop Target (Backpack Grid)
            const grid = document.getElementById('modal-backpack-grid');
            const rect = grid.getBoundingClientRect();
            
            if (upE.clientX >= rect.left && upE.clientX <= rect.right &&
                upE.clientY >= rect.top && upE.clientY <= rect.bottom) {
                
                const GAP = 2;
                const TOTAL_SIZE = 200;
                const CELL_SIZE = (TOTAL_SIZE - 2 * GAP) / 3;
                
                const relX = upE.clientX - rect.left;
                const relY = upE.clientY - rect.top;
                
                // Center drop logic
                const gridX = Math.floor(relX / (CELL_SIZE + GAP));
                const gridY = Math.floor(relY / (CELL_SIZE + GAP));

                if (InventorySystem.addAt(item, gridX, gridY)) {
                    State.tempLoot.splice(idx, 1);
                    this.renderLoot();
                    this.update();
                } else {
                    // alert("放不进去！");
                }
            }
        };

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
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
            // Add background tint for rarity
            if (item.rarity.id !== 'common') {
                div.style.background = item.rarity.color + '15'; // 15 = low opacity hex
            }
            
            let actionBtn = '';
            if (item.type === ItemTypes.FOOD) {
                actionBtn = `<button class="btn sm primary" style="margin-left:auto;" onclick="PetSystem.feed('${State.activePetId}')">喂食</button>`;
            }

            div.innerHTML = `
                <span style="font-size:20px;">${item.icon}</span>
                <div style="display:flex; flex-direction:column; margin-left:5px; flex:1;">
                    <span style="font-weight:bold;">${item.name}</span>
                    <span style="font-size:10px; color:#666;">${item.rarity.name} | 💰${item.value}</span>
                </div>
                ${actionBtn}
            `;
            list.appendChild(div);
        });
    },

    getInventoryLoad() {
        return State.inventory.reduce((sum, item) => sum + (item.size || 1), 0);
    },

    openLootModal() {
        // const currentLoad = this.getInventoryLoad(); // Deprecated
        const content = `
            <div style="display:flex; gap:20px; height:300px;">
                <div style="flex:1; background:#eee; padding:10px; border-radius:4px;">
                    <h4>📦 发现物资 (点击拾取)</h4>
                    <div id="loot-container" style="display:grid; grid-template-columns:repeat(4,1fr); gap:5px;"></div>
                </div>
                <div style="flex:1; background:#dce4e8; padding:10px; border-radius:4px; display:flex; flex-direction:column; align-items:center;">
                    <h4>🎒 背包整理</h4>
                    <div id="modal-backpack-grid"></div>
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
        const bDiv = document.getElementById('modal-backpack-grid');
        if (!cDiv || !bDiv) return;

        // Render Loot List
        cDiv.innerHTML = '';
        State.tempLoot.forEach((item, idx) => {
            const div = document.createElement('div');
            div.className = 'slot filled loot-pop'; // Add animation class
            div.style.animationDelay = `${idx * 0.1}s`; // Stagger delay
            
            // Show Name and Size
            let nameDisplay = item.name;
            if (item.type === ItemTypes.BIOMASS) nameDisplay += ` x${item.value}`;

            div.innerHTML = `
                ${item.icon}
                <div style="font-size:10px; text-align:center; line-height:1.1;">${nameDisplay}</div>
                <span style="font-size:9px; color:#666;">${item.w}x${item.h}</span>
            `;
            div.title = item.name + "\n" + (item.desc || '');
            div.style.borderColor = item.rarity.color;
            div.style.flexDirection = 'column';
            div.style.cursor = 'grab';
            
            // Click to Auto-Add
            div.onclick = () => {
                if (item.type === ItemTypes.BIOMASS) {
                    // Stack Biomass
                    const val = item.value || 10;
                    State.carriedBiomass += val;
                    State.tempLoot.splice(idx, 1);
                    this.renderLoot();
                    this.update();
                } else if (InventorySystem.add(item)) {
                    State.tempLoot.splice(idx, 1);
                    this.renderLoot();
                    this.update(); // Update main UI immediately
                } else {
                    // alert("背包空间不足！请整理背包。"); 
                }
            };

            // Drag to Add
            div.onmousedown = (e) => {
                // Prevent click triggering immediately
                // e.stopPropagation(); 
                if (item.type !== ItemTypes.BIOMASS) {
                    this.startDragLoot(e, item, idx, div);
                }
            };

            cDiv.appendChild(div);
        });

        // Render Backpack Grid (Read-onlyish, but shows layout)
        // Reuse the main update logic but target a specific div? 
        // Actually, let's just clone the logic for simplicity or make update() targetable.
        // For now, simple render:
        bDiv.innerHTML = '';
        bDiv.style.display = 'grid';
        bDiv.style.gridTemplateColumns = `repeat(3, 1fr)`;
        bDiv.style.gridTemplateRows = `repeat(3, 1fr)`;
        bDiv.style.gap = '2px';
        bDiv.style.width = '200px';
        bDiv.style.height = '200px';
        bDiv.style.position = 'relative';
        bDiv.style.background = '#bdc3c7';
        
        // Slots
        for(let i=0; i<9; i++) {
            const slot = document.createElement('div');
            slot.style.background = 'rgba(255,255,255,0.3)';
            slot.style.border = '1px solid rgba(0,0,0,0.1)';
            bDiv.appendChild(slot);
        }

        // Items
        const cellW = 200 / 3;
        const cellH = 200 / 3;
        State.inventory.forEach(slot => {
            const item = DB.items[slot.id];
            const div = document.createElement('div');
            div.innerHTML = item.icon;
            div.style.position = 'absolute';
            div.style.left = (slot.x * cellW) + 'px';
            div.style.top = (slot.y * cellH) + 'px';
            div.style.width = (item.w * cellW - 4) + 'px';
            div.style.height = (item.h * cellH - 4) + 'px';
            div.style.background = this.getElementColor(item.element);
            div.style.border = '2px solid #333';
            div.style.borderRadius = '4px';
            div.style.display = 'flex';
            div.style.alignItems = 'center';
            div.style.justifyContent = 'center';
            div.style.fontSize = '24px';
            
            // Allow removing in loot modal
            div.onclick = () => {
                if(confirm("丢弃这个物品吗？")) {
                    InventorySystem.remove(slot.uid);
                    this.renderLoot();
                    this.update(); // Update main UI immediately
                }
            };
            
            bDiv.appendChild(div);
        });
    },

    lootTakeAll() {
        // Try to add all
        let changed = false;
        // Iterate backwards to safely splice
        for (let i = State.tempLoot.length - 1; i >= 0; i--) {
            const item = State.tempLoot[i];
            if (item.type === ItemTypes.BIOMASS) {
                State.carriedBiomass += (item.value || 10);
                State.tempLoot.splice(i, 1);
                changed = true;
            } else if (InventorySystem.add(item)) {
                State.tempLoot.splice(i, 1);
                changed = true;
            }
        }
        if (changed) {
            this.renderLoot();
            this.update(); // Update main UI immediately
        }
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

    showManual() {
        const content = `
            <div style="text-align:left; max-height:400px; overflow-y:auto; padding-right:10px;">
                <div style="background:#fff3cd; border-left:4px solid #ffc107; padding:10px; margin-bottom:15px; font-size:13px;">
                    <strong>⚠️ 核心痛点与优化方向</strong>
                    <ul style="margin:5px 0; padding-left:20px;">
                        <li><strong>问题</strong>：当前版本宠物功能性弱、交互匮乏；探险循环割裂，等待体验不佳。</li>
                        <li><strong>目标</strong>：后续开发将聚焦<strong>轻量化、休闲娱乐化</strong>，重点强化宠物在核心循环中的价值与交互反馈。</li>
                        <li><strong>理念转变</strong>：
                            <ul>
                                <li><strong>家园是宠物的放大器</strong>（非宠物是家园的放大器）。</li>
                                <li><strong>为宠物建设家园</strong>（非宠物在家园当奴隶）。</li>
                            </ul>
                        </li>
                    </ul>
                </div>

                <h3 style="border-bottom:2px solid #3498db; padding-bottom:5px;">🚀 核心循环</h3>
                <p><b>基因培育</b> ➔ <b>宠物养成</b> ➔ <b>家园建设</b> ➔ <b>探险搜刮</b></p>

                <h3 style="border-bottom:2px solid #9b59b6; padding-bottom:5px; margin-top:20px;">1. 🧪 基因实验室</h3>
                <ul style="padding-left:20px; color:#555;">
                    <li><b>配方</b>：1个物种基因 (10碎片) + 特征模组。</li>
                    <li><b>模拟</b>：消耗10生物质，随机生成3个性格方案。</li>
                    <li><b>实体化</b>：消耗100生物质，创造宠物。</li>
                </ul>

                <h3 style="border-bottom:2px solid #f1c40f; padding-bottom:5px; margin-top:20px;">2. 🏡 家园与养成</h3>
                <ul style="padding-left:20px; color:#555;">
                    <li><b>需求</b>：关注饱食、心情、健康。</li>
                    <li><b>便便</b>：进食后易拉屎，<b>必须清理</b>否则影响健康。</li>
                    <li><b>互动</b>：点击可喂食/抚摸，按住可<b>拖拽/扔飞</b>宠物。</li>
                    <li><b>建造</b>：在商店购买家具，拖拽“上帝之手”调整摆放。家具可提供Buff（如恢复心情）。</li>
                </ul>

                <h3 style="border-bottom:2px solid #2ecc71; padding-bottom:5px; margin-top:20px;">3. 🗺️ 星际探险</h3>
                <ul style="padding-left:20px; color:#555;">
                    <li><b>移动</b>：点击节点移动，消耗 <b>2点饱食度</b>。</li>
                    <li><b>搜刮</b>：获得基因、物品和生物质（自动堆叠）。</li>
                    <li><b>背包</b>：将战利品<b>拖拽</b>至右侧网格中整理。</li>
                    <li><b>结算</b>：返回基地后，物品入库，生物质变现。</li>
                </ul>
                
                <h3 style="border-bottom:2px solid #e74c3c; padding-bottom:5px; margin-top:20px;">4. 💰 经济与建设</h3>
                <ul style="padding-left:20px; color:#555;">
                    <li><b>访客系统</b>：随机有外星访客造访，提交他们需求的物资可获得大量 <b>星际币</b>。</li>
                    <li><b>星际商店</b>：购买家具（提供Buff）、食物、玩具；出售多余资源。</li>
                </ul>

                <div style="background:#f0f0f0; padding:10px; margin-top:20px; border-radius:5px; font-size:12px;">
                    <b>🎮 演示推荐：</b> 实验室造宠 -> 家园互动/喂食/清理 -> 商店买家具 -> 探险搜刮资源。
                </div>
            </div>
        `;
        this.showModal("📖 玩法说明书", content);
    },

    showFloat(text, x, y, color='gold', container = null) {
        const div = document.createElement('div');
        div.innerText = text;
        div.style.position = 'absolute';
        div.style.left = x + 'px';
        div.style.top = y + 'px';
        div.style.color = color;
        div.style.fontWeight = 'bold';
        div.style.pointerEvents = 'none';
        div.style.transition = '1s';
        div.style.zIndex = '1000';
        div.style.textShadow = '1px 1px 2px black';
        
        if (container) {
            container.appendChild(div);
        } else {
            const active = document.querySelector('.view.active');
            if (active) active.appendChild(div);
            else document.getElementById('base-view').appendChild(div); 
        }
        
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
    if (State.scene === 'base' || State.scene === 'friend_home') {
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
        for(let i=0; i<15; i++) State.storage.push(Factory.createItem('frag_fire_lizard'));
        // 2. Water Ball Set (Enough for 1)
        for(let i=0; i<15; i++) State.storage.push(Factory.createItem('frag_water_ball'));
        // 3. Grass Cat Set (Enough for 1)
        for(let i=0; i<15; i++) State.storage.push(Factory.createItem('frag_grass_cat'));
        
        // 3. Modifiers
        State.storage.push(Factory.createItem('mod_wings'));
        State.storage.push(Factory.createItem('mod_cute'));
        State.storage.push(Factory.createItem('mod_glow'));
        
        // 4. Consumables
        State.storage.push(Factory.createItem('food_can'));
        
        // 5. Place Shop
        State.furniture.push({
            uid: 'shop_static',
            ...DB.items['bld_shop']
        });
        
        // 6. Place Travel Agent
        State.furniture.push({
            uid: 'travel_static',
            ...DB.items['bld_travel']
        });

        // Init Friend Home Data (Preset)
        State.friendHome.pets = [
            Factory.createPet('frag_fire_lizard', ['mod_wings', 'mod_horns'], { tags: ['好斗', '土豪'], drops: ['res_crystal', 'res_coal'], score: 500 }),
            Factory.createPet('frag_crystal_deer', ['mod_glow', 'mod_big'], { tags: ['高冷', '土豪'], drops: ['res_crystal', 'res_pearl'], score: 600 }),
            Factory.createPet('frag_thunder_tiger', ['mod_metal', 'mod_claw'], { tags: ['霸道', '土豪'], drops: ['res_crystal', 'res_biomass_l'], score: 800 })
        ];
        // Ensure friend pets have wool grown
        State.friendHome.pets.forEach(p => p.woolGrowth = 100);

        State.friendHome.furniture = [
            { id: 'fur_bonfire', x: 300, y: 200, type: 'furniture', icon: '🔥' },
            { id: 'fur_pool', x: 100, y: 100, type: 'furniture', icon: '🏊' },
            { id: 'fur_heater', x: 400, y: 300, type: 'furniture', icon: '🔥' },
            { id: 'bld_gym', x: 500, y: 100, type: 'building', icon: '🏋️' } // Rich people stuff
        ];

        // Initial Notification
        setTimeout(() => {
            alert("欢迎来到星际驿站！\n已为您发放少量基因片段。\n请前往【星际探险】收集更多资源！");
            // UISystem.switchScene('lab'); // Auto-switch removed to let user explore
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