"""
Dados de todas as cenas do jogo -- portas, itens, mensagens, setas de
navegação, etc. Isso substitui o antigo data/scenes.json: mesma estrutura
de informação, só que como dict Python puro, sem depender de arquivo
externo nem do módulo json.

Para adicionar uma cena nova: copie o formato de uma cena existente
dentro do dicionário SCENES abaixo.

Tipos de hotspot disponíveis (campo "type"):
- "navigate":      muda para outra cena (campo "target")
- "examine":       igual "navigate", usado semanticamente pra close-up
- "pickup":        adiciona um item ao inventário (campo "item")
- "message":       só mostra um texto, não muda de cena (campo "message")
- "image":         abre a imagem em close-up na tela (campo "image"); ao clicar
                   na imagem aparece o texto do campo "image_message".
                   Clicar fora da imagem (ou apertar ESC) fecha o close-up.
- "sequence_item": peça de um puzzle de ordem (ex: um frasco). Usa "puzzle_id"
                   (opcional, cai no "id" do puzzle da cena) e "value" (o
                   identificador dessa peça dentro da sequência esperada).
                   Ver campo "puzzle" da cena, mais abaixo.
- "climax_door":   porta final do jogo (a porta principal barrada do hall).
                   Ao ser clicada já com o item exigido (ver "requires_item"),
                   dispara o jumpscare da diretora seguido do minigame de
                   digitar letras/números aleatórios (ver GameManager em
                   game.py: start_ending_sequence / handle_key_press).
- "win":           termina o jogo com vitória

Campos opcionais:
- "requires_item":   só ativa o hotspot se o item estiver no inventário
- "requires_puzzle": só ativa o hotspot se o puzzle indicado já tiver sido
                     resolvido (mesmo "id" do campo "puzzle" da cena)
- "locked_message":  mensagem mostrada se faltar o item/puzzle acima
- "once":            True para o hotspot "sumir" depois de usado (ex: pickup)
- "arrow":           "left" ou "right" -- desenha uma seta triangular clicável
                     no lugar do rect, sem precisar de imagem própria

Campo opcional da CENA:
- "puzzle": define um puzzle de sequência (clicar hotspots "sequence_item" na
  ordem certa). Formato:
    {
        "id": "identificador_do_puzzle",
        "sequence": ["valor1", "valor2", "valor3", ...],
        "progress_message": "mostrado a cada acerto parcial",
        "wrong_message": "mostrado quando erra a ordem (reseta o progresso)",
        "solved_message": "mostrado quando completa a sequência certa",
    }
"""

