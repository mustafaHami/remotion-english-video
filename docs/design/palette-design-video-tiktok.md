# Palette design — vidéo TikTok « Make ou do ? »

Document de design pour réaliser la vidéo dans Remotion. Il contient tout : format, couleurs, typographie, composants, mascotte (dessin compris), zones sûres, textes, positions, minutage et animations.

## 1. Format

| | |
| --- | --- |
| Plateforme | TikTok (fonctionne aussi en Reels) |
| Taille | 1080 × 1920, 9:16 |
| Cadence | 30 fps |
| Durée | 16 s = 480 frames |
| Unité | `u` = unité du design, sur une scène de 360 × 640. **1u = 3px** |
| Couverture | image fixe 1080 × 1920 |
| Photo de profil | image fixe 1080 × 1080, recadrée en rond par TikTok |

Toutes les mesures de ce document sont en u. Le plus simple : construire la scène à 360 × 640, puis la mettre à l'échelle × 3 une seule fois.

```tsx
import {AbsoluteFill} from 'remotion';

export const Stage: React.FC<{bg: string; children: React.ReactNode}> = ({bg, children}) => (
  <AbsoluteFill style={{backgroundColor: bg}}>
    <div style={{width: 360, height: 640, position: 'relative', overflow: 'hidden',
      transform: 'scale(3)', transformOrigin: '0 0'}}>
      {children}
    </div>
  </AbsoluteFill>
);
```

## 2. Identité (à respecter partout)

- Fond en aplat de couleur vive, **une couleur par carte**. Une feuille crème monte par-dessus, coins hauts arrondis à 40u.
- Formes rondes et **en relief** : les boutons, options, pastilles et cartes ont un rebord dur dessous (ombre sans flou, par exemple `0 4u 0`).
- Typo joufflue : **Baloo 2 ExtraBold** pour ce qu'on lit en grand, **Nunito** pour le reste.
- Le texte est toujours `ink` #1E1B3A, blanc sur fond encre. La traduction française est toujours `violet` #6A3FD1.
- `coral` #FF6F59 est l'accent vif (trou pointillé, arc du minuteur, foulard du renard). **Il ne porte jamais de texte.**
- Bonne réponse = `success` #137A4B sur `successBg` #D4F5E3, **toujours avec une coche**, jamais la couleur seule.
- Pas de dégradé, pas d'emoji, pas d'ombre floue.
- Ton : tutoiement, phrases courtes, encourageant. Jamais « Faux ».

## 3. Couleurs

| Nom | Valeur | Usage |
| --- | --- | --- |
| `ink` | #1E1B3A | Texte, contours, tag, bulles, pattes du renard |
| `ink2` | #3A3654 | Chapeau de l'accroche, indice |
| `inkMuted` | #5E5A72 | « Demain » |
| `onInk` | #FFFFFF | Texte sur fond encre |
| `sheet` | #FFFDF8 | Feuille, cercles et étincelles décoratifs |
| `surface` | #FFFFFF | Options, pastilles, carte de fin, minuteur |
| `coral` | #FF6F59 | Trou pointillé, arc du minuteur |
| `violet` | #6A3FD1 | Traduction, sous-titres « + … » |
| `success` | #137A4B | Bonne réponse : texte, bordure, rebord |
| `successBg` | #D4F5E3 | Bonne réponse : fond |
| `mintSoft` | #DDF5EC | Pastille de la cloche |
| `star` | #FFD84D | Étoiles du renard |
| `line` | rgba(30,27,58,.16) | Bordure des options |
| `lineSoft` | rgba(30,27,58,.12) | Bordure des pastilles et de la carte de fin |
| `ledge` | rgba(30,27,58,.14) | Rebord standard |
| `ledgeStrong` | rgba(30,27,58,.3) | Rebord des bulles encre |
| `ledgeTile` | rgba(30,27,58,.25) | Rebord des tuiles de la couverture |
| `track` | rgba(30,27,58,.12) | Piste du minuteur |

**Fonds par scène :** lavande #A99BFF (scènes 1 à 4, couverture, photo de profil), citron #FFD84D (scène 5), menthe #6FD6AE (scène 6). Le changement de couleur accompagne le swipe d'une carte à l'autre.

**Renard :** pelage #FF9F6B, crème #FFFDF8, contour et pattes #1E1B3A, foulard #FF6F59, joues et langue #FF8A80.

## 4. Typographie

Chargement dans Remotion (accents français compris) :

```ts
import {loadFont as loadBaloo} from '@remotion/google-fonts/Baloo2';
import {loadFont as loadNunito} from '@remotion/google-fonts/Nunito';

const baloo = loadBaloo('normal', {weights: ['800'], subsets: ['latin', 'latin-ext']});
const nunito = loadNunito('normal', {weights: ['600', '700', '800'], subsets: ['latin', 'latin-ext']});
// display = baloo.fontFamily, body = nunito.fontFamily
```

