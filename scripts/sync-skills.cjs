const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),source=path.join(root,'.agents/skills'),target=path.join(root,'.claude/skills');
let changed=false;
for(const name of fs.readdirSync(source)){
 const from=path.join(source,name,'SKILL.md'),to=path.join(target,name,'SKILL.md');if(!fs.existsSync(from))continue;
 const text=fs.readFileSync(from,'utf8');
 if(process.argv.includes('--check')){if(!fs.existsSync(to)||fs.readFileSync(to,'utf8')!==text){console.error('Unsynchronized Claude skill:',name);changed=true;}}
 else{fs.mkdirSync(path.dirname(to),{recursive:true});fs.writeFileSync(to,text);}
}
if(changed)process.exitCode=1;
