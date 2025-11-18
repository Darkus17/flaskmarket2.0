from app import create_app
from models import db, Product

def add_products():
    app = create_app()

    sample_products = [
        {
            "name": "Игровая видеокарта RTX 4060",
            "description": "Мощная видеокарта для современных игр",
            "price": 32990
        },
        {
            "name": "Процессор AMD Ryzen 5 5600",
            "description": "6 ядер / 12 потоков, отличное соотношение цена/качество",
            "price": 14990
        },
        {
            "name": "Материнская плата MSI B550-A PRO",
            "description": "Совместима с Ryzen, поддержка PCIe 4.0",
            "price": 10490
        },
        {
            "name": "Оперативная память Kingston 16GB DDR4",
            "description": "Надежная и быстрая память для ПК",
            "price": 3990
        },
        {
            "name": "SSD NVMe Samsung 980 500GB",
            "description": "Очень быстрый NVMe для системы и игр",
            "price": 4990
        }
    ]

    with app.app_context():
        for item in sample_products:
            product = Product(
                name=item["name"],
                description=item["description"],
                price=item["price"],
                image_filename=None,   # картинки загрузишь сама в админке
                image_url=None
            )
            db.session.add(product)

        db.session.commit()
        print("✔ Добавлено товаров:", len(sample_products))

if __name__ == "__main__":
    add_products()