| Style | Police | Taille (u) | Graisse | Interligne / approche | Couleur | Où |
| --- | --- | --- | --- | --- | --- | --- |
| `hookTitle` | Baloo 2 | 40 | 800 | 1,04 / −0,02em | ink | « Un mot manque. Tu le trouves ? » |
| `endTitle` | Baloo 2 | 42 | 800 | 1,02 / −0,02em | ink | « Un piège par jour. » |
| `sentence` | Baloo 2 | 36 | 800 | 1,2 / −0,01em | ink | « Can you ___ me a favor? » |
| `tipHeading` | Baloo 2 | 40 | 800 | 1 | ink | « do » / « make » |
| `coverWord` | Baloo 2 | 54 | 800 | 1 | ink | Tuiles de la couverture |
| `coverJoin` | Baloo 2 | 28 | 800 | 1 | ink | « ou » sur la couverture |
| `teaser` | Baloo 2 | 28 | 800 | 1,05 | ink | « say ou tell ? » |
| `bubble` | Baloo 2 | 22 | 800 | 1 | blanc ou ink | Bulles du renard |
| `bubbleHook` | Baloo 2 | 24 | 800 | 1 | blanc | Bulle « Hello ! » |
| `timerDigit` | Baloo 2 | 30 | 800 | 1 | ink | 3, 2, 1 |
| `feedback` | Baloo 2 | 19 | 800 | 1,1 | success | « Bien joué si tu as dit do ! » |
| `translation` | Nunito | 17 | 800 | 1,35 | violet | Traduction |
| `lead` | Nunito | 17 | 800 | 1,35 | ink2 | Chapeau de l'accroche |
| `leadEnd` | Nunito | 16 | 800 | 1,35 | ink | Chapeau de la fin |
| `option` | Nunito | 19 | 800 | 1 | ink | make / do / give |
| `hint` | Nunito | 15 | 800 | 1,3 | ink2 | Indice |
| `pill` | Nunito | 15 | 800 | 1 | ink | Pastilles de l'astuce |
| `tipSub` | Nunito | 14 | 800 | 1,3 | violet | « + une action » |
| `tag` | Nunito | 13 | 800 | 1,2 | blanc | Tag de format |
| `meta` | Nunito | 13 | 800 | 1,2 | inkMuted | « Demain » |

## 5. Formes

| | u |
| --- | --- |
| Rayons | pilule 999, pastille et trou 14, option et tuile 20, carte et bulle 22, coin de queue de bulle 6, feuille 40 |
| Bordures | option, pastille, carte 2 ; trou pointillé et bulle pensée 3 |
| Rebords (ombre sans flou) | options, carte, minuteur `0 4 0 ledge` ; pastilles `0 3 0 ledge` ; bulles encre `0 4 0 ledgeStrong` ; tuiles de couverture `0 6 0 ledgeTile` ; bonne réponse `0 4 0 success` (`0 3 0` pour une pastille) |
| Marges | 20 à gauche ; contenu large de 284 sous y = 290 (voir zones sûres) |

## 6. Composants

**Tag de format** — padding 7 × 12, rayon 999, fond `ink`, texte `tag`. Toujours au-dessus du renard.

**Feuille** — de son `y` jusqu'en bas, pleine largeur, fond `sheet`, rayon 40 sur les coins hauts.

**Bulle encre** — padding 9 16 11, rayons `22 22 22 6` (le petit coin bas gauche pointe vers le renard), fond `ink`, texte blanc, rebord `0 4 0 ledgeStrong`.

**Bulle pensée** — padding 7 14 9, bordure 3 `ink`, fond blanc, texte `ink`, mêmes rayons, sans rebord.

**Trou vide** — 92 × 40, bordure 3 **pointillée** `coral`, rayon 14, posé 8u sous la ligne de base. Retour à la ligne juste après le trou.

**Trou rempli** — « do » en `sentence`, padding horizontal 12, rayon 14, fond `successBg`, texte `success`.

**Options de réponse** — 3 colonnes égales, écart 8, largeur totale 284, hauteur 56, rayon 20, texte `option` centré.
- Normale : fond blanc, bordure 2 `line`, rebord `0 4 0 ledge`.
- Juste : fond `successBg`, bordure 2 `success`, rebord `0 4 0 success`, texte `success`, coche de 16u (trait 3,4) puis 6u avant le mot.
- Écartée : opacité 0,45, sans rebord.

**Minuteur** — cercle blanc de 68, rebord `0 4 0 ledge`. Piste : cercle de rayon 27, trait 7, `track`. Arc : même cercle, trait 7, `coral`, bouts ronds, départ à midi. Chiffre centré en `timerDigit`.

**Indice** — icône commentaire 18u (trait 2,2, `ink`), 8u, texte `hint`.

**Pastille** — hauteur 34, padding horizontal 12, rayon 14, fond blanc, bordure 2 `lineSoft`, rebord `0 3 0 ledge`, texte `pill`. Version juste : couleurs success, rebord `0 3 0 success`, coche de 12u (trait 3,6) puis 6u.

**Colonnes de l'astuce** — 2 colonnes égales, écart 14. Dans chaque colonne : titre `tipHeading`, 4u, sous-titre `tipSub`, 8u, pastilles empilées (écart 8, alignées à gauche).

