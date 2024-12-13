from rest_framework import serializers

class CSVToXMLSerializer(serializers.Serializer):
    csv_file = serializers.FileField()
