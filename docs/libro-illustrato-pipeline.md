# Libro illustrato + video — pipeline operativa Higgsfield

Documento di lavoro. Nessun dato personale, nessuna foto: solo architettura, prompt
template e budget. I nomi dei personaggi sono placeholder (`[BAMBINA]`, `[MAMMA]`,
`[PAPA]`).

---

## 1. La decisione architetturale: Elements, non Soul

Higgsfield offre due modi per avere un personaggio ricorrente e coerente. Non sono
equivalenti e la scelta sbagliata blocca il progetto allo step del video.

| | **Soul (character training)** | **Elements (reference element)** |
|---|---|---|
| Foto necessarie | 5–20 della stessa persona | **1** |
| Tempo | ~10 min di training | istantaneo |
| Persone per inquadratura | **1 sola** | **più di una** |
| Modelli compatibili | solo Soul V2 / Soul Cinema | Nano Banana Pro/2, Seedream, GPT Image 2, Cinema Studio, **Seedance 2.0**, Kling 3.0 |

**Si va di Elements.** Tre motivi, in ordine di importanza:

1. **Seedance 2.0 non supporta Soul.** Se addestriamo un Soul, il libro viene bene e
   poi al momento del video ci troviamo davanti a un muro. Elements è compatibile con
   Seedance 2.0 in modo nativo.
2. **Soul gestisce una persona sola per immagine.** Metà del progetto è "anche noi
   insieme": famiglia nella stessa scena. Con Soul non è possibile, con Elements sì
   (più riferimenti nello stesso prompt).
3. **Serve una sola foto invece di venti.** Il tuo dubbio sulle foto si risolve da solo.

### Conseguenza sulle foto — il punto che ti interessava

Il flusso è a **due stadi**, ed è qui che sta la parte importante:

```
foto reale ──(usata UNA volta)──▶ ritratto cartoon ──▶ Element ──▶ tutte le 24 tavole + video
                                        ▲
                          da qui in poi la foto reale non serve più
```

L'Element **non viene creato dalla foto reale, ma dal ritratto cartoon generato**.
Quindi:

- servono **2–3 foto in totale**, non venti/trenta;
- vengono usate solo nella primissima generazione, per ricavare il personaggio;
- da quel momento la pipeline lavora su un disegno, non su tua figlia: il libro, le
  24 tavole e il video derivano tutti dal cartoon;
- l'output è dichiaratamente stilizzato, non fotorealistico — che è esattamente lo
  stile che vuoi e insieme la scelta più prudente.

Il "vestito che vogliamo" e tutto il resto si pilotano dal prompt sull'Element, senza
mai ritoccare le foto originali.

**Le 2–3 foto da scegliere** (una buona foto vale più di trenta mediocri):

1. frontale, viso intero, occhi aperti, luce naturale diffusa (no flash, no controluce);
2. tre quarti, stessa illuminazione;
3. figura intera in piedi, per proporzioni e corporatura.

Niente occhiali da sole, niente cappelli, niente altre persone nell'inquadratura, niente
foto con la faccia in ombra.

---

## 2. Fasi

### Fase 0 — Character master (~30 crediti)
Da 1 foto → ritratto cartoon 3D stile Pixar. Si itera finché la somiglianza convince:
è il passaggio su cui vale la pena spendere tentativi, perché tutto il resto ne dipende.
Modello: `nano_banana_2` (image-to-image), 2k.

### Fase 1 — Character sheet (~20 crediti)
Dal master si genera un model sheet: fronte / tre quarti / profilo / retro + 4 espressioni
(sorriso, sorpresa, imbronciata, addormentata). Higgsfield ha un workflow dedicato
(`character-sheet`) che va caricato prima di generare.
È il passaggio che garantisce la **coerenza** tra le 24 tavole: senza, il personaggio
"deriva" di pagina in pagina.

### Fase 2 — Elements (0 crediti)
Si registrano 3 Elements dai character sheet: `[BAMBINA]`, `[MAMMA]`, `[PAPA]`.
Operazione istantanea e gratuita. Da qui in poi ogni prompt li richiama.

### Fase 3 — Storia
Struttura consigliata per la fascia 3–6 anni: **24 tavole**, arco in 5 movimenti.

| Tavole | Movimento |
|---|---|
| 1–4 | Mondo ordinario — casa, famiglia, la routine |
| 5–8 | Innesco — succede qualcosa, la bambina parte |
| 9–14 | Viaggio — tre ostacoli, tre piccole vittorie |
| 15–19 | Crisi — l'ostacolo grosso, i genitori arrivano |
| 20–24 | Ritorno — casa, ma cambiata; ultima tavola speculare alla prima |

Regole: una frase per tavola (max 25 parole), rima o ritmo ripetuto, una formula
ricorrente che il bambino impara e anticipa ad alta voce. La tavola 24 riprende
l'inquadratura della tavola 1 — è il trucco che fa "chiudere" un albo illustrato.

### Fase 4 — Tavole (~100–140 crediti)
24 illustrazioni + copertina, `nano_banana_2` a 2k, formato 4:3 o 1:1.