**Carte de fin** — 284 × 84, rayon 22, fond blanc, bordure 2 `lineSoft`, rebord `0 4 0 ledge`, padding 0 14 0 18, contenu centré verticalement. À gauche, « Demain » (`meta`) au-dessus de « say ou tell ? » (`teaser`), écart 2. À droite, pastille ronde de 44 en `mintSoft` avec une cloche de 22u (trait 2,2).

**Tuiles de la couverture** — padding 8 22 10, rayon 20, fond blanc, rebord `0 6 0 ledgeTile`, rotation −5° pour « make » et 4° pour « do ? ». « ou » entre les deux en `coverJoin`, padding vertical 6. Colonne centrée, écart 2.

**Décor** — cercles `sheet` (opacité indiquée par scène) et étincelles à 4 branches en `sheet`. Ils peuvent flotter lentement (8u aller-retour en 4 s), jamais devant un texte.

### Icônes (viewBox 24 × 24, trait `ink`, bouts et jonctions ronds, pas de remplissage)

| Icône | Tracé |
| --- | --- |
| Coche | `M5 12.5l4.5 4.5L19 7.5` |
| Commentaire | `M4.5 18.5l1.2-3.6A7.5 7.5 0 1 1 9 18.2z` |
| Cloche | `M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 2h-15z` et `M10 20.5a2.2 2.2 0 0 0 4 0` |

### Étincelle (centre cx, cy ; demi-hauteur r)

`M cx,(cy−r) l 0.3125r,0.6875r l 0.6875r,0.3125r l −0.6875r,0.3125r l −0.3125r,0.6875r l −0.3125r,−0.6875r l −0.6875r,−0.3125r l 0.6875r,−0.3125r z`

Exemple pour r = 16 : `M300 186 l5 11 l11 5 l-11 5 l-5 11 l-5 -11 l-11 -5 l11 -5 z` (centre 300, 202).

## 7. La mascotte

Un renard original, à reproduire **exactement** depuis le SVG ci-dessous : ne pas changer ses proportions, ses couleurs ni son contour. Miroir horizontal autorisé : `translate(210 0) scale(-1 1)`.

- viewBox `0 0 210 240` pour toutes les poses, sauf **portrait** : viewBox `15 10 170 170` (carré, déborde coupé).
- Taille dans la vidéo : la **largeur** est donnée par scène ; hauteur = largeur × 240 / 210 (carré pour le portrait).
- Ordre de dessin = ordre du SVG. Chaque pose n'affiche que certains groupes (tableau après le SVG). Les éléments sans `id` sont toujours affichés.

