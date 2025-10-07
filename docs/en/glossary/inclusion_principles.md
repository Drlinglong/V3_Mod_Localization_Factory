# Paradox Mod Localization Factory - Glossary Inclusion Guidelines V1.0

## Core Principle: Less is More

Only words that are absolutely essential should be included in the glossary.

---

## 1. Must Include (Golden Standard)

### 1.1 Proper Nouns
- **People, Places, Countries**: `La Plata` -> `拉普拉塔`, `Bolivia` -> `玻利维亚`
- **Organizations, Factions, Powers**: `Shogunate` -> `幕府`
- **Unique Items, Technologies, Buildings**: `Mana` -> `魔力`, `Skymetal` -> `天金`

### 1.2 Key Game Mechanics Terminology
Words that have a special meaning within the game and must remain consistent globally.
- **Examples**: `Infamy` -> `恶名`, `Prestige` -> `威望`, `Convoy` -> `船队`

---

## 2. Strictly Exclude (Red Zone)

### 2.1 Common Verbs, Nouns, Adjectives
- **Forbidden**: `run`, `leader`, `Cave`, `Elephant`, `Experienced`, `Progress`, `Character`
- **Reason**: The AI is fully capable of handling these words based on context. Forcing a specific translation will only degrade the quality of the translation.

### 2.2 Logical and Common Words
- **Forbidden**: `NO`, `YES`, `Minor`, `Major`, `TODO`
- **Reason**: The translation of these words is 100% dependent on the context. `NO` can be "不", "否", or "无". Forcing it to be "不存在" is absurd.

### 2.3 Complex Phrases Containing Formatting
- **Forbidden**: `Historically` -> `#b 历史背景：#!`
- **Reason**: This kind of requirement should be handled in the prompt through more advanced instructions, not enforced by a fragile glossary entry.

---

## 3. Include with Caution (Gray Area)

### Words with multiple common translations that the community wishes to unify
- **Example**: `homelands` -> `本土`. It could be translated as "家园", "故土", etc. If the community decides to use only "本土" for consistency, it can be included.
- **Principle**: Must be discussed and its necessity confirmed before inclusion.
