const products = [
  {
    id: 1,
    name: 'عباية مخمل فاخرة',
    cat: 'عبايات',
    price: 389,
    old: 459,
    image: 'images/abaya1.jpg',
    badge: 'جديد'
  },
  {
    id: 2,
    name: 'عباية كريب ملكي',
    cat: 'عبايات',
    price: 297,
    old: 330,
    image: 'images/abaya2.jpg',
    badge: '-10%'
  },
  {
    id: 3,
    name: 'عطر يارا',
    cat: 'عطور',
    price: 620,
    old: 0,
    image: 'images/perfume1.jpg',
    badge: 'الأكثر مبيعًا'
  },
  {
    id: 4,
    name: 'عطر رويال بلو',
    cat: 'عطور',
    price: 449,
    old: 550,
    image: 'images/perfume2.jpg',
    badge: '-18%'
  },
  {
    id: 5,
    name: 'شنطة ديور سوداء',
    cat: 'شنط',
    price: 399,
    old: 0,
    image: 'images/bag1.jpg',
    badge: 'جديد'
  },
  {
    id: 6,
    name: "شنطه ديور انيقه",
    cat: 'شنط',
    price: 383,
    old: 450,
    image: 'images/bag2.jpg',
    badge: '-15%'
  }
];

let cart = [];
let current = 'الكل';

const grid = document.getElementById('productsGrid');

function card(p) {
  return `
    <article class="product">
      <div class="product-media">
        <span class="badge">${p.badge}</span>

        <img
          class="product-img"
          src="${p.image}"
          alt="${p.name}"
          loading="lazy"
          onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
        >

        <div class="image-error">
          تعذر تحميل الصورة
        </div>
      </div>

      <div class="product-info">
        <span class="product-cat">${p.cat}</span>

        <h3>${p.name}</h3>

        <div class="price">
          <div>
            <strong>${p.price} ر.س</strong>

            ${
              p.old
                ? `<span class="old">${p.old} ر.س</span>`
                : ''
            }
          </div>

          <button
            class="add"
            data-id="${p.id}"
            aria-label="إضافة للسلة">
            +
          </button>
        </div>
      </div>
    </article>
  `;
}

function render() {
  const searchInput = document.getElementById('searchInput');

  const q = searchInput
    ? searchInput.value.trim().toLowerCase()
    : '';

  const filtered = products.filter(p =>
    (current === 'الكل' || p.cat === current) &&
    (
      !q ||
      p.name.toLowerCase().includes(q) ||
      p.cat.toLowerCase().includes(q)
    )
  );

  grid.innerHTML = filtered.length
    ? filtered.map(card).join('')
    : '<p>لا توجد منتجات مطابقة.</p>';

  document.querySelectorAll('.add').forEach(button => {
    button.onclick = () => add(Number(button.dataset.id));
  });
}

function add(id) {
  const product = products.find(p => p.id === id);

  if (!product) return;

  const item = cart.find(x => x.id === id);

  if (item) {
    item.qty++;
  } else {
    cart.push({
      ...product,
      qty: 1
    });
  }

  updateCart();
  toast('تمت إضافة المنتج إلى السلة');
}

function updateCart() {
  const count = document.getElementById('cartCount');
  const box = document.getElementById('cartItems');
  const total = document.getElementById('cartTotal');

  const quantity = cart.reduce(
    (sum, item) => sum + item.qty,
    0
  );

  const totalPrice = cart.reduce(
    (sum, item) => sum + item.price * item.qty,
    0
  );

  count.textContent = quantity;

  if (!cart.length) {
    box.innerHTML = `
      <p style="color:#777;text-align:center;padding:40px 0">
        السلة فارغة حاليًا
      </p>
    `;
  } else {
    box.innerHTML = cart.map(item => `
      <div class="cart-row">

        <div>
          <b>${item.name}</b>

          <small>
            ${item.qty} × ${item.price} ر.س
          </small>
        </div>

        <button data-remove="${item.id}">
          حذف
        </button>

      </div>
    `).join('');
  }

  total.textContent = `${totalPrice} ر.س`;

  document.querySelectorAll('[data-remove]').forEach(button => {
    button.onclick = () => {
      cart = cart.filter(
        item => item.id !== Number(button.dataset.remove)
      );

      updateCart();
    };
  });
}

function toast(message) {
  const element = document.getElementById('toast');

  element.textContent = message;
  element.classList.add('show');

  setTimeout(() => {
    element.classList.remove('show');
  }, 1800);
}

function filter(category) {
  current = category;

  document.querySelectorAll('.filter').forEach(button => {
    button.classList.toggle(
      'active',
      button.dataset.filter === category
    );
  });

  render();

  document.getElementById('products').scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });
}

document.querySelectorAll('.filter').forEach(button => {
  button.onclick = () => {
    filter(button.dataset.filter);
  };
});

document.querySelectorAll('[data-filter]').forEach(button => {
  if (!button.classList.contains('filter')) {
    button.onclick = () => {
      filter(button.dataset.filter);
    };
  }
});

document
  .querySelectorAll('.nav a[data-category]')
  .forEach(link => {
    link.onclick = () => {
      filter(link.dataset.category);
    };
  });

const scrollButton = document.querySelector(
  '[data-scroll="products"]'
);

if (scrollButton) {
  scrollButton.onclick = () => {
    document.getElementById('products').scrollIntoView({
      behavior: 'smooth'
    });
  };
}

const searchButton = document.getElementById('searchBtn');

if (searchButton) {
  searchButton.onclick = render;
}

const searchInput = document.getElementById('searchInput');

if (searchInput) {
  searchInput.addEventListener('input', render);
}

document.getElementById('cartBtn').onclick = () => {
  document
    .getElementById('cartDrawer')
    .classList.add('open');

  document
    .getElementById('overlay')
    .classList.add('show');
};

function closeCart() {
  document
    .getElementById('cartDrawer')
    .classList.remove('open');

  document
    .getElementById('overlay')
    .classList.remove('show');
}

document.getElementById('closeCart').onclick = closeCart;
document.getElementById('overlay').onclick = closeCart;

document.getElementById('checkoutBtn').onclick = () => {
  if (!cart.length) {
    toast('أضيفي منتجًا أولًا');
    return;
  }

  const order = cart
    .map(item =>
      `${item.name} × ${item.qty} — ${item.price * item.qty} ر.س`
    )
    .join('\n');

  const total = cart.reduce(
    (sum, item) => sum + item.price * item.qty,
    0
  );

  const message =
`مرحبًا أثر،
أرغب بإتمام طلبي:

${order}

الإجمالي: ${total} ر.س

للتأكيد والتوصيل، أرجو التواصل معي.`;

  window.location.href =
    'https://wa.me/201556634099?text=' +
    encodeURIComponent(message);
};

document.getElementById('accountBtn').onclick = () => {
  toast('سيتم إضافة تسجيل الدخول لاحقًا');
};

document.getElementById('wishlistBtn').onclick = () => {
  toast('المفضلة جاهزة للتطوير');
};

render();
updateCart();