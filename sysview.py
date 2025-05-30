#!/usr/bin/env python3
import os
import shutil
import subprocess
import socket
import urllib.request

# Paleta de Cores
CINZA = '\033[90m'
VERDE = '\033[92m'
AMARELO = '\033[93m'
AZUL = '\033[94m'
VERMELHO = '\033[91m'
RESET = '\033[0m'

def formatar_tamanho(bytes_valor):
    if bytes_valor <= 0:
        return "0 B"
    unidades = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while bytes_valor >= 1024 and i < len(unidades) - 1:
        bytes_valor /= 1024
        i += 1
    return f"{bytes_valor:.1f} {unidades[i]}"

def total_disco():
    total, _, _ = shutil.disk_usage("/")
    return formatar_tamanho(total)

def memoria_total_swap():
    saida = subprocess.check_output(["free", "-b"]).decode().splitlines()
    mem = int(saida[1].split()[1])
    swap = int(saida[2].split()[1])
    return formatar_tamanho(mem), formatar_tamanho(swap)

def tem_systemd():
    return os.path.exists("/run/systemd/system")

def servicos_ativos():
    if tem_systemd():
        try:
            saida = subprocess.check_output(["systemctl", "list-units", "--type=service", "--state=running"]).decode()
            return len([l for l in saida.splitlines() if ".service" in l])
        except subprocess.CalledProcessError:
            return "Erro"
    return "N/A"

def servicos_cron():
    if tem_systemd():
        saida = subprocess.getoutput("systemctl list-units --type=service | grep cron")
        return len([l for l in saida.splitlines() if "cron" in l])
    return "N/A"

def top_5_pastas(path='/'):
    print(f"\n{CINZA}→ Calculando uso de espaço em '{path}'... Isso pode levar alguns segundos...{RESET}")
    saida = subprocess.getoutput(f"du -h --max-depth=1 {path} 2>/dev/null | sort -hr | head -n 6")
    return saida.strip().splitlines()[1:]

def uptime():
    return subprocess.getoutput("uptime -p")

def uso_cpu():
    return subprocess.getoutput("top -bn1 | grep 'Cpu(s)'")

def firewall_status():
    status = subprocess.getoutput("ufw status")
    linhas = status.splitlines()
    ativo = "Ativo" if "Status: active" in status else "Inativo"
    regras = [l for l in linhas[2:]] if len(linhas) > 2 else ["Nenhuma regra definida"]
    return ativo, regras

def usuarios_logados():
    return subprocess.getoutput("who")

def ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Não encontrado"

def ip_externo():
    try:
        with urllib.request.urlopen('https://api.ipify.org') as response:
            return response.read().decode()
    except:
        return "Não encontrado"

def atualizacoes_disponiveis():
    saida = subprocess.getoutput("apt list --upgradable 2>/dev/null | grep -v Listing")
    linhas = saida.splitlines()
    return len(linhas), linhas[:5]

def logs_criticos():
    return subprocess.getoutput("journalctl -p 3 -n 5 --no-pager") if tem_systemd() else "N/A"

def cabecalho():
    print("\033c", end="")  # clear
    print(f"{AZUL}+{'=' * 65}+{RESET}")
    print(f"{VERMELHO}              🔥 DASHBOARD DO SISTEMA UBUNTU 🔥{RESET}")
    print(f"{AZUL}+{'=' * 65}+{RESET}")

def main():
    cabecalho()

    total_mem, total_swap = memoria_total_swap()
    fw_status, fw_regras = firewall_status()
    atualizacoes, lista_atualizacoes = atualizacoes_disponiveis()

    print(f"\n{AZUL}:: RECURSOS DO SISTEMA ::{RESET}")
    print(f"{VERDE}→ DISCO TOTAL        : {AMARELO}{total_disco()}{RESET}")
    print(f"{VERDE}→ MEMÓRIA TOTAL      : {AMARELO}{total_mem}{RESET}")
    print(f"{VERDE}→ SWAP TOTAL         : {AMARELO}{total_swap}{RESET}")
    print(f"{VERDE}→ SERVIÇOS ATIVOS    : {AZUL}{servicos_ativos()}{RESET}")
    print(f"{VERDE}→ SERVIÇOS CRON      : {AZUL}{servicos_cron()}{RESET}")

    print(f"\n{AZUL}:: ESTADO DO SISTEMA ::{RESET}")
    print(f"{VERDE}→ UPTIME             : {CINZA}{uptime()}{RESET}")
    print(f"{VERDE}→ USO CPU            : {CINZA}{uso_cpu()}{RESET}")

    print(f"\n{AZUL}:: REDE ::{RESET}")
    print(f"{VERDE}→ IP LOCAL           : {AMARELO}{ip_local()}{RESET}")
    print(f"{VERDE}→ IP EXTERNO         : {AMARELO}{ip_externo()}{RESET}")

    print(f"\n{AZUL}:: FIREWALL (UFW) ::{RESET}")
    print(f"{VERDE}→ STATUS             : {VERMELHO if fw_status == 'Inativo' else VERDE}{fw_status}{RESET}")
    print(f"{VERDE}→ REGRAS             :{RESET}")
    for r in fw_regras:
        print(f"   {CINZA}- {r}{RESET}")

    print(f"\n{AZUL}:: USUÁRIOS LOGADOS ::{RESET}")
    print(f"{CINZA}{usuarios_logados()}{RESET}")

    print(f"\n{AZUL}:: ATUALIZAÇÕES DISPONÍVEIS ::{RESET}")
    print(f"{VERDE}→ QTD PACKS          : {AMARELO}{atualizacoes}{RESET}")
    for at in lista_atualizacoes:
        print(f"{CINZA}  - {at}{RESET}")

    print(f"\n{AZUL}:: ÚLTIMOS LOGS CRÍTICOS ::{RESET}")
    print(f"{CINZA}{logs_criticos()}{RESET}")

    print(f"\n{AZUL}:: TOP 5 PASTAS MAIS CHEIAS EM / ::{RESET}")
    for linha in top_5_pastas():
        print(f"{AZUL}→ {linha}{RESET}")

    print(f"\n{AZUL}+{'=' * 65}+{RESET}")

if __name__ == "__main__":
    main()
