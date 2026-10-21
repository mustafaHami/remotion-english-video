export type Platform = 'tiktok' | 'instagram';
export type DeclicData = {
  choices:readonly string[]; answer:string;
  challenge:{before:string;after:string;translation:string};
  recall:{before:string;after:string;translation:string};
  timing:{countdown:number;answer:number;contrast:number;recall:number;recallAnswer:number;end:number;duration:number};
};
export const declicData:DeclicData={
  choices:['make','do','give'],answer:'do',
  challenge:{before:'Can you',after:'me a favor?',translation:'Tu peux me rendre un service ?'},
  recall:{before:'I',after:'my homework.',translation:'Je fais mes devoirs.'},
  timing:{countdown:90,answer:180,contrast:300,recall:450,recallAnswer:555,end:600,duration:660},
};
export const platformCopy = {
  tiktok:{hook:'Tu dirais quoi ?',lead:'Pour demander un service.',end:'Retiens : do a favor.',cta:'Puis essaie de le réutiliser.'},
  instagram:{hook:'Le bon réflexe.',lead:'Un service à demander.',end:'Garde ce mémo.',cta:'do a favor · make a cake'},
} satisfies Record<Platform,{hook:string;lead:string;end:string;cta:string}>;
