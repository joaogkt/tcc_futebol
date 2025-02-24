from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import PlayerStats
from .forms import PlayerStatsForm
from django.contrib.auth.decorators import login_required
from players.models import Player
from .models import PlayerDesempenhoGeral
from django.db.models import Sum, Count, F
import matplotlib.pyplot as plt
import io
import urllib, base64
# Create your views here.

@login_required(login_url='login')
def player_stats_list(request):
    order = request.GET.get('order')

    valid_fields = ['jogador', 'gols', 'assistencia', 'passes_certos', 'passes_errados',
                    'desarmes', 'cartao_vermelho', 'cartao_amarelo', 'nota']

    if order not in valid_fields and order not in [f'-{field}' for field in valid_fields]:
        order = None  

    if order:
        new_order = order[1:] if order.startswith('-') else f'-{order}'
    else:
        new_order = 'jogador' 

    player_stats = PlayerStats.objects.all()
    if order:
        player_stats = player_stats.order_by(order)

    return render(request, 'player_stats_list.html', {
        'players': player_stats,
        'current_order': order,
        'new_order': new_order
    })

@login_required(login_url='login')
def player_stats_create(request):
    if request.method == "POST":
        form = PlayerStatsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('player_stats_list')
    else:
        form = PlayerStatsForm()
    return render(request, 'player_stats_form.html', {'form': form})


@login_required(login_url='login')
def player_stats_update(request, pk):
    player_stats = get_object_or_404(PlayerStats, pk=pk)

    if request.method == 'POST':
        form = PlayerStatsForm(request.POST, request.FILES, instance=player_stats)
        if form.is_valid():
            form.save()
            return redirect('player_stats_detail', pk=player_stats.pk)
    else:
        form = PlayerStatsForm(instance=player_stats)
    return render(request, 'player_stats_form.html', {'form': form})


@login_required(login_url='login')
def player_stats_detail(request, pk):
    player_stat = get_object_or_404(PlayerStats, pk=pk)
    return render(request, 'player_stats_detail.html', {'player_stat': player_stat})


@login_required(login_url='login')
def player_stats_delete(request, pk):
    player_stats = get_object_or_404(PlayerStats, pk=pk)
    if request.method == "POST":
        player_stats.delete()
        return redirect('player_stats_list')
    return render(request, 'player_stats_confirm_delete.html', {'player_stats': player_stats})

@login_required(login_url='login')
def desempenho_geral(request):
    jogadores = Player.objects.all()
    desempenho_total = []

    for jogador in jogadores:
        stats = PlayerStats.objects.filter(jogador=jogador).aggregate(
            total_gols=Sum('gols', default=0),
            total_assistencias=Sum('assistencia', default=0),
            total_passes_certos=Sum('passes_certos', default=0),
            total_passes_errados=Sum('passes_errados', default=0),
            total_desarmes=Sum('desarmes', default=0),
            total_cartoes_vermelhos=Sum('cartao_vermelho', default=0),
            total_cartoes_amarelos=Sum('cartao_amarelo', default=0),
            total_partidas=Count('id') 
        )
        total_partidas = PlayerStats.objects.filter(jogador=jogador).values('jogo').distinct().count()

        if total_partidas > 0: 
            media_nota = (
                PlayerStats.objects.filter(jogador=jogador).aggregate(Sum('nota'))['nota__sum'] or 0
            ) / max(total_partidas, 1) 

            desempenho, created = PlayerDesempenhoGeral.objects.update_or_create(
                jogador=jogador,
                defaults={
                    'total_gols': stats['total_gols'],
                    'total_assistencias': stats['total_assistencias'],
                    'total_passes_certos': stats['total_passes_certos'],
                    'total_passes_errados': stats['total_passes_errados'],
                    'total_desarmes': stats['total_desarmes'],
                    'total_cartoes_vermelhos': stats['total_cartoes_vermelhos'],
                    'total_cartoes_amarelos': stats['total_cartoes_amarelos'],
                    'media_nota': media_nota,
                    'total_partidas': total_partidas, 
                }
            )    
            desempenho_total.append(desempenho)

    return render(request, 'player_stats_total.html', {'desempenho_total': desempenho_total})


@login_required(login_url='login')
def desempenho_graficos(request):
    return render(request, 'player_stats_graficos.html')


@login_required(login_url='login')
def player_stats_detail(request, pk):
    player_stat = get_object_or_404(PlayerStats, pk=pk)
    player = Player.objects.all()

    labels = ['Gols', 'Assistências', 'Passes Certos', 'Passes Errados', 'Desarmes']
    values = [player_stat.gols, player_stat.assistencia, player_stat.passes_certos,
              player_stat.passes_errados, player_stat.desarmes]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color=['blue', 'green', 'orange', 'red', 'purple'])
    plt.ylabel("Quantidade")
    plt.title(f"Desempenho na Partida - {player_stat.jogador}")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode("utf-8")
    uri = f"data:image/png;base64,{string}"

    return render(request, 'player_stats_detail.html', {'player_stat': player_stat, 'player': player, 'chart': uri})


