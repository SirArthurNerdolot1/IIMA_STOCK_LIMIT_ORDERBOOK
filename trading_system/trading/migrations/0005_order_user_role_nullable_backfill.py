import django.db.models.deletion
from django.db import migrations, models


def forward_copy_users(apps, schema_editor):
    OldUser = apps.get_model("trading", "User")
    BaseUser = apps.get_model("trading", "BaseUser")
    for old_user in OldUser.objects.all():
        BaseUser.objects.update_or_create(
            id=old_user.id,
            defaults={
                "username": old_user.username,
                "role": "TRADER",
            },
        )


def backfill_user_role(apps, schema_editor):
    Order = apps.get_model("trading", "Order")
    for order in Order.objects.filter(user_role__isnull=True):
        if order.user and getattr(order.user, "role", None):
            order.user_role = order.user.role
            order.save(update_fields=["user_role"])


class Migration(migrations.Migration):

    dependencies = [
        ("trading", "0004_user_remove_trader_baseuser_ptr_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BaseUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=100, unique=True)),
                ("role", models.CharField(choices=[("TRADER", "Trader"), ("MARKET_MAKER", "Market Maker")], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="MarketMaker",
            fields=[
                ("baseuser_ptr", models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to="trading.baseuser")),
            ],
            bases=("trading.baseuser",),
        ),
        migrations.CreateModel(
            name="Trader",
            fields=[
                ("baseuser_ptr", models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to="trading.baseuser")),
            ],
            bases=("trading.baseuser",),
        ),
        migrations.RunPython(forward_copy_users, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="order",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="trading.baseuser"),
        ),
        migrations.AlterField(
            model_name="stoploss_order",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="trading.baseuser"),
        ),
        migrations.AlterField(
            model_name="trade",
            name="buyer",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="buy_trades", to="trading.baseuser"),
        ),
        migrations.AlterField(
            model_name="trade",
            name="seller",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sell_trades", to="trading.baseuser"),
        ),
        migrations.AddField(
            model_name="order",
            name="user_role",
            field=models.CharField(blank=True, choices=[("TRADER", "Trader"), ("MARKET_MAKER", "Market Maker")], max_length=30, null=True),
        ),
        migrations.RunPython(backfill_user_role, migrations.RunPython.noop),
    ]
