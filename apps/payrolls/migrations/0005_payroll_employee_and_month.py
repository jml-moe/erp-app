from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0003_employeesetting"),
        ("payrolls", "0004_alter_payroll_options_alter_payroll_month_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="payroll",
            name="employee",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name="payrolls", to="employees.employee"),
        ),
        migrations.AlterField(
            model_name="payroll",
            name="month",
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
