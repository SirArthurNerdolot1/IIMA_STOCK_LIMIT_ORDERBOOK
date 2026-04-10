from django.db import migrations


def remove_orphaned_orders(apps, schema_editor):
    Order = apps.get_model('trading', 'Order')
    Stoploss_Order = apps.get_model('trading', 'Stoploss_Order')
    Trade = apps.get_model('trading', 'Trade')
    BaseUser = apps.get_model('trading', 'BaseUser')

    valid_user_ids = set(BaseUser.objects.values_list('id', flat=True))

    orphaned_orders = Order.objects.exclude(user_id__in=valid_user_ids)
    orphaned_orders.delete()

    orphaned_stoploss_orders = Stoploss_Order.objects.exclude(user_id__in=valid_user_ids)
    orphaned_stoploss_orders.delete()

    orphaned_trades = Trade.objects.exclude(
        buyer_id__in=valid_user_ids
    ).union(
        Trade.objects.exclude(seller_id__in=valid_user_ids)
    )
    # union() returns a non-deletable queryset; collect IDs first
    orphaned_trade_ids = list(
        Trade.objects.exclude(buyer_id__in=valid_user_ids).values_list('id', flat=True)
    ) + list(
        Trade.objects.exclude(seller_id__in=valid_user_ids).values_list('id', flat=True)
    )
    Trade.objects.filter(id__in=orphaned_trade_ids).delete()


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0008_alter_baseuser_role_alter_order_user_role'),
    ]

    operations = [
        migrations.RunPython(remove_orphaned_orders, do_nothing),
    ]
