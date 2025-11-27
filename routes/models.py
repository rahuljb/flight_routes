from django.db import models


class Route(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class RouteNode(models.Model):
    route = models.ForeignKey(Route,on_delete=models.CASCADE, related_name="nodes")
    airport_code = models.CharField(max_length=10)
    position = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    parent = models.ForeignKey('self',null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    side = models.CharField( max_length=5, choices=(('left', 'Left'), ('right', 'Right')), null=True, blank=True, help_text="Is this node the left or right child of its parent?")
    class Meta:
        ordering = ["route", "position"]
        unique_together = ("route", "position")
