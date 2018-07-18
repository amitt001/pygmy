var su = 'default value';

function makeShort(tablink) {
  chrome.storage.sync.get({ restUrl: 'https://api.url.joor.net'}, 
    function(items) {
      var rest_url = items.restUrl;
      document.getElementById("backend").innerHTML = '\
        Backend used: <a href="'+rest_url+'">'+rest_url+'</a><br />\
        Change the backend using extension options.';
      rest_query( tablink, rest_url);
    }
  );
}

// REST client query
function rest_query(tablink, rest_url) { 
  var xhr = new XMLHttpRequest();
  xhr.open("POST", rest_url + '/api/shorten', true);
  xhr.setRequestHeader("Content-Type", "application/json");
  var req = {name:"John Rambo", time:"2pm"};
  var req = {
    secret_key: "", 
    expire_after: null, 
    is_protected: false, 
    owner: null, 
    is_custom: false, 
    short_code: "", 
    long_url: tablink, 
    description: null
  };
  var data = JSON.stringify(req);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      var jresponse = JSON.parse(xhr.responseText);
      su = jresponse.short_url; //+ '/' + jresponse.short_code;
      var link = "<a href=\""+su+"\">"+su+"</a>";
      document.getElementById("short-url").innerHTML = link;
      document.getElementById("short-url").addEventListener('click', function() {
        chrome.tabs.create({ url: su});
      })
    }
  }
  xhr.send(data);
}

chrome.tabs.getSelected(null,function(tab) {
  var tablink = tab.url; 
  document.getElementById("long-url").setAttribute('value',tablink);
  document.getElementById("short").onclick = function() {
    makeShort(tablink);
  };

  var cc = new ClipboardJS('#cc');
  cc.on('success', function(e) {
    document.getElementById('status').innerHTML = '<br /><strong>Copied to clipboard.</strong><br /><br />';
    setTimeout(function() {
      document.getElementById('status').innerHTML = '';
    }, 1500);
  });
  cc.on('error', function(e) {
      console.error('Action:', e.action);
      console.error('Trigger:', e.trigger);
  });
});

