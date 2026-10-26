# game.py
import random
import time
import sys
import json
import os

# ==========================
# Configurações e constantes
# ==========================
ARQUIVO_SAVE = "save.json"
CUSTO_POCAO = 50
CURA_POCAO = 350
DELAY_TEXTO = 0.02
OURO_INICIAL = 100
VIDA_BASE = 3000
VIDA_POR_LEVEL = 500
XP_POR_LEVEL = 100
BONUS_ATAQUE_POR_LEVEL = 40
BONUS_DEFESA_POR_LEVEL = 30
CHANCE_MERCADOR = 0.5

# ==========================
# Utilitários
# ==========================
def slow(text: str, delay: float = DELAY_TEXTO) -> None:
    """Exibe texto com efeito de digitação lenta."""
    for c in text:
        print(c, end="", flush=True)
        time.sleep(delay)
    print()

def limpar_tela() -> None:
    """Limpa a tela do terminal de forma portátil."""
    os.system("cls" if os.name == "nt" else "clear")

def vida_maxima(jogador: dict) -> int:
    """Vida máxima baseada no nível atual."""
    return VIDA_BASE + VIDA_POR_LEVEL * (jogador["level"] - 1)

def entrada_opcao(prompt: str, opcoes_validas: set[str]) -> str:
    """Lê uma opção do usuário garantindo que seja válida."""
    while True:
        escolha = input(prompt).strip()
        if escolha in opcoes_validas:
            return escolha
        slow("❌ Opção inválida! Tente novamente.")

# ==========================
# Persistência
# ==========================
def salvar_jogo(jogador: dict) -> None:
    """Salva o progresso em JSON e encerra o jogo (ou retorna)."""
    try:
        with open(ARQUIVO_SAVE, "w", encoding="utf-8") as arquivo:
            json.dump(jogador, arquivo, indent=4, ensure_ascii=False)
        slow("\n💾 Jogo salvo com sucesso!")
    except Exception as e:
        slow(f"\n❌ Erro ao salvar: {e}")

