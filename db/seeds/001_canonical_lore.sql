-- 001_canonical_lore.sql
-- Seed script: 22 Pathways and 22 Major Arcana Tarot Cards
-- Idempotent: safe to run multiple times

BEGIN;

-- 1. Insert Pathways
INSERT INTO pathways (id, name, chinese_name, description) VALUES
(1, 'Fool', '愚者', 'Pathway of change, bizarre miracles, concealment, history, and spiritual manipulation.'),
(2, 'Door', '学徒', 'Pathway of spatial traversal, sealing, replication of powers, and cosmic wandering.'),
(3, 'Error', '偷盗者', 'Pathway of theft, parasitic control, exploiting loopholes, and deceit.'),
(4, 'Visionary', '观众', 'Pathway of psychological insight, mind reading, dreaming, and mental manipulation.'),
(5, 'Sun', '太阳', 'Pathway of purification, light, dispelling evil, and divine charisma.'),
(6, 'Tyrant', '水手', 'Pathway of oceanic storms, lightning, extreme rage, and physical supremacy.'),
(7, 'White Tower', '阅读者', 'Pathway of omniscience, spell analysis, deductive reason, and mystical scholarship.'),
(8, 'Hanged Man', '秘祈人', 'Pathway of sacrifice, flesh manipulation, shadow corruption, and degenerate secrets.'),
(9, 'Darkness', '不眠者', 'Pathway of sleep, dream manipulation, stillness, calmness, and soul soothing.'),
(10, 'Death', '死神', 'Pathway of the underworld, necrotic decay, spirit summoning, and eternal rest.'),
(11, 'Twilight Giant', '战士', 'Pathway of unyielding martial prowess, dawn light, and protective defensive aura.'),
(12, 'Red Priest', '猎人', 'Pathway of fire, provocation, tactical warfare, and weather-scale conflagrations.'),
(13, 'Demoness', '刺客', 'Pathway of stealth, frost, catastrophic disease, curses, and deadly seduction.'),
(14, 'Black Emperor', '律师', 'Pathway of distortion, exploiting legal rules, disorder, and resurrection via order.'),
(15, 'Justiciar', '仲裁人', 'Pathway of discipline, creating binding prohibitions, imprisonment, and order enforcement.'),
(16, 'Wheel of Fortune', '怪物', 'Pathway of destiny perception, extreme luck, probability manipulation, and chaos.'),
(17, 'Moon', '药师', 'Pathway of biological creation, healing, moon mysticism, and beast-taming.'),
(18, 'Mother', '耕种者', 'Pathway of vitality, agricultural fertility, nature manipulation, and life nurturing.'),
(19, 'Hermit', '窥秘人', 'Pathway of occult observation, knowledge scrolls, fairy-tale manifestation, and constellation mysticism.'),
(20, 'Paragon', '通识者', 'Pathway of mechanical craftsmanship, scientific alchemy, invention, and material mastery.'),
(21, 'Chained', '异种', 'Pathway of curses, restraints, temperance against bestial instincts, and eerie manifestations.'),
(22, 'Abyss', '罪犯', 'Pathway of bloodlust, slaughter, corruption, sulfur, and deep demonic impulses.')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    chinese_name = EXCLUDED.chinese_name,
    description = EXCLUDED.description;

-- Reset sequence to ensure future auto-increment consistency
SELECT setval('pathways_id_seq', (SELECT MAX(id) FROM pathways));

-- 2. Insert 22 Major Arcana Cards
INSERT INTO tarot_cards (id, name, arcana_type, card_number, pathway_id, upright_meaning, reversed_meaning, mystical_lore) VALUES
(0, 'The Fool', 'major', 0, 1, 
 'New beginnings, infinite potential, innocence, leap of faith into the unknown, adventurous instinct.',
 'Recklessness, unwarranted risk-taking, folly, manipulation, naivety exploited by hidden forces.',
 'Corresponds to the Fool pathway. The traveler starting a journey above the gray fog, holding a walking stick and a white rose.'),

