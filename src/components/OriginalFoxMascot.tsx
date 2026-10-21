import React from 'react';
import {Img,staticFile,useCurrentFrame} from 'remotion';
const src=staticFile('mascots/original-fox-v8/poses.png');
/** Two-dimensional cutout: original identity, frame-driven forearm wave and bounce. */
export const OriginalFoxMascot=({end=false}:{end?:boolean})=>{
 const f=useCurrentFrame(),cheer=end&&f<90;
 const wave=7*Math.sin(2*Math.PI*f/30);
 const arm='M691 330 L702 274 L690 220 L720 171 L780 170 L806 197 L800 250 L760 300 L749 350 L736 380 L707 372 Z';
 const view=cheer?'910 0 700 887':'130 0 700 887';
 return <div style={{width:166,height:190,transform:`translateY(${-2+2*Math.cos(2*Math.PI*f/90)}px)`}}>
  <Img src={src} style={{position:'absolute',width:1,height:1,opacity:0}}/>
  <svg width="166" height="190" viewBox={view} role="img" aria-label={cheer?'Le renard te félicite':'Le renard fait coucou'} style={{overflow:'hidden'}}>
   <defs><mask id="original-fox-body" maskUnits="userSpaceOnUse" x="0" y="0" width="1774" height="887"><rect width="1774" height="887" fill="white"/><path d={arm} fill="black"/></mask><clipPath id="original-fox-arm"><path d={arm}/></clipPath></defs>
   {cheer?<image href={src} width="1774" height="887"/>:<><image href={src} width="1774" height="887" mask="url(#original-fox-body)"/><g transform={`rotate(${wave} 723 350)`}><image href={src} width="1774" height="887" clipPath="url(#original-fox-arm)"/></g></>}
  </svg>
 </div>;
};