def carregar_jogo() -> dict | None:
    """Carrega o progresso salvo, se existir."""
    if not os.path.exists(ARQUIVO_SAVE):
        return None
    try:
        with open(ARQUIVO_SAVE, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        campos = {"nome", "vida", "ataque", "defesa", "poções", "xp", "level", "ouro", "totem", "fase_atual"}
        if not isinstance(dados, dict) or not campos.issubset(dados.keys()):
            raise ValueError("Arquivo de save inválido.")
        slow("💾 Save encontrado! Continuando sua aventura sagrada...\n")
        time.sleep(1)
        return dados
    except Exception as e:
        slow(f"❌ Erro ao carregar save ({e}). Iniciando novo jogo...\n")
        return None

# ==========================
# Criação e progressão
# ==========================
def criar_jogador() -> dict:
    """Cria o personagem do jogador."""
    slow("🌟 Bem-vindo, futuro salvador de Britânia! 🌟")
    nome = input("\nDigite o nome do seu Guerreiro Sagrado: ").strip()
    while not nome:
        nome = input("Por favor, digite um nome válido: ").strip()
    jogador = {
        "nome": nome,
        "vida": VIDA_BASE,
        "ataque": 180,
        "defesa": 90,
        "poções": 3,
        "xp": 0,
        "level": 1,
        "ouro": OURO_INICIAL,
        "totem": 0,
        "fase_atual": 1  # 1, 2, 3
    }
    slow(f"\n⚔️ Que sua jornada comece, {jogador['nome']}!\n")
    return jogador

def level_up(jogador: dict) -> None:
    """Evolui o jogador ao atingir XP suficiente, com cura total."""
    leveis_subidos = 0
    while jogador["xp"] >= XP_POR_LEVEL:
        jogador["xp"] -= XP_POR_LEVEL
        jogador["level"] += 1
        leveis_subidos += 1
        jogador["ataque"] += BONUS_ATAQUE_POR_LEVEL
        jogador["defesa"] += BONUS_DEFESA_POR_LEVEL
        jogador["vida"] = vida_maxima(jogador)

        # Totem concedido ao atingir nível 2 pela primeira vez
        if jogador["level"] == 2 and jogador["totem"] == 0:
            jogador["totem"] = 1
            slow("\n✨ Você recebeu o TOTEM DE RESSURGIMENTO!")
            slow("Se sua vida zerar, você voltará com vida cheia uma única vez.\n")

    if leveis_subidos > 0:
        slow(f"\n⬆️ LEVEL UP! Você subiu {leveis_subidos} nível(is). Agora é nível {jogador['level']}.")
        slow(f"✨ Ataque +{BONUS_ATAQUE_POR_LEVEL * leveis_subidos} | Defesa +{BONUS_DEFESA_POR_LEVEL * leveis_subidos} | Vida restaurada!\n")
        time.sleep(1)

# ==========================
# Loja / Mercador
# ==========================
def mercador(jogador: dict) -> None:
    """Loja de poções usando ouro."""
    while True:
        slow("\n🛒 Um mercador encapuzado surge das sombras...")
        slow(f"💰 Seu ouro: {jogador['ouro']} | 🧪 Poções: {jogador['poções']}")
        print(f"1 ➜ Comprar poção ({CUSTO_POCAO} ouro)")
        print("2 ➜ Vender totem (não recomendado) - 50% do valor fictício")
        print("3 ➜ Sair")
        escolha = entrada_opcao("\nEscolha: ", {"1", "2", "3"})
        if escolha == "1":
            if jogador["ouro"] >= CUSTO_POCAO:
                jogador["ouro"] -= CUSTO_POCAO
                jogador["poções"] += 1
                slow("🧪 Poção comprada com sucesso!")
            else:
                slow("❌ Ouro insuficiente, guerreiro...")
        elif escolha == "2":
            if jogador["totem"] > 0:
                jogador["totem"] -= 1
                ganho = 25
                jogador["ouro"] += ganho
                slow(f"💰 Você vendeu o Totem por {ganho} de ouro...")
            else:
                slow("❌ Você não possui Totem para vender.")
        else:
            slow("Até breve, viajante!")
            break

# ==========================
# Combate
# ==========================
def verificar_morte(jogador: dict) -> bool:
    """Verifica morte; usa Totem se houver. Retorna True se for Game Over."""
    if jogador["vida"] > 0:
        return False
    if jogador["totem"] > 0:
        jogador["totem"] -= 1
        jogador["vida"] = vida_maxima(jogador)
        slow("\n🔮 O TOTEM BRILHA INTENSAMENTE!")
        slow("✨ Você foi ressuscitado com vida máxima! O Totem se despedaça...\n")
        time.sleep(1.2)
        return False
    slow("\n💀 Seu corpo cai... a escuridão toma conta...")
    slow("💀 GAME OVER - Você foi derrotado nas profundezas de Britânia.")
    time.sleep(2)
    return True

def batalha(jogador: dict, inimigo: dict) -> bool:
    """
    Sistema de batalha turno a turno.
    Retorna True se jogador venceu, False se o jogador morreu (Game Over handled).
    """
    vida_inimigo = inimigo["vida"]
    nome_inimigo = inimigo["nome"]
    slow(f"\n⚔️ Um {nome_inimigo} bloqueia seu caminho!\n")
    time.sleep(0.7)

    while vida_inimigo > 0 and jogador["vida"] > 0:
        print("\n" + "=" * 52)
        print(f"❤️ Vida: {jogador['vida']}/{vida_maxima(jogador)} | 🧪 Poções: {jogador['poções']} | 💰 Ouro: {jogador['ouro']} | 🔮 Totem: {jogador['totem']}")
        print(f"{nome_inimigo} ❤️ Vida: {vida_inimigo}")
        print("=" * 52)
        print("1 ⚔️ Atacar")
        print(f"2 🧪 Usar poção (+{CURA_POCAO} HP)")
        print("3 🛡️ Defender (reduz muito o próximo dano)")
        print("4 💾 Salvar e voltar ao menu")
        escolha = entrada_opcao("\n➤ Sua ação: ", {"1", "2", "3", "4"})

        defendeu = False

        # Ação do jogador
        if escolha == "1":
            variacao = random.randint(-25, 25)
            dano = max(jogador["ataque"] + variacao, 0)
            vida_inimigo -= dano
            slow(f"💥 Você ataca com fúria! ({dano} de dano)")
        elif escolha == "2":
            if jogador["poções"] > 0:
                jogador["poções"] -= 1
                jogador["vida"] = min(jogador["vida"] + CURA_POCAO, vida_maxima(jogador))
                slow(f"🧪 Você bebe uma poção e recupera {CURA_POCAO} de vida!")
            else:
                slow("❌ Você não tem poções!")
                continue
        elif escolha == "3":
            slow("🛡️ Você ergue o escudo e se prepara para o impacto...")
            defendeu = True
        elif escolha == "4":
            salvar_jogo(jogador)
            slow("Voltando ao menu principal...")
            time.sleep(0.7)
            return False  # volta ao menu sem marcar vitória

        # Ataque do inimigo (se ainda vivo)
        if vida_inimigo > 0:
            variacao_inimigo = random.randint(-20, 20)
            dano_base = inimigo["ataque"] + variacao_inimigo
            if defendeu:
                dano_recebido = max(dano_base - jogador["defesa"] * 2, 5)
            else:
                dano_recebido = max(dano_base - jogador["defesa"], 10)
            jogador["vida"] -= dano_recebido
            slow(f"⚔️ {nome_inimigo} ataca e causa {dano_recebido} de dano!")

        # Checar morte após turno completo
        if verificar_morte(jogador):
            return False

    # Vitória!
    if vida_inimigo <= 0:
        slow(f"\n🏆 {nome_inimigo} foi derrotado!")
        xp_ganho = random.randint(35, 55)
        ouro_ganho = random.randint(30, 70)
        # pequenos ajustes dependendo do inimigo
        xp_ganho = int(xp_ganho * inimigo.get("xp_mul", 1.0))
        ouro_ganho = int(ouro_ganho * inimigo.get("ouro_mul", 1.0))
        jogador["xp"] += xp_ganho
        jogador["ouro"] += ouro_ganho
        slow(f"✨ +{xp_ganho} XP | +{ouro_ganho} ouro")
        level_up(jogador)
        time.sleep(0.5)
        return True

    return False

# ==========================
# Fases do jogo
# ==========================
def fase_1(jogador: dict) -> bool:
    """Fase 1: Goblins — 3 encontros simples + boss menor."""
    slow("\n🌑 FASE 1 — AS FLORESTAS DA ESCURIDÃO 🌑\n")
    slow("Você desperta em meio a árvores retorcidas, com um céu vermelho-sangue ao fundo...")
    slow("Seu objetivo: atravessar a floresta e derrotar o guardião do Portão do Abismo!\n")
    time.sleep(0.9)

    inimigos_comuns = [
        {"nome": "Goblin das Sombras", "vida": 950, "ataque": 120, "xp_mul": 0.9, "ouro_mul": 0.8},
        {"nome": "Lobo Demoníaco", "vida": 1250, "ataque": 160, "xp_mul": 1.0, "ouro_mul": 1.0},
        {"nome": "Aberração das Trevas", "vida": 1600, "ataque": 200, "xp_mul": 1.1, "ouro_mul": 1.1},
    ]

    for i in range(1, 4):
        slow(f"\nAvançando pela floresta... ({i}/3)")
        inimigo = random.choice(inimigos_comuns)
        venceu = batalha(jogador, inimigo)
        if not venceu and jogador["vida"] > 0:
            # jogador salvou e voltou ao menu
            return False
        if random.random() < CHANCE_MERCADOR:
            mercador(jogador)

    # Boss da fase
    slow("\n🌑 O chão treme... um rugido infernal ecoa pela floresta!")
    slow("🔥 Diante de você surge o guardião do Portão do Abismo...")
    time.sleep(1)
    boss = {"nome": "Guardião do Portão (Chefe da Floresta)", "vida": 3000, "ataque": 240, "xp_mul": 1.3, "ouro_mul": 1.2}
    venceu = batalha(jogador, boss)
    if not venceu and jogador["vida"] > 0:
        return False

    slow("\n🎉 FASE 1 CONCLUÍDA COM SUCESSO! 🎉")
    jogador["fase_atual"] = 2
    time.sleep(0.8)
    return True

def fase_2(jogador: dict) -> bool:
    """Fase 2: Demônios Vermelhos — encontros mais fortes + boss médio."""
    slow("\n🔥 FASE 2 — AS PLANÍCIES EM CHAMAS 🔥\n")
    slow("As chamas cobrem as planícies. Demônios menores e elite patrulham a região.")
    slow("Seu objetivo aqui: derrotar os Demônios Vermelhos e fechar o portal secundário.\n")
    time.sleep(0.9)

    inimigos_comuns = [
        {"nome": "Demônio Vermelho Soldado", "vida": 2200, "ataque": 260, "xp_mul": 1.2, "ouro_mul": 1.1},
        {"nome": "Demônio Fornalha", "vida": 2600, "ataque": 300, "xp_mul": 1.3, "ouro_mul": 1.2},
        {"nome": "Cavaleiro Sombrio", "vida": 3200, "ataque": 340, "xp_mul": 1.4, "ouro_mul": 1.3},
    ]

    for i in range(1, 4):
        slow(f"\nMarchando pelas planícies... ({i}/3)")
        inimigo = random.choice(inimigos_comuns)
        venceu = batalha(jogador, inimigo)
        if not venceu and jogador["vida"] > 0:
            return False
        if random.random() < CHANCE_MERCADOR:
            mercador(jogador)

    # Boss da fase
    slow("\n💥 Um portal titânico se abre... o Demônio Vermelho Elite surge!")
    boss = {"nome": "Demônio Vermelho Elite – Guardião do Portal", "vida": 5200, "ataque": 420, "xp_mul": 1.6, "ouro_mul": 1.4}
    venceu = batalha(jogador, boss)
    if not venceu and jogador["vida"] > 0:
        return False

    slow("\n🎉 FASE 2 CONCLUÍDA! Você fechou o portal secundário.")
    jogador["fase_atual"] = 3
    time.sleep(0.8)
    return True

def fase_3(jogador: dict) -> bool:
    """Fase 3: Boss Final — várias ondas + boss final poderoso."""
    slow("\n♛ FASE 3 — O ABISMO DO REI DOS DEMÔNIOS ♛\n")
    slow("Você chega ao Portão do Abismo. Sombras se reúnem — a presença do Rei dos Demônios é palpável.")
    slow("Prepare-se: ondas de elite surgirão antes do confronto final.\n")
    time.sleep(1)

    ondas = [
        [ {"nome": "Soldado Abissal", "vida": 1800, "ataque": 200, "xp_mul": 1.1, "ouro_mul": 1.0},
          {"nome": "Soldado Abissal", "vida": 1800, "ataque": 200, "xp_mul": 1.1, "ouro_mul": 1.0} ],
        [ {"nome": "Cavaleiro do Abismo", "vida": 2800, "ataque": 320, "xp_mul": 1.3, "ouro_mul": 1.2},
          {"nome": "Aberração Abissal", "vida": 2600, "ataque": 300, "xp_mul": 1.3, "ouro_mul": 1.2} ],
        [ {"nome": "General Abissal", "vida": 4200, "ataque": 420, "xp_mul": 1.6, "ouro_mul": 1.4} ]
    ]

    for idx, onda in enumerate(ondas, start=1):
        slow(f"\n🌊 Onda {idx} se aproxima!")
        for inimigo in onda:
            venceu = batalha(jogador, inimigo)
            if not venceu and jogador["vida"] > 0:
                return False
            if random.random() < CHANCE_MERCADOR:
                mercador(jogador)

    # Boss final
    slow("\n🔥 O ABISMO TREME: O REI DOS DEMÔNIOS DESCE AO SEU ENCONTRO! 🔥")
    boss = {"nome": "Rei dos Demônios – Guardião do Portão", "vida": 16500, "ataque": 520, "xp_mul": 2.5, "ouro_mul": 2.0}
    venceu = batalha(jogador, boss)
    if not venceu and jogador["vida"] > 0:
        return False

    slow("\n🏆 VOCÊ DERROTOU O REI DOS DEMÔNIOS! BRITÂNIA FOI SALVA (POR AGORA)...")
    jogador["fase_atual"] = 4  # completou o jogo
    time.sleep(1.2)
    return True

# ==========================
# Treinar (grind)
# ==========================
def treinar(jogador: dict) -> None:
    """Área de treino: confrontos opcionais que não avançam fase."""
    slow("\n🏹 ZONA DE TREINO — Melhore suas habilidades sem avançar a história.")
    slow("Cada treino te dá XP e ouro, mas inimigos são fracos comparados à fase principal.")
    while True:
        print("\n1 ➜ Lutar (1 encontro)")
        print("2 ➜ Lutar x3 (3 encontros rápidos)")
        print("3 ➜ Voltar ao menu")
        escolha = entrada_opcao("\nEscolha: ", {"1", "2", "3"})
        if escolha == "3":
            break
        encontros = 1 if escolha == "1" else 3
        for i in range(encontros):
            inimigo = {"nome": "Dummies de Treino", "vida": 900 + jogador["level"] * 50, "ataque": 60 + jogador["level"] * 5, "xp_mul": 0.8, "ouro_mul": 0.5}
            venceu = batalha(jogador, inimigo)
            if not venceu:
                # se salvou e voltou ao menu, sai do treino
                return
        slow("\n✅ Treino concluído. Você pode treinar novamente ou voltar ao menu.")
        if random.random() < 0.3:
            slow("Um mercador de passagem aparece após seu treino.")
            mercador(jogador)

# ==========================
# Menu principal / loop do jogo
# ==========================
def mostrar_status(jogador: dict) -> None:
    slow(f"\n📊 STATUS — {jogador['nome']}")
    slow(f"Level: {jogador['level']} | XP: {jogador['xp']}/{XP_POR_LEVEL} | Vida: {jogador['vida']}/{vida_maxima(jogador)}")
    slow(f"Ataque: {jogador['ataque']} | Defesa: {jogador['defesa']} | Poções: {jogador['poções']} | Ouro: {jogador['ouro']} | Totem: {jogador['totem']}")
    slow(f"Fase atual: {jogador.get('fase_atual', 1)}")

def menu_principal(jogador: dict) -> None:
    while True:
        limpar_tela()
        slow("🌌 Bem-vindo ao mundo de Britânia...")
        slow("Um reino onde anjos caídos, demônios antigos e humanos lutam pelo destino final.\n")
        mostrar_status(jogador)
        print("\n= MENU PRINCIPAL =")
        print("1 ➜ Continuar/Avançar Fase")
        print("2 ➜ Treinar (grind)")
        print("3 ➜ Salvar jogo")
        print("4 ➜ Salvar e Sair")
        print("5 ➜ Sair sem salvar")
        escolha = entrada_opcao("\nEscolha: ", {"1", "2", "3", "4", "5"})

        if escolha == "1":
            fase = jogador.get("fase_atual", 1)
            if fase == 1:
                concluiu = fase_1(jogador)
                if concluiu:
                    slow("Você progrediu para a próxima fase.")
                time.sleep(0.8)
            elif fase == 2:
                concluiu = fase_2(jogador)
                if concluiu:
                    slow("Você progrediu para a próxima fase.")
                time.sleep(0.8)
            elif fase == 3:
                concluiu = fase_3(jogador)
                if concluiu:
                    slow("Você concluiu a campanha principal! Parabéns, guerreiro.")
                time.sleep(0.8)
            else:
                slow("\n✨ Você já completou todas as fases disponíveis. Parabéns!")
                time.sleep(1.2)
        elif escolha == "2":
            treinar(jogador)
        elif escolha == "3":
            salvar_jogo(jogador)
            time.sleep(0.8)
        elif escolha == "4":
            salvar_jogo(jogador)
            slow("Saindo... Até a próxima, Guerreiro Sagrado!\n")
            sys.exit()
        else:
            slow("Saindo sem salvar. Até a próxima!")
            # remover save se existir? não, só sair
            sys.exit()

# ==========================
# Início do jogo
# ==========================
def main() -> None:
    limpar_tela()
    slow("🌌 Bem-vindo ao mundo de Britânia...")
    slow("Você foi escolhido pelos deuses... um Guerreiro Sagrado com poder divino em suas veias!\n")
    time.sleep(0.6)

    jogador = carregar_jogo()
    if not jogador:
        jogador = criar_jogador()
    else:
        # garantir vida não maior que máximo
        jogador["vida"] = min(jogador.get("vida", vida_maxima(jogador)), vida_maxima(jogador))

    menu_principal(jogador)

if __name__ == "__main__":
    main()