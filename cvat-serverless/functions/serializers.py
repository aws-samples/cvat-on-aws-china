from rest_framework import serializers
from functions.models import Function


class FunctionSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    spec = serializers.CharField(required=False, allow_blank=True, max_length=5000)
    framework = serializers.CharField(required=False, allow_blank=True, max_length=100)
    description = serializers.CharField(allow_blank=True, max_length=100)
    type = serializers.CharField(required=False, allow_blank=True, max_length=100)
    help_message = serializers.CharField(allow_blank=True, max_length=100)
    animated_gif = serializers.CharField(allow_blank=True, max_length=100)
    min_pos_points = serializers.IntegerField()
    min_neg_points = serializers.IntegerField()
    startswith_box = serializers.BooleanField()
    status = serializers.CharField(required=False,allow_blank=True, max_length=100)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Function.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        # instance.name = validated_data.get('name', instance.name)
        # instance.spec = validated_data.get('spec', instance.spec)
        # instance.framework = validated_data.get('framework', instance.framework)
        # instance.description = validated_data.get('description', instance.description)
        # instance.type = validated_data.get('type', instance.type)
        # instance.help_message = validated_data.get('help_message', instance.help_message)
        # instance.animated_gif = validated_data.get('animated_gif', instance.animated_gif)
        # instance.min_pos_points = validated_data.get('min_pos_points', instance.min_pos_points)
        # instance.min_neg_points = validated_data.get('min_neg_points', instance.min_neg_points)
        # instance.startswith_box = validated_data.get('startswith_box', instance.startswith_box)
        # status.animated_gif = validated_data.get('status', instance.status)
        # instance.save()
        # return instance