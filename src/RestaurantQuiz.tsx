import React from 'react';
import {AbsoluteFill, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
const C={cream:'#FAF7F0',ink:'#26313B',muted:'#68736C',sage:'#B8C6AE',sageDark:'#546B54',rust:'#CC5835',line:'#E1DED4'};
const clamp={extrapolateLeft:'clamp' as const,extrapolateRight:'clamp' as const};
const lerp=(f:number,a:number,b:number,x:number,y:number)=>interpolate(f,[a,b],[x,y],clamp);
const enter=(frame:number,fps:number)=>spring({frame,fps,config:{damping:22,stiffness:110,mass:0.85}});
const atlasWidths=[512,512,512];
const Fox:React.FC=()=>{
 const f=useCurrentFrame();
 let x=750,y=1250,pose=0,opacity=1,flip=true;
 if(f<35){x=lerp(f,0,35,1130,750);y=1250;}
 else if(f<282){x=750;y=1250;pose=f<120?1:0;}
 else if(f<318){x=lerp(f,282,318,750,-240);y=1250;pose=1;}
 else if(f<329){opacity=0;}
 else if(f<474){x=730;y=lerp(f,329,354,-380,175);pose=1;flip=true;}
 else if(f<500){x=lerp(f,474,500,730,1130);y=175;pose=1;}
 else if(f<540){x=lerp(f,500,540,1130,740);y=1250;pose=1;}
 else{ x=740; y=1250;pose=2; }
 const bob=Math.sin(f/16)*3;
 const viewportWidth=pose===1?200:172;
 const clip=pose===1?"polygon(0 0,100% 0,100% 58%,84% 58%,84% 100%,0 100%)":pose===2?"polygon(18% 0,100% 0,100% 100%,0 100%,0 60%,18% 60%)":undefined;
 // The reusable raster atlas preserves the approved design while the rig is still pending.
 return <div style={{position:'absolute',left:x,top:y+bob,width:viewportWidth,height:344,clipPath:clip,overflow:'hidden',opacity,transform:`scaleX(${flip?-1:1}) rotate(${Math.sin(f/24)*0.8}deg)`,transformOrigin:'50% 90%'}}>
 <Img src={staticFile('fox-atlas.png')} style={{position:'absolute',maxWidth:'none',width:516,height:344,left:-pose*(atlasWidths[pose]/512)*172,top:0}}/>
 </div>;
};
const Text:React.FC<{children:React.ReactNode;size?:number;color?:string;weight?:number;style?:React.CSSProperties}> = ({children,size=76,color=C.ink,weight=650,style={}})=><div style={{fontSize:size,color,fontWeight:weight,lineHeight:1.12,letterSpacing:-1.5,...style}}>{children}</div>;
const Intro:React.FC=()=>{
 const f=useCurrentFrame(),{fps}=useVideoConfig();const s=enter(f,fps);
 return <div style={{position:'absolute',left:110,top:520,width:790,opacity:lerp(f,0,15,0,1),transform:`translateY(${(1-s)*35}px)`}}>
 <div style={{width:72,height:5,background:C.rust,marginBottom:42,borderRadius:4}}/>
 <Text size={104}>Time to pay.</Text>
 <Text size={41} weight={400} color={C.muted} style={{marginTop:35,letterSpacing:0}}>Au restaurant, demande l’addition.</Text>
 </div>;
};
const Quiz:React.FC=()=>{
 const f=useCurrentFrame(),{fps}=useVideoConfig();const s=enter(f,fps);
 return <div style={{position:'absolute',left:110,top:470,width:790,opacity:lerp(f,0,12,0,1),transform:`translateY(${(1-s)*25}px)`}}>
 <Text size={86}>What would<br/>you say?</Text>
 <Text size={38} weight={400} color={C.muted} style={{marginTop:25,marginBottom:65,letterSpacing:0}}>Choisis la phrase naturelle.</Text>
 {['The bill, please.','The addition, please.'].map((answer,i)=>{
  const a=enter(f-i*9-9,fps);
  return <div key={answer} style={{display:'flex',alignItems:'center',gap:30,height:136,border:`2px solid ${C.line}`,borderRadius:18,padding:'0 30px',marginBottom:24,opacity:lerp(f,i*9+9,i*9+20,0,1),transform:`translateX(${(1-a)*28}px)`,background:'#FFFDF8'}}>
   <span style={{fontSize:37,fontWeight:650,color:C.sageDark,width:42}}>{i===0?'A':'B'}</span><span style={{fontSize:49,fontWeight:550,letterSpacing:-0.7}}>{answer}</span>
  </div>;
 })}
 {f>85&&f<175?<div style={{position:'absolute',top:670,left:0,width:360,height:5,background:C.line,borderRadius:4,overflow:'hidden'}}><div style={{width:`${lerp(f,85,175,100,0)}%`,height:'100%',background:C.sageDark}}/></div>:null}
 {f>85&&f<175?<div style={{position:'absolute',left:630+Math.sin(f/24)*20,top:330+Math.sin(f/20)*32,opacity:0.7,transform:`rotate(${Math.sin(f/18)*12}deg)`}}>
  <svg width="75" height="75" viewBox="0 0 75 75"><circle cx="29" cy="29" r="19" stroke="#A99CB7" strokeWidth="5" fill="none"/><path d="M44 44L62 64" stroke="#A99CB7" strokeWidth="6" strokeLinecap="round"/></svg>
 </div>:null}
 </div>;
};
const Answer:React.FC=()=>{
 const f=useCurrentFrame(),{fps}=useVideoConfig();const s=enter(f,fps);
 return <div style={{position:'absolute',left:110,top:550,width:790,opacity:lerp(f,0,12,0,1),transform:`translateY(${(1-s)*28}px)`}}>
 <Text size={62} weight={500} color={C.muted}>The natural phrase</Text>
 <div style={{marginTop:48,padding:'58px 35px',background:'#EAF0E4',borderRadius:20}}>
  <Text size={77}>The <span style={{position:'relative'}}>bill<span style={{position:'absolute',left:0,bottom:-9,width:`${lerp(f,30,52,0,100)}%`,height:6,background:C.rust,borderRadius:5}}/></span>, please.</Text>
 </div>
 <Text size={39} weight={400} color={C.muted} style={{marginTop:38,letterSpacing:0}}>L’addition, s’il vous plaît.</Text>
 {f>65?<Text size={34} weight={450} color={C.sageDark} style={{marginTop:45,letterSpacing:0,opacity:lerp(f,65,78,0,1)}}>“Bill” = l’addition au restaurant.</Text>:null}
 </div>;
};
const Practice:React.FC=()=>{
 const f=useCurrentFrame();
 const listening=f<185;const speaking=f>=185&&f<325;
 return <div style={{position:'absolute',left:110,top:480,width:790,opacity:lerp(f,0,12,0,1)}}>
 <Text size={66} color={C.muted} weight={500}>{listening?'Listen. Then repeat.':'Your turn.'}</Text>
 <Text size={86} style={{marginTop:68}}>The bill, please.</Text>
 <Text size={38} weight={400} color={C.muted} style={{marginTop:35,letterSpacing:0}}>L’addition, s’il vous plaît.</Text>
 {listening?<div style={{display:'flex',gap:10,alignItems:'center',height:90,marginTop:80}}>
  {Array.from({length:19},(_,i)=><div key={i} style={{width:8,borderRadius:5,background:C.sageDark,height:(f>=96&&f<180?22+Math.abs(Math.sin(f/4+i*1.7))*42:10+Math.abs(Math.sin(i))*13),opacity:0.72}}/>)}
 </div>:<div style={{marginTop:85,fontSize:32,color:C.sageDark,letterSpacing:0,opacity:lerp(f,185,200,0,1)}}>À toi de répéter à voix haute.</div>}
 {speaking?<div style={{width:360,height:5,background:C.line,borderRadius:4,marginTop:24,overflow:'hidden'}}><div style={{height:'100%',background:C.sageDark,width:`${lerp(f,232,325,100,0)}%`}}/></div>:null}
 </div>;
};
const End:React.FC=()=>{
 const f=useCurrentFrame();
 return <div style={{position:'absolute',left:110,top:570,width:790,opacity:lerp(f,0,15,0,1)}}>
 <Text size={90}>Try it next time.</Text>
 <Text size={40} weight={400} color={C.muted} style={{marginTop:38,letterSpacing:0}}>Une phrase utile, une situation réelle.</Text>
 </div>;
};
const voiceTracks=[
 {frame:12,file:'intro.wav'},
 {frame:129,file:'question.wav'},
 {frame:311,file:'answer.wav'},
 {frame:386,file:'explain.wav'},
 {frame:492,file:'listen.wav'},
 {frame:576,file:'repeat.wav'},
 {frame:666,file:'your-turn.wav'},
 {frame:825,file:'outro.wav'},
];
export const RestaurantQuiz:React.FC=()=>{
 const f=useCurrentFrame();
 const label=f<480?'AT THE RESTAURANT':'SPEAKING PRACTICE';
 return <AbsoluteFill style={{backgroundColor:C.cream,fontFamily:'"Segoe UI",Arial,sans-serif',color:C.ink}}>
 <div style={{position:'absolute',left:110,top:165,fontSize:29,fontWeight:600,letterSpacing:3.8,color:C.sageDark}}>{label}</div>
 <Sequence from={0} durationInFrames={120}><Intro/></Sequence>
 <Sequence from={120} durationInFrames={180}><Quiz/></Sequence>
 <Sequence from={300} durationInFrames={180}><Answer/></Sequence>
 <Sequence from={480} durationInFrames={330}><Practice/></Sequence>
 <Sequence from={810} durationInFrames={90}><End/></Sequence>
 <Fox/>
 <div style={{position:'absolute',left:110,top:1715,width:650,height:3,background:C.line}}><div style={{height:3,width:`${f/899*100}%`,background:C.sageDark}}/></div>
 {voiceTracks.map(track=><Sequence key={track.file} from={track.frame}><Audio src={staticFile('audio/'+track.file)} volume={0.95}/></Sequence>)}
 </AbsoluteFill>;
};
