const {read,validate}=require('./lib/lesson.cjs');
for(let n=1;n<=14;n++){const l=validate(read(`src/options/option-${n}/content.json`));console.log(`Option ${n}: content, narration and assets valid`)}

for(const verb of ['have','can','could'])validate(read(`src/options/option-2/variants/${verb}.json`));

validate(read('content/examples/option-4-new-content.json'));
