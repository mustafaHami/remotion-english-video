import type {CSSProperties} from 'react';
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';
import {color} from './tokens';

export const fonts = {display: 'Prototype Baloo 2', body: 'Prototype Nunito'} as const;
let loading: Promise<void> | undefined;
export const designFontsReady = () => loading ?? Promise.resolve();
export const loadDesignFonts = () => {
  if (typeof document === 'undefined' || loading) return;
  const handle = delayRender('Chargement Baloo 2 / Nunito (polices locales)');
  loading = Promise.all([
    [fonts.display, 'fonts/Baloo2-Variable.ttf', '400 800'],
    [fonts.body, 'fonts/Nunito-Variable.ttf', '200 1000'],
  ].map(async ([family, file, weight]) => {
    const face = new FontFace(family, `url("${staticFile(file)}")`, {weight, style: 'normal'});
    document.fonts.add(await face.load());
  })).then(async () => {
    await document.fonts.ready;
    continueRender(handle);
  }).catch((error: unknown) => cancelRender(error));
};
const display = (size: number, lineHeight: number, letterSpacing = '0em'): CSSProperties => ({
  fontFamily: `"${fonts.display}"`, fontWeight: 800, fontSize: size, lineHeight, letterSpacing, color: color.ink,
});
const body = (size: number, lineHeight: number, tint: string = color.ink): CSSProperties => ({
  fontFamily: `"${fonts.body}"`, fontWeight: 800, fontSize: size, lineHeight, color: tint,
});
export const type = {
  hookTitle: display(40, 1.04, '-.02em'), endTitle: display(42, 1.02, '-.02em'),
  sentence: display(36, 1.2, '-.01em'), tipHeading: display(40, 1),
  coverWord: display(54, 1), coverJoin: display(28, 1), teaser: display(28, 1.05),
  timerDigit: display(30, 1), feedback: {...display(19, 1.1), color: color.success},
  translation: body(17, 1.35, color.violet), lead: body(17, 1.35, color.ink2),
  leadEnd: body(16, 1.35), option: body(19, 1), hint: body(15, 1.3, color.ink2),
  pill: body(15, 1), tipSub: body(14, 1.3, color.violet),
  tag: body(13, 1.2, color.onInk), meta: body(13, 1.2, color.inkMuted),
} satisfies Record<string, CSSProperties>;
