from django.db import models

# Create your models here.

class Function(models.Model):
	name = models.CharField(max_length=100, primary_key=True)
	spec = models.CharField(max_length=5000)
	framework = models.CharField(max_length=100)
	description = models.CharField(max_length=100)
	type = models.CharField(max_length=100)
	help_message = models.CharField(max_length=100)
	animated_gif = models.CharField(max_length=100)
	min_pos_points = models.IntegerField(default=1)
	min_neg_points = models.IntegerField(default=0)
	startswith_box = models.BooleanField(default=False)
	status = models.CharField(max_length=100)

	class Meta:
		ordering = ['name']