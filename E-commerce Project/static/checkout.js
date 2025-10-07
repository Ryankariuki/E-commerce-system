const cart = JSON.parse(sessionStorage.getItem('receipt_cart')) || [];

const dateNow = new Date();
const deliveryDate = new Date(dateNow);
deliveryDate.setDate(deliveryDate.getDate() + 3);

document.getElementById('date').textContent = dateNow.toLocaleString();
document.getElementById('delivery').textContent = deliveryDate.toDateString();

const productContainer = document.getElementById('products');
const totalDisplay = document.getElementById('total');
let total = parseFloat(sessionStorage.getItem('receipt_total')) || 0;

if (cart.length === 0) {
  productContainer.innerHTML = '<p class="text-center">Your cart is empty.</p>';
  totalDisplay.textContent = '0.00';
} else {
  cart.forEach(item => {
    const price = item.price;
    const quantity = item.quantity;
    const subtotal = price * quantity;

    const productEl = document.createElement('div');
    productEl.classList.add('product-item');
    productEl.innerHTML = `
      <div><strong>${item.name}</strong> (x${quantity})</div>
      <div>Ksh ${price.toFixed(2)} each — Subtotal: Ksh ${subtotal.toFixed(2)}</div>
      <div style="font-size: 13px; color: #777;">${item.description || ''}</div>
    `;
    productContainer.appendChild(productEl);
  });

  totalDisplay.textContent = total.toFixed(2);
}

fetch('/api/submit_order', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    products: cart,
    total: total,
    deliveryDate: deliveryDate.toISOString().split('T')[0]
  })
})
.then(response => {
  if (!response.ok) {
    throw new Error("Order submission failed.");
  }
  return response.json();
})
.then(data => {
  document.getElementById('orderId').textContent = data.order_id || 'N/A';
  const buyerName = sessionStorage.getItem('receipt_buyer_name') || `User #${data.user_id}`;
  document.getElementById('name').textContent = buyerName;

  // Cleanup
  localStorage.removeItem('cart');
  sessionStorage.removeItem('receipt_cart');
  sessionStorage.removeItem('receipt_total');
  sessionStorage.removeItem('receipt_buyer_name');
})
.catch(err => {
  alert("There was an error processing your order.");
  console.error(err);
});
