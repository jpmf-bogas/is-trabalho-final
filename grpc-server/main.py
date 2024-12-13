from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT
from lxml import etree
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc
import pg8000
import logging
import pandas as pd
import xml.etree.ElementTree as ET


# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

#Consult the file "server_services_pb2_grpc" to find out the name of the Servicer class of the "SendFileService" service
class SendFileService(server_services_pb2_grpc.SendFileServiceServicer):
    def __init__(self, *args, **kwargs):
        pass

    def SendFile(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        file_path = os.path.join(MEDIA_PATH, request.file_name + request.file_mime)
        ficheiro_em_bytes = request.file

        with open(file_path, 'wb') as f:
            f.write(ficheiro_em_bytes)
        logger.info(f"{DBHOST}:{DBPORT}", exc_info=True)
        # Establish connection to PostgreSQL
        try:
            # Connect to the database
            conn = pg8000.connect(user=f'{DBUSERNAME}',
            password=f'{DBPASSWORD}', host=f'{DBHOST}', port=f'{DBPORT}',
            database=f'{DBNAME}')
            cursor = conn.cursor()
            # SQL query to create a table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE NOT NULL,
            age INT
            );
            """
            # Execute the SQL query to create the table
            cursor.execute(create_table_query)
            # Commit the changes (optional in this case since it's a DDL query)
            conn.commit()
            # List tables in the database
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = cursor.fetchall()
            logger.info(f"Tables in database: {tables}")

            #name defined in the proto for the response "SendFileResponseBody"
            return server_services_pb2.SendFileResponseBody(success=True)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            context.set_details(f"Failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)

class CSVtoXMLService(server_services_pb2_grpc.CSVServiceServicer):
    def ConvertCSVToXML(self, request, context):
        csv_path = request.csv_path
        xml_path = request.xml_path

        # Check if the CSV file exists
        if not os.path.exists(csv_path):
            message = f"CSV file '{csv_path}' not found."
            logger.error(message)
            return server_services_pb2.CSVToXMLResponse(success=False, message=message)

        try:
            # Read the CSV using pandas
            df = pd.read_csv(csv_path)

            # Create the root XML element
            root = ET.Element("Items")

            # Iterate over DataFrame rows and create XML elements
            for _, row in df.iterrows():
                item = ET.SubElement(root, "Item")
                for col_name, value in row.items():
                    col_element = ET.SubElement(item, col_name)
                    col_element.text = str(value)

            # Write the XML to the specified file
            tree = ET.ElementTree(root)
            tree.write(xml_path, encoding="utf-8", xml_declaration=True)

            logger.info(f"XML successfully generated at '{xml_path}'.")
            return server_services_pb2.CSVToXMLResponse(success=True, message=f"XML file created at '{xml_path}'.")
        except Exception as e:
            error_message = f"Error converting CSV to XML: {str(e)}"
            logger.error(error_message, exc_info=True)
            context.set_details(error_message)
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.CSVToXMLResponse(success=False, message=error_message)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Consult the file "server_services_pb2_grpc" to see the name of the function generated to add the service to the server
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    # server_services_pb2_grpc.add_XMLServiceServicer_to_server(XMLServiceServicer(), server)
    server_services_pb2_grpc.add_CSVServiceServicer_to_server(CSVtoXMLService(), server)


    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    print("Server running:")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()