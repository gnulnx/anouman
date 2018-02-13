# Generated by Django 2.0.2 on 2018-02-13 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CloudGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('firewall', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True)),
                ('ip', models.GenericIPAddressField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('droplet_id', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('private_ip', models.GenericIPAddressField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SSHKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('public', models.TextField()),
                ('private', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='cloudgroup',
            name='machines',
            field=models.ManyToManyField(to='anouman.Machine'),
        ),
        migrations.AddField(
            model_name='cloudgroup',
            name='sshkeys',
            field=models.ManyToManyField(to='anouman.SSHKey'),
        ),
        migrations.AddField(
            model_name='cloudgroup',
            name='whitelist',
            field=models.ManyToManyField(to='anouman.IPAddress'),
        ),
    ]
