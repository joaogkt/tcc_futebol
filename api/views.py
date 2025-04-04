from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import PlayerDesempenhoGeralSerializer, PlayerSerializer, TeamSerializer, MatchesSerializer, PlayerStatsSerializer
from player_stats.models import PlayerDesempenhoGeral, PlayerStats
from players.models import Player
from drf_yasg.utils import swagger_auto_schema
from teams.models import Team
from matches.models import Matches
# Create your views here.


@swagger_auto_schema(
    method='get',
    operation_description="Obtém todas as estatísticas de desempenho dos jogadores.",
    responses={200: PlayerDesempenhoGeralSerializer(many=True)},
)
@api_view(['GET'])
def api_player_stats_total(request):
    desempenhos = PlayerDesempenhoGeral.objects.all()
    serializer = PlayerDesempenhoGeralSerializer(desempenhos, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    operation_description="Obtém todos os jogadores cadastrados.",
    responses={200: PlayerSerializer(many=True)},
)
@api_view(["GET"])
def api_players(request):
    jogadores = Player.objects.all()
    serializer = PlayerSerializer(jogadores, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description="Obtém todos os times cadastrados.",
    responses={200: TeamSerializer(many=True)},
)
@api_view(["GET"])
def api_teams(request):
    teams = Team.objects.all()
    serializer = TeamSerializer(teams, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description="Obtém todas as partidas cadastradas.",
    responses={200: MatchesSerializer(many=True)},
)
@api_view(["GET"])
def api_matches(request):
    matches = Matches.objects.all()
    serializer = MatchesSerializer(matches, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    operation_description="Obtém estatisticas por partida cadastrada.",
    responses={200: PlayerStatsSerializer(many=True)},
)
@api_view(["GET"])
def api_player_stats(request):
    player_stats = PlayerStats.objects.all()
    serializer = PlayerStatsSerializer(player_stats, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description="Obtém estatísticas de desempenho de um jogador específico pelo ID.",
    responses={200: PlayerDesempenhoGeralSerializer, 404: 'Desempenho geral não encontrado.'},
)
@api_view(['GET'])
def api_player_stats_by_id(request, pk):
    try:
        desempenho = PlayerDesempenhoGeral.objects.get(pk=pk)
    except PlayerDesempenhoGeral.DoesNotExist:
        return Response({'detail': 'Desempenho geral não encontrado.'}, status=404)

    serializer = PlayerDesempenhoGeralSerializer(desempenho)
    return Response(serializer.data)