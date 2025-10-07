const cartItems = JSON.parse(localStorage.getItem("cart")) || [];

    const cartTableBody = document.querySelector("#cart-table tbody");
    const cartTotalElement = document.getElementById("cart-total");

    function updateCartDisplay() {
      cartTableBody.innerHTML = "";
      let total = 0;

      if (cartItems.length === 0) {
        cartTableBody.innerHTML = `<tr><td colspan='5' class='text-center'>Your cart is empty.</td></tr>`;
        cartTotalElement.textContent = "Ksh0.00";
        return;
      }

      cartItems.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <img src="/static/images/${item.image_url}" alt="${item.name}" width="60" class="me-3 rounded">
                    <div>
                        <strong>${item.name}</strong><br>
                        <small class="text-muted">${item.description}</small>
                    </div>
                </div>
            </td>
            <td>Ksh${item.price.toFixed(2)}</td>
            <td><input type="number" class="form-control form-control-sm" value="${item.quantity}" style="width: 60px;" onchange="updateQuantity(${index}, this.value)"></td>
            <td> Ksh${itemTotal.toFixed(2)}</td>
            <td><button class="btn btn-sm btn-outline-danger" onclick="removeItem(${index})">Remove</button></td>
        `;
        cartTableBody.appendChild(row);
    });
    
    cartTotalElement.textContent = `Ksh${total.toFixed(2)}`;
}

function updateQuantity(index,  newQuantity) {
    const quantity = parseInt(newQuantity);
    if (!isNaN(quantity) && quantity > 0) {
        cartItems[index].quantity = quantity;
        localStorage.setItem("cart", JSON.stringify(cartItems));
        updateCartDisplay();
    } else {
        alert("Please enter a valid quantity (1 or more).");
        updateCartDisplay(); // Refresh display to show current quantities
    }
}

function removeItem(index) {
    cartItems.splice(index, 1);
    localStorage.setItem("cart", JSON.stringify(cartItems));
    updateCartDisplay();
}

function proceedToCheckout() {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const buyerName = localStorage.getItem('buyer_name') || 'Guest';

    if (cartItems.length === 0) {
        alert("Your cart is empty. Please add items before proceeding to checkout.");
        return;
    }

    const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    sessionStorage.setItem('receipt_cart', JSON.stringify(cartItems));
    sessionStorage.setItem('receipt_total', total);
    sessionStorage.setItem('receipt_buyer_name', buyerName);

    
    window.location.href = "/checkout";
}

document.addEventListener("DOMContentLoaded", updateCartDisplay);