```svg
<svg viewBox="0 0 210 240" xmlns="http://www.w3.org/2000/svg">
  <ellipse id="ground" cx="100" cy="228" rx="56" ry="7" fill="#1E1B3A" opacity=".12"/>
  <g id="float">
    <g id="tail" stroke="#1E1B3A" stroke-width="4" stroke-linejoin="round">
      <path d="M126 206 C 160 214, 200 196, 202 156 C 204 128, 190 108, 170 104 C 178 128, 170 156, 134 176 Z" fill="#FF9F6B"/>
      <path d="M170 104 C 190 108, 204 128, 202 156 C 194 146, 184 140, 175 137 C 177 126, 175 114, 170 104 Z" fill="#FFFDF8"/>
    </g>
    <path d="M60 200 C 56 166, 74 142, 100 142 C 126 142, 144 166, 140 200 C 139 210, 128 216, 100 216 C 72 216, 61 210, 60 200 Z" fill="#FF9F6B" stroke="#1E1B3A" stroke-width="4" stroke-linejoin="round"/>
    <path d="M82 202 C 80 182, 88 166, 100 166 C 112 166, 120 182, 118 202 C 112 208, 88 208, 82 202 Z" fill="#FFFDF8"/>
    <ellipse cx="80" cy="214" rx="15" ry="8" fill="#1E1B3A"/>
    <ellipse cx="120" cy="214" rx="15" ry="8" fill="#1E1B3A"/>

    <g id="arm-left-down" fill="none" stroke-linecap="round">
      <path d="M66 166 C 58 176, 56 188, 62 196" stroke="#1E1B3A" stroke-width="18"/>
      <path d="M66 166 C 58 176, 56 188, 62 196" stroke="#FF9F6B" stroke-width="10"/>
      <circle cx="62" cy="196" r="8" fill="#1E1B3A"/>
    </g>
    <g id="arm-right-down" fill="none" stroke-linecap="round">
      <path d="M134 166 C 142 176, 144 188, 138 196" stroke="#1E1B3A" stroke-width="18"/>
      <path d="M134 166 C 142 176, 144 188, 138 196" stroke="#FF9F6B" stroke-width="10"/>
      <circle cx="138" cy="196" r="8" fill="#1E1B3A"/>
    </g>
    <g id="arm-wave" fill="none" stroke-linecap="round">
      <path d="M66 164 C 42 160, 24 142, 17 114" stroke="#1E1B3A" stroke-width="18"/>
      <path d="M66 164 C 42 160, 24 142, 17 114" stroke="#FF9F6B" stroke-width="10"/>
      <circle cx="16" cy="111" r="8.5" fill="#1E1B3A"/>
      <path d="M8 96 C 12 88, 20 86, 26 89 M3 87 C 9 76, 22 73, 31 78" stroke="#1E1B3A" stroke-width="3"/>
    </g>
    <g id="arms-cheer" fill="none" stroke-linecap="round">
      <path d="M66 164 C 40 160, 20 140, 12 108" stroke="#1E1B3A" stroke-width="18"/>
      <path d="M66 164 C 40 160, 20 140, 12 108" stroke="#FF9F6B" stroke-width="10"/>
      <circle cx="11" cy="105" r="8.5" fill="#1E1B3A"/>
      <path d="M134 164 C 160 160, 180 140, 188 108" stroke="#1E1B3A" stroke-width="18"/>
      <path d="M134 164 C 160 160, 180 140, 188 108" stroke="#FF9F6B" stroke-width="10"/>
      <circle cx="189" cy="105" r="8.5" fill="#1E1B3A"/>
    </g>

    <g stroke-linejoin="round">
      <path d="M74 140 C 90 146, 110 146, 126 140 L 104 164 C 102 166, 98 166, 96 164 Z" fill="#FF6F59" stroke="#1E1B3A" stroke-width="4"/>
      <path d="M48 92 C 40 66, 40 40, 50 20 C 66 30, 82 48, 90 64 Z" fill="#FF9F6B" stroke="#1E1B3A" stroke-width="4"/>
      <path d="M55 80 C 51 63, 51 46, 55 34 C 65 42, 73 52, 79 62 Z" fill="#FFFDF8"/>
      <path d="M152 92 C 160 66, 160 40, 150 20 C 134 30, 118 48, 110 64 Z" fill="#FF9F6B" stroke="#1E1B3A" stroke-width="4"/>
      <path d="M145 80 C 149 63, 149 46, 145 34 C 135 42, 127 52, 121 62 Z" fill="#FFFDF8"/>
      <path d="M100 54 C 138 54, 160 76, 162 102 C 163 110, 168 118, 174 124 C 158 132, 140 146, 100 148 C 60 146, 42 132, 26 124 C 32 118, 37 110, 38 102 C 40 76, 62 54, 100 54 Z" fill="#FF9F6B"/>
      <path d="M30 123 C 46 110, 60 104, 72 106 C 84 108, 93 114, 100 119 C 107 114, 116 108, 128 106 C 140 104, 154 110, 170 123 C 152 136, 130 146, 100 147 C 70 146, 48 136, 30 123 Z" fill="#FFFDF8"/>
      <path d="M100 54 C 138 54, 160 76, 162 102 C 163 110, 168 118, 174 124 C 158 132, 140 146, 100 148 C 60 146, 42 132, 26 124 C 32 118, 37 110, 38 102 C 40 76, 62 54, 100 54 Z" fill="none" stroke="#1E1B3A" stroke-width="4"/>
      <ellipse cx="58" cy="124" rx="9" ry="5" fill="#FF8A80" opacity=".6"/>
      <ellipse cx="142" cy="124" rx="9" ry="5" fill="#FF8A80" opacity=".6"/>
      <path d="M92 116 C 92 112, 108 112, 108 116 C 108 120, 103 124, 100 124 C 97 124, 92 120, 92 116 Z" fill="#1E1B3A"/>
    </g>

    <g id="eyes-open">
      <ellipse cx="76" cy="96" rx="7" ry="9" fill="#1E1B3A"/>
      <ellipse cx="124" cy="96" rx="7" ry="9" fill="#1E1B3A"/>
      <circle cx="78.5" cy="92.5" r="2.6" fill="#FFFFFF"/>
      <circle cx="126.5" cy="92.5" r="2.6" fill="#FFFFFF"/>
    </g>
    <g id="eyes-up">
      <ellipse cx="78" cy="93" rx="7" ry="9" fill="#1E1B3A"/>
      <ellipse cx="126" cy="93" rx="7" ry="9" fill="#1E1B3A"/>
      <circle cx="80" cy="88.5" r="2.6" fill="#FFFFFF"/>
      <circle cx="128" cy="88.5" r="2.6" fill="#FFFFFF"/>
      <path d="M66 78 C 71 73, 79 72, 85 75 M115 75 C 121 72, 129 73, 134 78" fill="none" stroke="#1E1B3A" stroke-width="3.2" stroke-linecap="round"/>
    </g>
    <g id="eyes-happy" fill="none" stroke="#1E1B3A" stroke-width="4.2" stroke-linecap="round">
      <path d="M68 99 C 71 90, 81 90, 84 99"/>
      <path d="M116 99 C 119 90, 129 90, 132 99"/>
    </g>

    <path id="mouth-smile" d="M91 129 C 94 133, 98 133, 100 129 C 102 133, 106 133, 109 129" fill="none" stroke="#1E1B3A" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
    <path id="mouth-hmm" d="M94 131 C 98 133, 104 132, 109 128" fill="none" stroke="#1E1B3A" stroke-width="3.2" stroke-linecap="round"/>
    <g id="mouth-open">
      <path d="M90 128 C 92 143, 108 143, 110 128 C 104 131, 96 131, 90 128 Z" fill="#1E1B3A" stroke="#1E1B3A" stroke-width="2" stroke-linejoin="round"/>
      <path d="M94.5 137 C 97 141, 103 141, 105.5 137 C 103 135, 97 135, 94.5 137 Z" fill="#FF8A80"/>
    </g>

    <g id="arm-point" fill="none" stroke-linecap="round">
      <path d="M134 166 C 150 174, 166 182, 180 188" stroke="#1E1B3A" stroke-width="18"/>
      <path d="M134 166 C 150 174, 166 182, 180 188" stroke="#FF9F6B" stroke-width="10"/>
      <circle cx="182" cy="189" r="8.5" fill="#1E1B3A"/>
      <path d="M187 192 L 199 199" stroke="#1E1B3A" stroke-width="7"/>
    </g>
    <g id="arm-think">
      <g fill="none" stroke-linecap="round">
        <path d="M136 168 C 152 162, 148 146, 122 148" stroke="#1E1B3A" stroke-width="18"/>
        <path d="M136 168 C 152 162, 148 146, 122 148" stroke="#FF9F6B" stroke-width="10"/>
        <circle cx="120" cy="148" r="8.5" fill="#1E1B3A"/>
      </g>
      <circle cx="166" cy="58" r="5" fill="#FFFFFF" stroke="#1E1B3A" stroke-width="3"/>
      <circle cx="180" cy="40" r="8" fill="#FFFFFF" stroke="#1E1B3A" stroke-width="3"/>
    </g>
    <g id="arm-tip" fill="none" stroke-linecap="round">
      <path d="M134 166 C 152 160, 164 146, 170 130" stroke="#1E1B3A" stroke-width="18"/>
      <path d="M134 166 C 152 160, 164 146, 170 130" stroke="#FF9F6B" stroke-width="10"/>
      <circle cx="171" cy="127" r="8.5" fill="#1E1B3A"/>
      <path d="M172 120 L 174 107" stroke="#1E1B3A" stroke-width="7"/>
    </g>
    <g id="stars" fill="#FFD84D" stroke="#1E1B3A" stroke-width="3" stroke-linejoin="round">
      <path d="M28 41 C 29.5 49, 31 50.5, 39 52 C 31 53.5, 29.5 55, 28 63 C 26.5 55, 25 53.5, 17 52 C 25 50.5, 26.5 49, 28 41 Z"/>
      <path d="M194 50 C 195.2 56.4, 196.4 57.6, 202.8 58.8 C 196.4 60, 195.2 61.2, 194 67.6 C 192.8 61.2, 191.6 60, 185.2 58.8 C 191.6 57.6, 192.8 56.4, 194 50 Z"/>
      <path d="M172 12 C 172.9 16.8, 173.8 17.7, 178.6 18.6 C 173.8 19.5, 172.9 20.4, 172 25.2 C 171.1 20.4, 170.2 19.5, 165.4 18.6 C 170.2 17.7, 171.1 16.8, 172 12 Z"/>
    </g>
  </g>
</svg>
```