(1, 'The Magician', 'major', 1, 1,
 'Willpower, mastery of elements, manifestation, ingenuity, quick wit and resourcefulness.',
 'Deception, trickery, illusion, misdirected power, grand illusions masking vulnerability.',
 'Corresponds to the Fool pathway Sequence 7. The master of sleight of hand transforming reality with stagecraft.'),

(2, 'The High Priestess', 'major', 2, 9,
 'Intuition, sacred mysteries, subconscious wisdom, silence, stillness, hidden knowledge.',
 'Secrets revealed destructively, repressed intuition, superficial understanding, emotional coldness.',
 'Corresponds to the Darkness pathway. Silent sanctuary within the night, observing cosmic secrets veiled in mist.'),

(3, 'The Empress', 'major', 3, 18,
 'Abundance, fertility, nurturing growth, harmony with nature, maternal grace, artistic creation.',
 'Creative stagnation, overbearing smothering, neglect, depletion of vitality and resource.',
 'Corresponds to the Mother pathway. The nurturing matriarch cultivating harvest and life in ancient soil.'),

(4, 'The Emperor', 'major', 4, 14,
 'Authority, establishing structure, law, sovereignty, strategic dominion, stability.',
 'Tyranny, abuse of authority, rigidity, chaos provoked through oppressive distortion.',
 'Corresponds to the Black Emperor pathway. Sovereign ruler dictating laws and bending circumstances to royal will.'),

(5, 'The Hierophant', 'major', 5, 7,
 'Spiritual guidance, orthodoxy, tradition, structured teaching, moral counsel, institutional wisdom.',
 'Blind dogma, outdated orthodoxy, rebellion against spiritual constraints, corrupted doctrine.',
 'Corresponds to the White Tower pathway. The venerable scholar preserving sacred scrolls and esoteric rites.'),

(6, 'The Lovers', 'major', 6, 4,
 'Soul connections, alignment of values, critical choices, harmonious union, empathy.',
 'Disharmony, misaligned values, dangerous temptation, psychological projection, broken vows.',
 'Corresponds to the Visionary pathway. The intertwining of minds, hearts, and shared aspirations under divine witness.'),

(7, 'The Chariot', 'major', 7, 12,
 'Triumph, resolute will, conquest, victory over opposition, focused momentum, martial drive.',
 'Loss of direction, aggression without purpose, crushing defeat, recklessness leading to ruin.',
 'Corresponds to the Red Priest pathway. The iron war chariot charging through fire and battle lines.'),

(8, 'Strength', 'major', 8, 11,
 'Endurance, quiet fortitude, mastery over primal beast, patience, moral conviction.',
 'Raw brutality, self-doubt, vulnerability, exhaustion of inner resolve under pressure.',
 'Corresponds to the Twilight Giant pathway. The guardian mastering raging fury with steady, unyielding spirit.'),

(9, 'The Hermit', 'major', 9, 19,
 'Introspection, solitary search for truth, contemplation, beacon in the dark, occult study.',
 'Isolation, paranoia, overwhelming occult knowledge leading to madness, withdrawal from reality.',
 'Corresponds to the Hermit pathway. The lantern-bearer walking the snowy ridge uncovering hidden constellation lore.'),

(10, 'Wheel of Fortune', 'major', 10, 16,
 'Destiny, cyclic changes, turning tides of fortune, sudden serendipity, inevitable karmic motion.',
 'Unlucky sequence, resisting inevitable shifts, clinging to fleeting circumstance, chaotic misfortune.',
 'Corresponds to the Wheel of Fortune pathway. The ever-spinning silver wheel deciding the rise and fall of mortals.'),

(11, 'Justice', 'major', 11, 15,
 'Equilibrium, objective fairness, truth revealed, accountability, karmic balance.',
 'Bias, injustice, unfair sentencing, harsh condemnation, evasion of consequence.',
 'Corresponds to the Justiciar pathway. The scale of divine arbitration measuring every soul with unwavering precision.'),

