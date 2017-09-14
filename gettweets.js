const Twitter = require('twitter');

var client = new Twitter({
  consumer_key: 'iwmZ6FZn1cQR0YgXr4GbQIct2',
  consumer_secret: 'uNKmyGBNIaOFBqqdWsfpfRzIWMMuO093HefXRGtilhSxAir81f',
  access_token_key: '204320576-lAqtb8WTEC3cTflF8V1MMBfqEy5ztGv8YiVbsUWU',
  access_token_secret: 'dIzZXfDhqvkJ8ulqwGymTvO5R7nhIVHWVj9vrVItxz39d'
});

client.get('https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=rameshsrivats&count=100', function (err, data, res) {
	if (err) {
		console.log(err);
		process.exit(1);
	} else if (data) {
		data = JSON.stringify(data);
		console.log(JSON.parse(data));
	} else {
		console.log(res);
	}
});
