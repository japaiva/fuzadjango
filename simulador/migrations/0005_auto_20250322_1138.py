from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('simulador', '0004_alter_usuario_date_joined_alter_usuario_is_active_and_more'),  # Ajuste para sua última migração
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE NULL;
            ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE;
            ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS first_name VARCHAR(150) DEFAULT '';
            ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS last_name VARCHAR(150) DEFAULT '';
            ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
            ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_staff BOOLEAN DEFAULT FALSE;
            ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            """,
            """
            -- Não é necessário reverter (opcional)
            """
        ),
    ]
