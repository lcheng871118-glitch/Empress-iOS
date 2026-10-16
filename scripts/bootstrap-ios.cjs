'use strict';
const path=require('node:path');
const fs=require('node:fs');
const {startServer}=require('./server/index.cjs');
const rootDir=path.resolve(process.argv[2]||__dirname);
const saveDir=path.resolve(process.argv[3]||path.join(rootDir,'profile'));
fs.mkdirSync(saveDir,{recursive:true});
try{const iceFile=path.join(saveDir,'online-ice-servers.json');if(fs.existsSync(iceFile))process.env.EMPRESS_ICE_SERVERS=fs.readFileSync(iceFile,'utf8');}catch{}
console.log('[empress] bootstrap start, rootDir=' + rootDir + ' saveDir=' + saveDir);
startServer({port:3210,host:'127.0.0.1',rootDir,saveDir}).then(server=>{
  console.log('[empress] server ready on 127.0.0.1:3210');
  process.on('SIGTERM',()=>server.close().finally(()=>process.exit(0)));
}).catch(error=>{
  console.error('[empress] start failed: ' + (error && error.message ? error.message : String(error)));
  if (error && error.stack) console.error(error.stack);
  process.exitCode=1;
});
