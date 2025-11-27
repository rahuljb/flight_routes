from rest_framework import serializers
from .models import Route, RouteNode

class RouteNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteNode
        fields = ["id", "route", "airport_code", "position", "duration"]


class RouteSerializer(serializers.ModelSerializer):
    nodes = RouteNodeSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ["id", "name", "nodes"]
