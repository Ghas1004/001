"""
Sistema de colisão.

Regras:
  - jogadores e NPCs não atravessam uns aos outros (separação física);
  - batida entre polícia e ladrão causa dano por diferença de velocidade;
  - batida em NPC causa dano e empurra o jogador;
  - spike / barreira / óleo / tiro mantêm suas regras próprias.
"""

from src import settings


def verificar_colisao_jogadores(policia, ladrao):
    """
    Verifica e resolve uma colisão entre polícia e ladrão, se houver.
    Retorna o tipo de colisão ("leve", "media", "forte") ou None.
    A separação física roda sempre; o dano respeita o cooldown.
    """
    if policia.destruido or ladrao.destruido:
        return None

    if not policia.rect.colliderect(ladrao.rect):
        return None

    overlap_x = min(policia.rect.right, ladrao.rect.right) - max(policia.rect.left, ladrao.rect.left)
    overlap_y = min(policia.rect.bottom, ladrao.rect.bottom) - max(policia.rect.top, ladrao.rect.top)
    batida_lateral = overlap_x < overlap_y and policia.faixa != ladrao.faixa

    _separar_carros(policia, ladrao)
    _igualar_velocidade_ao_bater(policia, ladrao)

    if policia.cooldown_colisao > 0 or ladrao.cooldown_colisao > 0:
        return None

    diferenca_velocidade = abs(policia.velocidade_atual - ladrao.velocidade_atual)

    if diferenca_velocidade < settings.LIMIAR_COLISAO_LEVE:
        tipo = "leve"
        dano = settings.DANO_COLISAO_LEVE
    elif diferenca_velocidade < settings.LIMIAR_COLISAO_MEDIA:
        tipo = "media"
        dano = settings.DANO_COLISAO_MEDIA
    else:
        tipo = "forte"
        dano = settings.DANO_COLISAO_FORTE

    # Batida de lado (troca de faixa em cima do outro) sempre causa impacto claro
    if batida_lateral:
        dano = max(dano, settings.DANO_COLISAO_LATERAL)
        if dano >= settings.DANO_COLISAO_FORTE:
            tipo = "forte"
        elif dano >= settings.DANO_COLISAO_MEDIA:
            tipo = "media"

    policia.aplicar_dano(dano)
    ladrao.aplicar_dano(dano)

    policia.cooldown_colisao = settings.COOLDOWN_COLISAO
    ladrao.cooldown_colisao = settings.COOLDOWN_COLISAO

    return tipo


def verificar_colisao_trafego(jogador, trafego):
    """
    Colisão do jogador com cada NPC. Impede atravessar e aplica dano.
    Retorna o tipo textual da última batida com dano, ou None.
    """
    if jogador.destruido:
        return None

    tipo_msg = None
    for npc in trafego:
        if not jogador.rect.colliderect(npc.rect):
            continue

        _separar_jogador_e_npc(jogador, npc)

        if jogador.cooldown_colisao > 0:
            continue

        impacto = abs(jogador.velocidade_atual - settings.VELOCIDADE_REFERENCIA)
        dano = int(settings.DANO_COLISAO_TRAFEGO_BASE + impacto * settings.DANO_COLISAO_TRAFEGO_POR_IMPACTO)
        dano = max(settings.DANO_COLISAO_LEVE, min(settings.DANO_COLISAO_FORTE, dano))

        jogador.aplicar_dano(dano)
        jogador.velocidade_atual = max(0.0, jogador.velocidade_atual - impacto * 0.35)
        jogador.cooldown_colisao = settings.COOLDOWN_COLISAO_TRAFEGO

        if dano >= settings.DANO_COLISAO_FORTE:
            tipo_msg = "forte"
        elif dano >= settings.DANO_COLISAO_MEDIA:
            tipo_msg = "media"
        else:
            tipo_msg = "leve"

    return tipo_msg


def _eixo_de_separacao(a_rect, b_rect, mesma_faixa):
    """Na mesma faixa prioriza Y (batida traseira); senão usa o menor overlap."""
    overlap_x = min(a_rect.right, b_rect.right) - max(a_rect.left, b_rect.left)
    overlap_y = min(a_rect.bottom, b_rect.bottom) - max(a_rect.top, b_rect.top)
    if overlap_x <= 0 or overlap_y <= 0:
        return 0, 0, None
    if mesma_faixa or overlap_y <= overlap_x:
        return overlap_x, overlap_y, "y"
    return overlap_x, overlap_y, "x"


