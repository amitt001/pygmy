// Saves settings to chrome.storage
function save_options() {
  var rest_url = document.getElementById('rest_url').value;
  chrome.storage.sync.set({ 'restUrl': rest_url}, 
    function() {
      console.log('saved');
      // Update status to let user know options were saved.
      var status = document.getElementById('status');
      status.innerHTML = '<br /><strong>Settings saved.</strong><br /><br />';
      setTimeout(function() {
        status.innerHTML = '';
      }, 1500);
    }
  );
}

// Restore settings from chrome.storage
function restore_options() {
  // Set default
  chrome.storage.sync.get({ restUrl: 'https://api.url.joor.net'}, 
    function(items) {
      document.getElementById('rest_url').value = items.restUrl;
    }
  );
}

// linking events to the previous functions
document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click', save_options);