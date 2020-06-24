from models import Message, HandleDB, Product, ProductAttr, Category


def init_texts():
    Message.objects.create(
        title=Message.TITLES['options'],
        body='Below are the available options. Choose one.'
    )
    Message.objects.create(
        title=Message.TITLES['basket'],
        body='Your basket'
    )
    Message.objects.create(
        title=Message.TITLES['greetings'],
        body='Well, hello! Kayurmatik here to assist you. Choose one of the options'
    )
    Message.objects.create(
        title=Message.TITLES['test'],
        body='test test'
    )

def init_products():
    # prod = ProductAttr(
    #     weight=1.332
    # )

    Product.objects.create(
        attr = ProductAttr(weight=1.332),
        title= 'Title prod2',
        description = 'me.StringField(min_length=2, max_length=4096)',
        price = 123,
        # image = me.FileField(required=True),
        category = '5ee216c1b5ee6e200dcdc952'
    )

def init_categories():
    Category.objects.create(

    )

if __name__ == '__main__':
    init_categories()