def _separar_carros(a, b):
    """Afasta dois carros de jogador para não ficarem sobrepostos."""
    mesma_faixa = a.faixa == b.faixa
    overlap_x, overlap_y, eixo = _eixo_de_separacao(a.rect, b.rect, mesma_faixa)
    if eixo is None:
        return

    folga = settings.FOLGA_COLISAO

    if eixo == "y":
        deslocamento = (overlap_y / 2) + folga
        if a.y <= b.y:
            a.y = max(settings.Y_MIN, a.y - deslocamento)
            b.y = min(settings.Y_MAX, b.y + deslocamento)
        else:
            a.y = min(settings.Y_MAX, a.y + deslocamento)
            b.y = max(settings.Y_MIN, b.y - deslocamento)
    else:
        deslocamento = (overlap_x / 2) + folga
        if a.x <= b.x:
            a.x -= deslocamento
            b.x += deslocamento
        else:
            a.x += deslocamento
            b.x -= deslocamento
        a.cancelar_troca_faixa()
        b.cancelar_troca_faixa()

    a.rect.center = (int(a.x), int(a.y))
    b.rect.center = (int(b.x), int(b.y))


def _separar_jogador_e_npc(jogador, npc):
    """Impede o jogador de atravessar um NPC."""
    mesma_faixa = jogador.faixa == npc.faixa
    overlap_x, overlap_y, eixo = _eixo_de_separacao(jogador.rect, npc.rect, mesma_faixa)
    if eixo is None:
        return

    folga = settings.FOLGA_COLISAO

    if eixo == "y":
        minimo = (jogador.rect.height + npc.rect.height) / 2 + folga
        if jogador.y < npc.y or (jogador.y == npc.y and jogador.velocidade_atual >= settings.VELOCIDADE_REFERENCIA):
            # Jogador na frente / empurrando o NPC para baixo
            npc.y = jogador.y + minimo
        else:
            # Jogador atrás: fica colado na traseira, sem furar
            jogador.y = min(settings.Y_MAX, npc.y + minimo)
            if jogador.velocidade_atual > settings.VELOCIDADE_REFERENCIA:
                jogador.velocidade_atual = settings.VELOCIDADE_REFERENCIA
    else:
        deslocamento = overlap_x + folga
        if jogador.x <= npc.x:
            jogador.x -= deslocamento
        else:
            jogador.x += deslocamento
        jogador.cancelar_troca_faixa()

    jogador.rect.center = (int(jogador.x), int(jogador.y))
    npc.rect.center = (int(npc.x), int(npc.y))

    # Garante 0 overlap mesmo com arredondamento do rect
    if jogador.rect.colliderect(npc.rect):
        if eixo == "y":
            if jogador.y <= npc.y:
                npc.y = jogador.y + (jogador.rect.height + npc.rect.height) / 2 + folga + 1
            else:
                jogador.y = min(
                    settings.Y_MAX,
                    npc.y + (jogador.rect.height + npc.rect.height) / 2 + folga + 1,
                )
            jogador.rect.center = (int(jogador.x), int(jogador.y))
            npc.rect.center = (int(npc.x), int(npc.y))
        else:
            if jogador.x <= npc.x:
                jogador.x -= folga + 1
            else:
                jogador.x += folga + 1
            jogador.rect.center = (int(jogador.x), int(jogador.y))


def _igualar_velocidade_ao_bater(a, b):
    """Quem vem por trás mais rápido é freado até a velocidade do da frente."""
    if a.y < b.y:
        frente, tras = a, b
    else:
        frente, tras = b, a

    if tras.velocidade_atual > frente.velocidade_atual:
        tras.velocidade_atual = frente.velocidade_atual


def verificar_colisao_spike(carro, spike):
    """
    Etapa 7: se o carro passar por cima da faixa de pregos, ela é
    consumida (só funciona uma vez) e o carro fica com o pneu furado.
    """
    if spike is None or spike.usada or carro.destruido:
        return False

    if carro.rect.colliderect(spike.rect):
        spike.usada = True
        carro.aplicar_pneu_furado()
        return True

    return False


def verificar_colisao_barreira(carro, barreira):
    """
    Etapa 8: bater na barreira causa dano, zera a velocidade e empurra
    o carro para trás. A barreira continua no lugar -- se o carro não
    trocar de faixa, pode bater de novo depois que o cooldown passar.
    """
    if barreira is None or carro.destruido:
        return False

    if carro.cooldown_colisao > 0:
        return False

    if not carro.rect.colliderect(barreira.rect):
        return False

    carro.aplicar_dano(settings.DANO_BARREIRA)
    carro.velocidade_atual = 0
    carro.cooldown_colisao = settings.COOLDOWN_COLISAO
    carro.y = min(settings.Y_MAX, carro.y + settings.EMPURRAO_BARREIRA)
    carro.rect.center = (int(carro.x), int(carro.y))

    return True


def verificar_colisao_oleo(carro, oleo):
    """Etapa 9: óleo causa derrapagem temporária na polícia (uso único)."""
    if oleo is None or oleo.usada or carro.destruido:
        return False

    if carro.rect.colliderect(oleo.rect):
        oleo.usada = True
        carro.aplicar_derrapagem()
        return True

    return False


def verificar_colisao_projetil(carro, projetil):
    """Etapa 9: tiro traseiro causa dano direto ao acertar a polícia."""
    if projetil is None or projetil.atingiu or carro.destruido:
        return False

    if carro.rect.colliderect(projetil.rect):
        projetil.atingiu = True
        carro.aplicar_dano(settings.DANO_TIRO)
        return True

    return False
