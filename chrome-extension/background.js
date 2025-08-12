chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchData') {
    fetch(request.url, request.options || {})
      .then(response => response.json())
      .then(data => sendResponse({success: true, data}))
      .catch(error => sendResponse({success: false, error: error.message}));
    return true;
  }
});