from django.db import migrations


def seed_data(apps, schema_editor):
    from website.seed_data import INITIAL_FAQS, INITIAL_ERROR_CODES

    FAQ = apps.get_model('website', 'FAQ')
    ErrorCode = apps.get_model('website', 'ErrorCode')

    for item in INITIAL_FAQS:
        FAQ.objects.get_or_create(
            question=item['question'],
            defaults={
                'category': item['category'],
                'keywords': item['keywords'],
                'answer': item['answer'],
                'order': item['order'],
                'is_active': True,
            }
        )

    for item in INITIAL_ERROR_CODES:
        ErrorCode.objects.get_or_create(
            code=item['code'],
            defaults={
                'title': item['title'],
                'category': item['category'],
                'summary': item['summary'],
                'description': item['description'],
                'resolution': item['resolution'],
                'ai_guidance': item['ai_guidance'],
            }
        )


def reverse_seed(apps, schema_editor):
    FAQ = apps.get_model('website', 'FAQ')
    ErrorCode = apps.get_model('website', 'ErrorCode')
    FAQ.objects.all().delete()
    ErrorCode.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_errorcode_faq_supportticket'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
