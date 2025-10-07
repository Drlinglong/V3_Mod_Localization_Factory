# Paradox Mod Localization Factory: A Tour of the Translation Process (Final Revised Edition)

Hello! Have you ever wondered how, after you hand over an all-English Paradox game mod to the "Localization Factory," it transforms into the Chinese version we are familiar with? This process is like a magical automated factory, filled with precise procedures.

This document will act as your tour guide, taking you through the factory's assembly line to see how English sentences are accurately translated into Chinese. We'll try to explain it in the simplest way possible, so even if you don't understand code, you can grasp the magic behind it.

---

### Stop 1: The Preparation Workshop (Creating the Mod Framework)

Before the translation begins, the factory first gets all the preparation work done. It creates a brand-new folder, which will be the "home" for our final localized mod.

1.  **Build Directory Structure**: The factory will set up all the necessary subfolders according to Paradox's game standards, such as `localisation`, `metadata`, etc.
2.  **Copy Non-Text Assets**: To make the mod ready for direct use, the factory thoughtfully copies the original mod's **cover image** (e.g., `thumbnail.png`) and other necessary resource files into the newly created folder, untouched.

After this step, a complete framework for the localized mod is ready and waiting to be filled with content.

### Stop 2: Raw Material Intake & Disassembly (Parsing YML Files)

Our "raw material" is the localization files from the mod, usually ending in `.yml`. They look like this:

```yml
some_event_title:0 "An Interesting Event"
some_event_description:0 "A long description about what is happening in this interesting event..."
```

This file is like a task list. `some_event_title` and `some_event_description` are the **unique identifiers (we call them "keys")** for each task. The English text in quotes, `"An Interesting Event"`, is the **specific content to be processed (we call it the "value")**.

The factory's second step is to take this task list apart, accurately identifying which part is the key and which is the value to be translated. It carefully records this information to ensure no mix-ups occur in subsequent steps.

### Stop 3: Consulting the "Jargon" Bible (The Glossary System)

In the world of translation, inconsistent terminology is the biggest fear. For example, `Infamy` in the game might be translated by some as “恶名” and by others as “骂名”. To maintain a consistent experience throughout the game, the "Localization Factory" is equipped with a very strict "jargon" bible—the **Glossary**.

This bible dictates the single, standard translation for all core terms, for instance:

- `Infamy` -> `恶名`
- `Prestige` -> `威望`
- `Shogunate` -> `幕府`

Before official translation begins, the factory prepares the corresponding glossary for the current game. It's like giving the translator a mandatory handbook, telling them: "When you see these words, you must translate them this way. No improvising!"

### Stop 4: Writing "Sticky Notes" for the AI (Five-Part Prompt Assembly)

Our main translator is a very intelligent AI. But even the smartest AI needs clear instructions. If we just throw `"An Interesting Event"` at it, the translation might be good, but not necessarily faithful, elegant, and accurate, and it might mess up the complex formatting of Paradox games.

Therefore, one of the most crucial processes in the factory is to carefully prepare a "sticky note" for the AI, also known as a **Prompt**. This note is dynamically assembled and divided into five parts to ensure everything is foolproof:

1.  **Part One: Role-playing**
    We first establish a "persona" for the AI, telling it: "You are a professional translator specializing in the grand strategy game Victoria 3, well-versed in 19th-century history and linguistic styles." This helps the AI's tone match the game's context.

2.  **Part Two: The Core Task**
    We tell the AI what to do simply and directly: "Please translate the list of texts I provide from English to Simplified Chinese."

3.  **Part Three: Formatting Rules**
    This is the most technical part, where we use a very strict tone to inform the AI of the formatting rules it must follow. For example: "Your response MUST be a JSON array with the exact same number of items," "DO NOT add extra quotes around your translated words," and "#BOLD must be followed by a space." These rules ensure the result returned by the AI can be correctly read by the program.

4.  **Part Four: Game Syntax Rules**
    Paradox games have a lot of special syntax, like `[Concept('concept_key')]` or `[SCOPE.somenpc.GetFirstName]`. In this section, we tell the AI in detail: "When you see these complex codes wrapped in square brackets with periods and single quotes, do not translate them! Keep them as they are!"

5.  **Part Five: Glossary Terms**
    Finally, we pick out the relevant terms from the "jargon" bible prepared in Stop 3 and add them as a final instruction: "Final reminder, for this task, `Infamy` must be translated as `恶名`, and `Prestige` must be translated as `威望`."

With this combined approach, we can ensure the AI "dances in chains," leveraging its powerful translation capabilities while strictly adhering to our specifications.

### Stop 5: AI Translation & Final Assembly

After receiving this detailed "sticky note," the AI translator quickly returns its translation result, for example, `“一个有趣的事件”`.

Once the factory gets this translation, it proceeds to "final assembly." It finds the previously recorded **unique identifier (Key)**, `some_event_title`, and fills in the translated Chinese text, assembling it into a new Chinese localization file that conforms to the Paradox game format:

```yml
l_simp_chinese:
 some_event_title:0 "一个有趣的事件"
 # ... other translated entries
```

### Stop 6: Translating Mod Info (Processing Metadata)

A complete mod package includes not just the in-game text but also the mod's name and description displayed in the launcher. After translating all the in-game text, the factory specifically processes this **metadata**.

It calls the AI again, but this time with a simpler prompt designed for short texts (like mod titles), to translate fields such as `name` and `description` in the `.metadata` file. This ensures your localized mod offers a complete Chinese experience, inside and out.

### Stop 7: The Final Quality Check Before Shipping (Validators)

Before a product leaves the assembly line, it must undergo strict quality control! The "Localization Factory" has two "quality inspectors":

1.  **Format Validator**: Checks if the assembled file fully complies with Paradox's formatting requirements. For instance, are the quotes properly closed? Is the indentation correct? If these details are wrong, the text might not display correctly in the game.
2.  **Glossary Validator**: Double-checks all the translated Chinese text to see if any terms slipped through the cracks. For example, was `Prestige` accidentally translated as “声望” instead of the required “威望”? This inspector flags all translations that don't comply with the "jargon" bible.

Only a product that passes these two strict quality checks is considered a qualified localization file.

---

### End of the Tour

From creating the mod framework and copying the cover image, to disassembling the original text, consulting the glossary, carefully instructing the AI, and finally translating metadata and performing quality checks, a complete, **ready-to-subscribe-and-use** localized mod package is born. We hope this "factory tour" has helped you understand our workflow! Although the process may seem complex, every step is designed to ensure the final localization quality meets the highest standards.
