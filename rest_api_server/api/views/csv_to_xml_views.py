from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.csv_to_xml_serializer import CSVToXMLSerializer
import tempfile
import pandas as pd
import xml.etree.ElementTree as ET
import os
import logging
logger = logging.getLogger(__name__)

class CSVToXMLView(APIView):
    def post(self, request):
        logger.info("CSV to XML endpoint hit.")
        serializer = CSVToXMLSerializer(data=request.data)
        if serializer.is_valid():
            csv_file = serializer.validated_data['csv_file']

            # Save CSV to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_csv:
                csv_path = temp_csv.name
                temp_csv.write(csv_file.read())

            # Generate temporary XML path
            xml_path = tempfile.mktemp(suffix='.xml')

            try:
                # Convert CSV to XML
                df = pd.read_csv(csv_path)
                root = ET.Element("Items")

                for _, row in df.iterrows():
                    item = ET.SubElement(root, "Item")
                    for col_name, value in row.items():
                        col_element = ET.SubElement(item, col_name)
                        col_element.text = str(value)

                tree = ET.ElementTree(root)
                tree.write(xml_path, encoding="utf-8", xml_declaration=True)

                # Read and return the generated XML
                with open(xml_path, 'r') as xml_file:
                    xml_content = xml_file.read()

                return Response({"message": "CSV converted to XML successfully.", "xml": xml_content},
                                status=status.HTTP_200_OK)
                # TODO: Save the xml_content 
            except Exception as e:
                return Response({"error": f"Conversion failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            finally:
                # Cleanup temporary files
                os.remove(csv_path)
                if os.path.exists(xml_path):
                    os.remove(xml_path)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
