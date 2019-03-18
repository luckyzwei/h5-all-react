const evJson = JSON.parse(process.env.npm_config_argv)
const param = evJson.original[evJson.original.length - 1].slice(2)
console.log(`env--${param}`);
var configJson = require('../configPath.json');

var realobj = configJson[param]
var fs = require('fs')
// 替换pathNam
// fs.readFile(`${process.cwd()}/src/constants/OriginName.js`,
//     'utf8', (err, data) => {
//         if (err) {
//             return console.log(err);
//         }
//
//         var regx = /ORIGIN_NAME = .*/;
//         var data = data.replace(regx,
//             `ORIGIN_NAME = '${realobj.serverPath.originName}'`)
//
//         fs.writeFile(`${process.cwd()}/src/constants/OriginName.js`, data, 'utf8', (err) => {
//
//             if (err) return console.log(err);
//
//         });
//
//         console.log('pathname -- changed');
//
//     })
// 替换image path
fs.readFile(`${process.cwd()}/src/assets/css/custom.scss`,
    'utf8', (err, data) => {
        if (err) {
            return console.log(err);
        }

        var regx = /\$img-path: .*/

        var data = data.replace(regx,
            `$img-path: '${realobj.serverPath.imgPath}';`)

        fs.writeFile(`${process.cwd()}/src/assets/css/custom.scss`, data, 'utf8', (err) => {

            if (err) return console.log(err);

        });

        console.log('imagepath -- changed');

    })
// 替换webpack打包path
fs.readFile(`${process.cwd()}/node_modules/react-scripts/config/paths.js`,
    'utf8', (err, data) => {
        if (err) {
            return console.log(err);
        }
        var regx = /envPublicUrl = .*/
        var data = data.replace(regx,
            `envPublicUrl = '${realobj.accessPath}'`)

        fs.writeFile(`${process.cwd()}/node_modules/react-scripts/config/paths.js`, data, 'utf8', (err) => {

            if (err) return console.log(err);

        });
        console.log('config-path -- changed');
    })