**Groupes affichés par pose** (✓ = affiché ; le reste est masqué)

| Groupe | salut | montre | reflechit | bravo | astuce | portrait |
| --- | --- | --- | --- | --- | --- | --- |
| `ground`, `tail` | ✓ | ✓ | ✓ | ✓ | ✓ | |
| `arm-left-down` | | ✓ | ✓ | | ✓ | ✓ |
| `arm-right-down` | ✓ | | | | | ✓ |
| `arm-wave` | ✓ | | | | | |
| `arms-cheer` | | | | ✓ | | |
| `eyes-open` | ✓ | ✓ | | | ✓ | ✓ |
| `eyes-up` | | | ✓ | | | |
| `eyes-happy` | | | | ✓ | | |
| `mouth-smile` | | ✓ | | | | ✓ |
| `mouth-hmm` | | | ✓ | | | |
| `mouth-open` | ✓ | | | ✓ | ✓ | |
| `arm-point` | | ✓ | | | | |
| `arm-think` | | | ✓ | | | |
| `arm-tip` | | | | | ✓ | |
| `stars` | | | | ✓ | | |

**Animations au repos** (à calculer depuis la frame, `t` en secondes, `loop(t, p) = 0,5 − 0,5·cos(2π·t / p)` qui va de 0 à 1 puis revient à 0) :

| Élément | Mouvement |
| --- | --- |
| `float` | translation verticale −4·loop(t, 3) |
| `tail` | rotation 5°·loop(t, 2,6) autour de (130, 200) |
| Clignement (`eyes-open`) | rayon vertical des yeux 9 ; sur un cycle de 4,5 s, de 92 % à 96 % il passe de 9 à 1, de 96 % à 100 % de 1 à 9. Masquer les reflets blancs sous 5 |
| `arm-wave` | rotation −6° + 14°·loop(t, 1) autour de (66, 164) |
| `arm-point` | translation (3, 2)·loop(t, 0,8) |
| `stars` | échelle 0,85 + 0,15·loop(t, 1,2) autour du centre de chaque étoile : (28, 52), (194, 58,8), (172, 18,6) |

