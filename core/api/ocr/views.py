from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiResponse, extend_schema

from core.models.propiedades_residentes import Vehiculo, Visita
from core.utils.plate_ocr import PlateOCRException, PlateOCRService

from .serializers import (
    PlateImageUploadSerializer,
    VehiculoOCRSerializer,
    VisitaOCRSerializer,
)


class PlateOCRView(APIView):
    """Detecta placas bolivianas a partir de una imagen y devuelve el match correspondiente."""

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=PlateImageUploadSerializer,
        responses={
            200: OpenApiResponse(description="Placa detectada y asociada a un vehículo o visita."),
            404: OpenApiResponse(description="No se detectó una placa registrada en el sistema."),
        },
        summary="Detectar placa desde imagen",
        description=(
            "Recepciona una imagen, ejecuta OCR para reconocer placas bolivianas y retorna "
            "información del vehículo registrado o de la visita autorizada asociada."
        ),
    )
    def post(self, request, *args, **kwargs):
        serializer = PlateImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_file = serializer.validated_data["image"]
        image_bytes = image_file.read()
        image_file.seek(0)

        try:
            candidates, raw_text = PlateOCRService.extract_plate_candidates(image_bytes)
        except PlateOCRException as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not candidates:
            return Response(
                {
                    "status": "not_found",
                    "plate": None,
                    "candidates": [],
                    "raw_text": raw_text,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        vehicle_match = None
        vehicle_plate = None
        for candidate in candidates:
            vehicle = (
                Vehiculo.objects.select_related("propietario")
                .filter(placa__iexact=candidate)
                .first()
            )
            if vehicle:
                vehicle_match = vehicle
                vehicle_plate = candidate
                break

        if vehicle_match:
            return Response(
                {
                    "status": "vehicle_match",
                    "plate": vehicle_plate,
                    "candidates": candidates,
                    "raw_text": raw_text,
                    "vehicle": VehiculoOCRSerializer(vehicle_match).data,
                },
                status=status.HTTP_200_OK,
            )

        visit_match = None
        visit_plate = None
        for candidate in candidates:
            visit = (
                Visita.objects.select_related("persona_autorizante")
                .filter(vehiculo_placa__iexact=candidate)
                .first()
            )
            if visit:
                visit_match = visit
                visit_plate = candidate
                break

        if visit_match:
            return Response(
                {
                    "status": "visit_match",
                    "plate": visit_plate,
                    "candidates": candidates,
                    "raw_text": raw_text,
                    "visit": VisitaOCRSerializer(visit_match).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "not_found",
                "plate": candidates[0] if candidates else None,
                "candidates": candidates,
                "raw_text": raw_text,
            },
            status=status.HTTP_404_NOT_FOUND,
        )