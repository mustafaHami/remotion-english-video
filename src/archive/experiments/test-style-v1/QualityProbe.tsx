import {useLayoutEffect} from 'react';
import {getRemotionEnvironment, useCurrentFrame} from 'remotion';
import {designFontsReady,fonts} from '../../../design/typography';

/** Render-only measurements; no effect on the animation or timing. */
export const QualityProbe = ({swipeStarts=[300,420],top=40,bottom=520,right=300}:{swipeStarts?:readonly number[];top?:number;bottom?:number;right?:number}) => {
  const frame = useCurrentFrame();
  useLayoutEffect(() => {
    if (!getRemotionEnvironment().isRendering) return;
    let disposed=false;
    void designFontsReady().then(()=>{
    if(disposed) return;
    if (document.fonts.status !== 'loaded' || document.fonts.size < 2) return;
    const duringSwipe = swipeStarts.some(start=>frame>=start&&frame<start+14);
    const violations: string[] = [];
    for (const el of document.querySelectorAll<HTMLElement>('[data-safe]')) {
      let opacity = 1;
      for (let node: HTMLElement | null = el; node; node = node.parentElement) opacity *= Number(getComputedStyle(node).opacity);
      if (opacity < .05) continue;
      const rect = el.getBoundingClientRect();
      const box = {x: rect.left/3, y: rect.top/3, right: rect.right/3, bottom: rect.bottom/3};
      if (!duringSwipe && (box.x < -.1 || box.right>360.1 || box.y < top-.1 || box.bottom > bottom+.1 || (box.bottom>290 && box.right>right+.1))) violations.push(`${el.dataset.safe}: ${JSON.stringify(box)}`);
      // The timer's inset digit wrapper scales; its glyph stays inside the ring.
      if (el.dataset.safe !== 'timer' && el.scrollWidth > el.clientWidth+1) violations.push(`overflow: ${el.dataset.safe}`);
    }
    // Compare layout blocks. Font em-boxes extend beyond Baloo's visible glyphs
    // and would incorrectly flag the charter's tight line heights as collisions.
    if (!duringSwipe) {
      const textBoxes: {owner: Element; name: string; rect: DOMRect}[] = [];
      for (const owner of document.querySelectorAll('[data-safe]')) {
        let opacity = 1;
        for (let node: Element | null = owner; node; node = node.parentElement) opacity *= Number(getComputedStyle(node).opacity);
        if (opacity < .8) continue;
        textBoxes.push({owner,name:owner.getAttribute('data-safe')!,rect:owner.getBoundingClientRect()});
      }
      for (let i=0;i<textBoxes.length;i++) for(let j=i+1;j<textBoxes.length;j++) {
        const a=textBoxes[i], b=textBoxes[j];
        if(a.owner===b.owner) continue;
        if(Math.min(a.rect.right,b.rect.right)-Math.max(a.rect.left,b.rect.left)>2 && Math.min(a.rect.bottom,b.rect.bottom)-Math.max(a.rect.top,b.rect.top)>2) violations.push(`text collision: ${a.name} / ${b.name}`);
      }
    }
    for(const connector of document.querySelectorAll<SVGElement>('[data-pair-connector]')){
      if(Number(getComputedStyle(connector).opacity)<.05)continue;
      const row=connector.dataset.pairConnector;
      const label=document.querySelector(`[data-safe="opposite-a-${row}"]`);
      if(!label)continue;
      const a=connector.getBoundingClientRect(),b=label.getBoundingClientRect();
      const delta=Math.abs(a.top+a.height/2-b.top-b.height/2)/3;
      if(delta>.1)violations.push(`connector row alignment: ${row} (${delta.toFixed(3)}u)`);
    }
    const loaded = [...document.fonts].filter(face=>face.status==='loaded').map(face=>face.family);
    let centerError=0;
    for(const el of document.querySelectorAll('[data-center]')){
      const rect=el.getBoundingClientRect();const error=Math.abs((rect.left+rect.width/2)/3-180);
      centerError=Math.max(centerError,error);
      if(error>.1) violations.push(`centering: ${el.getAttribute('data-center')} (${error.toFixed(3)}u)`);
    }
    for(const el of document.querySelectorAll('[data-center-column]')){
      const rect=el.getBoundingClientRect();const expected=76+104*Number(el.getAttribute('data-center-column'));
      const error=Math.abs((rect.left+rect.width/2)/3-expected);centerError=Math.max(centerError,error);
      if(error>.1) violations.push(`header centering: ${el.getAttribute('data-center-column')}`);
    }
    for(const wrapper of document.querySelectorAll('[data-ink-column]')){
      const image=wrapper.querySelector<HTMLElement>('[data-static-ink-center]');
      if(image){
        const rect=image.getBoundingClientRect();
        const center=rect.left/3+Number(image.dataset.staticInkCenter);
        const expected=76+104*Number(wrapper.getAttribute('data-ink-column'));
        const error=Math.abs(center-expected);centerError=Math.max(centerError,error);
        if(error>.1)violations.push(`static ink centering: ${wrapper.getAttribute('data-ink-column')}`);
        continue;
      }
      const path=wrapper.querySelector<SVGGraphicsElement>('[data-writing-ink]');if(!path)continue;
      const box=path.getBBox(),matrix=path.getScreenCTM();if(!matrix)continue;
      const center=new DOMPoint(box.x+box.width/2,box.y+box.height/2).matrixTransform(matrix);
      const expected=76+104*Number(wrapper.getAttribute('data-ink-column'));
      const error=Math.abs(center.x/3-expected);centerError=Math.max(centerError,error);
      if(error>.1)violations.push(`ink centering: ${wrapper.getAttribute('data-ink-column')} (${error.toFixed(3)}u)`);
    }
    console.log('STYLE_QA '+JSON.stringify({frame,duringSwipe,violations,loaded,
      fonts: [fonts.display,fonts.body].map(family=>document.fonts.check(`800 36px "${family}"`, 'Écris piège français')),
      masks:document.querySelectorAll('[data-safe-mask]').length,
      centerError,
    }));
    });
    return ()=>{disposed=true;};
  }, [frame,swipeStarts,top,bottom,right]);
  return null;
};