# @login_required(login_url='login')
# def desempenho_graficos(request):
#     jogadores = Player.objects.all()

#     nomes = []
#     gols = []
#     assistencias = []
#     notas = []

#     for jogador in jogadores:
#         stats = PlayerDesempenhoGeral.objects.filter(jogador=jogador).aggregate(
#             total_gols=Sum('total_gols', default=0),
#             total_assistencias=Sum('total_assistencias', default=0),
#             media_nota=Sum('media_nota', default=0)
#         )

#         nomes.append(f"{jogador.first_name} {jogador.last_name}")
#         gols.append(stats['total_gols'])
#         assistencias.append(stats['total_assistencias'])
#         notas.append(stats['media_nota'])

#     plt.figure(figsize=(10, 5))
#     plt.bar(nomes, gols, color='blue', label="Gols")
#     plt.bar(nomes, assistencias, color='green', bottom=gols, label="Assistências")
#     plt.xlabel("Jogadores")
#     plt.ylabel("Quantidade")
#     plt.title("Gols e Assistências por Jogador")
#     plt.xticks(rotation=45)
#     plt.legend()

#     buf = io.BytesIO()
#     plt.savefig(buf, format="png")
#     buf.seek(0)
#     string = base64.b64encode(buf.read()).decode("utf-8")
#     chart1 = f"data:image/png;base64,{string}"

#     plt.figure(figsize=(10, 5))
#     plt.bar(nomes, notas, color='purple')
#     plt.xlabel("Jogadores")
#     plt.ylabel("Nota Média")
#     plt.title("Média de Notas dos Jogadores")
#     plt.xticks(rotation=45)

#     buf = io.BytesIO()
#     plt.savefig(buf, format="png")
#     buf.seek(0)
#     string = base64.b64encode(buf.read()).decode("utf-8")
#     chart2 = f"data:image/png;base64,{string}"

#     return render(request, 'player_stats_graficos.html', {'chart1': chart1, 'chart2': chart2})

# @login_required(login_url='login')
# def desempenho_graficos(request):
#     jogadores = Player.objects.all()
#     desempenho_total = []
#     estatisticas_jogadores = {}

#     for jogador in jogadores:
#         stats = PlayerDesempenhoGeral.objects.filter(jogador=jogador)

#         estatisticas = {
#             "gols": [],
#             "assistencias": [],
#             "passes_certos": [],
#             "passes_errados": [],
#             "desarmes": [],
#             "cartoes_vermelhos": [],
#             "cartoes_amarelos": [],
#             "notas": [],
#             "partidas": [],
#         }

#         for stat in stats:
#             estatisticas["gols"].append(stat.total_gols)
#             estatisticas["assistencias"].append(stat.total_assistencias)
#             estatisticas["passes_certos"].append(stat.total_passes_certos)
#             estatisticas["passes_errados"].append(stat.total_passes_errados)
#             estatisticas["desarmes"].append(stat.total_desarmes)
#             estatisticas["cartoes_vermelhos"].append(stat.total_cartoes_vermelhos)
#             estatisticas["cartoes_amarelos"].append(stat.total_cartoes_amarelos)
#             estatisticas["notas"].append(stat.media_nota)
#             estatisticas["partidas"].append(stat.total_partidas)

#         estatisticas_jogadores[f'{jogador.first_name} {jogador.last_name}'] = estatisticas

#     return render(request, 'player_stats_graficos.html', {
#         'estatisticas_jogadores': estatisticas_jogadores
#     })


@login_required(login_url='login')
def desempenho_graficos(request):
    jogadores = Player.objects.all()
    estatisticas_jogadores = {}

    for jogador in jogadores:
        stats = PlayerDesempenhoGeral.objects.filter(jogador=jogador).first()

        if stats:
            estatisticas_jogadores[f'{jogador.first_name} {jogador.last_name}'] = {
                "gols": stats.total_gols,
                "assistencias": stats.total_assistencias,
                "passes_certos": stats.total_passes_certos,
                "passes_errados": stats.total_passes_errados,
                "desarmes": stats.total_desarmes,
                "cartoes_vermelhos": stats.total_cartoes_vermelhos,
                "cartoes_amarelos": stats.total_cartoes_amarelos,
                "notas": stats.media_nota,
                "partidas": stats.total_partidas
            }

    return render(request, 'player_stats_graficos.html', {
        'estatisticas_jogadores': estatisticas_jogadores
    })
