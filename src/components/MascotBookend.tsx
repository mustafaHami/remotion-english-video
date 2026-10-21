import React from 'react';
import {useCurrentFrame} from 'remotion';
import {OptionScene,Text,Tile} from './OptionPrimitives';
import {FrontalFoxMascot} from './FrontalFoxMascot';
import {progress} from '../design/motion';
import {color} from '../design/tokens';
export const Bookend=({title,end=false,farewellAt=110,mascot,staticMascot=true}:{title:string;end?:boolean;farewellAt?:number;mascot?:React.ReactNode;staticMascot?:boolean})=>{
  const f=useCurrentFrame();const farewell=end&&f>=farewellAt;
  const lift=!staticMascot&&end&&f<80?-8*Math.sin(Math.PI*progress(f,16,40)):0;
  return <OptionScene title={end?'Bien joué !':title} guide={end?'Un pas de plus dans ton anglais.':'Écoute, cherche, puis découvre la réponse.'} completeAt={end?(staticMascot?-18:0):9999} success={end} quietDecor animateEntrance={!staticMascot}>
    <Tile x={88} y={20} w={160} h={36} fill={end?color.successBg:color.lemon} correct={end} name="mascot-heading" size={22}>{end?'Bravo !':'Tu es prêt ?'}</Tile>
    <div data-center="mascot" style={{position:'absolute',left:85,top:75,width:166,height:190,transform:`translateY(${lift}px)`}}>{mascot??<FrontalFoxMascot end={end} refinedMotion/>}</div>
    <Text y={272} h={28} size={end?18:16} name="mascot-message" tint={end?color.success:color.ink}>{end?'Tu as terminé cet exercice !':title}</Text>
    <Text y={307} h={24} size={14} start={end?farewellAt:15} name="mascot-footer" tint={color.violet}>{end?'À bientôt !':'À toi de jouer.'}</Text>
  </OptionScene>;
};
