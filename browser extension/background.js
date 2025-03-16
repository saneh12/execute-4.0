chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "fetchAltText") {
        fetch("http://127.0.0.1:5000/auto-alt-text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: request.url })
        })
        .then(response => response.json())
        .then(data => sendResponse({ updated_html: data.updated_html }))
        .catch(error => sendResponse({ error: error.toString() }));

        return true;  
    }
});
