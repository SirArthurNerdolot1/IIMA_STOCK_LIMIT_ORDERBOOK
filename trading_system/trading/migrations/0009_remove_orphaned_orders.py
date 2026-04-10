from django.db import migrations


def remove_orphaned_orders(apps, schema_editor):
    # Use raw SQL DELETE with NOT IN subqueries to reliably remove records
    # whose foreign-key user references no longer exist in trading_baseuser.
    # The Django ORM exclude() approach proved unreliable in the previous
    # migration (0009), so we bypass the ORM entirely here.

    # --- Order ---
    schema_editor.execute(
        """
        DELETE FROM trading_order
        WHERE user_id NOT IN (SELECT id FROM trading_baseuser)
        """
    )
    # Report how many rows were affected (cursor.rowcount after execute)
    print(
        f"[0009] Deleted orphaned trading_order rows "
        f"(user_id not in trading_baseuser)"
    )

    # --- Stoploss_Order ---
    schema_editor.execute(
        """
        DELETE FROM trading_stoploss_order
        WHERE user_id NOT IN (SELECT id FROM trading_baseuser)
        """
    )
    print(
        f"[0009] Deleted orphaned trading_stoploss_order rows "
        f"(user_id not in trading_baseuser)"
    )

    # --- Trade (buyer or seller missing) ---
    schema_editor.execute(
        """
        DELETE FROM trading_trade
        WHERE buyer_id  NOT IN (SELECT id FROM trading_baseuser)
           OR seller_id NOT IN (SELECT id FROM trading_baseuser)
        """
    )
    print(
        f"[0009] Deleted orphaned trading_trade rows "
        f"(buyer_id or seller_id not in trading_baseuser)"
    )


def do_nothing(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0008_alter_baseuser_role_alter_order_user_role'),
    ]

    operations = [
        migrations.RunPython(remove_orphaned_orders, do_nothing),
    ]