Changement de pose = coupe franche, avec un petit écrasement (voir le storyboard).

## 8. Zones sûres TikTok

L'interface TikTok recouvre ces zones : ni texte ni réponse dedans.

| Zone | u | px (1080 × 1920) |
| --- | --- | --- |
| Haut (onglets) | y 0 → 40 | 0 → 120 |
| Droite (boutons) | x 300 → 360, y 290 → 520 | x 900 → 1080, y 870 → 1560 |
| Bas (légende, son) | y 520 → 640 | 1560 → 1920 |

Sous y = 290, le contenu s'arrête à x = 304 (912px).

## 9. Textes

À reprendre tels quels, espaces avant « ? » et « ! » compris.

| Élément | Texte |
| --- | --- |
| Tag (scènes 1 à 4) | Phrase à trou · Le piège du jour |
| Tag (scène 5) | Astuce · Make ou do ? |
| Tag (couverture) | Le piège du jour · #1 |
| Titre de l'accroche | Un mot manque. / Tu le trouves ? (2 lignes) |
| Chapeau de l'accroche | Réponds avant le renard. |
| Phrase | Can you [trou] / me a favor? (retour à la ligne après le trou) |
| Réponse | do |
| Traduction | Tu peux me rendre un service ? |
| Options | make · do · give |
| Indice | Écris ta réponse en commentaire |
| Retour | Bien joué si tu as dit do ! |
| Bulles | Hello ! · Lequel ? · Hmm… · C'est do ! · Retiens ça ! · À demain ! |
| Astuce, colonne 1 | do · + une action · a favor (juste) · homework · the dishes · your best |
| Astuce, colonne 2 | make · + créer, fabriquer · a cake · a mistake · money · a decision |
| Titre de fin | Un piège / par jour. (2 lignes) |
| Chapeau de fin | Abonne-toi, le renard revient demain. |
| Carte de fin | Demain · say ou tell ? |
| Couverture | make · ou · do ? |

## 10. Les scènes

| # | Frames | Fond | Feuille dès y | En résumé |
| --- | --- | --- | --- | --- |
| 1 Accroche | 0–59 | lavande | 470 | Le titre entre ligne par ligne, le renard surgit et fait coucou, bulle « Hello ! ». |
| 2 Question | 60–149 | lavande | 250 | Même carte : la feuille monte pendant que le renard se réduit et passe en haut à gauche. La phrase, la traduction puis les 3 options entrent. Le trou respire. |
| 3 Réfléchis | 150–239 | lavande | 250 | Le renard réfléchit, bulle « Hmm… ». Le minuteur compte 3, 2, 1 et son arc se vide. Indice en bas. |
| 4 Réponse | 240–299 | lavande | 250 | « do » tombe dans le trou, l'option « do » passe en juste avec un rebond, les autres s'effacent. Le renard saute, bulle « C'est do ! ». |
| 5 Astuce | 300–419 | citron | 230 | Swipe vers le haut. « do » et « make » apparaissent, puis leurs pastilles. |
| 6 Fin | 420–479 | menthe | 392 | Swipe. Titre, bulle « À demain ! », la carte monte, la cloche sonne. |

### Positions (u) — chaque scène une fois ses entrées terminées

Pour les blocs de texte, `y` est le haut du bloc. Le tag est toujours en (20, 52).

**Scène 1 · Accroche**

| Élément | x | y | Taille | Contenu |
| --- | --- | --- | --- | --- |
| Titre | 20 | 96 | largeur 320 | `hookTitle`, 2 lignes |
| Chapeau | 20 | 189 | | `lead` |
| Renard | 26 | 232 | largeur 230 | salut |
| Bulle encre | 208 | 230 | | « Hello ! » en `bubbleHook` |
| Décor | | | | cercle (322, 112) r 64 à 22 % ; étincelles (300, 202) r 16 et (28, 257) r 11 |

**Scène 2 · Question**

| Élément | x | y | Taille | Contenu |
| --- | --- | --- | --- | --- |
| Renard | 14 | 72 | largeur 168 | montre |
| Bulle encre | 196 | 112 | | « Lequel ? » |
| Phrase | 20 | 272 | largeur 284 | `sentence`, trou vide |
| Traduction | 20 | 368 | | `translation` |
| Options | 20 | 428 | 284 × 56 | make · do · give |
| Décor | | | | cercle (330, 96) r 58 à 22 % ; étincelle (304, 199) r 13 |

**Scène 3 · Réfléchis** — comme la scène 2, avec :

| Élément | x | y | Taille | Contenu |
| --- | --- | --- | --- | --- |
| Renard | 14 | 72 | largeur 168 | reflechit |
| Bulle pensée | 178 | 96 | | « Hmm… » |
| Minuteur | 266 | 152 | 68 | chiffre 3, 2, 1 |
| Indice | 20 | 496 | | icône + `hint` |
| Décor | | | | cercle (330, 96) r 58 à 22 %, sans étincelle |

