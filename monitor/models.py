from django.db import models

class SensorData(models.Model):
    devid = models.CharField(max_length=100, blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    umidade = models.FloatField(blank=True, null=True)
    temperatura = models.FloatField(blank=True, null=True)
    profundidade = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    raw_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SensorData {self.devid} at {self.created_at}"