(12, 'The Hanged Man', 'major', 12, 8,
 'Enlightened surrender, viewing reality from a reversed angle, willing sacrifice for revelation.',
 'Futile martyrdom, stagnation, martyrdom complex, needless suffering, corrupting sacrifice.',
 'Corresponds to the Hanged Man pathway. The mystic suspended between worlds gazing into forbidden mysteries.'),

(13, 'Death', 'major', 13, 10,
 'Profound transformation, necessary endings, shedding old skin, passage into renewal.',
 'Fear of transition, clinging to rotten forms, decay without rebirth, spiritual morbidity.',
 'Corresponds to the Death pathway. The silent river of the underworld closing one chapter to birth the next.'),

(14, 'Temperance', 'major', 14, 21,
 'Moderation, alchemy of opposing forces, balance, restraint of desires, patient synthesis.',
 'Extremism, indulgent excess, loss of temperance, inner monster breaking the chains.',
 'Corresponds to the Chained pathway. The disciplined soul pouring water between urns, holding back inner bestiality.'),

(15, 'The Devil', 'major', 15, 22,
 'Material bondage, shadow desires, destructive obsession, entrapment in carnal instincts.',
 'Severing chains, awakening to manipulation, confronting the shadow self, escaping corruption.',
 'Corresponds to the Abyss pathway. The sulfurous temptation whispering seductive promises in dark alcoves.'),

(16, 'The Tower', 'major', 16, 6,
 'Sudden upheaval, lightning revelation, collapse of false edifices, cataclysmic liberation.',
 'Avoiding disaster narrowly, delayed reckoning, lingering in ruins, fear of catastrophic truth.',
 'Corresponds to the Tyrant pathway. The storm strike tearing down towering stone walls to clear the sky.'),

(17, 'The Star', 'major', 17, 9,
 'Hope, spiritual renewal, serenity, transcendent inspiration, light guiding the wanderer.',
 'Despair, loss of faith, disillusionment, cold detachment from reality.',
 'Corresponds to the Darkness pathway. The evening star shining clear over the misty horizon of Backlund.'),

(18, 'The Moon', 'major', 18, 17,
 'Mystery, subconscious dreams, illusion, uncanny intuition, cyclical biological tides.',
 'Deceptive visions, paranoia, terror of the dark, losing sanity in eerie nocturnal shadows.',
 'Corresponds to the Moon pathway. Crimson radiance awakening dormant instincts and occult vitality.'),

(19, 'The Sun', 'major', 19, 5,
 'Radiance, warmth, clarity, celebration, triumphant joy, purification of shadows.',
 'Blinding pride, scorching heat, false optimism, overwhelming glare concealing subtlety.',
 'Corresponds to the Sun pathway. The holy dawn dispelling all filth and foul specters from the world.'),

(20, 'Judgement', 'major', 20, 10,
 'Resurrection, awakening, reckoning of past actions, decisive calling to higher purpose.',
 'Self-doubt, refusal of calling, avoidance of reckoning, haunting by unresolved ghosts.',
 'Corresponds to the Death pathway. The solemn trumpet awakening sleeping souls to their true destiny.'),

(21, 'The World', 'major', 21, 2,
 'Wholeness, completion of cycle, mastery across realms, cosmic fulfillment, harmonious arrival.',
 'Incompletion, delayed fulfillment, near miss, reluctance to cross the threshold into the next stage.',
 'Corresponds to the Door pathway. The grand traveler holding the universe in balance, stepping through cosmic gates.')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    arcana_type = EXCLUDED.arcana_type,
    card_number = EXCLUDED.card_number,
    pathway_id = EXCLUDED.pathway_id,
    upright_meaning = EXCLUDED.upright_meaning,
    reversed_meaning = EXCLUDED.reversed_meaning,
    mystical_lore = EXCLUDED.mystical_lore;

COMMIT;