**Scène 4 · Réponse** — comme la scène 2, avec :

| Élément | x | y | Taille | Contenu |
| --- | --- | --- | --- | --- |
| Renard | 14 | 72 | largeur 168 | bravo |
| Bulle encre | 200 | 120 | | « C'est do ! » |
| Phrase | 20 | 272 | largeur 284 | trou rempli « do » |
| Options | 20 | 428 | 284 × 56 | « do » juste, « make » et « give » écartées |
| Retour | 20 | 496 | | `feedback` |
| Décor | | | | cercle (330, 96) r 58 à 22 % ; étincelles (300, 212) r 16 et (250, 81) r 11 |

**Scène 5 · Astuce**

| Élément | x | y | Taille | Contenu |
| --- | --- | --- | --- | --- |
| Tag | 20 | 52 | | « Astuce · Make ou do ? » |
| Renard | 16 | 64 | largeur 150 | astuce |
| Bulle encre | 178 | 104 | | « Retiens ça ! » |
| Colonnes | 20 | 254 | largeur 284 | do / make |
| Décor | | | | cercle (326, 92) r 60 à 30 % ; étincelle (306, 189) r 13 |

**Scène 6 · Fin** (pas de tag)

| Élément | x | y | Taille | Contenu |
| --- | --- | --- | --- | --- |
| Titre | 20 | 56 | largeur 320 | `endTitle`, 2 lignes |
| Chapeau | 20 | 150 | | `leadEnd` |
| Renard | 28 | 176 | largeur 200 | salut |
| Bulle encre | 204 | 200 | | « À demain ! » |
| Carte de fin | 20 | 416 | 284 × 84 | Demain · say ou tell ? |
| Décor | | | | cercle (318, 250) r 70 à 22 % ; étincelles (304, 126) r 16 et (30, 207) r 11 |

### Animations, frame par frame

« Entre » = opacité 0 → 1 + translation verticale indiquée → 0. « Pop » = échelle 0,6 → 1 + opacité 0 → 1, origine au petit coin de la bulle (bas gauche). Les courbes sont détaillées en section 11.

| Frame | Durée | Élément | Mouvement | Courbe |
| --- | --- | --- | --- | --- |
| 0 | 8 | Titre, ligne 1 | entre depuis +12u | spring |
| 4 | 8 | Titre, ligne 2 | entre depuis +12u | spring |
| 2 | 14 | Renard | échelle 0,6 → 1 et +40u → 0, origine bas centre | bounce |
| 10 | 8 | Chapeau | entre depuis +8u | spring |
| 14 | 8 | Bulle « Hello ! » | pop | spring |
| 52 | 6 | Titre, chapeau, bulle | sortent : opacité → 0, −8u | standard |
| 60 | 14 | Feuille | y 470 → 250 | swipe |
| 60 | 14 | Renard | pose montre ; (26, 232, largeur 230) → (14, 72, largeur 168) | swipe |
| 70 | 8 | Phrase | entre depuis +12u | spring |
| 72 | 8 | Bulle « Lequel ? » | pop | spring |
| 76 | 8 | Traduction | entre depuis +8u | spring |
| 78 | → 240 | Trou | respire : échelle 1 ↔ 1,04, période 30 frames | sinus |
| 82 | 8 | Option make | entre depuis +16u | spring |
| 86 | 8 | Option do | entre depuis +16u | spring |
| 90 | 8 | Option give | entre depuis +16u | spring |
| 150 | 6 | Renard | pose reflechit + écrasement scaleY 0,96 → 1, origine bas | press |
| 150 | 4 | Bulle « Lequel ? » | sort : opacité → 0 | standard |
| 154 | 8 | Bulle « Hmm… » | pop | spring |
| 156 | 14 | Minuteur | échelle 0 → 1 | bounce |
| 156 | 84 | Arc du minuteur | se vide : 100 % → 0 % du cercle | linéaire |
| 156 | 6 | Chiffre | « 3 », puis « 2 » à 186 et « 1 » à 216 ; à chaque fois échelle 1,15 → 1 | spring |
| 160 | 8 | Indice | entre depuis +8u | spring |
| 240 | 6 | Minuteur, indice, bulle « Hmm… » | sortent : opacité → 0 (minuteur échelle → 0,6) | standard |
| 242 | 4 | Trou vide | pointillés : opacité → 0 | standard |
| 242 | 14 | « do » dans le trou | tombe : −16u → 0, échelle 0,8 → 1, opacité 0 → 1 | bounce |
| 242 | 12 | Renard | pose bravo + saut : 0 → −10u → 0 | standard |
| 244 | 6 | Option do | passe en juste (couleurs + coche) | standard |
| 244 | 16 | Option do | rebond : échelle 1 → 1,05 → 1 | bounce |
| 244 | 8 | Options make et give | opacité → 0,45, rebord retiré | standard |
| 248 | 8 | Bulle « C'est do ! » | pop | spring |
| 256 | 8 | Retour | entre depuis +8u | spring |
| 300 | 14 | Carte | swipe : la carte lavande sort par le haut, la carte citron entre par le bas | swipe |
| 314 | 8 | Bulle « Retiens ça ! » | pop | spring |
| 318 | 8 | « do » | échelle 0,8 → 1 + opacité | spring |
| 322 | 8 | « + une action » | entre depuis +6u | spring |
| 326 | 8 | « make » | échelle 0,8 → 1 + opacité | spring |
| 330 | 8 | « + créer, fabriquer » | entre depuis +6u | spring |
| 334 | 8 chacune | Pastilles | entrent depuis +10u : colonne do à 334, 338, 342, 346 ; colonne make à 336, 340, 344, 348 | spring |
| 360 | 16 | Pastille « a favor » | rebond : échelle 1 → 1,06 → 1 | bounce |
| 420 | 14 | Carte | swipe vers la carte menthe | swipe |
| 428 | 8 | Titre de fin, ligne 1 | entre depuis +12u | spring |
| 432 | 8 | Titre de fin, ligne 2 | entre depuis +12u | spring |
| 438 | 8 | Chapeau de fin | entre depuis +8u | spring |
| 440 | 8 | Bulle « À demain ! » | pop | spring |
| 446 | 10 | Carte de fin | monte : +20u → 0, opacité 0 → 1 | spring |
| 456 | 12 | Cloche | sonne : rotation 0 → 12 → −10 → 6 → 0°, origine haut centre | standard |

