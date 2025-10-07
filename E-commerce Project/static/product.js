function addToCart(id, name, price, image_url, description) {
  let cart = JSON.parse(localStorage.getItem("cart")) || [];
  const existing = cart.find(item => item.id === id);
  
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ id: id, name: name, price: parseFloat(price), image_url: image_url, description: description, quantity: 1 });
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  alert("Product added to cart!");
}

document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/products")
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById("products-grid");
        container.innerHTML = "";

        data.forEach(product => {
            const card = `
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <img src="/static/images/${product.image_url}" class="card-img-top" alt="${product.name}">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text">${product.description}</p>
                        <p class="card-text fw-bold">Ksh ${product.price.toFixed(2)}</p>
                        <button class="btn btn-outline-primary mt-auto"
                            onclick="addToCart(${product.id}, \'${product.name}\', ${product.price}, \'${product.image_url}\', \'${product.description}\')">
                            Add to Cart
                        </button>
                    </div>
                </div>
            </div>
            `;
            container.innerHTML += card;
        });
    });
});
