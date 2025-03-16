async function generateAndDisplayAltText() {
    let images = document.querySelectorAll("img");
    let imageUrls = [];
    images.forEach(img => {
        if (img.src) {
            imageUrls.push(img.src);
        }
    });

    if (imageUrls.length === 0) return;

    let response = await fetch("http://127.0.0.1:5000/generate_alt_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_urls: imageUrls })
    });

    let altTextData = await response.json();

    images.forEach(img => {
        let altText = altTextData[img.src] || "No description available";
        
        let textElement = document.createElement("p");
        textElement.textContent = `[AI Generated: ${altText}]`;
        textElement.style.fontSize = "14px";
        textElement.style.color = "blue"; // Customize color
        textElement.style.fontStyle = "italic";
        
        img.insertAdjacentElement("afterend", textElement);
    });

    console.log("AI-generated descriptions displayed below images.");
}

generateAndDisplayAltText();