## 11. Mouvement

| Nom | ms | Frames à 30 fps | Courbe | Usage |
| --- | --- | --- | --- | --- |
| `press` | 120 | 4 | `Easing.bezier(0.3, 0.7, 0.4, 1)` | Écrasement au changement de pose |
| `fade` | 200 | 6 | `standard` | Sorties, changements de couleur |
| `reveal` | 280 | 8 | `spring` = `Easing.bezier(0.2, 1.2, 0.3, 1)` | Bulles, textes, options qui entrent |
| `drop` | 460 | 14 | `bounce` = `Easing.bezier(0.2, 1.5, 0.4, 1)` | Le mot qui tombe dans le trou |
| `success` | 520 | 16 | `bounce` | Rebond de la bonne réponse |
| `swipe` | — | 14 | `spring({config: {damping: 20, stiffness: 180, mass: 1}})` | Changement de carte, réorganisation 1 → 2 |
| `float` | 4000 | 120 | sinus | Décor, 8u aller-retour |

`standard` = `Easing.bezier(0.2, 0.9, 0.3, 1)`.

Règles :
- Une seule chose importante bouge à la fois ; les entrées s'enchaînent en quinconce (environ 4 frames d'écart).
- `bounce` est réservé aux réussites et aux apparitions marquantes (renard, minuteur, mot qui tombe, bonne réponse).
- Pas de flou de mouvement, pas de rotation du texte, pas d'effet « machine à écrire ».
- Chaque texte reste lisible au moins 1 s après son entrée.
- Swipes 4 → 5 et 5 → 6 : la carte entière (fond, feuille, contenu) glisse verticalement, comme dans un fil. Le passage 1 → 2 n'est pas un swipe : c'est la même carte qui se réorganise.

**Sons (facultatif) :** petit « pop » pour les bulles et les options, « tic » à chaque chiffre du minuteur, « ding » à la frame 244, « whoosh » léger aux swipes (300 et 420).

## 12. Couverture et photo de profil

**Couverture** (1080 × 1920, image fixe, fond lavande). TikTok la recadre en 3:4 dans la grille du profil : tout l'important tient entre y = 80 et y = 560.

| Élément | x | y | Taille | Contenu |
| --- | --- | --- | --- | --- |
| Tag | centré | 92 | | « Le piège du jour · #1 » |
| Mots | centrés | 140 | | tuile « make », « ou », tuile « do ? » |
| Renard | 85 | 336 | largeur 190 | reflechit |
| Décor | | | | cercles (300, 150) r 80 à 20 % et (40, 420) r 56 à 16 % ; étincelles (306, 336) r 16 et (52, 175) r 11 |

**Photo de profil** (scène de 360 × 360, export 1080 × 1080, fond lavande). Cercle `sheet` (180, 200) r 132 à 22 % ; étincelles (296, 100) r 16 et (62, 123) r 11 ; renard en pose portrait en (30, 60), largeur 300. Le bas du renard touche le bord inférieur : la coupe disparaît dans le rond de TikTok.

## 13. Contrôle avant export

- [ ] Positions, tailles et couleurs conformes aux tableaux ci-dessus, scène par scène.
- [ ] Aucun texte ni réponse dans les zones sûres.
- [ ] Textes identiques à la section 9.
- [ ] Baloo 2 et Nunito réellement chargées (pas de police système de remplacement).
- [ ] La bonne réponse a toujours sa coche, pas seulement le vert.
- [ ] Le renard est celui du SVG, sans retouche.
- [ ] Vidéo en H.264, 1080 × 1920, 30 fps ; couverture et photo de profil exportées en PNG à part.
