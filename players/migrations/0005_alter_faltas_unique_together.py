# Generated by Django 5.1.6 on 2025-05-13 18:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gerencia', '0002_remove_turma_faixa_etaria'),
        ('players', '0004_faltas'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='faltas',
            unique_together={('aluno', 'turma', 'data')},
        ),
    ]
