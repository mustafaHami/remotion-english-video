import {color, ledge} from './tokens';
import {type} from './typography';

/** Versioned test extension: preserve v1 while exploring a more editorial layout. */
export const editorial = {
  title: {...type.hookTitle, fontSize: 34, lineHeight: 1.12, whiteSpace:'nowrap' as const},
  sentence: {...type.sentence, fontSize: 23, lineHeight: 1.2, whiteSpace:'nowrap' as const},
  body: {...type.lead, fontSize: 15, whiteSpace:'nowrap' as const},
  translation: {...type.translation, fontSize: 14, whiteSpace:'nowrap' as const},
  label: {...type.meta, fontSize: 11, letterSpacing: '.07em', whiteSpace:'nowrap' as const},
  panel: {background:color.sheet, border:`2px solid ${color.ink}`, borderRadius:28, boxShadow:ledge(6,color.ink)},
  safe: {top:64,bottom:508,right:300},
} as const;