### Fase 5 — Impaginazione (0 crediti)
PDF pronto per la stampa: testo + immagini, margini e dorso corretti. Lo produco io
direttamente, senza consumare crediti.

### Fase 6 — Video (~270–350 crediti per 60 secondi)
Si scelgono 12 tavole chiave. Ogni tavola diventa lo `start_image` di una clip
Seedance 2.0 da 5 secondi. Vantaggio: il video eredita esattamente lo stile del libro,
niente rischio di deriva.

---

## 3. Prompt template

### Character master (fase 0)
```
3D animated feature film character portrait of a young girl, Pixar/Disney animation
style, soft subsurface-scattering skin, large expressive eyes, rounded friendly
proportions, warm cinematic three-point lighting, neutral studio background,
head and shoulders, facing camera.
Keep the child's distinctive traits: [colore capelli], [taglio], [colore occhi],
[tratti caratteristici].
Wholesome, warm, family-friendly.
```
Foto reale come `medias` con role `image`.

### Tavola singola (fase 4)
```
Children's picture book illustration, 3D animated feature film style, Pixar-like
rendering, warm cinematic lighting, rich but soft color palette, shallow depth of
field, wide establishing shot with generous empty sky area for the text.

<<<BAMBINA_ID>>> [azione] in [ambiente].
[Descrizione atmosfera / ora del giorno / meteo.]
Outfit: [descrizione vestito].
Mood: [emozione].

Consistent character design across the series. No text, no letters, no watermark.
```

### Tavola con famiglia
```
... <<<BAMBINA_ID>>> holding hands with <<<MAMMA_ID>>> and <<<PAPA_ID>>> while ...
```

### Clip video (fase 6)
```
Gentle cinematic animation. [Soggetto] [movimento lento e specifico].
Camera: slow push-in / gentle pan left / static.
Subtle ambient motion: [foglie, capelli, tessuto, luce].
Preserve the exact art style, colors and character design of the source frame.
```
Parametri: `start_image` = job id della tavola, `duration: 5`, `resolution: 720p`,
`mode: std`, `generate_audio: false` (l'audio si gestisce a parte, per controllarlo).

**Blocco stile da ripetere identico in ogni prompt** — è ciò che tiene insieme
le 24 tavole:
```
3D animated feature film style, Pixar-like rendering, soft global illumination,
warm color grading, shallow depth of field, family-friendly.
```

---

## 4. Budget — costi reali verificati

Costi rilevati direttamente dall'API (crediti per generazione):

| Operazione | Costo |
|---|---|
| Nano Banana 2 — immagine 1k | 1,5 |
| Nano Banana 2 — immagine 2k | 2 |
| Seedance 2.0 — 5s 720p fast | 17,5 |
| Seedance 2.0 — 5s 720p std | 22,5 |
| Seedance 2.0 — 5s 1080p std | 45 |

### Preventivo su 1000 crediti

| Voce | Calcolo | Crediti |
|---|---|---|
| Character master, 3 personaggi + iterazioni | ~25 × 2 | 50 |
| Character sheet, 3 personaggi | ~10 × 2 | 20 |
| 24 tavole, ~2 tentativi ciascuna | ~50 × 2 | 100 |
| Copertina e retro | 4 × 2 | 8 |
| **Subtotale libro** | | **~180** |
| Video 60s: 12 clip da 5s @720p std | 12 × 22,5 | 270 |
| Margine ritentativi video (~30%) | | 80 |
| **Subtotale video** | | **~350** |
| **Totale** | | **~530** |

**1000 crediti bastano con margine ampio.** Restano ~470 crediti, sufficienti per
portare il video a 2 minuti oppure per rifare parecchie tavole.

Nota: il libro costa pochissimo (~180). **Il video è l'80% della spesa.** Se il budget
si stringe, si taglia sui secondi di video, mai sulle tavole.

### 720p o 1080p?
A 1080p il video da 60s passa da ~350 a ~700 crediti: il totale sale a ~880 su 1000,
troppo tirato per gestire imprevisti. Consiglio: **generare a 720p std** e valutare
`upscale_video` sulle clip finali migliori (da verificare come costo prima di
impegnarcisi). Alternativa: 1080p solo su 4–5 scene chiave, 720p sul resto.

---

## 5. Cosa serve prima di partire

Da decidere/fornire:

1. **2–3 foto** secondo i criteri della sezione 1.
2. Nome della protagonista, età, e 3–4 cose che ama (animali, luoghi, oggetti,
   personaggi) — servono a costruire una storia che sia davvero sua.
3. Se compaiono anche mamma e papà: 1 foto ciascuno, stessi criteri.
4. Tema della storia: avventura, buonanotte, primo giorno di scuola, superamento
   di una paura, nascita di un fratellino.
5. Formato: quadrato 20×20 (classico da regalo) o orizzontale 24×18 (più cinematografico).

Nota operativa: il piano non dipende dall'acquisto dei crediti. Storia, struttura delle
24 tavole e prompt completi si scrivono a costo zero — i crediti servono solo al momento
di premere "genera".
