import config from './render-config.json';

export const options = config;
export const optionData = {
  pronouns: [
    {subject:'I',verb:'am'}, {subject:'You',verb:'are'}, {subject:'He',verb:'is'},
    {subject:'She',verb:'is'}, {subject:'It',verb:'is'}, {subject:'We',verb:'are'}, {subject:'They',verb:'are'},
  ],
  opposites: [
    ['big','small'],['hot','cold'],['fast','slow'],['open','closed'],['happy','sad'],
    ['near','far'],['light','dark'],['full','empty'],['early','late'],['strong','weak'],
  ],
  gap:{before:'Can you',answer:'do',after:'me a favor?',choices:['make','do'],translation:'Tu peux me rendre un service ?'},
  restaurant:{choices:['The bill, please.','The addition, please.'],translation:'L’addition, s’il vous plaît.'},
  contrast:{first:'She said hello.',second:'She told me a story.',firstFr:'Elle a dit bonjour.',secondFr:'Elle m’a raconté une histoire.'},
  collocations:[{verb:'do',rest:'a favor',translation:'rendre un service'},{verb:'make',rest:'a cake',translation:'faire un gâteau'}],
  correction:{before:'I am agree.',after:'I agree.',translation:'Je suis d’accord.'},
  dialogue:[{en:'Can you do me a favor?',fr:'Tu peux me rendre un service ?'},{en:'Sure. What do you need?',fr:'Bien sûr. De quoi as-tu besoin ?'}],
  listen:{phrase:'The bill, please.',translation:'L’addition, s’il vous plaît.',audio:'audio/options/the-bill-please.mp3',starts:[90,420]},
  recall:{prompt:'Tu pourrais m’aider ?',answer:'Could you help me?'},
  transfer:{first:'do a favor',prompt:'I ___ my homework.',answer:'I do my homework.',translation:'Je fais mes devoirs.'},
  phrasal:{base:'get',particle:'off',phrase:'get off the bus',translation:'descendre du bus'},
} as const;
