from django.shortcuts import render
from .mongodb_services import MongoDBService
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import TokenAuthentication

class LearningPathView(APIView):


    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mongo_service = MongoDBService()
        self.collection_name = 'learning_paths'

    def post(self, request):
        """Create a new learning path or multiple learning paths."""
        data = request.data
        if isinstance(data, list):  # Insert multiple documents
            try:
                inserted_ids = self.mongo_service.insert_many(self.collection_name, data)
                return Response({"message": "Data saved successfully!", "inserted_ids": [str(i) for i in inserted_ids]},
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif isinstance(data, dict):  # Insert a single document
            try:
                inserted_id = self.mongo_service.insert_one(self.collection_name, data)
                return Response({"message": "Data saved successfully!", "inserted_id": str(inserted_id)},
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "Invalid data format."}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """Retrieve all learning paths or a single learning path by ID."""
        if pk:
            try:
                document = self.mongo_service.find_by_id(self.collection_name, pk)
                if document:
                    document["_id"] = str(document["_id"])
                    return Response(document, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Learning path not found."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            try:
                documents = self.mongo_service.find_all(self.collection_name)
                for doc in documents:
                    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
                return Response(documents, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Update a learning path by ID."""
        try:
            update_data = request.data
            modified_count = self.mongo_service.update_one(self.collection_name, pk, update_data)
            if modified_count:
                return Response({"message": "Learning path updated successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No document found with the given ID."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete a learning path by ID."""
        try:
            deleted_count = self.mongo_service.delete_one(self.collection_name, pk)
            if deleted_count:
                return Response({"message": "Learning path deleted successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No document found with the given ID."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

