# Design System Specification: The Digital Atelier

## 1. Overview & Creative North Star
**Creative North Star: "The Curated Manuscript"**
This design system moves away from the sterile "SaaS dashboard" aesthetic and toward a high-end, editorial experience. It envisions the interface not as a software tool, but as a living academic manuscript. By blending the structured clarity of *Notion* with the conversational intelligence of *ChatGPT*, we create a space of deep focus. 

The system breaks the "template" look through **intentional asymmetry**—using wide margins for annotations and offset headers—and **tonal depth**. We prioritize the "white space" of the paper over the "chrome" of the UI, ensuring that the AI’s literature analysis feels like an organic extension of the scholar’s thought process.

---

## 2. Colors & Surface Philosophy
The palette is rooted in the tactile history of academia—ink on cream paper—reimagined for a high-performance digital display.

### Surface Hierarchy & Nesting
To achieve a premium feel, we move beyond flat grids. We use the **Surface Tier** system to create a sense of stacked vellum.
*   **Base:** `surface` (#fbf9f5) – The primary desk surface.
*   **Sectioning:** `surface-container-low` (#f5f3ef) – Used for large sidebar or background areas to create a soft "recess."
*   **Focus Elements:** `surface-container-lowest` (#ffffff) – Used for the active "document" or "chat bubble" to make it pop against the cream background.

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to separate major sections. Division must be achieved through background shifts. For example, a `surface-container-low` navigation panel should sit flush against a `surface` main content area. The eye perceives the color shift as a boundary, creating a cleaner, more sophisticated "limitless" layout.

### The "Glass & Tonal" Rule
For floating elements like "AI Suggestion" popovers, use **Glassmorphism**:
*   **Fill:** `surface_container_lowest` at 80% opacity.
*   **Effect:** Backdrop blur (12px to 20px).
*   **Purpose:** This allows the underlying text to peek through, maintaining the "scholarly focus" without breaking the user’s flow with an opaque block.

---

## 3. Typography: The Editorial Voice
Our typography pairings balance the modernism of *Inter* with the authoritative, architectural structure of *Manrope*.

*   **Display & Headlines (Manrope):** Used for document titles and section starts. The wide apertures of Manrope provide a modern, "Tech-Forward" academic feel.
*   **Body & UI (Inter):** Optimized for high-density literature analysis. *Inter* provides the neutral, high-readability foundation required for long-form reading.

**Hierarchy as Identity:**
*   **Display-LG (3.5rem):** Reserved for hero analytical insights.
*   **Title-SM (1rem):** The workhorse for UI labels, set in Semi-Bold to contrast against the paper-like background.
*   **Body-MD (0.875rem):** The default for literature excerpts, utilizing a 1.6 line-height to ensure the "scholarly" breathing room.

---

## 4. Elevation & Depth
In this system, depth is a function of light and layering, not structural scaffolding.

### The Layering Principle
Avoid traditional shadows where possible. Instead, stack your tokens:
1.  **Level 0:** `surface_dim` (The background "tabletop")
2.  **Level 1:** `surface` (The "paper" sheets)
3.  **Level 2:** `surface_container_lowest` (The "active" card)

### Ambient Shadows & "Ghost Borders"
When an element must float (e.g., a modal or a floating action button):
*   **Shadow:** Use a large blur (24px+) with a 4% opacity of `on_secondary_fixed`. This creates a soft, ambient lift rather than a harsh drop shadow.
*   **The Ghost Border:** For accessibility in input fields, use `outline_variant` at **15% opacity**. It should feel like a faint pencil mark, not a heavy ink stroke.

---

## 5. Components

### Buttons & CTAs
*   **Primary:** `primary` (#00288e) fill with `on_primary` text. Use a subtle linear gradient from `primary` to `primary_container` to add "soul" and depth to the button face.
*   **Secondary:** `surface_container_high` fill. No border. This creates a "pressed-into-the-paper" look.
*   **Tertiary:** Ghost style. Use `primary` text with no container.

### The Analysis Card
*   **Layout:** No dividers. Use `Spacing-8` (1.75rem) to separate the title from the metadata.
*   **Styling:** Use `surface_container_lowest` and an `xl` (0.75rem) corner radius.
*   **Interaction:** On hover, shift the background to `surface_bright` and apply an ambient shadow.

### Chat & Literature Inputs
*   **Text Fields:** `surface_container_low` background with an `md` (0.375rem) radius. Labels should be `label-md` in `on_surface_variant`.
*   **AI Indicators:** Use a `tertiary_container` (#872d00) accent spark for AI-generated insights to distinguish them from human-authored text without using "warning" colors.

### Chips (Annotations)
*   **Style:** Pill-shaped (`full` radius).
*   **Color:** `secondary_container` with `on_secondary_container` text. These should feel like "Post-it" notes tucked into the margins.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use asymmetrical margins. Place the primary text slightly off-center to leave room for AI "marginalia" (notes in the margins).
*   **Do** use `surface-tier` nesting to define importance.
*   **Do** treat icons as "linear illustrations"—keep stroke weights consistent at 1.5px.

### Don’t:
*   **Don’t** use 100% black (#000000). Use `on_surface` (#1b1c1a) for maximum readability on the cream background.
*   **Don’t** use divider lines between list items. Use the **Spacing Scale (4 or 5)** to create separation through "void space."
*   **Don’t** use sharp corners. Stick to the `lg` (0.5rem) and `xl` (0.75rem) tokens to keep the experience feeling approachable and organic.