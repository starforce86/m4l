# Generated by Django 3.2.18 on 2023-03-10 03:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("chapters", "0013_auto_20220808_1704"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChapterMembershipChapterAppField",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "position",
                    models.IntegerField(
                        blank=True, default=0, null=True, verbose_name="Position"
                    ),
                ),
                ("label", models.CharField(max_length=2000, verbose_name="Label")),
                (
                    "field_name",
                    models.CharField(blank=True, default="", max_length=100),
                ),
                (
                    "required",
                    models.BooleanField(
                        blank=True, default=False, verbose_name="Required"
                    ),
                ),
                (
                    "display",
                    models.BooleanField(blank=True, default=True, verbose_name="Show"),
                ),
                (
                    "customizable",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="Chapter leaders can customize this field.",
                    ),
                ),
                (
                    "admin_only",
                    models.BooleanField(default=False, verbose_name="Admin Only"),
                ),
                (
                    "field_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "Set to Default"),
                            ("CharField", "Text"),
                            ("CharField/django.forms.Textarea", "Paragraph Text"),
                            ("BooleanField", "Checkbox"),
                            ("ChoiceField", "Select One (Drop Down)"),
                            (
                                "ChoiceField/django.forms.RadioSelect",
                                "Select One (Radio Buttons)",
                            ),
                            ("MultipleChoiceField", "Multi select (Drop Down)"),
                            (
                                "MultipleChoiceField/django.forms.CheckboxSelectMultiple",
                                "Multi select (Checkboxes)",
                            ),
                            ("CountrySelectField", "Countries Drop Down"),
                            ("EmailField", "Email"),
                            ("FileField", "File upload"),
                            ("DateField/django.forms.widgets.SelectDateWidget", "Date"),
                            ("DateTimeField", "Date/time"),
                            ("section_break", "Section Break"),
                        ],
                        max_length=64,
                        verbose_name="Field Type",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        max_length=200,
                        verbose_name="Description",
                    ),
                ),
                (
                    "help_text",
                    models.CharField(
                        blank=True, default="", max_length=300, verbose_name="Help Text"
                    ),
                ),
                (
                    "choices",
                    models.CharField(
                        blank=True,
                        help_text="Comma separated options where applicable",
                        max_length=1000,
                        verbose_name="Choices",
                    ),
                ),
                (
                    "default_value",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=200,
                        verbose_name="Default Value",
                    ),
                ),
                (
                    "css_class",
                    models.CharField(
                        blank=True, default="", max_length=200, verbose_name="CSS Class"
                    ),
                ),
                (
                    "chapter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="membership_app_fields",
                        to="chapters.chapter",
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "membership_app",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="all_chapter_fields",
                        to="chapters.chaptermembershipapp",
                    ),
                ),
            ],
            options={
                "verbose_name": "Chapter Field",
                "verbose_name_plural": "Chapter Fields",
                "ordering": ("position",),
            },
        ),
    ]
