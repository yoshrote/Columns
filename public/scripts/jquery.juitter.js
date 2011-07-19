(function($) {
	var conf = {},
		numMSG = 20; // set the number of messages to be show
		containerDiv="juitterContainer", // //Set a place holder DIV which will receive the list of tweets example <div id="juitterContainer"></div>
		loadMSG="Loading messages...", // Loading message, if you want to show an image, fill it with "image/gif" and go to the next variable to set which image you want to use on
		imgName="loader.gif", // Loading image, to enable it, go to the loadMSG var above and change it to "image/gif"
		readMore="Read it on Twitter", // read more message to be show after the tweet content
		nameUser="image" // insert "image" to show avatar of "text" to show the name of the user that sent the tweet
		live:"live-20", //optional, disabled by default, the number after "live-" indicates the time in seconds to wait before request the Twitter API for updates, I do not recommend to use less than 60 seconds.
		// end of configuration

		// some global vars
		aURL="";msgNb=1;
		var username, listname, time, lang, contDiv, loadMSG, numMSG, readMore, ultID, filterWords;
		var running=false;
		// Twitter API Urls
	function setTweetDate(dt){
		var twdate = new Date(dt);
		var now = new Date();
		var yr = now.getYear() - twdate.getYear();
		var mo = now.getMonth() - twdate.getMonth();
		var day = now.getDate() - twdate.getDate();
		var hr = now.getHours() - twdate.getHours();
		var min = now.getMinutes() - twdate.getMinutes();
		var sec = now.getSeconds() - twdate.getSeconds();
		var dtstring = '';
		if(yr > 0){
			dtstring += yr.toString() + ' year';
			if(yr > 1)
				dtstring += 's';
		}
		else if(mo > 0){
			dtstring += mo.toString() + ' month';
			if(mo > 1)
				dtstring += 's';
		}
		else if(day > 0){
			dtstring += day.toString() + ' day';
			if(day > 1)
				dtstring += 's';
		}
		else if(hr > 0){
			dtstring += hr.toString() + ' hour';
			if(hr > 1)
				dtstring += 's';
		}
		else if(min > 0){
			dtstring += min.toString() + ' minute';
			if(min > 1)
				dtstring += 's';
		}
		else{
			dtstring += sec.toString() + ' second';
			if(sec > 1)
				dtstring += 's';
		}
		return dtstring;
	}
	$.Juitter = {
		registerVar: function(opt){
			username = opt.username;
			listname = opt.listname;
			timer=opt.live;
			lang=opt.lang?opt.lang:"";
			contDiv=opt.placeHolder?opt.placeHolder:containerDiv;
			loadMSG=opt.loadMSG?opt.loadMSG:loadMSG;
			numMSG=opt.total?opt.total:numMSG;
			readMore=opt.readMore?opt.readMore:readMore;
			filterWords=opt.filter;
			openLink=opt.openExternalLinks?"target='_blank'":"";
		},
		start: function(opt) {
			ultID=0;
			if($("#"+contDiv)){
				this.registerVar(opt);
				// show the load message
				this.loading();
				// create the URL  to be request at the Twitter API
				aURL = 'http://api.twitter.com/1/'+username+'/lists/'+listname+'/statuses.json?per_page='+numMSG;
				// query the twitter API and create the tweets list
				this.conectaTwitter(1);
				// if live mode is enabled, schedule the next twitter API query
				if(timer!=undefined&&!running) this.temporizador();
			}
		},
		update: function(){
			this.conectaTwitter(2);
			if(timer!=undefined) this.temporizador();
		},
		loading: function(){
			$("#juitterContainer").html(loadMSG);
		},
		conectaTwitter: function(e){
			// query the twitter api and create the tweets list
			$.ajax({
				url: aURL,
				type: 'GET',
				dataType: 'jsonp',
				timeout: 1000,
				error: function(){ $("#juitterContainer").html("fail#"); },
				success: function(json){
					$("#juitterContainer").html("");
					container = $("<ul>");
					$.each(json, function(i,item){
						var tweetstr = $("<li></li>")
							.append(
								'<a class="tw_name" href="http://twitter.com/'
								+ item.user.screen_name + '">' + item.user.screen_name + '</a>'
							).append(
								'<p class="tw_text">' + item.text + '</p>'
							).append(
								'<a class="tw_date" href="http://twitter.com/'
								+ item.user.screen_name + '/status/' + item.id + '">' + setTweetDate(item.created_at) + '</a>'
							);
						$(tweetstr).linkify();
						container.append(tweetstr);
					});
					container.css('padding-left','0');
					$("#juitterContainer").append(container);
				}
			});
		},
		filter: function(s){
			if(filterWords){
				searchWords = filterWords.split(",");
				if(searchWords.length>0){
					cleanHTML=s;
					$.each(searchWords,function(i,item){
						sW = item.split("->").length>0 ? item.split("->")[0] : item;
						rW = item.split("->").length>0 ? item.split("->")[1] : "";
						regExp=eval('/'+sW+'/gi');
						cleanHTML = cleanHTML.replace(regExp, rW);
					});
				} else cleanHTML = s;
				return cleanHTML;
			} else return s;
		},
		temporizador: function(){
			// live mode timer
			running=true;
			aTim = timer.split("-");
			if(aTim[0]=="live" && aTim[1].length>0){
				tempo = aTim[1]*1000;
				setTimeout("$.Juitter.update()",tempo);
			}
		}
	};
})(jQuery);
