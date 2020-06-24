from models import Category, Product, Message, HandleDB


def seed_category(categ_titles: list, categ_descr: list = None):
    if not categ_descr:
        categ_descr = [(item + ' descr') for item in categ_titles]
    categ_list = list()
    categories = zip(categ_titles, categ_descr)
    for record in categories:
        categ_list.append({'title': record[0], 'description': record[1]})
    HandleDB().fill_category_collection(categ_list)


if __name__ == '__main__':
    """seeding categories"""
    seed_category(['Accessories', 'Menswear', 'Sportswear', 'Womenswear'])

    """seeding subcategories"""
    accessories = ['Belts', 'Gloves', 'Hats']
    menswear = ['Trousers', 'Tie', 'Jacket']
    sportswear = ['Leggins', 'Tracksuits', 'Tops', 'Tanks']
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
    seed_category(categ_titles=hats)

    """matching subsubcategories to subcategories"""
    subcategory = Category.objects.get(title='Hats')
    for record in hats:
        subcategory.add_subcategory(Category.objects.get(title=record))

    """seeding messages"""
    HandleDB().fill_message_collection([{'title': 'options', 'body': 'Below are the available options. Choose '
                                                                     'one.'}])
    HandleDB().fill_message_collection(
        [{'title': 'greetings', 'body': 'Hey hey, I am here to assist you. Make your choice'}])

    HandleDB().fill_message_collection(
        [{'title': 'no_product', 'body': 'Sorry, there are no products in this category'}])

    """seeding products"""
    category = Category.objects.get(title='Belts')
    HandleDB().fill_product_collection([{'title': 'leather belt',
                                         'description': 'nice leather belt',
                                         'price': 10,
                                         'category': category,
                                         'image': ".\\images\\belt.jpg"}])

    category = Category.objects.get(title='Gloves')
    HandleDB().fill_product_collection([{'title': 'No Fear Gloves',
                                         'attr': {'color': 'brown', 'weight': 3},
                                         'description': 'Biking gloves',
                                         'price': 12.3,
                                         'category': category}])
