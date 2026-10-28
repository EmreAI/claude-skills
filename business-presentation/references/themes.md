# Themes, logo and images

The user picks the theme at the start (SKILL.md, Step 1). A theme changes the **cover, agenda, section dividers and closing slide**, plus the colours and fonts. **Content slides always keep the grid in `design.md` and stay light**, so charts and tables stay easy to read. Use one theme for the whole deck.

All themes should look professional, not flashy. One decorative idea per deck, used the same way every time.

## The four themes

| Theme | Look | Good for |
|---|---|---|
| **Clean** (default) | Off-white with one blue accent. The cover has a large accent block and fine concentric arcs. | Any topic, and the safe choice when unsure. |
| **Midnight** | The cover, dividers and closing slide are deep navy with fine glowing line waves and cyan accents. Content slides are light with navy titles. | Tech, digital, data, finance and platform topics. |
| **Classic** | Navy and white with serif titles and thin rules. The cover is navy with fine white line arcs. | Strategy cases, company analyses and anything that should feel formal. |
| **Company colours** | The cover and dividers use the company's brand colour and show its logo. Content slides are light with the brand colour as accent. | Decks about one company. |

### Tokens

| Token | Clean | Midnight | Classic | Company colours |
|---|---|---|---|---|
| Dark background (cover, dividers, closing) | none, the cover is light | `#0A1A36` → `#12306A`, linear gradient at 135° | `#0F2547` flat | brand primary (see below) |
| Light background (content) | `#FDFDFC` | `#FDFDFC` | `#FFFFFF` | `#FDFDFC` |
| Title colour on content slides | `#1B1F24` | `#0A1A36` | `#0F2547` | `#1B1F24` |
| Top rule (3 px, `design.md`) | `#1B1F24` → `#2B59C3` | `#0A1A36` → `#3FD0D9` | `#0F2547` flat | `#1B1F24` → brand accent |
| Accent on light slides (highlight bars, tracker, rules) | `#2B59C3` | `#1D5FD1` | `#2557A7` | brand colour, darkened until it reaches 3:1 on white |
| Light accent tint (second series, increases) | `#A8BCEB` | `#9DBDF5` | `#A9BFE3` | brand colour mixed 55% with white |
| Accent on dark slides | none | `#3FD0D9` (cyan) | `#FFFFFF` | white |
| Title font | Inter / Arial | Inter / Arial | Source Serif 4 / Georgia | Inter / Arial |
| Body font | Inter / Arial | Inter / Arial | Inter / Arial | Inter / Arial |

The font pairs are Claude Slides / PowerPoint. Never use a company's own brand font.

## Decorative graphics

The cover, section dividers and closing slide are full-bleed and have no frame. Content slides always use the frame from `design.md`.

Decorative graphics appear on the cover, section dividers and closing slide only, never on content slides. They sit behind the text, so in Claude Slides they are listed first in the slide as a pinned element. They never cross the title. Keep the left 55% of the slide free for text.

- **Line waves (Midnight).** 18 to 24 thin smooth curves (stroke 1.5 to 2 px) running across the lower half of the slide. Each curve is offset a little more than the one before, so the bundle fans out like a ribbon. The stroke is a linear gradient from cyan `#3FD0D9` to blue `#4F8CFF`, with opacity between 0.35 and 0.8.
- **Concentric arcs (Clean, Classic).** 7 to 10 concentric circles centred just outside the bottom-right corner, with a 2 px stroke and no fill. Clean uses the accent at 12 to 30% opacity on the light cover. Classic uses white at 10 to 25% opacity on navy.
- **Brand block (Company colours).** A large flat field in the brand colour covering the right 40% of the cover (or the whole cover if white text has enough contrast on it). Add the concentric arcs in white at 10 to 20% opacity if the slide needs more life.

How to draw them:
- **Claude Slides.** Inline `<svg>` with paths or circles, without text, under 52 KB. It is pinned at full size and placed first in the slide.
- **PowerPoint.** Draw the same SVG, convert it to PNG at 1920 × 1080 and insert it as a full-slide picture sent to the back. If that is not possible, use the flat theme colours without the graphic.

## Cover layout

| Element | Position and style |
|---|---|
| Logo (company decks) | Top left at x 128, y 112. Height 72 to 96 px, width at most 320 px. |
| Course | 24 px, uppercase, letter-spacing 3 px, accent colour (accent on dark slides when the cover is dark). |
| Title | 80 to 88 px, bold (serif in Classic), at most 2 lines, at most 1150 px wide. |
| Subtitle | 36 px, muted, or white at 75% on dark covers. |
| Team and date | 28 px, semibold. The team members' names go here if the user gave them, otherwise `[TEAM: names]`. |
| Photo (optional) | Either the right half of the slide (960 × 1080, cropped to fill), or the full slide with a dark scrim `rgba(10,26,54,0.65)` and white text. |

The title block is vertically centred and starts at x 128 (x 200 in Clean, after the accent bar).

## Closing slide

The closing slide uses the same look as the cover: a dark background and graphic in Midnight and Classic, a light background with arcs in Clean, and the brand block with logo in Company colours. It shows one line ("Questions?" or "Thank you"), the team names and optionally one contact line. It never carries new content.

## Logo

A company deck should show the logo of the company it analyses. It goes large on the cover and the closing slide, and small (48 to 56 px high) at the top right of the header band on every content slide (`design.md`). If the user does not want it on every slide, it stays on the cover and closing slide only. The team label at the top right keeps the team and the course on every slide, so the deck is clearly a student analysis.

1. **Where the file comes from**, in this order.
   - A logo file the user gave.
   - Wikimedia Commons, if the user chose it in the intake round (SKILL.md, Step 4 describes how to find the file). If Commons has no suitable file, the company's own press or brand page is the fallback, under the same permission. Name the page in the sources.
   - Otherwise leave a placeholder. In Claude Slides, use an empty image frame with `alt="Company logo"` at the logo position, which the user fills with one click in the editor. Put the placeholder on the cover only, so the user does not have to fill 15 frames. In PowerPoint, use a light grey box labelled "Add logo", ideally on the slide master so one change fills every slide. Name the open logo in the delivery message.
2. **Never draw or rebuild a logo** from memory, as SVG or as text.
3. **Use the logo as it is.** Do not recolour, stretch, crop or add effects. On dark covers, use the version made for dark backgrounds if the company provides one. Otherwise place the logo on a white rounded card with 24 px padding.
4. **Keep it a student deck.** The course, the team and the date stay on the cover. No company slogans, no copying of the company's own slide templates.
5. Decks that compare several companies show only the main company's logo on the cover, or no logo if there is no main company.

## Images

- **Priority.** Use the user's own images first. Then, in Claude Slides, use the Slides photo library if the Artifact tool offers `photo_search`, following the type's photo-library rules. Otherwise use no photo, because the decorative graphic is enough.
- **Where.** Images go on the cover, section dividers and closing slide. Content slides use images only when the image is the evidence, for example a product photo the user gave.
- **Honesty.** A stock photo never pretends to show the company's own product, office, people or event. A game controller photo is fine on an Xbox cover. A photo labelled "Xbox headquarters" is only fine if it really is.
- **Missing files.** Never invent an image file. If a slide needs a specific picture the user has not given, leave an empty frame and name it in the delivery message.
