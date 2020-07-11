from models import Category, Product, Message


def seed_category(categ_titles: list, categ_descr: list = None):
    if not categ_descr:
        categ_descr = [(item + ' descr') for item in categ_titles]
    categ_list = list()
    categories = zip(categ_titles, categ_descr)
    for record in categories:
        categ_list.append({'title': record[0], 'description': record[1]})
    Category().fill_category_collection(categ_list)


if __name__ == '__main__':
    """seeding categories"""
    seed_category(['Accessories', 'Menswear', 'Sportswear'])

    """seeding subcategories"""
    accessories = ['Belts', 'Gloves', 'Hats']
    menswear = ['Trousers', 'Tie', 'Jacket']
    sportswear = ['Leggins', 'Tracksuits']

    seed_category(categ_titles=accessories)
    seed_category(categ_titles=menswear)
    seed_category(categ_titles=sportswear)


    """matching subcategories to categories"""
    category = Category.objects.get(title='Accessories')
    for record in accessories:
        category.add_subcategory(Category.objects.get(title=record))

    category = Category.objects.get(title='Menswear')
    for record in menswear:
        category.add_subcategory(Category.objects.get(title=record))

    category = Category.objects.get(title='Sportswear')
    for record in sportswear:
        category.add_subcategory(Category.objects.get(title=record))

    """seeding sub-subcategories"""
    hats = ['Caps', 'Winter hats', 'Headbands']
    menswear_trousers = ['Winter trousers', 'Summer trousers']

    seed_category(categ_titles=menswear_trousers)
    seed_category(categ_titles=hats)

    trousers_subcategory = Category.objects.get(title='Trousers')
    for record in menswear_trousers:
        trousers_subcategory.add_subcategory(Category.objects.get(title=record))

    hats_subcategory = Category.objects.get(title='Hats')
    for record in hats:
        hats_subcategory.add_subcategory(Category.objects.get(title=record))

    """matching subsubcategories to subcategories"""
    winter_trousers = ['Ski winter trousers']
    seed_category(categ_titles=winter_trousers)
    winter_trousers_subcategory = Category.objects.get(title='Winter trousers')
    winter_trousers_subcategory.add_subcategory(Category.objects.get(title='Ski winter trousers'))

    """seeding messages"""
    Message().fill_message_collection([{'title': 'options', 'body': 'Below are the available options. Choose '
                                                                     'one.'},
                                        {'title': 'greetings', 'body': 'Hey hey, I am here to assist you. Make your choice'},
                                        {'title': 'no_product', 'body': 'Sorry, there are no products in this category'},
                                        {'title': 'add_basket', 'body': 'Click to add it to your basket'},
                                        {'title': 'basket', 'body': 'Your basket:'},
                                        {'title': 'sales', 'body': 'Click to view all discounted products'},
                                        {'title': 'added_to_basket', 'body': 'Successfully added to the basket'},
                                        {'title': 'empty_basket', 'body': 'Seems like your basket is empty. '
                                                                          'Go to the main menu and add some products'},
                                        {'title': 'basket_cleared', 'body': 'Your basket was cleared'},
                                        {'title': 'order_registered', 'body': 'Your order # {} was registered.\n '
                                                                              'Order details:\n {} \nThank You.'}])


    """seeding products"""
    category = Category.objects.get(title='Belts')
    Product().fill_product_collection([{'title': 'leather belt',
                                         'description': 'nice leather belt',
                                         'price': 10,
                                         'discount': 0,
                                         'category': category,
                                         'image': ".\\images\\belt.jpg"}])

    category = Category.objects.get(title='Gloves')
    Product().fill_product_collection([{'title': 'No Fear Gloves',
                                         'attr': {'color': 'brown', 'weight': 3},
                                         'description': 'Biking gloves',
                                         'price': 12.3,
                                         'discount': 0,
                                         'category': category,
                                         'image': None}])
    Product().fill_product_collection([{'title': 'Fluffy gloves',
                                         'attr': {'color': 'brown', 'weight': 3},
                                         'description': 'Biking gloves',
                                         'price': 12.3,
                                         'discount': 33,
                                         'category': category,
                                         'image': None}])
    Product().fill_product_collection([{'title': 'Blizzard ski trousers',
                                         'attr': {'color': 'light red', 'weight': 3},
                                         'description': 'blizzard descr',
                                         'price': 45,
                                         'discount': 19,
                                         'category': Category.objects.get(title='Ski winter trousers'),
                                         'image': None}])