SCENES = {
    "hall_entrada": {
        "background": "assets/scenes/hall_entrada.png",
        "hotspots": [
            {
                "id": "cadeado",
                "rect": [755, 385, 90, 90],
                "type": "message",
                "message": "Um cadeado enferrujado com corrente. Precisa de uma chave ou algo pra arrombar.",
                "label": "Cadeado",
            },
            {
                "id": "quadro_avisos",
                "rect": [375, 320, 145, 185],
                "type": "image",
                "image": "assets/items/carta.png",
                "image_message": (
                    "Mãe,\n"
                    "Você disse que hoje chegaria cedo.\n"
                    "Eu esperei.\n"
                    "A casa ficou em silêncio, e o relógio continuou andando.\n"
                    "De novo, você ficou na escola depois que todos foram embora.\n"
                    "Eu sei que você precisa trabalhar. Sei que quer fazer tudo direito.\n"
                    "Mas quando você fica lá até tarde, parece que esquece que existe uma casa esperando por você.\n"
                    "Ontem, ouvi seus passos no corredor.\n"
                    "Achei que tinha chegado.\n"
                    "Levantei da cama e fui até a porta.\n"
                    "Mas você não estava aqui.\n"
                    "Os passos continuaram mesmo assim.\n"
                    "Mãe... por favor.\n"
                    "Pare de fazer hora extra.\n"
                    "Volte para casa antes de escurecer.\n"
                    "Jante com a gente. Sente no sofá. Pergunte como foi o nosso dia.\n"
                    "Só fique com a família.\n"
                    "Porque ontem, quando eu estava esperando você voltar, alguém bateu na janela do meu quarto.\n"
                    "Três vezes.\n"
                    "Toc. Toc. Toc.\n"
                    "Eu não abri.\n"
                    "Então ouvi sua voz do outro lado:\n"
                    "\"Filha... abre. Sou eu.\"\n"
                    "Eu fiquei quieta.\n"
                    "Porque, naquele mesmo instante, ouvi a chave girando na porta da nossa casa.\n"
                    "Você tinha acabado de chegar.\n"
                    "Quando desci as escadas, você estava lá.\n"
                    "Parada na sala.\n"
                    "Me olhando.\n"
                    "E então...\n"
                    "alguém bateu novamente na janela do meu quarto.\n"
                    "Três vezes.\n"
                    "Toc. Toc. Toc.\n"
                    "Mãe...\n"
                    "Se você está lendo esta carta...\n"
                    "não olhe para a janela.\n"
                    "Porque eu acabei de ouvir sua voz lá fora.\n"
                    "E ela está dizendo:\n"
                    "\"Filha... você ainda está acordada?\""
                ),
                "label": "Quadro de avisos",
            },
            {
                "id": "estante_livros",
                "rect": [1040, 355, 195, 350],
                "type": "message",
                "message": "Uma estante empoeirada, cheia de livros velhos. Não parece se mover.",
                "label": "Estante de livros",
            },
            {
                "id": "esqueleto",
                "rect": [1140, 555, 195, 190],
                "type": "message",
                "message": "Um esqueleto caído há muito tempo. Não parece ter nada de útil com ele.",
                "label": "Esqueleto",
            },
            {
                "id": "escrivaninha",
                "rect": [800, 545, 155, 160],
                "type": "pickup",
                "item": "lanterna (sem pilhas)",
                "message": "Você pegou uma lanterna. Está sem pilhas -- precisa achar pilhas em algum lugar.",
                "once": True,
                "label": "Escrivaninha quebrada",
            },
            {
                "id": "cadeira",
                "rect": [400, 500, 165, 225],
                "type": "message",
                "message": "Uma cadeira velha de madeira, quebrada.",
                "label": "Cadeira",
            },
            {
                "id": "armario_esquerdo",
                "rect": [0, 330, 150, 295],
                "type": "message",
                "message": "Armários enferrujados. Todos trancados, exceto por danos.",
                "label": "Armários",
            },
            {
                "id": "armario_direito",
                "rect": [1450, 300, 150, 355],
                "type": "message",
                "message": "Mais armários, cobertos de teias de aranha.",
                "label": "Armários",
            },
            {
                "id": "seta_corredor",
                "rect": [1490, 790, 90, 80],
                "type": "navigate",
                "target": "corredor_hospital",
                "arrow": "right",
                "label": "Ir para o corredor",
            },
            {
                "id": "porta_trancada",
                "rect": [520, 100, 560, 600],
                "type": "climax_door",
                "requires_item": "chave da saída",
                "locked_message": "A porta está barrada com tábuas e presa por um cadeado. Você precisa de uma chave que abra esse cadeado.",
                "label": "Porta principal",
            },
        ],
    },

    "corredor_hospital": {
        "background": "assets/scenes/corredor_hospital.png",
        "hotspots": [
            {
                "id": "seta_voltar_hall",
                "rect": [20, 790, 90, 80],
                "type": "navigate",
                "target": "hall_entrada",
                "arrow": "left",
                "label": "Voltar ao hall",
            },
            # --- PORTA QUE ABRE (1 de 2): leva para a sala 3.1 ---
            {
                "id": "porta_esq_1",
                "rect": [232, 260, 72, 342],
                "type": "navigate",
                "target": "sala_3_1",
                "door_light": True,
                "label": "Porta entreaberta",
            },
            {
                "id": "porta_esq_2",
                "rect": [375, 285, 83, 160],
                "type": "message",
                "message": "Trancada e sem nenhuma fresta de luz. Não vai abrir.",
                "label": "Porta (esquerda)",
            },
            {
                "id": "porta_esq_3",
                "rect": [479, 299, 69, 132],
                "type": "message",
                "message": "Emperrada, escura por baixo. Não consegue abrir.",
                "label": "Porta (esquerda, fundo)",
            },
            # --- PORTA QUE ABRE (2 de 2): leva para a sala 3.2 (sala de química) ---
            {
                "id": "porta_dir_1",
                "rect": [1266, 298, 64, 314],
                "type": "navigate",
                "target": "sala_3_2",
                "door_light": True,
                "requires_item": "chave dourada",
                "locked_message": "A porta está trancada. A fechadura é antiga -- precisa de uma chave.",
                "label": "Porta trancada",
            },
            {
                "id": "porta_dir_2",
                "rect": [1146, 285, 83, 160],
                "type": "message",
                "message": "Trancada e sem nenhuma fresta de luz. Não vai abrir.",
                "label": "Porta (direita)",
            },
            {
                "id": "porta_dir_3",
                "rect": [1049, 299, 83, 132],
                "type": "message",
                "message": "Emperrada, escura por baixo. Não consegue abrir.",
                "label": "Porta (direita, fundo)",
            },
            {
                "id": "porta_placa",
                "rect": [1385, 248, 140, 372],
                "type": "message",
                "message": "Uma porta com uma placa antiga pendurada. Ilegível pela sujeira.",
                "label": "Porta com placa",
            },
            {
                "id": "porta_fundo",
                "rect": [757, 319, 83, 139],
                "type": "navigate",
                "target": "sala_diretora",
                "door_light": True,
                "requires_item": "chave da diretoria",
                "locked_message": "A porta no final do corredor está trancada com uma fechadura pequena e antiga. Precisa de uma chave.",
                "label": "Porta da diretoria",
            },
            {
                "id": "esqueleto_esq",
                "rect": [104, 514, 215, 181],
                "type": "message",
                "message": "Mais um esqueleto largado no chão. Nada de útil aqui.",
                "label": "Esqueleto",
            },
            {
                "id": "esqueleto_dir",
                "rect": [1389, 514, 208, 181],
                "type": "message",
                "message": "Outro esqueleto, encolhido perto da parede.",
                "label": "Esqueleto",
            },
        ],
    },

    # =====================================================================
    # CENA 3.1 -- SALA DE MATEMÁTICA (atrás da porta da ESQUERDA do corredor).
    # É aqui que fica a CHAVE que destranca a porta da direita (cena 3.2).
    # Rects calibrados sobre assets/scenes/sala_3_1.png (1600x900).
    # =====================================================================
    "sala_3_1": {
        "background": "assets/scenes/sala_3_1.png",
        "hotspots": [
            {
                "id": "chave_mesa",
                "rect": [698, 710, 124, 72],
                "type": "pickup",
                "item": "chave dourada",
                "message": "Você pegou a chave dourada. Alguém a deixou bem no meio da mesa, como se quisesse que fosse encontrada.",
                "once": True,
                "label": "Chave dourada",
            },
            {
                "id": "livro_1",
                "rect": [406, 600, 136, 104],
                "type": "message",
                "message": "Livro 1: contas de somar, com a letra de uma criança. Nada entre as páginas.",
                "label": "Livro 1",
            },
            {
                "id": "livro_2",
                "rect": [542, 600, 136, 104],
                "type": "message",
                "message": "Livro 2: as páginas estão coladas por mofo. Não abre.",
                "label": "Livro 2",
            },
            {
                "id": "livro_3",
                "rect": [678, 600, 132, 104],
                "type": "message",
                "message": "Livro 3: alguém riscou todos os números do capítulo com força, rasgando o papel.",
                "label": "Livro 3",
            },
            {
                "id": "livro_4",
                "rect": [810, 600, 126, 104],
                "type": "message",
                "message": "Livro 4: no fim do livro, a mesma frase repetida página após página: \"não conte em voz alta\".",
                "label": "Livro 4",
            },
            {
                "id": "livro_5",
                "rect": [936, 600, 122, 104],
                "type": "message",
                "message": "Livro 5: dobrando o 2 cinco vezes chega-se a 32. Alguém escreveu 32 na contracapa e circulou várias vezes.",
                "label": "Livro 5",
            },
            {
                "id": "papel_rasgado",
                "rect": [1052, 600, 178, 156],
                "type": "message",
                "message": "Uma folha de prova. A única questão respondida diz: \"o número que falta abre o que está preso lá embaixo\".",
                "label": "Folha de prova",
            },
            {
                "id": "quadro_negro",
                "rect": [450, 160, 766, 312],
                "type": "message",
                "message": "2, 4, 8, 16... cada número é o dobro do anterior. O último quadrado ficou em branco.",
                "label": "Quadro-negro",
            },
            {
                "id": "espaco_vazio",
                "rect": [1038, 262, 104, 106],
                "type": "message",
                "message": "O quadrado em branco no fim da sequência. Depois de 16 viria 32.",
                "label": "Quadrado em branco",
            },
            {
                "id": "armario_aberto",
                "rect": [152, 178, 72, 424],
                "type": "pickup",
                "item": "pilhas",
                "message": "No fundo do armário aberto havia duas pilhas. Parecem ainda ter carga.",
                "once": True,
                "label": "Armário aberto",
            },
            {
                "id": "armarios_fechados",
                "rect": [0, 170, 150, 440],
                "type": "message",
                "message": "Armários de aluno, amassados e trancados. Nenhum cede.",
                "label": "Armários",
            },
            {
                "id": "mesa_professor",
                "rect": [300, 800, 1050, 100],
                "type": "message",
                "message": "A mesa do professor. As gavetas estão emperradas, cheias de giz quebrado.",
                "label": "Mesa do professor",
            },
            {
                "id": "porta_saida_sala1",
                "rect": [1415, 155, 136, 448],
                "type": "navigate",
                "target": "corredor_hospital",
                "door_light": True,
                "label": "Porta para o corredor",
            },
            {
                "id": "seta_voltar_corredor_esq",
                "rect": [20, 790, 90, 80],
                "type": "navigate",
                "target": "corredor_hospital",
                "arrow": "left",
                "label": "Voltar ao corredor",
            },
        ],
    },

    # =====================================================================
    # CENA 3.2 -- SALA DE QUÍMICA (atrás da porta da DIREITA do corredor,
    # destrancada com a "chave dourada" da sala 3.1).
    #
    # Puzzle: 4 frascos com símbolos (triângulo, hexágono, círculo, quadrado)
    # ficam na bancada central. Um bilhete ao lado mostra a ordem certa de
    # clicar nos frascos. Acertando a sequência, uma chave aparece dentro
    # do béquer vazio no meio da bancada -- essa é a "chave da diretoria".
    # Ela NÃO abre nenhuma porta desta sala: é preciso voltar ao corredor
    # e usá-la na última porta do fundo (ver "porta_fundo" em
    # corredor_hospital), que leva à cena "sala_diretora".
    #
    # Rects são uma primeira estimativa sobre a arte enviada (1600x900) --
    # ligue o modo debug (tecla D) no jogo pra ver os contornos e ajustar
    # os números caso alguma área não bata direito com o desenho.
    # =====================================================================
    "sala_3_2": {
        "background": "assets/scenes/sala_3_2.jpeg",
        "puzzle": {
            "id": "quimica_frascos",
            "sequence": ["quadrado", "circulo", "triangulo", "hexagono"],
            "progress_message": "O líquido borbulha suavemente e muda de cor. Até agora, certo...",
            "wrong_message": "O frasco borbulha com força e depois some o brilho -- ordem errada. Comece de novo.",
            "solved_message": "Os quatro frascos reagem em cadeia e uma luz surge dentro do béquer vazio ao lado.",
        },
        "hotspots": [
            {
                "id": "seta_voltar_corredor_dir",
                "rect": [20, 790, 90, 80],
                "type": "navigate",
                "target": "corredor_hospital",
                "arrow": "left",
                "label": "Voltar ao corredor",
            },
            {
                "id": "armario_reagentes",
                "rect": [120, 145, 340, 300],
                "type": "message",
                "message": "Um armário de vidro cheio de frascos de reagentes empoeirados. A maioria dos rótulos apagou com o tempo.",
                "label": "Armário de reagentes",
            },
            {
                "id": "pia_esquerda",
                "rect": [0, 355, 165, 130],
                "type": "message",
                "message": "Uma pia velha de laboratório, a torneira pinga sem parar.",
                "label": "Pia",
            },
            {
                "id": "quadro_quimica",
                "rect": [540, 150, 590, 205],
                "type": "message",
                "message": "Um átomo, um frasco erlenmeyer e uma molécula desenhados no quadro-negro. Restos de uma aula que nunca terminou.",
                "label": "Quadro-negro",
            },
            {
                "id": "porta_lateral_trancada",
                "rect": [1170, 150, 165, 355],
                "type": "message",
                "message": "Uma porta secundária, trancada por fora com ferrolhos enferrujados. Não parece ser usada há anos.",
                "label": "Porta trancada",
            },
            {
                "id": "quadro_plantas",
                "rect": [1430, 150, 170, 200],
                "type": "message",
                "message": "Um pôster velho de plantas, manchado de umidade. Quase irreconhecível.",
                "label": "Pôster de plantas",
            },
            {
                "id": "pia_direita",
                "rect": [850, 360, 160, 130],
                "type": "message",
                "message": "Outra pia de laboratório, com vidrarias empilhadas do lado.",
                "label": "Pia",
            },
            {
                "id": "tubos_ensaio",
                "rect": [1330, 540, 165, 160],
                "type": "message",
                "message": "Um suporte com tubos de ensaio, todos com um líquido avermelhado dentro. Parece sangue, mas deve ser só corante.",
                "label": "Tubos de ensaio",
            },
            {
                "id": "suporte_vazio",
                "rect": [230, 545, 200, 215],
                "type": "message",
                "message": "Um suporte de metal vazio, feito pra segurar tubos de ensaio. Não há nada nele agora.",
                "label": "Suporte vazio",
            },
            {
                "id": "bilhete_formulas",
                "rect": [1060, 640, 300, 170],
                "type": "message",
                "message": "Um bilhete com símbolos desenhados em ordem: quadrado, círculo, triângulo, hexágono. Deve ser a ordem certa de mexer nos frascos ao lado.",
                "label": "Bilhete com símbolos",
            },
            {
                "id": "bequer_chave",
                "rect": [635, 700, 155, 80],
                "type": "pickup",
                "item": "chave da diretoria",
                "message": "Uma pequena chave dourada surge brilhando no fundo do béquer vazio, como se tivesse se formado ali. Você a pega.",
                "once": True,
                "requires_puzzle": "quimica_frascos",
                "locked_message": "Só um béquer vazio na bancada. Os frascos ao lado devem servir pra alguma coisa.",
                "label": "Béquer",
            },
            {
                "id": "frasco_triangulo",
                "rect": [455, 458, 153, 242],
                "type": "sequence_item",
                "value": "triangulo",
                "label": "Frasco verde (triângulo)",
            },
            {
                "id": "frasco_hexagono",
                "rect": [608, 458, 150, 240],
                "type": "sequence_item",
                "value": "hexagono",
                "label": "Frasco azul (hexágono)",
            },
            {
                "id": "frasco_circulo",
                "rect": [758, 458, 114, 242],
                "type": "sequence_item",
                "value": "circulo",
                "label": "Frasco vermelho (círculo)",
            },
            {
                "id": "frasco_quadrado",
                "rect": [888, 458, 127, 242],
                "type": "sequence_item",
                "value": "quadrado",
                "label": "Frasco amarelo (quadrado)",
            },
        ],
    },

    # =====================================================================
    # SALA DA DIRETORIA -- acessada pela ÚLTIMA porta do corredor
    # ("porta_fundo" em corredor_hospital), destrancada pela "chave da
    # diretoria" encontrada na sala de química (cena 3.2).
    #
    # Aqui tem uma segunda chave, em cima da mesa ("chave da saída"). É ela
    # que abre a porta principal barrada do hall de entrada (cena 1) --
    # abrir essa porta dispara o jumpscare final e o minigame de escape.
    # =====================================================================
    "sala_diretora": {
        "background": "assets/scenes/sala_diretora.jpeg",
        "hotspots": [
            {
                "id": "seta_voltar_corredor",
                "rect": [20, 790, 90, 80],
                "type": "navigate",
                "target": "corredor_hospital",
                "arrow": "left",
                "label": "Voltar ao corredor",
            },
            {
                "id": "chave_mesa_diretora",
                "rect": [508, 640, 100, 50],
                "type": "pickup",
                "item": "chave da saída",
                "message": "Uma chave pequena e enferrujada, esquecida em cima da mesa. Talvez seja a última que falta.",
                "once": True,
                "label": "Chave na mesa",
            },
            {
                "id": "abajur_mesa",
                "rect": [40, 440, 200, 200],
                "type": "message",
                "message": "Um abajur antigo, ainda aceso. É a única luz de verdade que você viu essa noite.",
                "label": "Abajur",
            },
            {
                "id": "mesa_diretora",
                "rect": [0, 560, 780, 300],
                "type": "message",
                "message": "A mesa da diretora. Papéis velhos e mofados cobrem quase tudo, exceto o espaço em volta do abajur.",
                "label": "Mesa",
            },
            {
                "id": "armario_gavetas",
                "rect": [125, 195, 220, 400],
                "type": "message",
                "message": "Um armário de gavetas enferrujado. Todas emperradas, exceto a poeira que se acumulou em cima.",
                "label": "Armário de gavetas",
            },
            {
                "id": "quadro_parede",
                "rect": [365, 150, 135, 155],
                "type": "message",
                "message": "Um quadro na parede, tomado pelo mofo. Não dá pra ver o que era a imagem original.",
                "label": "Quadro",
            },
            {
                "id": "janela_luar",
                "rect": [660, 60, 260, 340],
                "type": "message",
                "message": "A janela dá pra fora, com a lua cheia iluminando o pátio. Está emperrada -- não vai abrir.",
                "label": "Janela",
            },
            {
                "id": "armario_vidro",
                "rect": [1140, 80, 220, 380],
                "type": "message",
                "message": "Um armário de vidro com as portas quebradas. Restam só alguns livros empoeirados dentro.",
                "label": "Armário de vidro",
            },
            {
                "id": "mesa_lateral_livros",
                "rect": [1295, 390, 220, 220],
                "type": "message",
                "message": "Uma pilha de livros e pastas em cima de um móvel baixo, todos úmidos e colados entre si.",
                "label": "Pilha de livros",
            },
        ],
    },
}
