// “Eerst wacht JavaScript tot de pagina helemaal geladen is.
// Dan zoekt het alle knoppen om een product toe te voegen.
// Bij een klik stopt hij even het formulier, toont een melding
// en verstuurt daarna het formulier alsnog.”





// “Deze code wacht eerst tot de pagina helemaal geladen is.
// Daarna zoekt hij alle knoppen waarmee je een product kunt toevoegen.
// Bij een klik wordt het formulier tijdelijk gestopt.
// De productnaam wordt opgehaald en er verschijnt een melding.
// Na een korte vertraging wordt het formulier alsnog verstuurd.”
// WACHT TOT DE PAGINA KLAAR IS
// =========================
// Deze code start pas als de hele pagina is geladen

document.addEventListener("DOMContentLoaded", function() {

    // Zoek alle "Toevoegen aan winkelwagen" knoppen
    const cartButtons = document.querySelectorAll(".product-card .btn");

    // Ga door elke knop heen
    cartButtons.forEach(function(btn) {

        // Kijk of er op de knop wordt geklikt
        btn.addEventListener("click", function(event) {

            // Stop dat het formulier meteen verstuurt
            event.preventDefault(); 
            
            // Zoek het productblok waar de knop in zit
            const productCard = btn.closest(".product-card");

            // Als het productblok bestaat
            if (productCard) {

                // Pak de naam van het product
                const productName = productCard.querySelector("h2").innerText;

                // Laat een melding zien op het scherm
                showNotification(productName + " is toegevoegd aan de winkelwagen!");
                
                // Wacht een klein beetje
                setTimeout(function() {

                    // Zoek het formulier van de knop
                    const form = btn.closest("form");

                    // Verstuur daarna het formulier
                    if (form) {
                        form.submit();
                    }
                }, 600);
            }
        });
    });
});

// “Deze functie laat een melding zien op de pagina.
// Eerst worden oude meldingen verwijderd.
// Daarna wordt een nieuw HTML-element gemaakt met de tekst.
// Dat element wordt aan de pagina toegevoegd
// en na vijf seconden automatisch weggehaald.”

// MELDING LATEN ZIEN
// =========================
// Deze functie laat een korte melding zien bovenaan de pagina
function showNotification(message) {

    // Verwijder oude meldingen als die er nog zijn
    const existingNotifications = document.querySelectorAll(".add-to-cart-notification");
    existingNotifications.forEach(n => n.remove());
    
    // Maak een nieuw blok voor de melding
    const notification = document.createElement("div");

    // Geef het blok een naam (class) voor de styling
    notification.className = "add-to-cart-notification";

    // Zet de tekst in de melding
    notification.innerHTML = "✓ " + message;
    
    // Zet de melding op de pagina
    document.body.appendChild(notification);
    
    // Haal de melding weg na 5 seconden
    setTimeout(function() {
        notification.remove();
    }, 5000);
}


// FORMULIER CONTROLEREN

// “Hier worden alle formulieren gecontroleerd.
// Wanneer een formulier wordt verstuurd, kijkt de code of alle velden zijn ingevuld.
// Lege velden krijgen een rode rand.
// Als niet alles is ingevuld, wordt het formulier niet verzonden
// en verschijnt er een waarschuwing.”

// Zoek alle formulieren op de pagina
const forms = document.querySelectorAll("form");

// Ga door elk formulier heen
forms.forEach(function(form) {

    // Als iemand het formulier wil versturen
    form.addEventListener("submit", function(event) {

        // Zoek alle invoervelden
        const inputs = form.querySelectorAll("input, textarea");

        // We denken eerst: alles is goed
        let valid = true;

        // Controleer elk veld
        inputs.forEach(function(input) {

            // Als het veld leeg is
            if (!input.value.trim()) {
                valid = false;

                // Maak de rand rood
                input.style.border = "2px solid red";
            } else {
                // Normale rand als het veld is ingevuld
                input.style.border = "1px solid #ddd";
            }
        });

        // Als niet alles is ingevuld
        if (!valid) {

            // Stop het versturen
            event.preventDefault();

            // Geef een melding
            alert("Vul alle velden in voordat je verstuurt!");
        }
    });
});
