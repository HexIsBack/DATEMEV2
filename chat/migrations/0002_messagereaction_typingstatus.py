from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageReaction',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.IntegerField()),
                ('user_id',    models.IntegerField()),
                ('emoji',      models.CharField(max_length=8)),
                ('created',    models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'app_label': 'chat',
                'unique_together': {('message_id', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='TypingStatus',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typer_id',    models.IntegerField()),
                ('receiver_id', models.IntegerField()),
                ('updated_at',  models.DateTimeField(auto_now=True)),
            ],
            options={
                'app_label': 'chat',
                'unique_together': {('typer_id', 'receiver_id')},
            },
        ),
    ]
