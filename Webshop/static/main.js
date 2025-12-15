document.addEventListener("DOMContentLoaded", function() {
    // Find all buttons met class "btn" in product cards
    const cartButtons = document.querySelectorAll(".product-card .btn");

    cartButtons.forEach(function(btn) {
        btn.addEventListener("click", function(event) {
            event.preventDefault(); 
            
            const productCard = btn.closest(".product-card");
            if (productCard) {
                const productName = productCard.querySelector("h2").innerText;
                showNotification(productName + " is toegevoegd aan de winkelwagen!");
                
                setTimeout(function() {
                    const form = btn.closest("form");
                    if (form) {
                        form.submit();
                    }
                }, 600);
            }
        });
    });
});

function showNotification(message) {
    const existingNotifications = document.querySelectorAll(".add-to-cart-notification");
    existingNotifications.forEach(n => n.remove());
    
    const notification = document.createElement("div");
    notification.className = "add-to-cart-notification";
    notification.innerHTML = "✓ " + message;
    
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.remove();
    }, 5000);
}

const forms = document.querySelectorAll("form");

forms.forEach(function(form) {
    form.addEventListener("submit", function(event) {
        const inputs = form.querySelectorAll("input, textarea");
        let valid = true;

        inputs.forEach(function(input) {
            if (!input.value.trim()) {
                valid = false;
                input.style.border = "2px solid red";
            } else {
                input.style.border = "1px solid #ddd";
            }
        });

        if (!valid) {
            event.preventDefault();
            alert("Vul alle velden in voordat je verstuurt!");
        }
    });
});
