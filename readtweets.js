const fs   = require('fs');
const path = require('path');
const hanson = require('hanson');

function readDir (cb) {
	fs.readdir(path.resolve(process.cwd(), 'users'), (err, files) => {
		if (err) {
			console.error(err);
			cb(err, null);
		} else if (files && files.length) {
			cb(null, files);
		} else {
			console.info("No output files in the folder");
			cb(null, null);
		}
	})
}

function getFiles (cb) {
	readDir((err, files) => {
		if (err) {
			process.exit(1);
		} else if (files && files.length) {
			cb(null, files);
		} else {
			process.exit(0);
		}
	})
}

function readTweets() {
	getFiles((err, files) => {
		if (err) {
			process.exit(1);
		} else if (files && files.length) {
			files.forEach(function(f) {
				fs.readFile(path.resolve(process.cwd(), 'users' + '/' + f), (err, data) => {
				// fs.readFile('output.json', (err, data) => {
					if (err) {
						process.exit(1);
					} else if (data) {
						data = {"tweets": JSON.parse(data)};
						// data.forEach(function(entry) {
						// 	console.log(entry.text);
						// })
						// console.log(data.length);
						fs.writeFile(f, JSON.stringify(data), (err) => {
							if (err) throw err;
							console.log('It\'s saved!');
						});
					} else {
						process.exit(0);
					}
				})
			})
		} else {
			console.log("No users exist");
			process.exit(0);
		}
	})
}

readTweets();
