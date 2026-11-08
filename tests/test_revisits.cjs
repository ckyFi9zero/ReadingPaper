const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const vm=require('node:vm');const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../assets/revisits.js'),'utf8');
function setup(query=''){
 const el=(value='')=>({value,hidden:false,events:{},addEventListener(k,f){this.events[k]=f},focus(){this.focused=true}});
 const nodes={'#revisit-search':el(),'#revisit-status':el('all'),'#revisit-count':el(),'#revisit-empty':el(),'#revisit-reset':el()};
 const cards=[{revisitState:'reviewed',revisitSearch:'3d-unoutdet 教师 伪标签'},{revisitState:'not-yet',revisitSearch:'rpsnownet 雪'}].map(dataset=>({dataset,hidden:false}));
 nodes['#revisit-list']={querySelectorAll:()=>cards};const state={};
 vm.runInNewContext(source,{document:{querySelector:id=>nodes[id]},URLSearchParams,location:{search:query,pathname:'/ReadingPaper/revisits.html',hash:''},history:{replaceState(a,b,url){state.url=url}}});
 return {nodes,cards,state,shown:()=>cards.filter(c=>!c.hidden).length};
}
test('topic status and keyword intersect; reset restores all',()=>{const x=setup('?status=reviewed&q=教师');assert.equal(x.shown(),1);x.nodes['#revisit-status'].value='not-yet';x.nodes['#revisit-status'].events.change();assert.equal(x.shown(),0);assert.equal(x.nodes['#revisit-empty'].hidden,false);x.nodes['#revisit-reset'].events.click();assert.equal(x.shown(),2);assert.equal(x.state.url,'/ReadingPaper/revisits.html');});
test('invalid status falls back and URL reload preserves selection',()=>{const x=setup('?status=bad');assert.equal(x.shown(),2);x.nodes['#revisit-status'].value='not-yet';x.nodes['#revisit-status'].events.change();assert.equal(x.shown(),1);assert.equal(setup(new URL(x.state.url,'https://example.test').search).shown(),1);});
