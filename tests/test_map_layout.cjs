const assert = require('node:assert/strict');
const {layoutForest} = require('../assets/map-layout.js');
function check(entries, roots) {
  const layout = layoutForest(entries, roots);
  assert.equal(Object.keys(layout.positions).length, entries.length);
  assert.deepEqual(layout, layoutForest(entries, roots));
  const positions = Object.values(layout.positions);
  for (let i=0; i<positions.length; i++) {
    const a=positions[i];
    assert(a.x>=0 && a.y>=0 && a.x+a.width<=layout.width && a.y+a.height<=layout.height);
    for (const b of positions.slice(i+1)) {
      assert(a.x+a.width<=b.x || b.x+b.width<=a.x || a.y+a.height<=b.y || b.y+b.height<=a.y, 'nodes must not overlap');
    }
  }
  for (const entry of entries) {
    const parent=layout.positions[entry.id];
    for (const child of entry.children) assert(layout.positions[child].x>parent.x+parent.width, 'every edge extends right');
  }
  return layout;
}
const entries = [{id:'root',width:220,height:58,children:['route','other']},
  {id:'route',width:220,height:80,children:['module']},
  {id:'module',width:220,height:58,children:['follow-up']},
  {id:'follow-up',width:220,height:110,children:[]},
  {id:'other',width:220,height:58,children:[]},
  {id:'second-root',width:220,height:100,children:[]}];
const layout=check(entries,['root','second-root']);
assert.equal(layout.positions['follow-up'].depth,3);
check([],[]);
// Deep and broad trees with varying multiline node heights.
for (let count of [2,19,27,100]) {
  const nodes=Array.from({length:count},(_,i)=>({id:String(i),width:220,height:50+(i*37)%90,children:[]}));
  for(let i=1;i<count;i++)nodes[Math.floor((i-1)/3)].children.push(String(i));
  check(nodes,['0']);
}
console.log('PASS: deterministic left-to-right layout, all nodes retained, no overlaps, multiline/deep/broad/empty forests');
