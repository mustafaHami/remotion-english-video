import React from 'react';
import {Img,staticFile,useCurrentFrame,interpolate,Easing} from 'remotion';
import {tween} from '../design/motion';
const src=staticFile('mascots/fox-front/poses.png');
/** Front-facing cutout, preserving the original palette and scarf. */
export const FrontalFoxMascot=({end=false,refinedMotion=false}:{end?:boolean;refinedMotion?:boolean})=>{
 const f=useCurrentFrame(),cheer=end&&f<90;
 const gestureFrame=end?f-90:f;
 const wave=refinedMotion?6*Math.sin(2*Math.PI*(gestureFrame-4)/30)*tween(gestureFrame,0,6)*(1-tween(gestureFrame,48,12)):7*Math.sin(2*Math.PI*f/30);
 const approval=interpolate(f,[0,8,23,35,46,66,89],[0,5,-18,-13,-18,0,0],{easing:Easing.bezier(.4,0,.2,1),extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 const thumbArm='M1300 260 L1340 290 L1378 320 L1370 275 L1370 245 L1388 216 L1408 214 L1420 245 L1437 263 L1444 315 L1445 370 L1430 409 L1402 425 L1375 430 L1295 355 Z';
 const arm='M750 350 L755 300 L747 230 L745 200 L780 172 L830 174 L855 200 L849 250 L820 280 L810 350 L795 380 L773 378 Z';
 const view=cheer?'900 0 660 887':'280 0 660 887';
 return <div style={{width:166,height:190,transform:refinedMotion?'none':`translateY(${-2+2*Math.cos(2*Math.PI*f/90)}px)`}}>
  <Img src={src} style={{position:'absolute',width:1,height:1,opacity:0}}/>
  <svg width="166" height="190" viewBox={view} role="img" aria-label={cheer?'Le renard de face te felicite':'Le renard de face fait coucou'} style={{overflow:'hidden'}}>
   <defs><mask id="frontal-fox-body" maskUnits="userSpaceOnUse" x="0" y="0" width="1774" height="887"><rect width="1774" height="887" fill="white"/><path d={arm} fill="black"/><ellipse cx="785" cy="369" rx="31" ry="26" fill="white"/></mask><clipPath id="frontal-fox-arm"><path d={arm}/></clipPath><mask id="frontal-thumb-body" maskUnits="userSpaceOnUse" x="0" y="0" width="1774" height="887"><rect width="1774" height="887" fill="white"/><path d={thumbArm} fill="black"/><rect x="0" y="0" width="1324" height="887" fill="white"/><ellipse cx="1305" cy="310" rx="22" ry="31" fill="white"/></mask><clipPath id="frontal-thumb-arm"><path d={thumbArm}/></clipPath><clipPath id="frontal-fox-cell"><rect x={cheer?887:0} y="0" width="887" height="887"/></clipPath></defs>
   <g clipPath="url(#frontal-fox-cell)">{cheer?(refinedMotion?<><image href={src} width="1774" height="887" mask="url(#frontal-thumb-body)"/><g transform={`rotate(${approval} 1305 310)`}><image href={src} width="1774" height="887" clipPath="url(#frontal-thumb-arm)"/></g></>:<image href={src} width="1774" height="887"/>):<><image href={src} width="1774" height="887" mask="url(#frontal-fox-body)"/><g transform={`rotate(${wave} 785 350)`}><image href={src} width="1774" height="887" clipPath="url(#frontal-fox-arm)"/></g></>}</g>
  </svg>
 </div>;
};
